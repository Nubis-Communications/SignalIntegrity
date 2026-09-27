class Waveform(list):
    def __init__(self,x=None,y=None):
        if isinstance(x,Waveform):
            self.td=x.td
            list.__init__(self,x)
        elif isinstance(x,TimeDescriptor):
            self.td=x
            if isinstance(y,list):
                list.__init__(self,y)
            elif isinstance(y,(float,int,complex)):
                list.__init__(self,[y.real for _ in range(x.K)])
            else:
                list.__init__(self,[0 for _ in range(x.K)])
        else:
            self.td=None
            list.__init__(self,[])
    def Times(self,unit=None):
        return self.td.Times(unit)
    def TimeDescriptor(self):
        return self.td
    def Values(self,unit=None):
        if unit==None:
            return list(self)
        elif unit =='abs':
            return [abs(y) for y in self]
...
