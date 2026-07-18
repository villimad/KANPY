import numpy as np
from ValueCont import *
from OpCont import *
from NetScheme import *
from OpGraph import *
from SplineParam import *
from ForwardCalc import *
from scipy.optimize import minimize
from scipy.optimize import differential_evolution as de

class RandomCalc:
    def __init__(self, input_apr):
            self.op_cont = OpCont()
            self.val_cont = ValueCont()
            self.net_scheme = NetScheme([3, 2, 2])
            self.spline_param = SplineParam(20, 0, 1, 20, 2)
            self.op_graph = OpGraph(self.net_scheme, self.op_cont, self.val_cont, spline_param=self.spline_param)
            self.op_graph.main()

            self.input_apr = input_apr



    def init_values(self):
        self.input_val = []
        self.output_val = []

        for value in self.val_cont.values:
            if (type(value.value_type) == type(Input())):
                self.input_val.append(value)   
                continue

            if (type(value.value_type) == type(Weight())): 
                value.value = np.random.random() * 10
                continue

            if (type(value.value_type) == type(CoeffSpline())): 
                value.value = np.random.random() * 10
                continue
                
            if (type(value.value_type) == type(Output())): 
                self.output_val.append(value)
                continue

        for q in range(len(self.input_val)):
            self.input_val[q].value = self.input_apr[q]

    def solve(self):
        self.init_values()
        calc = ForwardCalc(self.op_graph)
        calc.main()

        visual = VisualOpGraph(self.op_graph)
        visual.visualGraphCSV()

        for value in self.output_val:
            print('Output ', value.ido, ' = ', value.value)

if __name__ == "__main__":
    cl = RandomCalc([1, 2, 3])
    cl.solve()




        

        
