import numpy as np
import pandas as pd
from ValueCont import *
from OpCont import *
from NetScheme import *
from SplineParam import *

class OpGraph:
    # в этом классе строим граф операций с переменными
    def __init__(self, net_scheme : NetScheme, op_cont : OpCont, value_cont : ValueCont, spline_param = None):
        self.net_scheme = net_scheme
        self.op_cont = op_cont
        self.value_cont = value_cont
        self.input_value = []
        self.psi_scheme = []
        self.spline_param = spline_param
    
    def created_graph(self):
        for level in range(self.net_scheme.deep):
            self.created_level(level)

    def created_level(self, level_number):
        if level_number !=  (self.net_scheme.deep - 1):
            line = range(self.net_scheme.scheme[level_number+1]) # np.linspace(0, self.net_scheme.scheme[level_number+1] - 1, self.net_scheme.scheme[level_number+1])
        if  level_number ==  (self.net_scheme.deep - 1):
            line = [-1]
        
        if level_number == 0:
            for q in range(self.net_scheme.scheme[0]):
                name = 'Input' + str(q)   
                self.value_cont.created_value(-q, value=0, name=name, value_type=Input()) 


        for q_upper in line:
            for q_now in range(self.net_scheme.scheme[level_number]):
                psi_number = [level_number, q_upper, q_now]
                if level_number != 0:
                    op_in_sum = []
                    ido_in_sum = []
                    value_in_psi_sum = []

                    for q in range(self.net_scheme.scheme[level_number-1]):
                        op = self.op_cont.search_for_psi_number([level_number - 1, q_now, q])
                        op_in_sum.append(op)
                        ido_in_sum.append(op.ido)
                        value_in_psi_sum.append(op.out_value)

                    future_ido_psi_sum = self.op_cont.get_future_ido()
                    value_out = self.value_cont.created_value(future_ido_psi_sum, name='Psi sum ' + str(q_upper))
                    op_in = self.op_cont.created_op(type_of_op=Sum(), input_op_id=ido_in_sum, last_op=False, in_values=value_in_psi_sum, out_value=value_out, psi_number=psi_number)
                    value_in = value_out
                
                input_op_id_act_func = [-1]

                if level_number == 0:
                    value_in = self.value_cont.find_for_ido(-q_now)[0]
                    input_op_id_act_func = [-1]
                else:
                    input_op_id_act_func = [op_in.ido]

                future_ido = self.op_cont.get_future_ido()    
                name2 = 'ActFunc(Input ' + str(q_now) + ')'
                value_out = self.value_cont.created_value(future_ido, value=0, name=name2)
                op_act = self.op_cont.created_op(type_of_op=ActFunc(), input_op_id=input_op_id_act_func, last_op=False, in_values=[value_in], out_value=value_out, psi_number=psi_number)

                future_ido_for_prod = self.op_cont.get_future_ido()
                value_wb = self.value_cont.created_value(future_ido_for_prod, value=0, name='wb' + str(q_now), value_type=Weight())
                name_for_prod = 'wb * ActFunc(Input ' + str(q_now) + ')'
                value_prod_res = self.value_cont.created_value(future_ido_for_prod, value=0, name=name_for_prod)
                op_prod_act_func = self.op_cont.created_op(type_of_op=Prod(), input_op_id=[op_act.ido], in_values=[value_in, value_wb], out_value=value_prod_res, psi_number=psi_number)
                
                input_op_id_spline = [-1]
                if level_number != 0:
                    input_op_id_spline = [op_in.ido]

                future_ido_for_spline = self.op_cont.get_future_ido()
                value_spline = self.value_cont.created_value(future_ido_for_spline, value=0, name='Spline (Input ' + str(q_now) + ')')
                value_spline_c_in = []
                for q in range(self.spline_param.c_len): # коэффициенты сплайна
                    name_s = 'Spline c' + str(q)
                    # ИСПРАВИТЬ VALUE на другое
                    value_spline_coeff = self.value_cont.created_value(future_ido_for_spline, value=0, name=name_s, value_type=CoeffSpline())
                    value_spline_c_in.append(value_spline_coeff)
                op_spline = self.op_cont.created_op(type_of_op=Spline(), input_op_id=input_op_id_spline, last_op=False, in_values=[value_in, value_spline_c_in], out_value=value_spline, psi_number=psi_number)

                future_ido_for_prod_spline = self.op_cont.get_future_ido()
                value_ws = self.value_cont.created_value(future_ido_for_prod_spline, value=0, name='ws' + str(q_now), value_type=WeightSpline())
                name_for_prod_spline = 'ws * Spline(Input ' + str(q_now) + ')'
                value_prod_spline = self.value_cont.created_value(future_ido_for_prod_spline, value=0, name=name_for_prod_spline)
                op_prod_spline = self.op_cont.created_op(type_of_op=Prod(), input_op_id=[op_spline.ido], last_op=False, in_values=[value_ws, value_spline], out_value=value_prod_spline, psi_number=psi_number)

                future_ido_node = self.op_cont.get_future_ido()
                if  level_number ==  (self.net_scheme.deep - 1):
                    value_node = self.value_cont.created_value(future_ido_node, name='Sum node ' + str(q_now), value_type=Output())
                else:
                    value_node = self.value_cont.created_value(future_ido_node, name='Sum node ' + str(q_now))

                op_node = self.op_cont.created_op(type_of_op=Sum(), input_op_id=[op_prod_act_func.ido, op_prod_spline.ido], last_op=True, in_values=[op_prod_act_func.out_value, op_prod_spline.out_value], out_value=value_node, psi_number=psi_number)
                    
    def main(self):
        self.created_graph()

class VisualOpGraph:
    def __init__(self, op_graph:OpGraph):
        self.op_graph = op_graph
        self.op_cont = op_graph.op_cont
        self.str_count = ''

    def visualGraph(self):
        visual_op_arr = []
        for q in range(self.op_graph.net_scheme.scheme[-1]):
            psi_number = [self.op_graph.net_scheme.deep - 1, -1, q]
            op = self.op_cont.search_for_psi_number(psi_number)
            visual_op_arr.append(op)

        for op in visual_op_arr:
            self.visualOpNode(op)

        logs = open("D:/научная работа/СТАТЬИ В РАБОТЕ/СТАТЬЯ СЕТИ Колмогорова Арнольда/log.txt", "w+")
        logs.write(self.str_count)
        logs.close()

    def visualOpNode(self, op_node):
        space_value = self.op_graph.net_scheme.deep - op_node.psi_number[0]

        self.str_count = self.str_count + '\n' + '\t'*space_value  +'Psi number = ' + str(op_node.psi_number)
        self.str_count = self.str_count + '\n' + '\t'*space_value  +'Name = ' + str(op_node.out_value.name)
        self.str_count = self.str_count + '\n' + '\t'*space_value  +'Type = ' + str(type(op_node.out_value.value_type))
        self.str_count = self.str_count + '\n' + '\t'*space_value +'Ido = ' + str(op_node.ido)
        self.str_count = self.str_count + '\n' + '\t'*space_value  +'IN IDO:' + str(op_node.ido) + ' = {'
        if (op_node.psi_number[0] == 0) and (op_node.input_op_id == [-1]):
           self.str_count = self.str_count + '\n' + '\t'*space_value  +'Input'
        else:
            for ido in op_node.input_op_id:
                self.visualOpNode(self.op_cont.search_for_ido(ido))
        self.str_count = self.str_count + '\n' + '\t'*space_value + '} IDO:' + str(op_node.ido)

    def visualGraphCSV(self):
        max_col = self.op_graph.net_scheme.deep
        max_prod = []

        for q in range(self.op_graph.net_scheme.deep - 1):
            prod = self.op_graph.net_scheme.scheme[q] * self.op_graph.net_scheme.scheme[q + 1]
            max_prod.append(prod)

        max_row = max(max_prod)
        
        elements_line = [0] * max_col 
        data = np.array([[elements_line] * max_row][0]).tolist()

        visual_op_arr_ido = []

        for q in range(len(self.op_graph.op_cont.op)):
            if not (self.op_graph.op_cont.op[q].ido in visual_op_arr_ido):
                visual_op_arr_ido.append(self.op_graph.op_cont.op[q].ido)
                self.visualOpNodeLine(data, self.op_graph.op_cont.op[q])

        df = pd.DataFrame(data)
        df.to_csv('data.csv',  sep=';', index=False, header=False, mode='w+')


    def visualOpNodeLine(self, data, op_node:OpNode):
        if op_node.last_op != True:
            return

        disp_str = ""

        psi_number = op_node.psi_number

        col_in_table = psi_number[0]
        row_in_table = psi_number[2] + psi_number[1] * self.op_graph.net_scheme.scheme[psi_number[0]]

        disp_str = disp_str + "Psi number = " + str(psi_number)
        disp_str = disp_str + "; value = " + str(op_node.out_value.value)

        data[row_in_table][col_in_table] = disp_str

if __name__ == "__main__":
    op_cont = OpCont()
    val_cont = ValueCont()
    net_scheme = NetScheme([2, 3, 2, 1])
    spline_param = SplineParam(40, 0, 1, 40, 2)
    op_graph = OpGraph(net_scheme, op_cont, val_cont, spline_param=spline_param)
    op_graph.main()

    visual = VisualOpGraph(op_graph)
    visual.visualGraphCSV()
    