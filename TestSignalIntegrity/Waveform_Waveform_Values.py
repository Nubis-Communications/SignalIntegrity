class Waveform(object):
    def __init__(self,x=None,y=None):
        if isinstance(x,Waveform):
            self.m_t=x.m_t
            self.m_y=x.m_y
        elif isinstance(x,TimeDescriptor):
            self.m_t=x
            if isinstance(y,list):
                self.m_y=y
            else:
                self.m_y=[0 for k in range(x.N)]
        else:
            self.m_t=None
            self.m_y=None
    def __len__(self):
        return len(self.m_y)
    def __getitem__(self,item):
        return self.m_y[item]
    def __setitem__(self,item,value):
        self.m_y[item]=value
        return self
    def Times(self,unit=None):
        return self.m_t.Times(unit)
    def TimeDescriptor(self):
        return self.m_t
    def Values(self,unit=None):
        if unit==None:
            return self.m_y
        elif unit =='abs':
            return [abs(y) for y in self.m_y]
...
