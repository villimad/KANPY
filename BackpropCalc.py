import numpy as np
from NetScheme import *
from OpCont import *
from OpGraph import *
from ValueCont import *
from BackpropGraph import *
from scipy.interpolate import BSpline

class BackpropCalc:
    def __init__(self, backprop_graph:BackpropGraph):
        self.backprop_graph = backprop_graph
        self.forward_op_graph = backprop_graph.forward_op_graph
        self.cash_cont = backprop_graph.cash_cont

    def calc_op_back_op_graph_all(self):
        self.complited_cash_node = []
        for cash_node in self.cash_cont.cash_node_array:
            op_cont = cash_node.op_cont
            value_cont = cash_node.value_cont
            self.calc_op_back_op_graph_ones(op_cont)

    def calc_op_back_op_graph_ones(self, op_cont):
        for op in op_cont.op:
            if type(op.type_of_op) == type(DerivationPlus()):
                self.calc_der_op_plus(op)
            if type(op.type_of_op) == type(DerivationProd()):
                self.calc_der_op_prod(op)
            if type(op.type_of_op) == type(DerivationSilu()):
                self.calc_der_op_silu(op)
            if type(op.type_of_op) == type(DerivationSpline()):
                self.calc_der_op_spline(op)

    def calc_der_op_plus(self, op):
        value = op.out_value
        value.value = 1

    def calc_der_op_prod(self, op):
        in_values = op.in_values
        result = 1
        for value in in_values:
            result = result * value.value
        op.out_value.value = result

    def calc_der_op_silu(self, op):
        in_value = op.in_values[0]
        dsilu_dx = self.sigma(in_value.value) + in_value.value * (1 - self.sigma(in_value.value))
        op.out_value.value = dsilu_dx

    def sigma(self, x):
        return 1 / (1 + np.exp(-x))

    def calc_der_op_spline(self, op):
        spline_param = self.forward_op_graph.spline_param
        k = spline_param.k
        value_c_coeff = [val.value for val in op.in_values[1]]
        t_line = np.linspace(spline_param.t_min, spline_param.t_max, spline_param.t_len)
        spl = BSpline(t_line, value_c_coeff, k)
        dspl_dx = spl(op.in_values[0], nu=1)[0]
        op.out_value = dspl_dx




    def create_graph_list(self):
        self.out_values = []
        self.weight = []
        self.c_coeff = []
        self.weight_spline = []

        for value in self.forward_op_graph.op_graph.value_cont:
            if type(Output()) == type(value.type_value):
                self.out_values.append(value)

            if type(Weight()) == type(value.type_value):
                self.weight.append(value)

            if type(CoeffSpline()) == type(value.type_value):
                self.c_coeff.append(value)

            if type(WeightSpline()) == type(value.type_value):
                self.weight_spline.append(value)        

    def get_der_for_out(self):
        for out_value in self.out_values:
            for weight in self.weight:
                self.get_value_der(out_value, weight)
            for c_coeff in self.c_coeff:
                self.get_value_der(out_value, c_coeff)
            for weight_spline in self.weight_spline:
                self.get_value_der(out_value, weight_spline)

    def get_value_der(self, value1, value2):
        pass
                
