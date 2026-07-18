import numpy as np

class SplineParam:
    def __init__(self, t_len, t_min, t_max, c_len, k):
        # t - knots
        # c - spline_koef
        # k - degree
        self.t_len = t_len
        self.t_min = t_min
        self.t_max = t_max
        self.c_len = c_len
        self.k = k
        
