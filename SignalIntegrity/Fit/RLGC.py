'''
Created on Jan 26, 2018

@author: pete
'''
from LevMar import LevMar
from Matrix import Matrix

import SignalIntegrity.SParameters.Devices as dev
import math,cmath
from SignalIntegrity.SParameters.SParameters import SParameters

class RLGCSolver(LevMar):
    def __init__(self,sp,guess,callback=None):
        self.m_Sections=0
        self.m_sp=sp
        v=self.VectorizeSp(sp)
        LevMar.__init__(self,callback)
        LevMar.Initialize(self, Matrix([[g] for g in guess]), Matrix(v))
    def Results(self):
        return self.m_x
    def fF(self,x):
        R=x[0][0]
        L=x[1][0]
        G=x[2][0]
        C=x[3][0]
        Rse=x[4][0]
        df=x[5][0]
        fList=[0.0000001 if f==0 else f for f in self.m_sp.m_f]
        approximate=False
        if approximate:
            tline=dev.TLineTwoPortRLGC(fList, R, Rse, L, G, C, df, self.m_sp.m_Z0, self.m_Sections)
        else:
            fList=[0.0001 if f==0 else f for f in self.m_sp.m_f]
            Z0=self.m_sp.m_Z0
            seriesZ=[R+Rse*math.sqrt(f)+1j*2.*math.pi*f*L for f in fList]
            shuntY=[G+2.*math.pi*f*C*(1j+df) for f in fList]
            Zc=[cmath.sqrt(z/y) for (z,y) in zip(seriesZ,shuntY)]
            gamma=[cmath.sqrt(z*y) for (z,y) in zip(seriesZ,shuntY)]
            rho=[(zc-Z0)/(zc+Z0) for zc in Zc]
            D=[1-r*r*cmath.exp(-2.*g) for (r,g) in zip(rho,gamma)]
            S11=[r*(1-cmath.exp(-2*g))/d for (r,g,d) in zip(rho,gamma,D)]
            S12=[(1.-r*r)*cmath.exp(-g)/d for (r,g,d) in zip(rho,gamma,D)]
            tline=SParameters(fList,[[[s11,s12],[s12,s11]] for (s11,s12) in zip(S11,S12)])
        v=self.VectorizeSp(tline)
        return Matrix(v)
    def fJ(self,x,Fx=None):
        R=x[0][0]
        L=x[1][0]
        G=x[2][0]
        C=x[3][0]
        Rse=x[4][0]
        df=x[5][0]
        fList=[0.0001 if f==0 else f for f in self.m_sp.m_f]
        Z0=self.m_sp.m_Z0
        Z=[R+Rse*math.sqrt(f)+1j*2.*math.pi*f*L for f in fList]
        dZdR=[1 for _ in fList]
        dZdRse=[math.sqrt(f) for f in fList]
        dZdL=[2.*1j*math.pi*f for f in fList]
        dZdG=[0 for _ in fList]
        dZdC=[0 for _ in fList]
        dZddf=[0 for _ in fList]
        dZ=[dZdR,dZdL,dZdG,dZdC,dZdRse,dZddf]
        Y=[G+2.*math.pi*f*C*(1j+df) for f in fList]
        dYdR=[0 for _ in fList]
        dYdRse=[0 for _ in fList]
        dYdL=[0 for _ in fList]
        dYdG=[1 for _ in fList]
        dYdC=[2.*math.pi*f*(1j+df) for f in fList]
        dYddf=[2.*math.pi*f*C for f in fList]
        dY=[dYdR,dYdL,dYdG,dYdC,dYdRse,dYddf]
        gamma=[cmath.sqrt(z*y) for (z,y) in zip(Z,Y)]
        dgamma=[[1./(2.*cmath.sqrt(z*y))*(dz*y+z*dy)
                for (z,y,dz,dy) in zip(Z,Y,dZ[a],dY[a])]
                    for a in range(6)]
        Zc=[cmath.sqrt(z/y) for (z,y) in zip(Z,Y)]
        dZc=[[-1./2*(-dz*y+z*dy)/(y*y*cmath.sqrt(z/y))
                for (z,y,dz,dy) in zip(Z,Y,dZ[a],dY[a])]
                    for a in range(6)]
        rho=[(zc-Z0)/(zc+Z0) for zc in Zc]
        drho=[[2.*dzc*Z0/((zc+Z0)*(zc+Z0))
                for (zc,dzc) in zip(Zc,dZc[a])]
                    for a in range(6)]
        eg=[cmath.exp(-g) for g in gamma]
        e2g=[egx*egx for egx in eg]
        e3g=[egx*egx*egx for egx in eg]
        e4g=[egx*egx*egx*egx for egx in eg]
        rho2=[r*r for r in rho]
        rho3=[r*r*r for r in rho]
        rho4=[r*r*r*r for r in rho]
        S11=[r*(1-e2)/(1-r2*e2) for (r,e2,r2) in zip(rho,e2g,rho2)]
        S12=[(1-r2)*e/(1-r2*e2) for (r2,e,e2) in zip(rho2,eg,e2g)]
        dS11=[[(2*r*e2-2.*r3*e2)/((r2*e2-1)*(r2*e2-1))*dg+
               (-e2-r2*e4+1.+r2*e2)/((r2*e2-1)*(r2*e2-1))*dr
                    for (r,r2,r3,r4,e,e2,e3,e4,dg,dr) in 
                        zip(rho,rho2,rho3,rho4,eg,e2g,e3g,e4g,dgamma[a],drho[a])]
                            for a in range(6)]
        dS12=[[(e3*r4-e-e3*r2+e*r2)/((r2*e2-1)*(r2*e2-1))*dg+
               (-2.*e*r+2.*e3*r)/((r2*e2-1)*(r2*e2-1))*dr
                    for (r,r2,r3,r4,e,e2,e3,e4,dg,dr) in
                        zip(rho,rho2,rho3,rho4,eg,e2g,e3g,e4g,dgamma[a],drho[a])]
                            for a in range(6)]
        dS=[[[[dS11[a][n],dS12[a][n]],[dS12[a][n],dS11[a][n]]]
                for n in range(len(fList))]
                    for a in range(6)]
        vdS=[self.VectorizeSp(ds) for ds in dS]
        S=[[[s11,s12],[s12,s11]] for (s11,s12) in zip(S11,S12)]
        vS=self.VectorizeSp(S)
        Fx=vS
        if Fx is None:
            Fx=self.fF(x)
        M = x.rows()
        R = len(Fx)
        J = Matrix.initialized(0,R,M)
        for m in range(M):
            pFpxm=vdS[m]
            for r in range(R):
                J[r][m]=pFpxm[r][0]
        return J
    def VectorizeSp(self,sp):
        spd=[M for M in sp]
        v=[[spd[n][r][c]] for n in range(len(spd)) for r in range(len(spd[0])) for c in range(len(spd[0]))]
        return v
    @staticmethod
    def AdjustVariablesAfterIteration(x):
        for r in range(x.rows()):
            x[r][0]=abs(x[r][0].real)
        return x