class FrequencyDomain(list):
    def __init__(self,f=None,resp=None):
        self.m_f=FrequencyList(f)
        if not resp is None:
            list.__init__(self,resp)
    def FrequencyList(self):
        return self.m_f
    def Frequencies(self,unit=None):
        return self.m_f.Frequencies(unit)
    def Values(self,unit=None):
        if unit==None:
            return list(self)
        elif unit =='dB':
            return [-3000. if (abs(self[n]) < 1e-15) else
                     20.*math.log10(abs(self[n]))
                        for n in range(len(self.m_f))]
        elif unit == 'mag':
            return [abs(self[n]) for n in range(len(self.m_f))]
        elif unit == 'rad':
            return [cmath.phase(self[n]) for n in range(len(self.m_f))]
        elif unit == 'deg':
            return [cmath.phase(self[n])*180./math.pi
                        for n in range(len(self.m_f))]
        elif unit == 'real':
            return [self[n].real for n in range(len(self.m_f))]
        elif unit == 'imag':
            return [self[n].imag for n in range(len(self.m_f))]
...
    def ReadFromFile(self,fileName):
        with open(fileName,'rU' if sys.version_info.major < 3 else 'r') as f:
            self.ReadFromFileStream(f)
        return self
...
    def WriteToFile(self,fileName):
        with open(fileName,"w") as f:
            self.WriteToFileStream(f)
        return self
...
