class Waveform(object):
    def __init__(self,x=None,y=None):
        if isinstance(x,Waveform):
            self.td=x.td
            self.values=np.array(x.values,copy=True)
        elif isinstance(x,TimeDescriptor):
            self.td=x
            if y is None:
                self.values=np.zeros(int(x.K))
            elif isinstance(y,(float,int,complex)):
                self.values=np.full(int(x.K),y.real,dtype=float)
            else:
                self.values=Waveform._coerce(y)
        else:
            self.td=None
            self.values=np.array([],dtype=float)
    @staticmethod
...
    def Times(self,unit=None):
        return self.td.Times(unit)
    def TimeDescriptor(self):
        return self.td
    def Values(self,unit=None):
        if unit==None:
            return self.values.copy()
        elif unit =='abs':
            return np.abs(self.values)
...
