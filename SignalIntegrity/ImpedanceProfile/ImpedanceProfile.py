'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
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
        S11 = sp.Response(port,port)
        zn2 = [cmath.exp(-1j*2.*math.pi*n/N*1/2) for n in range(N+1)]
        for _ in range(sections):
            rho = 1/(2.*N)*(S11[0].real + S11[N].real +
                 sum([2.*S11[n].real for n in range(1,N)]))
            self.m_rho.append(rho)
            rho2=rho*rho
            S11=[(-S11[n]+S11[n]*rho2*zn2[n]-rho*zn2[n]+rho)/
                (rho2+S11[n]*rho*zn2[n]-S11[n]*rho-zn2[n])
                for n in range(N+1)]
    def __getitem__(self,item):
        return self.m_rho[item]
    def __len__(self):
        return len(self.m_rho)
    def SParameters(self,f):
        N = len(f)-1
        Td=1./(4.*f[N])
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