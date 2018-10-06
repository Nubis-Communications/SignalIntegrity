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
    def ReadFromFile(self,fileName):
        with open(fileName,"rU") as f:
            data=f.readlines()
        if data[0].strip('\n')!='UnevenlySpaced':
            N = int(str(data[0]))
            Fe = float(str(data[1]))
            frl=[line.split(' ') for line in data[2:]]
            resp=[float(fr[0])+1j*float(fr[1]) for fr in frl]
            self.m_f=EvenlySpacedFrequencyList(Fe,N)
            list.__init__(self,resp)
        else:
            frl=[line.split(' ') for line in data[1:]]
            f=[float(fr[0]) for fr in frl]
            resp=[float(fr[1])+1j*float(fr[2]) for fr in frl]
            self.m_f=GenericFrequencyList(f)
            list.__init__(self,resp)
        return self
    def WriteToFile(self,fileName):
        fl=self.FrequencyList()
        with open(fileName,"w") as f:
            if fl.CheckEvenlySpaced():
                f.write(str(fl.N)+'\n')
                f.write(str(fl.Fe)+'\n')
                for v in self.Response():
                    f.write(str(v.real)+' '+str(v.imag)+'\n')
            else:
                f.write('UnevenlySpaced\n')
                for n in range(len(fl)):
                    f.write(str(fl[n])+' '+str(self.Response()[n].real)+' '+
                    str(self.Response()[n].imag)+'\n')
        return self
...
