# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

import SignalIntegrity.SParameters.Devices as dev
import math,cmath
from SignalIntegrity.SParameters.SParameters import SParameters
from LevMar import LevMar

from numpy import zeros

class RLGCFitter(LevMar):
    def __init__(self,sp,guess,callback=None):
        self.m_sp=sp
        self.f=self.m_sp.m_f
        self.Z0=self.m_sp.m_Z0
        v=self.VectorizeSp(sp)
        LevMar.__init__(self,callback)
        LevMar.Initialize(self, [[g] for g in guess], v)
        self.ones=[1 for _ in self.f]
        self.dZdR=self.ones
        self.dZdRse=[math.sqrt(f) for f in self.f]
        self.p2f=[2.*math.pi*f for f in self.f]
        self.dZdL=[1j*p2f for p2f in self.p2f]
        self.zeros=[0 for _ in self.f]
        self.dZdG=self.zeros
        self.dZdC=self.zeros
        self.dZddf=self.zeros
        self.dYdR=self.zeros
        self.dYdRse=self.zeros
        self.dYdL=self.zeros
        self.dYdG=self.ones
    def fF(self,x):
        (R,L,G,C,Rse,df)=(x[0][0],x[1][0],x[2][0],x[3][0],x[4][0],x[5][0])
        # pragma: silent exclude
        try:
            1./G
        except:
            G=1e-12
        try:
            1./R
        except:
            R=1e-12
        # pragma: include
        self.Z=[R+Rse*math.sqrt(f)+1j*2.*math.pi*f*L for f in self.f]
        self.Y=[G+2.*math.pi*f*C*(1j+df) for f in self.f]
        self.gamma=[cmath.sqrt(z*y) for (z,y) in zip(self.Z,self.Y)]
        self.Zc=[cmath.sqrt(z/y) for (z,y) in zip(self.Z,self.Y)]
        self.rho=[(zc-self.Z0)/(zc+self.Z0) for zc in self.Zc]
        self.rho2=[r*r for r in self.rho]
        self.eg=[cmath.exp(-g) for g in self.gamma]
        self.e2g=[egx*egx for egx in self.eg]
        self.S11=[r*(1-e2)/(1-r2*e2) for (r,e2,r2) in zip(self.rho,self.e2g,self.rho2)]
        self.S12=[(1-r2)*e/(1-r2*e2) for (r2,e,e2) in zip(self.rho2,self.eg,self.e2g)]
        S=[[[s11,s12],[s12,s11]] for (s11,s12) in zip(self.S11,self.S12)]
        vS=self.VectorizeSp(S)
        return vS
    def fJ(self,x,Fx=None):
        if self.m_Fx is None: self.m_Fx=self.fF(x)
        (R,L,G,C,Rse,df)=(x[0][0],x[1][0],x[2][0],x[3][0],x[4][0],x[5][0])
        dZ=[self.dZdR,self.dZdL,self.dZdG,self.dZdC,self.dZdRse,self.dZddf]
        dYdC=[p2f*(1j+df) for p2f in self.p2f]
        dYddf=[p2f*C for p2f in self.p2f]
        dY=[self.dYdR,self.dYdL,self.dYdG,dYdC,self.dYdRse,dYddf]
        dgamma=[[1./(2.*cmath.sqrt(z*y))*(dz*y+z*dy)
                for (z,y,dz,dy) in zip(self.Z,self.Y,dZ[a],dY[a])]
                    for a in range(6)]
        dZc=[[-1./2*(-dz*y+z*dy)/(y*y*cmath.sqrt(z/y))
                for (z,y,dz,dy) in zip(self.Z,self.Y,dZ[a],dY[a])]
                    for a in range(6)]
        drho=[[2.*dzc*self.Z0/((zc+self.Z0)*(zc+self.Z0))
                for (zc,dzc) in zip(self.Zc,dZc[a])]
                    for a in range(6)]
        e3g=[egx*egx*egx for egx in self.eg]
        e4g=[egx*egx*egx*egx for egx in self.eg]
        rho3=[r*r*r for r in self.rho]
        rho4=[r*r*r*r for r in self.rho]
        dS11=[[(2*r*e2-2.*r3*e2)/((r2*e2-1)*(r2*e2-1))*dg+
            (-e2-r2*e4+1.+r2*e2)/((r2*e2-1)*(r2*e2-1))*dr
                for (r,r2,r3,r4,e,e2,e3,e4,dg,dr) in
                    zip(self.rho,self.rho2,rho3,rho4,self.eg,
                        self.e2g,e3g,e4g,dgammadx,drhodx)]
                            for (dgammadx,drhodx) in zip(dgamma,drho)]
        dS12=[[(e3*r4-e-e3*r2+e*r2)/((r2*e2-1)*(r2*e2-1))*dg+
            (-2.*e*r+2.*e3*r)/((r2*e2-1)*(r2*e2-1))*dr
                for (r,r2,r3,r4,e,e2,e3,e4,dg,dr) in
                    zip(self.rho,self.rho2,rho3,rho4,self.eg,
                        self.e2g,e3g,e4g,dgammadx,drhodx)]
                            for (dgammadx,drhodx) in zip(dgamma,drho)]
        dS=[[[[dS11[a][n],dS12[a][n]],[dS12[a][n],dS11[a][n]]]
                for n in range(len(self.f))]
                    for a in range(6)]
        vdS=[self.VectorizeSp(ds) for ds in dS]
        return [[vdS[m][r][0] for m in range(len(x))] for r in range(len(Fx))]
    def VectorizeSp(self,sp):
        spd=[M for M in sp]
        v=[[spd[n][r][c]] for n in range(len(spd))
           for r in range(len(spd[0]))
                for c in range(len(spd[0]))]
        return v
    @staticmethod
    def AdjustVariablesAfterIteration(x):
        for r in range(len(x)):
            x[r][0]=abs(x[r][0].real)
        return x
    def Results(self):
        return self.m_x
