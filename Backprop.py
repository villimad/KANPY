import numpy as np
import pandas as pd
from collections import deque
from NetScheme import *
from OpCont import *
from OpGraph import *
from ValueCont import *
from scipy.interpolate import BSpline


class BackpropTable:
    def __init__(self):
        self.table = dict()
    
    def push_in_table(self, value_output, value_for_der, value):
        id_node = (value_output.idv, value_for_der.idv)
        self.table.update({id_node: value})

    def get_from_table(self, out_value_ido, der_value_ido):
        return self.table[(out_value_ido, der_value_ido)]

    def save_to_csv(self, name=''):
        df = pd.DataFrame.from_dict(self.table, orient='index')
        df.to_csv('backprop' + name + '.csv',  sep=';', header=False, mode='w+')

class BackpropBufferTable:
    # write for every nodes op_graph derivation for o_1 ... o_n
    # rewrite
    def __init__(self):
        self.table = dict()

    def push_in_table(self, op, value_output, value):
        id_table = (op.ido, value_output.idv)
        self.table.update({id_table: value})

    def get_from_table(self, op_ido, value_output_idv):
        # rewrite
        return self.table[(op_ido, value_output_idv)]

class Backprop:
    def __init__(self, op_graph:OpGraph, table:BackpropTable, buffer_table):
        self.op_cont = op_graph.op_cont
        self.value_cont = op_graph.value_cont
        self.table = table
        self.backprop_buffer_table = buffer_table
        self.op_graph = op_graph

    def create_start_ways_pool(self):
        self.ways_pool = deque()
        for value_out in self.value_cont.output_value:
            op = self.op_cont.op[value_out.ido]
            new_way = (-1, op.ido) # now_way it is turple = (ido prev operation, ido now operation)
            self.ways_pool.append(new_way)
            
    def main_cicle(self):
        ind = 0
        while True:
            ind = ind + 1
            if len(self.ways_pool) == 0:
                break
            now_way = self.ways_pool[0]
            if now_way[1] == -1: # if its input
                self.ways_pool.popleft()
                continue

            now_op = self.op_cont.search_for_ido(now_way[1])
            if isinstance(now_op.out_value.value_type, Output):
                self.der_output_node(now_op)
                
            if not isinstance(now_op.out_value.value_type, Output):
                self.der_operation_node(now_way)

            self.ways_pool.popleft()
            for ido in now_op.input_op_id:
                way = (now_op.ido, ido)
                self.ways_pool.append(way)

    def der_output_node(self, op):
        for value_output in self.value_cont.output_value:
            if value_output is op.out_value:
                self.table.push_in_table(value_output, op.out_value, 1)
                self.backprop_buffer_table.push_in_table(op, op.out_value, 1)
            else:
                self.table.push_in_table(value_output, op.out_value, 0)
                self.backprop_buffer_table.push_in_table(op, value_output, 0)

    def der_operation_node(self, now_way): # !!!!!!!!!
        ido = now_way[1]
        op = self.op_cont.search_for_ido(ido)
        self.pref_op(op)

    def pref_op(self, op):
        # for every operation
        pref_der_value = dict()
        for value_output in self.value_cont.output_value:
            idv = value_output.idv
            for ido in op.backward_chain:
                pref_op = self.op_cont.search_for_ido(ido)
                der_for_op = self.der_pref_operation(pref_op, op)
                der_res = self.backprop_buffer_table.get_from_table(ido, idv)

                try: 
                    pref_der_value[idv] = pref_der_value[idv] + der_res * der_for_op 
                except:
                    pref_der_value[idv] = der_res * der_for_op

        self.write_in_buffer_table(op, pref_der_value)

        # find derivation for every Weight or Spline or SWeight

        for value in op.in_values:
           self.der_for_value_in_op(op, value)

    def der_pref_operation(self, op1, op2):
        # dop1 / dop2
        if isinstance(op1.type_of_op, Sum):
            return self.der_sum(op1, op2)
        if isinstance(op1.type_of_op, Prod):
            return self.der_prod(op1, op2)
        if isinstance(op1.type_of_op, ActFunc):
            return self.der_actfunc(op1, op2)
        if isinstance(op1.type_of_op, Spline):
            return self.der_spline(op1, op2)

    def der_sum(self, op1, op2):
        return 1

    def der_prod(self, op1, op2):
        res = 1
        for ido in op1.input_op_id:
            if ido != op2.ido:
                value = self.op_cont.search_for_ido(ido).out_value.value
                res = res * value    
        return res

    def der_actfunc(self, op1, op2):
        value = op2.out_value.value
        res = self.sigma(value) + value * self.sigma(value) * (1 - self.sigma(value)) #добавить про производные по Output
        return res
    
    def der_spline(self, op1, op2):
        spline_param = self.op_graph.spline_param
        k = spline_param.k
        value_c_coeff = [val.value for val in op1.in_values[1]]
        t_line = np.linspace(spline_param.t_min, spline_param.t_max, spline_param.t_len)
        spl = BSpline(t_line, value_c_coeff, k)
        dspl_dx = spl(op1.in_values[0].value, nu=1)
        return dspl_dx

    def sigma(self, x):
        return 1 / (1 + np.exp(-x))

    def write_in_buffer_table(self, op, pref_der_value):
        for idv in pref_der_value.keys():
            value_output = self.value_cont.search_for_idv(idv)
            self.backprop_buffer_table.push_in_table(op, value_output, pref_der_value[idv])

    def der_for_value_in_op(self, op, value):
        # d(op) / d(value)
        if isinstance(op.type_of_op, Spline):
            return self.der_value_spline(op)
        if isinstance(op.type_of_op, Prod):
            return self.der_value_prod(op)
   
    def der_value_prod(self, op):
        for value in op.in_values:
            if isinstance(value.value_type, Weight) or isinstance(value.value_type, WeightSpline):
                if value.value == 0 and op.out_value.value != 0:
                    raise Exception('Not valid prod')
                else:
                    der_value = op.out_value.value / value.value
                for value_out in self.value_cont.output_value:
                    der_res = self.backprop_buffer_table.get_from_table(op.ido, value_out.idv) * der_value
                    self.table.push_in_table(value_out, value, der_res)    

    def der_value_spline(self, op):
        spline_param = self.op_graph.spline_param
        t_line = np.linspace(spline_param.t_min, spline_param.t_max, spline_param.t_len)
        k = spline_param.k
        x_point = [op.in_values[0].value]
        x_point = np.nan_to_num(x_point)
        jacobian_matrix = BSpline.design_matrix(x_point, t_line, k, extrapolate=True).toarray()

        for q in range(len(op.in_values[1])):
            der = jacobian_matrix[0][q]
            for value_out in self.value_cont.output_value:
                der_for_table = self.backprop_buffer_table.get_from_table(op.ido, value_out.idv) * der
                self.table.push_in_table(value_out, op.in_values[1][q], der_for_table)

    def get_all_derivation(self):
        self.create_start_ways_pool()
        self.main_cicle()

if __name__ == "__main__":

    op_cont = OpCont()
    val_cont = ValueCont()
    net_scheme = NetScheme([2, 3, 2, 1])
    spline_param = SplineParam(40, -1, 1, 40, 2)
    op_graph = OpGraph(net_scheme, op_cont, val_cont, spline_param=spline_param)
    op_graph.main()


    bt = BackpropTable()
    bbuffert = BackpropBufferTable()
    backprop = Backprop(op_graph, bt, bbuffert)

    backprop.get_all_derivation()
    bt.save_to_csv()

    