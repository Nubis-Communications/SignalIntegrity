from SignalIntegrity.SParameters import SParameters
import math
import cmath
from SignalIntegrity.Devices import IdealTransmissionLine
from SignalIntegrity.Conversions import S2T
from SignalIntegrity.Conversions import T2S
from numpy import matrix

class ImpedanceProfile(object):
    def __init__(self,sp,sections,port):
        N = len(sp)-1
        self.m_Td = 1./(2.*sp.f()[N])
        self.m_rho = []
        self.m_Z0 = sp.m_Z0
        S11 = [sp[n][port-1][port-1] for n in range(N+1)]
        z = [cmath.exp(1j*2.*math.pi*n/(2.*N)) for n in range(N+1)]
        for m in range(sections):
            acc=S11[n].real + S11[n].real
            for n in range(1,N-1):
                acc = acc + 2.*S11[n].real
            rho = 1/(2.*N)*acc
            self.m_rho.append(rho)
            for n in range(N+1):
                nS11 = (-S11[n]+S11[n]*rho*rho/(z[n]*z[n])-rho/(z[n]*z[n])+rho)
                nS11 = nS11/(rho*rho+S11[n]*rho/(z[n]*z[n])-S11[n]*rho-1./(z[n]*z[n]))
                S11[n]=nS11
    def __getitem__(self,item):
        return self.m_rho[item]
    def __len__(self):
        return len(self.m_rho)
    def SParameters(self,f):
        N = len(f)-1
        Td=1./(2.*f[N])
        Gsp=[]
        for n in range(N+1):
            gamma = 1j*2.*math.pi*f[n]*Td
            tacc=matrix([[1.,0.],[0.,1.]])
            for m in range(len(self)):
                tacc=tacc*matrix(S2T(IdealTransmissionLine(self[m],gamma)))
            G=T2S(tacc.tolist())
            Gsp.append(G)
        sp = SParameters(f,Gsp,self.m_Z0)
        return sp