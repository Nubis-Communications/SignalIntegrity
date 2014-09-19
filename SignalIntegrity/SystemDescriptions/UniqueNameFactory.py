class UniqueNameFactory:
    def __init__(self,prefix):
        self.m_UniqueNumber = 1
        self.m_Prefix = prefix
    def Name(self):
        Name = self.m_Prefix+str(self.m_UniqueNumber)
        self.m_UniqueNumber+=1
        return Name

