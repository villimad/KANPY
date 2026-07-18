import numpy as np
from ValueCont import *
from OpCont import *
from NetScheme import *
from OpGraph import *
from SplineParam import *
from ForwardCalc import *
from BackpropGraph import *
from scipy.optimize import minimize
from scipy.optimize import differential_evolution as de

class KANExp:
    def __init__(self):
        self.op_cont = OpCont()
        self.val_cont = ValueCont()
        self.net_scheme = NetScheme([1, 2, 2, 1])
        self.spline_param = SplineParam(15, 0, 4, 15, 3)
        self.op_graph = OpGraph(self.net_scheme, self.op_cont, self.val_cont, spline_param=self.spline_param)
        self.op_graph.main()

        self.input_line = np.linspace(0, 3, 10)
        self.output_line = np.exp(self.input_line)
        self.output_KAN = []
        self.record_output = False


    def init_values(self):
        self.input = []
        self.output = []
        self.coeff_spl = []
        self.weight = []

        for value in self.val_cont.values:
            if (type(value.value_type) == type(Input())):
                self.input.append(value)
                continue

            if (type(value.value_type) == type(Weight())): 
                value.value = np.random.uniform(-1, 1)
                self.weight.append(value)
                continue

            if (type(value.value_type) == type(WeightSpline())): 
                value.value = np.random.random()
                self.weight.append(value)
                continue

            if (type(value.value_type) == type(CoeffSpline())): 
                value.value = np.random.normal(loc=0, scale=0.1)
                self.coeff_spl.append(value)
                continue
                
            if (type(value.value_type) == type(Output())): 
                self.output.append(value)
                continue
    
    def init_x(self):
        x0 = []
        for q in range(len(self.coeff_spl)):
            x0.append(self.coeff_spl[q].value)

        for q in range(len(self.weight)):
            x0.append(self.weight[q].value)

        self.x0 = x0

        return x0
    
    def init_bounds(self):
        self.bounds = []
        for x_arg in self.x0:
            bound = (-1, 1)
            self.bounds.append(bound)

    def values_from_x(self, x):
        for q in range(len(self.coeff_spl)):
            self.coeff_spl[q].value = x[q]

        for q in range(len(self.weight)):
            self.weight[q].value = x[len(self.coeff_spl) - 1 + q]


    def solve_KAN(self):
        delta = 0
        for q in range(len(self.input_line)):
            self.input[0].value = self.input_line[q]
            calc = ForwardCalc(self.op_graph)
            calc.main()
            out_res = self.output[0].value
            if self.record_output == True:
                self.output_KAN.append(out_res)
            delta = delta + (out_res - self.output_line[q])**2
        return delta


    def start(self):
        self.init_values()
        self.init_x()
        self.init_bounds()


    def cell(self, x):
        self.values_from_x(x)
        res = self.solve_KAN()
        # print(res)
        return res

    def optim(self):
        self.start()
        x0 = self.init_x()
        res = minimize(self.cell, x0, method='L-BFGS-B', tol=10**(-12), options={'disp': True, 'maxiter': 300})
        # res = de(self.cell, self.bounds, disp=True, workers=-1, strategy='best1bin', maxiter=100, atol=10**(-12))
        print('res = ', res.x, 'cell = ', res.fun)

        self.values_from_x(res.x)
        self.record_output = True
        self.solve_KAN()

        
if __name__ == "__main__":
    cl = KANExp()
    # op_graph = cl.op_graph
    # cash = CashCont()
    # bp = BackpropGraph(op_graph, cash)
    # bp.main()
    
    cl.optim() 

    

    visual = VisualOpGraph(cl.op_graph)
    visual.visualGraphCSV()


           

