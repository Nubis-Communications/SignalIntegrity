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

class TLineTwoPortRLGCAnalytic(SParameters):
    def __init__(self,f, R, Rse, L, G, C, df, Z0):
        self.R=R
        self.Rse=Rse
        self.L=L
        self.G=G
        self.C=C
        self.df=df
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        # pragma: silent exclude
        from SignalIntegrity.Devices.TLineTwoPort import TLineTwoPort
        # pragma: include
        f=self.m_f[n]
        Z=self.R+self.Rse*math.sqrt(f)+1j*2*math.pi*f*self.L
        Y=self.G+2.*math.pi*f*self.C*(1j+self.df)
        try:
            Zc=cmath.sqrt(Z/Y)
        except:
            Zc=self.m_Z0
        gamma=cmath.sqrt(Z*Y)
        return TLineTwoPort(Zc,gamma,self.m_Z0)
