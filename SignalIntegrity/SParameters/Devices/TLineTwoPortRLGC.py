'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import math,cmath

from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Devices.TLineTwoPort import TLineTwoPort

class TLineTwoPortRLGC(SParameters):
    def __init__(self,f, R, Rse, L, G, C, df, Z0, K=0):
        self.m_K=K
        if K==0:
            self.R=R
            self.Rse=Rse
            self.L=L
            self.G=G
            self.C=C
            self.df=df
        else:
            # pragma: silent exclude
            from SignalIntegrity.SParameters.Devices.TLineTwoPortRLGCApproximate import TLineTwoPortRLGCApproximate
            # pragma: include
            self.m_approx=TLineTwoPortRLGCApproximate(f,R,Rse,L,G,C,df,Z0,K)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        if self.m_K==0:
            f=self.m_f[n]
            Z=self.R+self.Rse*math.sqrt(f)+1j*2*math.pi*f*self.L
            Y=self.G+2.*math.pi*f*self.C*(1j+self.df)
            try:
                Zc=cmath.sqrt(Z/Y)
            except:
                Zc=self.m_Z0
            gamma=cmath.sqrt(Z*Y)
            return TLineTwoPort(Zc,gamma,self.m_Z0)
        else: return self.m_approx[n]
