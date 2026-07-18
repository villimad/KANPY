
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
        assert(self.future_ind == False)
        if len(self.op_id) == 0:
            ido = 0
        else:
            ido = self.op_id[-1] + 1
        self.future_ind = True
        return ido
    
    def created_op(self, type_of_op, input_op_id, last_op=False, in_values=None, out_value=None, psi_number=None):
        self.future_ind = False
        ido = self._created_ido()
        op = OpNode(ido, type_of_op, input_op_id,  last_op, in_values, out_value, psi_number)
        self.op.append(op)
        return op
    
    def search_for_psi_number(self, psi_number):
        # поиск конечных операций для узла psi_number
        op_psi_number = None
        for op in self.op:
            if (op.last_op == True) and (op.psi_number[0] == psi_number[0]) and (op.psi_number[1] == psi_number[1]) and (op.psi_number[2] == psi_number[2]):
                op_psi_number = op
        return op_psi_number
    
    def search_for_ido(self, ido):
        for op in self.op:
            if op.ido == ido:
                return op

class Operation:
    type_operation_number = 0

class Sum(Operation):
    type_operation_number = 1
    name = "Sum"

class Prod(Operation):
    type_operation_number = 2
    name = "Prod"

class ActFunc(Operation):
    type_operation_number = 3
    name = "ActFunc"

class Spline(Operation):
    # first place x over plac is c coeff (spline's)
    type_operation_number = 4
    name = "Spline"

class DerivationPlus(Operation):
    type_operation_number = 5
    name = "DerivationPlus"

class DerivationProd(Operation):
    type_operation_number = 6
    name = "DerivationProd"

class DerivationSilu(Operation):
    type_operation_number = 7
    name = "DerivationSilu"

class DerivationSpline(Operation):
    type_operation_number = 8
    name = "DerivationSpline"

class OpNode:
    def __init__(self, ido, type_of_op, input_op_id,  last_op=True, in_values=None, out_value=None, psi_number=None):
        self.type_of_op = type_of_op # тип операции
        self.input_op_id = input_op_id # узлы операции входящие в данный узел
        self.ido = ido # id узла
        self.last_op = last_op # эта операция последняя в узле?
        self.in_values = in_values # переменные на вход [list]
        self.out_value = out_value # переменная на выход
        self.psi_number = psi_number # index пси функции как в статье [номер суммы (уровень), индекс верхнего уровня (i_1), индекс текущего уровня (i_0)]
        # для сумм [номер суммы (уровень), индекс верхнего уровня (i_1)]
        
    def info(self):
        print('self.psi_number = ', self.psi_number)
        print('self.type_of_op = ', self.type_of_op)
        print('self.input_op_id = ', self.input_op_id)
        print('self.ido = ', self.ido)
        print('self.last_op = ', self.last_op)
        print('self.in_values = ', self.in_values)
        print('self.out_value = ', self.out_value)
