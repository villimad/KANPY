class ValueCont:
    # контейнер переменных
    def __init__(self):
        self.values_id = []
        self.values = dict()
        self.output_value = []
        self.input_value = dict()
    
    def _created_idv(self):
        if len(self.values_id) == 0 :
            idv = 0
        else:
            idv = self.values_id[-1] + 1
        self.values_id.append(idv)
        return idv
    
    def created_value(self, ido, value=0, name='Noname', value_type=None):
        idv = self._created_idv()
        value = Value(idv, ido, value, name, value_type=value_type)
        self.values.update({idv: value})
        if isinstance(value_type, Output):
            self.output_value.append(value)

        if isinstance(value_type, Input):
            self.input_value.update({idv: value})
            
        return value

    def find_for_ido(self, ido):
        result = []
        for key in self.values.keys():
            if self.values[key].ido == ido:
                result.append(self.values[key])
        return result

    def search_for_idv(self, idv):
        return self.values[idv]
        

class Value:
    def __init__(self, idv, ido, value=0, name='Noname', value_type=None):
        self.idv = idv # id величины
        self.ido = ido # id операции к которой пренадлежит величина
        self.value = value # величина внутри переменной
        self.name = name
        self.value_type = value_type

class ValueType:
    type_value_number = 0

class Input(ValueType):
    type_value_number = 1

class Output(ValueType):
    type_value_number = 2

class Weight(ValueType):
    type_value_number = 3

class CoeffSpline(ValueType):
    type_value_number = 4

class WeightSpline(ValueType):
    type_value_number = 5
