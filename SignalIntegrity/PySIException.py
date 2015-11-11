class PySIException(Exception):
    def __init__(self,value,message=''):
        self.parameter=value
        self.message=message
    def __str__(self):
        return repr(self.parameter)