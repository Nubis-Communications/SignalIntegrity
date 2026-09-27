class Port(object):
    def __init__(self):
        self.A=''
        self.B=''
        self.M=''
    def IsConnected(self):
        return self.A != ''
    def Print(self,level=0):
        if level==0:
            print('\n','Node','Name')
        for t in range(3):
            if not t==0:
                if level >= 2:
                    print(repr('').strip('\'').rjust(6), end=' ')
                if level >= 1:
                    print(repr('').strip('\'').rjust(4), end=' ')
                    print(repr('').strip('\'').rjust(4), end=' ')
            if t==0:
                print(repr('A').rjust(4),repr(self.A).rjust(4))
            elif t==1:
                print(repr('B').rjust(4),repr(self.B).rjust(4))
            else:
                print(repr('M').rjust(4),repr(self.M).rjust(4))
