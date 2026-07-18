import numpy as np
from NetScheme import *
from OpCont import *
from OpGraph import *
from ValueCont import *


class BackpropGraph:
    def __init__(self, forward_op_graph, cash_cont):
        self.forward_op_graph = forward_op_graph
        self.cash_cont = cash_cont        

    def create_back_graph(self):
        for op in self.forward_op_graph.op_cont.op:
            self.get_op_der(op)
        
    def get_op_der(self, op):
        inner_op_array = []

        # if activation func after input
        if (len(op.input_op_id) == 1) and (op.input_op_id[0] == -1):
            return

        for inner_op_ido in op.input_op_id:
            inner_op_array.append(self.forward_op_graph.op_cont.search_for_ido(inner_op_ido))

        for in_op in inner_op_array:
            self.derivation(op, in_op)
    
    def derivation(self, op1, op2):
        # d(op1) / d(op2)
        
        search_res = self.cash_cont.search_in_cash(op1, op2)

        if search_res[0]:
            return

        if type(op1.type_of_op) == type(Sum()):
            self.calc_plus(op1, op2)

        if type(op1.type_of_op) == type(Prod()):
            self.calc_prod(op1, op2)

        if type(op1.type_of_op) == type(ActFunc()):
            self.calc_act_func(op1, op2)

        if type(op1.type_of_op) == type(Spline()):
            self.calc_spline(op1, op2)

    def calc_plus(self, op1, op2):
        # d(op1) / d(op2)
        op_cont = OpCont()
        value_cont = ValueCont()
        ido = op_cont.get_future_ido()
        value = value_cont.created_value(ido, value=op2.out_value.value)
        op = op_cont.created_op(type_of_op=DerivationPlus(), input_op_id=[-1], last_op=True, in_values=[value], out_value=[value])
        self.cash_cont.create_cash_node(op1, op2, op_cont, value_cont)

    def calc_prod(self, op1, op2):
        op_cont = OpCont()
        value_cont = ValueCont()
        
        in_ops = []
        in_values = []

        for ido in op1.input_op_id:
            op = self.forward_op_graph.op_cont.search_for_ido(ido)
            if not (op is op2):
                in_ops.append(op)
                in_values.append(op.out_value)

        ido = op_cont.get_future_ido()
        out_value = value_cont.created_value(ido)

        op_cont.created_op(type_of_op=DerivationProd(), input_op_id=[-1], last_op=True, in_values=in_values, out_value=out_value)
        self.cash_cont.create_cash_node(op1, op2, op_cont, value_cont)

    def calc_act_func(self, op1, op2):
        # d(op1) / d(op2)
        op_cont = OpCont()
        value_cont = ValueCont()

        ido = op_cont.get_future_ido()
        out_value = value_cont.created_value(ido)

        op = op_cont.created_op(type_of_op=DerivationSilu(), input_op_id=[-1], last_op=True, in_values=op1.in_values, out_value=out_value)
        self.cash_cont.create_cash_node(op1, op2, op_cont, value_cont)

    def calc_spline(self, op1, op2):
        # d(op1) / d(op2)
        # сделать производную по весам
        op_cont = OpCont()
        value_cont = ValueCont()

        ido = op_cont.get_future_ido()
        out_value = value_cont.created_value(ido)

        op = op_cont.created_op(type_of_op=DerivationSpline(), input_op_id=[-1], last_op=True, in_values=op1.in_values, out_value=out_value)
        self.cash_cont.create_cash_node(op1, op2, op_cont, value_cont)
   
    def main(self):
        self.create_back_graph()

class CashCont:
    def __init__(self):
        self.cash_node_array = []

    def create_cash_node(self, op1, op2, op_cont, value_cont):
        cash_node = CashNode(op1, op2, op_cont, value_cont)
        self.cash_node_array.append(cash_node)
        return cash_node

    def search_in_cash(self, op1, op2):
        if (len(self.cash_node_array) == 0):
            return (False, None)

        for cash in self.cash_node_array:
            if ((op1 is cash.op1) and (op2 is cash.op2)):
                return (True, cash)
            else:
                return (False, None)
                
class CashNode:
    def __init__(self, op1, op2, op_cont, value_cont):
        # d (op1) / d (op2)
        self.op1 = op1
        self.op2 = op2
        self.op_cont = op_cont
        self.value_cont = value_cont


