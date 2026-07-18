class NetScheme:
    def __init__(self, param_array):
        self.scheme = param_array
        self.deep = len(param_array)
        self.input = param_array[0]
        self.output = param_array[-1]