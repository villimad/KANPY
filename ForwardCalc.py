import numpy as np
from ValueCont import *
from OpCont import *
from NetScheme import *
from OpGraph import *
from SplineParam import *
from scipy.interpolate import BSpline

class ForwardCalc:
    def __init__(self, op_graph):
        self.op_graph = op_graph
        self.complited_op = []
    
    def calc_node(self, op_node):
        # Calculation node for node type
        if type(op_node.type_of_op) == type(Sum()):
            self.calc_plus(op_node)

        if type(op_node.type_of_op) == type(Prod()):
            self.calc_prod(op_node)

        if type(op_node.type_of_op) == type(ActFunc()):
            self.calc_act_func(op_node)

        if type(op_node.type_of_op) == type(Spline()):
            self.calc_spline(op_node) 

    def calc_plus(self, op_node):
        values = op_node.in_values
        value_out_res = 0
        for q in range(len(values)):
            value_out_res = value_out_res + values[q].value
        op_node.out_value.value = value_out_res
        self.complited_op.append(op_node)

    def calc_prod(self, op_node):
        values = [val.value for val in op_node.in_values]
        value_out_res = 1
        for val in values:
            value_out_res = value_out_res * val
        op_node.out_value.value = value_out_res
        self.complited_op.append(op_node)

    def calc_act_func(self, op_node):
        # silu(x)
        value_in = op_node.in_values[0].value
        res = value_in / (1 + np.exp(-value_in))
        op_node.out_value.value = res
        self.complited_op.append(op_node)

    def calc_spline(self, op_node):
        # spline(x)
        value_x = op_node.in_values[0].value
        value_c_coeff = [val.value for val in op_node.in_values[1]]

        spline_param = self.op_graph.spline_param

        t_line = np.linspace(spline_param.t_min, spline_param.t_max, spline_param.t_len)
        k = spline_param.k
        spl = BSpline(t_line, value_c_coeff, k)
        
        op_node.out_value.value = spl(value_x)

        self.complited_op.append(op_node)

    def solve_graph(self):
        # graph
        op_cont = self.op_graph.op_cont
        for op in op_cont.op:
            if op in self.complited_op:
                continue
            self.calc_node(op)

    def main(self):
        self.solve_graph()

if __name__ == "__main__":

    op_cont = OpCont()
    val_cont = ValueCont()
    net_scheme = NetScheme([2, 3, 1])
    spline_param = SplineParam(40, 0, 1, 40, 2)
    op_graph = OpGraph(net_scheme, op_cont, val_cont, spline_param=spline_param)
    op_graph.main()

    calc = ForwardCalc(op_graph)
    calc.main()

    visual = VisualOpGraph(op_graph)
    visual.visualGraphCSV()
