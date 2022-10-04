from src.PX4Parameter import get_parameters 

class Parameterclass:
    
    def __init__(self, List, Description, Value, Range, Information):
        self.list = List
        self.description = Description
        self.value = Value
        self.range = Range
        self.information = Information
        
    def show_parameter_list(self):
        param = get_parameters()
        
        for i in param:
            self.list.addItem(param['name'])
