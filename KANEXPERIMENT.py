import numpy as np
from NetScheme import *
from OpCont import *
from OpGraph import *
from ValueCont import *
from Backprop import *
from Updater import *
from KAN import *
from ForwardCalc import *
from Initiator import *
from Updater import *

def real_func(arr_x):
    return sum(arr_x)

def create_data(size_input, size_output, size_data=100):
    # make input
    data_input = []
    data_output = []
    for q in range(size_data):
        input_arr = []
        for input_q in range(size_input):
            input_arr.append(np.random.uniform(-1, 1))
        data_input.append(input_arr)
        data_output.append([real_func(data_input[q])])

    return [data_input, data_output]


if __name__ == "__main__":
    op_cont = OpCont()
    val_cont = ValueCont()
    net_scheme = NetScheme([2,  1, 1])
    spline_param = SplineParam(3, -1.5, 1.5, 3, 2)
    op_graph = OpGraph(net_scheme, op_cont, val_cont, spline_param=spline_param)
    op_graph.main()
    
    # input_data = [2, 3]
    init_w = Initiator(op_graph)
    init_w.init_value()


    bt = BackpropTable()
    bbuffert = BackpropBufferTable()
    backprop = Backprop(op_graph, bt, bbuffert)
    backprop.get_all_derivation()
    bt.save_to_csv('1')

    data = create_data(2, 1, 1000)

    planer = StandartPlaner(0.01)

    method = Adam(op_graph=op_graph, planer=planer)
    method = AdamMode(op_graph)
    

    updater = Updater(op_graph=op_graph, backprop=backprop, data=data, loss_func=MSE(), edu_method=MiniBatch(), method=method, minibatch_size=1000)
    
    method.put_updater(updater)

    for q in range(0, 200):
        updater.run_updater()
        updater.save_loss_values_to_csv()
    

    visual = VisualOpGraph(op_graph)
    visual.visual_value_cont()
    visual.visualGraphCSV()
    
    backprop.get_all_derivation()
    bt.save_to_csv('2')
