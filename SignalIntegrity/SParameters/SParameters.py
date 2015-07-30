from numpy import empty
from numpy import array
import cmath
import math
import string

from SignalIntegrity.Conversions import ReferenceImpedance
from SignalIntegrity.FrequencyDomain.FrequencyList import FrequencyList
from SignalIntegrity.FrequencyDomain.FrequencyResponse import FrequencyResponse

class SParameters():
    def __init__(self,f,data,Z0=50.0):
        self.m_sToken='S'; self.m_d=data; self.m_Z0=Z0
        self.m_f=FrequencyList(f)
        if not data is None:
            if len(data)>0: self.m_P=len(data[0])
    def __getitem__(self,item): return self.m_d[item]
    def __len__(self): return len(self.m_f)
    def f(self): return self.m_f
    def Response(self,ToP,FromP): return [mat[ToP-1][FromP-1] for mat in self]
    def WriteToFile(self,name,formatString=None):
        freqMul = 1e6; freqToken = 'MHz'; cpxType = 'MA'; Z0 = 50.0
        if not formatString is None:
            lineList = string.lower(formatString).split('!')[0].split()
            if len(lineList)>0:
                if 'hz' in lineList: freqToken = 'Hz'; freqMul = 1.0
                if 'khz' in lineList: freqToken = 'KHz'; freqMul = 1e3
                if 'mhz' in lineList: freqToken = 'MHz'; freqMul = 1e6
                if 'ghz' in lineList: freqToken = 'GHz'; freqMul = 1e9
                if 'ma' in lineList: cpxType = 'MA'
                if 'ri' in lineList: cpxType = 'RI'
                if 'db' in lineList: cpxType = 'DB'
                if 'r' in lineList: Z0=float(lineList[lineList.index('r')+1])
        spfile=open(name,'w')
        spfile.write('# '+freqToken+' '+cpxType+' '+self.m_sToken+' R '+str(Z0)+'\n')
        for n in range(len(self.m_f)):
            line=[str(self.m_f[n]/freqMul)]
            mat=self[n]
            if Z0 != self.m_Z0: mat=ReferenceImpedance(mat,Z0,self.m_Z0)
            if self.m_P == 2: mat=array(mat).transpose().tolist()
            for r in range(self.m_P):
                for c in range(self.m_P):
                    val = mat[r][c]
                    if cpxType == 'MA':
                        line.append(str(round(abs(val),6)))
                        line.append(str(round(cmath.phase(val)*180./math.pi,6)))
                    elif cpxType == 'RI':
                        line.append(str(round(val.real,6)))
                        line.append(str(round(val.imag,6)))
                    elif cpxType == 'DB':
                        line.append(str(round(20*math.log10(abs(val)),6)))
                        line.append(str(round(cmath.phase(val)*180./math.pi,6)))
            pline = ' '.join(line)+'\n'
            spfile.write(pline)
        spfile.close()
        return self
    def Resample(self,fl):
        if self.m_d is None:
            self.m_f=fl
            return
        fl=FrequencyList(fl)
        f=FrequencyList(self.f()); f.CheckEvenlySpaced()
        SR=[empty((self.m_P,self.m_P)).tolist() for n in range(fl.N+1)]
        for o in range(self.m_P):
            for i in range(self.m_P):
                res = FrequencyResponse(f,self.Response(o+1,i+1)).Resample(fl)
                for n in range(len(fl)):
                    SR[n][o][i]=res[n]
        return SParameters(fl,SR,self.m_Z0)