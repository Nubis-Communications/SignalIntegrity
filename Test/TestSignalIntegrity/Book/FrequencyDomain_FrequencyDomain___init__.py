class FrequencyDomain(object):
    def __init__(self,f=None,resp=None):
        self.m_f=FrequencyList(f)
        if resp is not None:
            self.values=np.asarray(resp,dtype=complex)
        else:
            self.values=np.array([],dtype=complex)
...
    def FrequencyList(self):
        return self.m_f
    def Frequencies(self,unit=None):
        return self.m_f.Frequencies(unit)
    def Values(self,unit=None):
        if unit==None:
            return self.values.copy()
        elif unit =='dB':
            mag=np.abs(self.values)
            result=np.full(len(mag),-3000.)
            nonzero=mag>=1e-15
            result[nonzero]=20.*np.log10(mag[nonzero])
            return result.tolist()
        elif unit == 'mag':
            return np.abs(self.values).tolist()
        elif unit == 'rad':
            return np.angle(self.values).tolist()
        elif unit == 'deg':
            return np.degrees(np.angle(self.values)).tolist()
        elif unit == 'real':
            return self.values.real.tolist()
        elif unit == 'imag':
            return self.values.imag.tolist()
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
