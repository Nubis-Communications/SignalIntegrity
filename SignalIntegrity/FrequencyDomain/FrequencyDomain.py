'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import fft
import math
import cmath

from SignalIntegrity.FrequencyDomain.FrequencyList import FrequencyList
from SignalIntegrity.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.FrequencyDomain.FrequencyList import GenericFrequencyList

class FrequencyDomain(object):
    def __init__(self,f=None,resp=None):
        self.m_f=FrequencyList(f)
        self.m_resp=resp
    def __getitem__(self,item): return self.m_resp[item]
    def __setitem__(self,item,value):
        self.m_resp[item]=value
        return self
    def __len__(self): return len(self.m_resp)
    def FrequencyList(self):
        return self.m_f
    def Frequencies(self,unit=None):
        return self.m_f.Frequencies(unit)
    def Values(self,unit=None):
        if unit==None:
            return self.m_resp
        elif unit =='dB':
            return [-3000. if (abs(self.m_resp[n]) < 1e-15) else
                     20.*math.log10(abs(self.m_resp[n]))
                        for n in range(len(self.m_f))]
        elif unit == 'mag':
            return [abs(self.m_resp[n]) for n in range(len(self.m_f))]
        elif unit == 'rad':
            return [cmath.phase(self.m_resp[n]) for n in range(len(self.m_f))]
        elif unit == 'deg':
            return [cmath.phase(self.m_resp[n])*180./math.pi
                        for n in range(len(self.m_f))]
        elif unit == 'real':
            return [self.m_resp[n].real for n in range(len(self.m_f))]
        elif unit == 'imag':
            return [self.m_resp[n].imag for n in range(len(self.m_f))]
    def ReadFromFile(self,fileName):
        with open(fileName,"rU") as f:
            data=f.readlines()
        if data[0].strip('\n')!='UnevenlySpaced':
            N = int(str(data[0]))
            Fe = float(str(data[1]))
            frl=[line.split(' ') for line in data[2:]]
            resp=[float(fr[0])+1j*float(fr[1]) for fr in frl]
            self.m_f=EvenlySpacedFrequencyList(Fe,N)
            self.m_resp=resp
        else:
            frl=[line.split(' ') for line in data[1:]]
            f=[float(fr[0]) for fr in frl]
            resp=[float(fr[1])+1j*float(fr[2]) for fr in frl]
            self.m_f=GenericFrequencyList(f)
            self.m_resp=resp
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
    def __eq__(self,other):
        if self.FrequencyList() != other.FrequencyList():
            return False # pragma: no cover
        if len(self.Values()) != len(other.Values()):
            return False # pragma: no cover
        for k in range(len(self.Values())):
            if abs(self.Values()[k] - other.Values()[k]) > 1e-5:
                return False # pragma: no cover
        return True
    def __ne__(self,other):
        return not self == other

