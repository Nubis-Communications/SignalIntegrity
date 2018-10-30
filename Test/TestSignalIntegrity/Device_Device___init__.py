class Device(list):
    def __init__(self,Name,Ports,Type='device'):
        self.Name = Name
        list.__init__(self,[Port() for _ in range(Ports)])
        self.SParameters = self.SymbolicMatrix(Name,Ports)
        self.Type=Type
    def AssignSParameters(self,SParameters):
        self.SParameters=SParameters
    @staticmethod
    def SymbolicMatrix(Name,Rows,Columns=-1):
        if Columns == -1:
            Columns = Rows
        if Rows == 1 and Columns == 1:
            return [[Name]]
        return [[Name+'_'+(str(r+1)+str(c+1) if r<9 and c<9 else str(r+1)+','+str(c+1))
                for c in range(Columns)] for r in range(Rows)]
    def Print(self,level=0):
        if level==0:
            print('\n','Name','Port','Node','Name')
        for p in range(len(self)):
            if p==0:
                print(repr(self.Name).rjust(4), end=' ')
            else:
                if level==1:
                    print(repr('').strip('\'').rjust(6), end=' ')
                print(repr('').strip('\'').rjust(4), end=' ')
            print(repr(p+1).rjust(4), end=' ')
            self[p].Print(level+1)
