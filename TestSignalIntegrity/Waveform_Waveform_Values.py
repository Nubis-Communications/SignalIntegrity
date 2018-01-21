class Waveform(object):
    def __init__(self,x=None,y=None):
        if isinstance(x,Waveform):
            self.td=x.td
            self.x=x.x
        elif isinstance(x,TimeDescriptor):
            self.td=x
            if isinstance(y,list):
                self.x=y
            elif isinstance(y,(float,int,complex)):
                self.x=[y.real for k in range(x.K)]
            else:
                self.x=[0 for k in range(x.K)]
        else:
            self.td=None
            self.x=None
    def __len__(self):
        return len(self.x)
    def __getitem__(self,item):
        return self.x[item]
    def __setitem__(self,item,value):
        self.x[item]=value
        return self
    def Times(self,unit=None):
        return self.td.Times(unit)
    def TimeDescriptor(self):
        return self.td
    def Values(self,unit=None):
        if unit==None:
            return self.x
        elif unit =='abs':
            return [abs(y) for y in self.x]
...
