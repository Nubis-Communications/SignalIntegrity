class PySIException(Exception):
    def __init__(self,value):
        self.parameter=value
    def __str__(self):
        return repr(self.parameter)