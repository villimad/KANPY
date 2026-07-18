import numpy as np

# class SplineB:
#     def __init__(self, c, w_b, w_s):
#         self.c = c
#         self.w_b = w_b
#         self.w_s = w_s
    
#     def b(self, x):
#         return x / (1 + np.exp(-x))
    
#     def spline(self, x, t, k):
#         n = len(t) - k - 1
#         assert (n >= k+1) and (len(self.c) >= n)
#         return sum(self.c[i] * self.B(x, k, i, t) for i in range(n))
    
#     def B(self, x, k, i, t):
#         if k == 0:
#             return 1.0 if t[i] <= x < t[i+1] else 0.0
#         if t[i+k] == t[i]:
#             c1 = 0.0
#         else:
#             c1 = (x - t[i]) / (t[i+k] - t[i]) * self.B(x, k-1, i, t)
#         if t[i+k+1] == t[i+1]:
#             c2 = 0.0
#         else:
#             c2 = (t[i+k+1] - x) / (t[i+k+1] - t[i+1]) * self.B(x, k-1, i+1, t)
#         return c1 + c2
    
#     def act_func(self, x):
#         ...

# class Graphgroup:
#     def __init__(self, d, w, c, t, k):
#         self.d = d
#         self.w = w
#         self.c = c
#         self.t = t
#         self.k = k

# class Graph:
#     def __init__(self, width, deep):
#         self.width = width
#         self.deep  = deep 
    
#     def init_graph(self):
#         self.groups = []
#         for d in range(self.deep):
#             self.groups.append([])
#             for w in range(self.width):
#                 self.groups[d].append([])
#         print("Array groups complited!")
        
#     def create_group(self, d, w, c, t, k):
#         self.groups[d][w] = Graphgroup(d, w, c, t, k)
        
#     def create_regular_cross(self, k, x_min, x_max, steps):
#         t = np.linspace(x_min, x_max, steps)
#         for d in range(self.deep):
#             for w in range(self.width):
#                 c = self.create_c_koeff(k)
#                 self.create_group(d, w, c, t, k)       
#         print("Regular cross complited!")
                
#     def create_c_koeff(self, rang):
#         return np.random.normal(0, 0.1, rang)

# type_of_neuron
# 'SplineB'
# 'input'
# 'output'

class NetElement:
    def __init__(self, type_of_group, d, w, input_numbers, output_numbers):
        self.type_of_group = type_of_group # тип нейрона
        self.d = d # порядок по глубине
        self.w = w # порядок по ширине
        self.input_numbers = input_numbers # массив идентификационных номеров входящих в нейрон
        self.output_numbers = output_numbers # массив идентификационных номеров в которые входит нейрон
    
class NetGraph:
    def __init__(self, input_deal, func_deal, output_deal):
        self.input_deal = input_deal # количество входов
        self.func_deal = func_deal # размерность по функциям
        self.output_deal = output_deal # количество выходов


# operation
# 'sum'
# 'activation_func'
# 'splineB'
# 'input'
# 'output'
# 'prod' (*)

class OpCont:
    # контейнер операций
    def __init__(self):
        self.op_id = []
        self.op = []
        self.future_ind = False # id занят future
    
    def _created_ido(self):
        if len(self.op_id) == 0:
            ido = 0
        else:
            ido = self.op_id[-1] + 1
        self.op_id.append(ido)
        return ido
    
    def get_future_ido(self):
        # будущий ido
        assert(self.future_ind == True)
        if len(self.op_id) == 0:
            ido = 0
        else:
            ido = self.op_id[-1] + 1
        self.future_ind = True
        return ido
    
    def created_op(self, group, type_of_op, input_op_id, last_op=True, in_values=None, out_values=None):
        self.future_ind = False
        ido = self._created_ido()
        op = OpNode(ido, group, type_of_op, input_op_id,  last_op, in_values, out_values)
        self.op_id.append(ido)
        self.op.append(op)
        return op
    
    def search_for_d_w_group(self, deep, width):
        # поиск id конечных операций для узла group
        ido_array = []
        for op in self.op:
            if (op.last_op == True) and (op.group == (deep, width)):
                ido_array.append(op.ido)
        return ido_array
            
class OpNode:
    def __init__(self, ido, group, type_of_op, input_op_id,  last_op=True, in_values=None, out_value=0):
        self.group = group # узел к которомум принадлежит узел операции (группа операций)
        self.type_of_op = type_of_op # тип операции
        self.input_op_id = input_op_id # узлы операции входящие в данный узел
        self.ido = ido # id узла
        self.last_op = last_op # эта операция последняя в узле?
        self.in_values = in_values # переменные на вход [list]
        self.out_value = out_value # переменная на выход
        
    def info(self):
        print('self.group = ', self.group)
        print('self.type_of_op = ', self.type_of_op)
        print('self.input_op_id = ', self.input_op_id)
        print('self.ido = ', self.ido)
        print('self.last_op = ', self.last_op)
        print('self.in_values = ', self.in_values)
        print('self.out_value = ', self.out_value)

class ValueCont:
    # контейнер переменных
    def __init__(self):
        self.values_id = []
        self.values = []
    
    def _created_idv(self):
        if len(self.values_id == 0) :
            idv = 0
        else:
            idv = self.values_id[-1] + 1
        self.values_id.append(idv)
        return idv
    
    def created_value(self, ido, value=0, name='Noname'):
        idv = self._created_idv()
        value = Value(idv, ido, value, name)
        self.values.append(value)
        return value

class Value:
    def __init__(self, idv, ido, value=0, name='Noname'):
        self.idv = idv # id величины
        self.ido = ido # id операции к которой пренадлежит величина
        self.value = value # величина внутри переменной
        self.name = name    

class OpGraph:
    # в этом классе строим граф операций с переменными
    def __init__(self, net_graph, op_cont, value_cont):
        self.net = net_graph
        self.input_deal = net_graph.input_deal
        self.func_deal = net_graph.func_deal
        self.output_deal = net_graph.output_deal
        self.op_cont = op_cont
        self.value_cont = value_cont
    
    def search_last_group_op(self, group):
        # поиск последней операции для узла
        # group (d, w) 
        for op in self.op_cont.op:
            if op.group == group and op.last_op == True:
                return op.ido
                   
    def create_op_graph(self):
        pass


    
    def create_op_graph2(self):
        pass
        # for d in range(self.deep):
        #     for w in range(self.width):
        #         if d==0:
        #             # если рассматриваемый узел входной
        #             type_of_op = 'input'
        #             group = (d, w)
        #             input_op_id = [-1]
        #             last_op = True
        #             value = 0
        #             op_id = self.op_cont.get_future_ido()
        #             name = str('input' + str(w))
        #             value = self.value_cont.created_value(op_id, value=0, name=name)
        #             self.op_cont.created_op(group, type_of_op, input_op_id, last_op=last_op, in_values=[value], out_value=value)   
                    
        #         if d!=0 and d!=self.deep-1:
        #             pass

                        


if __name__ == "__main__":
    op_cont = OpCont()
    val_cont = ValueCont()
    
             
                
                


