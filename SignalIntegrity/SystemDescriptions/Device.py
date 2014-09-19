from Port import Port

class Device:
    def __init__(self,Name,Ports):
        self.m_Name = Name
        self.m_Ports = [Port() for p in range(Ports)]
        self.m_S = self.SymbolicMatrix(Name,Ports)
    def get_S(self):
        return self.m_S
    def set_S(self, value):
        self.m_S = value
    def del_S(self):
        self.m_S = self.SymbolicMatrix(self.m_Name,self.m_Ports)
    def __getitem__(self,item):
        return self.m_Ports[item]
    def __len__(self):
        return len(self.m_Ports)
    @property
    def pName(self):
        return self.m_Name
    @staticmethod
    def SymbolicMatrix(Name,Rows,Columns=-1):
        if Columns == -1:
            Columns = Rows
        if Rows == 1 and Columns == 1:
            return [[ Name ]]
        else:
            return [ [ Name+'_'+ (str(r+1)+str(c+1) if r<9 and c<9 else str(r+1)+','+str(c+1))
                for c in range(Columns) ] for r in range(Rows) ]
    def Print(self,level=0):
        if level==0:
            print '\n','Name','Port','Node','Name'
        for p in range(len(self)):
            if p==0:
                print repr(self.pName).rjust(4),
            else:
                if level==1:
                    print repr('').strip('\'').rjust(6),
                print repr('').strip('\'').rjust(4),
            print repr(p+1).rjust(4),
            self[p].Print(level+1)
    pSParameters = property(get_S, set_S, del_S, "S-parameters of Device")

