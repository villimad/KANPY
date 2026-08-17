import numpy as np
from NetScheme import *
from OpCont import *
from OpGraph import *
from ValueCont import *
from Backprop import *

class Initiator:
    def __init__(self, op_graph):
        self.op_graph = op_graph
        self.value_cont = op_graph.value_cont
        self.op_cont = op_graph.op_cont

    def init_value(self):
        for key in self.value_cont.values.keys():
            value = self.value_cont.values[key]
            if isinstance(value.value_type, Weight): 
                value.value = np.random.uniform(-1, 1)
                continue

            if isinstance(value.value_type, WeightSpline): 
                value.value = np.random.random()
                continue

            if isinstance(value.value_type, CoeffSpline): 
                value.value = np.random.normal(loc=0, scale=0.1)
                continue

class InitiatorFromData:
    pass

class InputCreate:
    def __init__(self, value_cont, input_data):
        self.value_cont = value_cont
        self.input_data = input_data # one row array

    def apruve_data(self):
        if len(self.input_data) != len(self.value_cont.input_value):
            raise Exception('Input dimensions is not apruve')
        return True

    def create(self):
        ind = 0
            
        for key in self.value_cont.input_value.keys():
            data = self.input_data[ind]
            self.value_cont.input_value[key] = data
            ind = ind + 1

    def main(self):
        self.apruve_data()
        self.create()
    