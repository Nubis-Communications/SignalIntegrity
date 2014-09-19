class Port(object):
    def __init__(self):
        self.m_A=''
        self.m_B=''
        self.m_M=''
    @property
    def pA(self):
        return self.m_A
    def get_B(self):
        return self.m_B
    def get_M(self):
        return self.m_M
    @pA.setter
    def pA(self, value):
        self.m_A = value
    def set_B(self, value):
        self.m_B = value
    def set_M(self, value):
        self.m_M = value
    @pA.deleter
    def pA(self):
        self.m_A = ''
    def del_B(self):
        self.m_B = ''
    def del_M(self):
        self.m_M = ''
    #pA = property(get_A, set_A, del_A, "A Node Connection")
    pB = property(get_B, set_B, del_B, "B Node Connection")
    pM = property(get_M, set_M, del_M, "Stimulus Name")
    def IsConnected(self):
        return self.pA != ''
    def Print(self,level=0):
        if level==0:
            print '\n','Node','Name'        
        for t in range(3):
            if not t==0:
                if level >= 2:
                    print repr('').strip('\'').rjust(6),
                if level >= 1:
                    print repr('').strip('\'').rjust(4),
                    print repr('').strip('\'').rjust(4),
            if t==0:
                print repr('A').rjust(4),repr(self.pA).rjust(4)
            elif t==1:
                print repr('B').rjust(4),repr(self.pB).rjust(4)
            else:
                print repr('M').rjust(4),repr(self.pM).rjust(4)

