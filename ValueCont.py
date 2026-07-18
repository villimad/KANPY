class ValueCont:
    # контейнер переменных
    def __init__(self):
        self.values_id = []
        self.values = []
    
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
        self.values.append(value)
        return value

    def find_for_ido(self, ido):
        result = []
        for q in range(len(self.values)):
            if self.values[q].ido == ido:
                result.append(self.values[q])
        return result

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

