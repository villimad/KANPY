import numpy as np
from scipy.optimize import differential_evolution as de
from scipy.optimize import shgo, minimize, direct
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.interpolate import BSpline as BS

class BSpline:
    def __init__(self, P, t, k):
        # P - array control points
        # t - non-decreasing sequence of real numbers
        # k - order of the polynomial segments of the B-spline curve
        self.P = P
        self.t = t
        self.k = k
    
    def get_for_x(self, x):
        self.x = x    
    
    def apruv_range_t(self):
        if (len(self.t)) >= (len(self.P) + self.k + 1):
            return True
        else:
            return False
    
    def create_N_array(self):
        # Normalized B-spline blending functions
        if not self.apruv_range_t():
            print("Error with t interval")
            return
        
        self.N = np.zeros((self.k + 1, len(self.P) + 1))
        for k in range(0, self.k+1):
            i_max = self.k 
            for i in range(len(self.P)):
                if k==0:
                    if (self.t[i] <= self.x) and (self.t[i+1] > self.x):
                        self.N[0][i] = 1.0
                    else:
                        self.N[0][i] = 0.0
                    continue
                if k!=0:
                    A = ((self.x - self.t[i]) / (self.t[i + k] - self.t[i])) * self.N[k-1][i]
                    B = ((self.t[i+k+1] - self.x) / (self.t[i+k+1] - self.t[i+1])) * self.N[k-1][i+1]
                    self.N[k][i] = A + B
                    
    def sol_sum(self):
        res = 0.0
        for q in range(len(self.P)):
            res = res + self.N[self.k][q] * self.P[q]
        return res
               
    def main(self, x):
        self.get_for_x(x)
        self.create_N_array()
        return self.sol_sum()  

class OptimSpline:
    def __init__(self, a, b, k):
        self.interv = np.linspace(a, b, 40)
        self.k = k
        
    def spline_res(self, x):
        # cl = BSpline(x, self.interv, self.k)
        # y = np.linspace(self.interv[0], self.interv[-1], 40)
        # res = [abs(cl.main(y[q]) - np.sin(y[q])) for q in range(len(y))]
        # # print('res = ', sum(res))
        # return sum(res)

        spl = BS(self.interv, x, self.k)
        y = np.linspace(self.interv[0], self.interv[len(self.interv) - self.k - 1], len(self.interv))
        res = [(spl(y[q]) - np.sin(y[q]))**2 for q in range(len(y))]
        # print('res = ', sum(res))
        return sum(res)
    
    def cell(self, x):
        res = self.spline_res(x)
        return res
    
    def create_bounds(self):
        bounds = []
        for q in range(len(self.interv) - self.k - 1):
            new_bound = (-1000, 1000)
            bounds.append(new_bound)
        return bounds

    def get_x0(self):
        x0_arr = []
        for _ in range(len(self.interv) - self.k - 1):
            x0_arr.append(np.random.randint(-100, 100)) 
        return x0_arr
        
    def optim(self):
        bounds = self.create_bounds()
        x0 = self.get_x0()
        # res = de(self.cell, bounds, disp=True, workers=-1, strategy='best1bin', maxiter=3000, atol=10**(-12))
        # res = shgo(self.cell, bounds, options={'disp': True, 'workers': 4})
        res = minimize(self.cell, x0, method='trust-constr', tol=10**(-12), options={'disp': True, 'maxiter': 10000})
        # res = direct(self.cell, bounds)
        print('res = ', res.x, 'cell = ', res.fun)


if __name__ == "__main__":
    cl = OptimSpline(0, 10, 3)
    cl.optim()
