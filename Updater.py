import numpy as np
import pandas as pd
from NetScheme import *
from OpCont import *
from OpGraph import *
from ValueCont import *
from Backprop import *
from ForwardCalc import *
from Initiator import *
import copy
from scipy.interpolate import BSpline

# planer learning rate
class Planer:
    pass

class StandartPlaner(Planer):
    def __init__(self, lr):
        self.lr = lr
        pass

    def calc_lr(self, t):
        return self.lr

class CosineWarmup(Planer):
    def __init__(self, lr_max, lr_min, T_total, T_warmup):
        self.lr_max = lr_max
        self.lr_min = lr_min
        self.T_total = T_total
        self.T_warmup = T_warmup

    def calc_lr(self, t):
        if t <= self.T_warmup:
            return self.lr_max * (t / self.T_warmup)

        if t > self.T_warmup:
            return self.lr_min + 0.5 * (self.lr_max - self.lr_min) * (1 + np.cos(np.pi * (t - self.T_warmup) / (self.T_total - self.T_warmup)))

# type of method
class MinimizeMethod:
    pass

class Adam(MinimizeMethod):
    def __init__(self, op_graph:OpGraph, planer:Planer, lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-8):
        self.value_cont = op_graph.value_cont
        self.beta_1 = beta_1
        self.beta_2 = beta_2
        self.epsilon = epsilon
        self.lr = lr
        self.t = 0
        self.first = True
        self.planer = planer

    def update(self, upd_table):
        self.t = self.t + 1

        self.lr = self.planer.calc_lr(self.t)

        keys = upd_table.table.keys()
        if self.first:
            self.m = np.zeros(len(keys)).tolist()
            self.v = np.zeros(len(keys)).tolist()
            self.first = False
        
        ind = 0

        for idv in keys:
            grad = upd_table.get_from_table(idv)
            self.m[ind] = self.beta_1 * self.m[ind] + (1 - self.beta_1) * grad
            self.v[ind] = self.beta_2 * self.v[ind] + (1 - self.beta_2) * (grad ** 2)

            m_corrected = self.m[ind] / (1 - self.beta_1 ** self.t)
            v_corrected = self.v[ind] / (1 - self.beta_2 ** self.t)

            value = self.value_cont.search_for_idv(idv)
            new_value = value.value - (self.lr / (np.sqrt(v_corrected) + self.epsilon)) * m_corrected
            value.value = new_value
            ind = ind + 1

class AdamMode(MinimizeMethod):
    def __init__(self, op_graph:OpGraph, lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=1e-8):
        self.value_cont = op_graph.value_cont
        self.beta_1 = beta_1
        self.beta_2 = beta_2
        self.epsilon = epsilon
        self.lr = lr
        self.t = 0
        self.first = True
        self.value_cont_h = copy.copy(self.value_cont)
        self.upd_table_h = None
        self.good_number = 0
        

    def put_updater(self, updater):
        self.updater = updater
        self.loss_values = self.updater.loss_values

    def apruve_ways(self):
        if self.loss_values[-1] > self.real_loss:
            self.good_number = 0
            self.lr = self.lr / 2
            self.upd_table = copy.copy(self.upd_table_h)
            self.value_cont = copy.copy(self.value_cont_h)
        else:
            self.good_number = self.good_number + 1
            if self.good_number == 5:
                self.lr = self.lr * 2
            else:
                self.real_loss = self.loss_values[-1]
            self.upd_table_h = copy.copy(self.upd_table)
            
        

    def update(self, upd_table):
        self.upd_table = upd_table
        self.t = self.t + 1

        if self.t > 1:
            self.apruve_ways()

        keys = self.upd_table.table.keys()

        if self.first:
            self.first = False
            self.upd_table_h = copy.copy(upd_table)
            self.m = np.zeros(len(keys)).tolist()
            self.v = np.zeros(len(keys)).tolist()
            self.real_loss = self.loss_values[-1]
            
        ind = 0

        for idv in keys:
            grad = self.upd_table.get_from_table(idv)
            self.m[ind] = self.beta_1 * self.m[ind] + (1 - self.beta_1) * grad
            self.v[ind] = self.beta_2 * self.v[ind] + (1 - self.beta_2) * (grad ** 2)

            m_corrected = self.m[ind] / (1 - self.beta_1 ** self.t)
            v_corrected = self.v[ind] / (1 - self.beta_2 ** self.t)

            value = self.value_cont.search_for_idv(idv)
            new_value = value.value - (self.lr / (np.sqrt(v_corrected) + self.epsilon)) * m_corrected
            value.value = new_value
            ind = ind + 1

            self.m_h = copy.copy(self.m)
            self.v_h = copy.copy(self.v)

class SGD(MinimizeMethod):
    def __init__(self, op_graph:OpGraph, lr=0.001):
        self.value_cont = op_graph.value_cont
        self.lr = lr
        self.t = 0

    def update(self, upd_table):
        self.t = self.t + 1
        keys = upd_table.table.keys()
        ind = 0

        for idv in keys:
            grad = upd_table.get_from_table(idv)
            value = self.value_cont.search_for_idv(idv)
            new_value = value.value - self.lr * grad
            value.value = new_value
            ind = ind + 1
    
class RMSprop(MinimizeMethod):
    def __init__(self, op_graph:OpGraph, lr=0.001, beta=0.9, epsilon=1e-8):
        self.value_cont = op_graph.value_cont
        self.lr = lr
        self.t = 0
        self.beta = beta
        self.epsilon = epsilon
        self.first = True

    def update(self, upd_table):
        self.t = self.t + 1
        keys = upd_table.table.keys()
        ind = 0

        if self.first:
            self.v = np.zeros(len(keys)).tolist()
            self.first = False

        for idv in keys:
            grad = upd_table.get_from_table(idv)
            value = self.value_cont.search_for_idv(idv)
            self.v[ind] = self.beta * self.v[ind] + (1 - self.beta) * (grad ** 2)
            new_value = value.value - (self.lr / (np.sqrt(self.v[ind]) + self.epsilon)) * grad
            value.value = new_value
            ind = ind + 1

class LBFGS(MinimizeMethod):
    def __init__(self, op_graph:OpGraph, lr=0.001, m=10):
        self.value_cont = op_graph.value_cont
        self.lr = lr
        self.t = 0
        self.m = m
        self.s_memory = []
        self.y_memory = []
        self.rho_memory = []
        
    def update(self, upd_table):
        pass 


# type of loss function
class LossFunction:
    pass

class MAE(LossFunction):
    # Mean Absolute Error
    def loss_func(self, y_out, y_real):
        y_out_np = np.array(y_out)
        y_real_np = np.array(y_real)
        loss = np.sum(np.abs(y_out_np - y_real_np)) / y_out_np.shape[0]
        return loss

    def der_loss_func(self, y_out, y_real):
        y_out_np = np.array(y_out)
        y_real_np = np.array(y_real)
        return np.sign(y_out_np - y_real_np) / y_out_np.shape[0]

class MSE(LossFunction):
    def loss_func(self, y_out, y_real):
        y_out_np = np.array(y_out)
        y_real_np = np.array(y_real)
        loss = np.sum((y_out_np - y_real_np)**2) / y_out_np.shape[0]
        return loss

    def der_loss_func(self, y_out, y_real):
        y_out_np = np.array(y_out)
        y_real_np = np.array(y_real)
        return 2 * (y_out_np - y_real_np)/ y_out_np.shape[0]
    
#type of method education
class EduMethod:
    pass

class AllData(EduMethod):
    pass

class MiniBatch(EduMethod):
    pass

class Updater:
    def __init__(self, op_graph:OpGraph, backprop:Backprop, data, method, loss_func, edu_method, minibatch_size=0):
        self.backprop_table = backprop.table
        self.method = method # method minimize
        self.loss_func = loss_func
        self.edu_method = edu_method
        self.data = data # data [[[], [], [], [] - point_args] , [[], [], [], [] - point_result]]
        self.updater_table_buffer = []
        self.op_graph = op_graph
        self.epoch = 0
        self.minibatch_size = minibatch_size
        self.backprop = backprop
        self.mini_batch = 0
        self.loss_values = []
        self.mini_batch = 0
        self.loss_minibatch = []

    def get_output_idv(self):
        # find output idv
        self.output_idv = []
        for value in self.op_graph.value_cont.output_value:
            self.output_idv.append(value.idv)

    def get_input_idv(self):
        # find input idv
        self.input_idv = []
        for value in self.op_graph.value_cont.input_value:
            self.input_idv.append(value.idv)

    def put_data_to_input(self, data_tuple):
        # put data from data tuple to input value
        ind = 0
        for key in self.op_graph.value_cont.input_value.keys():
            self.op_graph.value_cont.input_value[key].value = data_tuple[0][ind]
            ind = ind + 1

    def get_result_der_loss(self, data_res):
        y_out = []
        for out_idv in self.output_idv:
            value = self.op_graph.value_cont.search_for_idv(out_idv).value
            y_out.append(value)

        y_real = data_res
        result = self.loss_func.der_loss_func(y_out, y_real)
        if isinstance(self.edu_method, MiniBatch):
            self.loss_minibatch.append(self.loss_func.loss_func(y_out, y_real))
            if self.mini_batch == (self.minibatch_size - 1): ## ?? - 1
                self.loss_values.append(sum(self.loss_minibatch) / len(self.loss_minibatch)) # for tests
                self.loss_minibatch.clear()
        else:
            self.loss_values.append(self.loss_func.loss_func(y_out, y_real))
        return result
        
    def get_new_value(self, idv_out, idv_value, data_tuple):
        # der_loss = self.get_result_der_loss(data_tuple[1])
        out_number = self.out_reverse_chain[idv_out]
        der_out_loss = self.der_loss[out_number]
        der_value = self.backprop_table.get_from_table(idv_out, idv_value)
        der_result = der_value * der_out_loss
        return der_result

    def create_updater_table(self, data_tuple):
        # find new value for derivation and put in updater table
        self.updater_table_buffer.append(UpdaterTable())
        self.der_loss = self.get_result_der_loss(data_tuple[1])
        for key in self.backprop_table.table.keys():
            new_value = self.get_new_value(key[0], key[1], data_tuple)
            try:
                old_value = self.updater_table_buffer[-1][key[1]]
                self.updater_table_buffer[-1].table[key[1]] = old_value + new_value
            except:
                self.updater_table_buffer[-1].table[key[1]] = new_value
        return self.updater_table_buffer[-1]

    def make_output_chain(self):
        # make chain beetwen number out value in list and idv
        self.get_output_idv()
        self.out_chain = self.output_idv
        self.out_reverse_chain = dict()
        for q in range(len(self.output_idv)):
            self.out_reverse_chain.update({self.output_idv[q]: q})

    def make_input_chain(self):
        # make chain beetwen number input value in list and idv
        self.get_input_idv()
        self.in_chain = self.input_idv
        self.in_reverse_chain = dict()
        for q in range(len(self.input_idv)):
            self.in_reverse_chain.update({self.input_idv[q]: q})

    def weight_upd(self): # подвинул вместе с весами выходы с входами
        # calculation and update weight
        upd_table = self.updater_table_buffer[-1]
        self.method.update(upd_table)        
    
    def clear_updater_table_buffer(self):
        self.updater_table_buffer = []

    def minibatch_table_upd(self):
        for key in self.updater_table_buffer[-1].table.keys():
            for q in range(len(self.updater_table_buffer) - 1):
               self.updater_table_buffer[-1].table[key] = self.updater_table_buffer[-1].table[key] + self.updater_table_buffer[q].table[key] 

        for key in self.updater_table_buffer[-1].table.keys():
            self.updater_table_buffer[-1].table[key] = self.updater_table_buffer[-1].table[key] / len(self.updater_table_buffer)
            

    def updater_step(self, data_tuple):
        # updater one streps
        self.put_data_to_input(data_tuple)

        forward_prop = ForwardCalc(self.op_graph)
        forward_prop.main()
        
        if isinstance(self.edu_method, AllData):
            self.backprop.get_all_derivation()
            table = self.create_updater_table(data_tuple)
            self.weight_upd()
            self.clear_updater_table_buffer()

        if isinstance(self.edu_method, MiniBatch):
            self.mini_batch = self.mini_batch + 1
            self.backprop.get_all_derivation()
            table = self.create_updater_table(data_tuple)
            if self.mini_batch == self.minibatch_size:
                self.minibatch_table_upd()
                self.weight_upd()
                self.clear_updater_table_buffer()
                self.mini_batch = 0
                # self.backprop.get_all_derivation()      

    def run_updater(self):
        # run updater work
        # self.apruve_data()
        print("Updater STARTED")
        self.make_output_chain()
        education_size = len(self.data[0])
        for q in range(education_size):
            if ((q / 100) - int(q / 100)) == 0:
                print('Education step : ', q)
            self.epoch = q
            self.updater_step((self.data[0][q], self.data[1][q]))
            if self.mini_batch == 0:
                visual = VisualOpGraph(self.op_graph)
                visual.visual_value_cont(str(q))

        print("Updater FINISHED")

    def save_loss_values_to_csv(self):
        df = pd.DataFrame(self.loss_values)
        df.to_csv('loss_values.csv',  sep=';', index=False, header=False, mode='w+')
       
class UpdaterTable:
    # derivation weight for loss functon
    def __init__(self):
        self.table = dict()

    def push_in_table(self, idv_weight_value, value):
        key = idv_weight_value
        self.table.update(key, value)

    def get_from_table(self, idv):
        return self.table[idv]
        