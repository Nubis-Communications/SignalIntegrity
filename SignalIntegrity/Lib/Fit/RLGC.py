"""
RLGC.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

import math,cmath
from SignalIntegrity.Lib.Fit.LevMar import LevMar

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
    def fF(self,a):
        (R,L,G,C,Rse,df)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0])
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
        self.D=[1-r2*e2 for (e2,r2) in zip(self.e2g,self.rho2)]
        self.S11=[r*(1-e2)/d for (r,e2,d) in zip(self.rho,self.e2g,self.D)]
        self.S12=[(1-r2)*e/d for (r2,e,d) in zip(self.rho2,self.eg,self.D)]
        S=[[[s11,s12],[s12,s11]] for (s11,s12) in zip(self.S11,self.S12)]
        vS=self.VectorizeSp(S)
        return vS
    def fJ(self,a,Fa=None):
        if self.m_Fa is None: self.m_Fa=self.fF(a)
        (R,L,G,C,Rse,df)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0])
        dZ=[self.dZdR,self.dZdL,self.dZdG,self.dZdC,self.dZdRse,self.dZddf]
        dYdC=[p2f*(1j+df) for p2f in self.p2f]
        dYddf=[p2f*C for p2f in self.p2f]
        dY=[self.dYdR,self.dYdL,self.dYdG,dYdC,self.dYdRse,dYddf]
        dgamma=[[1./(2.*cmath.sqrt(z*y))*(dz*y+z*dy)
                for (z,y,dz,dy) in zip(self.Z,self.Y,dZ[i],dY[i])]
                    for i in range(6)]
        dZc=[[-1./2*(-dz*y+z*dy)/(y*y*cmath.sqrt(z/y))
                for (z,y,dz,dy) in zip(self.Z,self.Y,dZ[i],dY[i])]
                    for i in range(6)]
        drho=[[2.*dzc*self.Z0/((zc+self.Z0)*(zc+self.Z0))
                for (zc,dzc) in zip(self.Zc,dZc[i])] for i in range(6)]
        D2=[d*d for d in self.D]
        dS11=[[-2.*r*e2*(r2-1)/d2*dg+(1-e2)*(1+r2*e2)/d2*dr
                for (r,r2,e2,d2,dg,dr) in
                    zip(self.rho,self.rho2,self.e2g,D2,dgdx,drdx)]
                            for (dgdx,drdx) in zip(dgamma,drho)]
        dS12=[[e*(r2-1)*(1+r2*e2)/d2*dg-2.*r*e*(1-e2)/d2*dr
                for (r,r2,e,e2,d2,dg,dr) in
                    zip(self.rho,self.rho2,self.eg,self.e2g,D2,dgdx,drdx)]
                            for (dgdx,drdx) in zip(dgamma,drho)]
        dS=[[[[dS11[i][n],dS12[i][n]],[dS12[i][n],dS11[i][n]]]
                for n in range(len(self.f))] for i in range(6)]
        vdS=[self.VectorizeSp(ds) for ds in dS]
        return [[vdS[m][r][0] for m in range(len(a))] for r in range(len(Fa))]
    def VectorizeSp(self,sp):
        N=range(len(sp));P=range(len(sp[0]))
        v=[[sp[n][r][c]] for n in N for r in P for c in P]
        return v
    def AdjustVariablesAfterIteration(self,a):
        for r in range(len(a)):
            a[r][0]=abs(a[r][0].real)
        return a
    def Results(self):
        return self.m_a

class RLGCFitter2(LevMar):
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
        self.dYdL0=self.zeros
        self.dYdLinf=self.zeros
        self.dYdfm=self.zeros
        self.dYdb=self.zeros
        self.dYdG=self.ones
    def fF(self,a):
        (R,G,C,Rse,df,L0,Linf,fm,b)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0],a[6][0],a[7][0],a[8][0])
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
        self.ffm=[f/fm for f in self.f]
        self.ffmb=[pow(ffm,b) for ffm in self.ffm]
        self.L=[(L0+Linf*ffmb)/(1.+ffmb) for ffmb in self.ffmb]
        self.Z=[R+Rse*math.sqrt(f)+1j*2.*math.pi*f*L for (L,f) in zip(self.L,self.f)]
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
    def fJ(self,a,Fa=None):
        if self.m_Fa is None: self.m_Fa=self.fF(a)
        (R,G,C,Rse,df,L0,Linf,fm,b)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0],a[6][0],a[7][0],a[8][0])
        dffmbdfm=[-ffmb*b/fm for ffmb in self.ffmb]
        dffmbdb=[ffmb*math.log(ffm+1e-15) for (ffmb,ffm) in zip(self.ffm,self.ffmb)]
        dLdL0=[1./(1.+ffmb) for ffmb in self.ffmb]
        dLdLinf=[ffmb/(1.+ffmb) for ffmb in self.ffmb]
        dLdfm=[(Linf-L0)/((1.+ffmb)*(1.+ffmb))*dffmbdfme for (ffmb,dffmbdfme) in zip(self.ffmb,dffmbdfm)]
        dLdb=[(Linf-L0)/((1.+ffmb)*(1.+ffmb))*dffmbdbe for (ffmb,dffmbdbe) in zip(self.ffmb,dffmbdb)]
        dZdL0=[dZdL*dLdL0e for (dZdL,dLdL0e) in zip(self.dZdL,dLdL0)]
        dZdLinf=[dZdL*dLdLinfe for (dZdL,dLdLinfe) in zip(self.dZdL,dLdLinf)]
        dZdfm=[dZdL*dLdfme for (dZdL,dLdfme) in zip(self.dZdL,dLdfm)]
        dZdb=[dZdL*dLdbe for (dZdL,dLdbe) in zip(self.dZdL,dLdb)]
        dZ=[self.dZdR,self.dZdG,self.dZdC,self.dZdRse,self.dZddf,dZdL0,dZdLinf,dZdfm,dZdb]
        dYdC=[p2f*(1j+df) for p2f in self.p2f]
        dYddf=[p2f*C for p2f in self.p2f]
        dY=[self.dYdR,self.dYdG,dYdC,self.dYdRse,dYddf,self.dYdL0,self.dYdLinf,self.dYdfm,self.dYdb]
        dgamma=[[1./(2.*cmath.sqrt(z*y))*(dz*y+z*dy)
                for (z,y,dz,dy) in zip(self.Z,self.Y,dZ[i],dY[i])]
                    for i in range(9)]
        dZc=[[-1./2*(-dz*y+z*dy)/(y*y*cmath.sqrt(z/y))
                for (z,y,dz,dy) in zip(self.Z,self.Y,dZ[i],dY[i])]
                    for i in range(9)]
        drho=[[2.*dzc*self.Z0/((zc+self.Z0)*(zc+self.Z0))
                for (zc,dzc) in zip(self.Zc,dZc[i])]
                    for i in range(9)]
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
        dS=[[[[dS11[i][n],dS12[i][n]],[dS12[i][n],dS11[i][n]]]
                for n in range(len(self.f))]
                    for i in range(9)]
        vdS=[self.VectorizeSp(ds) for ds in dS]
        return [[vdS[m][r][0] for m in range(len(a))] for r in range(len(Fa))]
    def VectorizeSp(self,sp):
        N=range(len(sp));P=range(len(sp[0]))
        v=[[sp[n][r][c]] for n in N for r in P for c in P]
        return v
    def AdjustVariablesAfterIteration(self,a):
        for r in range(len(a)):
            a[r][0]=abs(a[r][0].real)
        return a
    def Results(self):
        return self.m_a
