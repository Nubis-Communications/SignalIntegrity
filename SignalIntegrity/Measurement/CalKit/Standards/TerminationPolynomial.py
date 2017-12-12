'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Devices.TerminationC import TerminationC
from SignalIntegrity.Devices.TerminationL import TerminationL

class TerminationPolynomial(object):
    def __init__(self,a0=0.0,a1=0.0,a2=0.0,a3=0.0):
        self.a0=a0
        self.a1=a1
        self.a2=a2
        self.a3=a3
    def Polynomial(self,f):
        return ((self.a3*f+self.a2)*f+self.a1)*f+self.a0
 
class TerminationCPolynomial(SParameters,TerminationPolynomial):
    def __init__(self,f,C0=0.0,C1=0.0,C2=0.0,C3=0.0,Z0=50.):
        TerminationPolynomial.__init__(self,C0,C1,C2,C3)
        SParameters.__init__(self,f,None,Z0)
    def PolynomialC(self,n):
        f=self.m_f[n]
        return self.Polynomial(f)
    def __getitem__(self,n):
        return TerminationC(self.PolynomialC(n),self.m_f[n],self.m_Z0)

class TerminationLPolynomial(SParameters,TerminationPolynomial):
    def __init__(self,f,L0=0.0,L1=0.0,L2=0.0,L3=0.0,Z0=50.):
        TerminationPolynomial.__init__(self,L0,L1,L2,L3)
        SParameters.__init__(self,f,None,Z0)
    def PolynomialL(self,n):
        f=self.m_f[n]
        return self.Polynomial(f)
    def __getitem__(self,n):
        return TerminationL(self.PolynomialL(n),self.m_f[n],self.m_Z0)
