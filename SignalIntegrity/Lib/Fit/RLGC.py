"""
RLGC.py
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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
import numpy as np
from numpy import array
from SignalIntegrity.Lib.Fit.LevMar import LevMar

class RLGCFitter(LevMar):
    epsilonG=1e-15
    """fits a two-port RLGC transmission line to s-parameters"""
    def __init__(self,sp,guess,callback=None):
        """Constructor  
        Initializes the fit of an RLGC transmission line.
        @param sp instance of class SParameters containing the s-parameters to fit to.
        @param guess list of variables as a guess __a__ at the variables defining the transmission line.  
        The guess __a__ is arranged in the following order:
        - a[0] - R - the total series resistance (in ohms).
        - a[1] - L - the total series inductance (in henrys).
        - a[2] - G - the total shunt conductance (in farads).
        - a[3] - C - the total shunt capacitance (in siemens).
        - a[4] - R - the total skin-effect resistance (in ohms/sqrt(Hz)).
        - a[5] - df - the dissipation factor, or loss tangent (unitless).
        @param callback (optional, defaults to None) instance of the class CallBacker containing a callback.
        """
        self.m_sp=sp
        self.f=self.m_sp.m_f
        self.Z0=self.m_sp.m_Z0
        v=self.VectorizeSp(sp)
        LevMar.__init__(self,callback)
        # frequency-dependent base vectors (numpy arrays) used to evaluate the
        # transmission-line s-parameters and their partial derivatives for every
        # frequency at once.  These must be set up before Initialize, which
        # evaluates fF.
        self.farr=np.array(self.f,dtype=float)
        self.sqrtfarr=np.sqrt(self.farr)
        self.p2farr=2.*math.pi*self.farr
        self.onesarr=np.ones(len(self.f))
        self.zerosarr=np.zeros(len(self.f))
        # pragma: silent exclude
        # The partial derivative of Z with respect to Rse ought to be sqrt(f)*(1+1j),
        # but the fitter converges much, much better using just sqrt(f).
        # pragma: include
        self.dZdRsearr=self.sqrtfarr
        LevMar.Initialize(self, array([[g] for g in guess]), array(v))
    def fF(self,a):
        """Calculates the s-parameters of a two-port transmission line as a function of transmission line parameters provided.
        @param a list of transmission line parameters __a__.  
        The parameters in __a__ are arranged in the following order:
        - a[0] - R - the total series resistance (in ohms).
        - a[1] - L - the total series inductance (in henrys).
        - a[2] - G - the total shunt conductance (in farads).
        - a[3] - C - the total shunt capacitance (in siemens).
        - a[4] - R - the total skin-effect resistance (in ohms/sqrt(Hz)).
        - a[5] - df - the dissipation factor, or loss tangent (unitless).
        @return numpy array containing the s-parameters in vectorized form.
        Vectorized form means each frequency is stacked on top of one another, with the s-parameter matrix for each frequency
        having its columns stacked on top of one another, thus forming one long vector.
        """
        (R,L,G,C,Rse,df)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0])
        if G==0: G=self.epsilonG
        if R==0: R=self.epsilonG
        self.Z=R+Rse*(1+1j)*self.sqrtfarr+1j*self.p2farr*L
        self.Y=G+self.p2farr*C*(1j+df)
        self.gamma=np.sqrt(self.Z*self.Y)
        self.Zc=np.sqrt(self.Z/self.Y)
        self.rho=(self.Zc-self.Z0)/(self.Zc+self.Z0)
        self.rho2=self.rho*self.rho
        self.eg=np.exp(-self.gamma)
        self.e2g=self.eg*self.eg
        self.D=1-self.rho2*self.e2g
        self.S11=self.rho*(1-self.e2g)/self.D
        self.S12=(1-self.rho2)*self.eg/self.D
        # vectorized s-parameters: per frequency the 2x2 matrix [[S11,S12],[S12,S11]]
        # unrolled as [S11,S12,S12,S11]
        vS=np.empty((4*len(self.f),1),dtype=complex)
        vS[0::4,0]=self.S11; vS[1::4,0]=self.S12
        vS[2::4,0]=self.S12; vS[3::4,0]=self.S11
        return vS
    def fJ(self,a,Fa=None):
        """Calculates the Jacobian matrix as a function of transmission line parameters provided.
        @param a list of transmission line parameters __a__.  
        The parameters in __a__ are arranged in the following order:
        - a[0] - R - the total series resistance (in ohms).
        - a[1] - L - the total series inductance (in henrys).
        - a[2] - G - the total shunt conductance (in farads).
        - a[3] - C - the total shunt capacitance (in siemens).
        - a[4] - R - the total skin-effect resistance (in ohms/sqrt(Hz)).
        - a[5] - df - the dissipation factor, or loss tangent (unitless).
        @param Fa (optional, defaults to None) precalculated value of F(a) from fF().
        This is provided to avoid recalculation of F(a), if already computed previously.
        @return numpy array containing Jacobian.
        This is a six column array where each row corresponds to an s-parameter in the vectorized s-parameters matrix and
        each column is the partial derivative of that s-parameter with respect to one of the transmission line parameters.
        """
        if self.m_Fa is None: self.m_Fa=self.fF(a)
        (R,L,G,C,Rse,df)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0])
        Z=self.Z; Y=self.Y; gamma=self.gamma; Zc=self.Zc
        rho=self.rho; rho2=self.rho2; eg=self.eg; e2g=self.e2g
        dZ=[self.onesarr,1j*self.p2farr,self.zerosarr,
            self.zerosarr,self.dZdRsearr,self.zerosarr]
        dY=[self.zerosarr,self.zerosarr,self.onesarr,
            self.p2farr*(1j+df),self.zerosarr,self.p2farr*C]
        D2=self.D*self.D
        J=np.empty((4*len(self.f),len(a)),dtype=complex)
        for m in range(len(a)):
            dgamma=(dZ[m]*Y+Z*dY[m])/(2.*gamma)
            dZc=-1./2*(-dZ[m]*Y+Z*dY[m])/(Y*Y*Zc)
            drho=2.*dZc*self.Z0/((Zc+self.Z0)*(Zc+self.Z0))
            dS11=-2.*rho*e2g*(rho2-1)/D2*dgamma+(1-e2g)*(1+rho2*e2g)/D2*drho
            dS12=eg*(rho2-1)*(1+rho2*e2g)/D2*dgamma-2.*rho*eg*(1-e2g)/D2*drho
            J[0::4,m]=dS11; J[1::4,m]=dS12; J[2::4,m]=dS12; J[3::4,m]=dS11
        return J
    def VectorizeSp(self,sp):
        """Helper function to vectorize s-parameters
        @param sp instance of class SParameters
        @return list of list array where each row is an element of the vectorized s-parameters.
        Vectorized form means each frequency is stacked on top of one another, with the s-parameter matrix for each frequency
        having its columns stacked on top of one another, thus forming one long vector.
        """
        N=range(len(sp));P=range(len(sp[0]))
        v=[[sp[n][r][c]] for n in N for r in P for c in P]
        return v
    def AdjustVariablesAfterIteration(self,a):
        """Adjusts the transmission line parameters after each iteration.  
        In the case of a transmission line, the adjustment is to enforce that each parameter is real and not negative.
        @param a list of transmission line parameters __a__.  
        The parameters in __a__ are arranged in the following order:
        - a[0] - R - the total series resistance (in ohms).
        - a[1] - L - the total series inductance (in henrys).
        - a[2] - G - the total shunt conductance (in farads).
        - a[3] - C - the total shunt capacitance (in siemens).
        - a[4] - R - the total skin-effect resistance (in ohms/sqrt(Hz)).
        - a[5] - df - the dissipation factor, or loss tangent (unitless).
        @return the adjusted transmission line parameters.
        """
        for r in range(len(a)):
            a[r][0]=abs(a[r][0].real)
        a[2][0]=max(self.epsilonG,a[2][0])
        return a
    def Results(self):
        """Gets the fitted transmission line parameters.
        @return list of transmission line parameters __a__.  
        The parameters in __a__ are arranged in the following order:
        - a[0] - R - the total series resistance (in ohms).
        - a[1] - L - the total series inductance (in henrys).
        - a[2] - G - the total shunt conductance (in farads).
        - a[3] - C - the total shunt capacitance (in siemens).
        - a[4] - R - the total skin-effect resistance (in ohms/sqrt(Hz)).
        - a[5] - df - the dissipation factor, or loss tangent (unitless).
        """
        return [r[0].real for r in self.m_a]

class RLGCFitter2(LevMar):
    def __init__(self,sp,guess,callback=None):
        self.m_sp=sp
        self.f=self.m_sp.m_f
        self.Z0=self.m_sp.m_Z0
        v=self.VectorizeSp(sp)
        LevMar.__init__(self,callback)
        # frequency-dependent base vectors (numpy arrays), set up before Initialize
        # (which evaluates fF), used to evaluate every frequency at once.
        self.farr=np.array(self.f,dtype=float)
        self.sqrtfarr=np.sqrt(self.farr)
        self.p2farr=2.*math.pi*self.farr
        self.onesarr=np.ones(len(self.f))
        self.zerosarr=np.zeros(len(self.f))
        self.dZdRsearr=self.sqrtfarr*(1+1j)
        self.dZdLarr=1j*self.p2farr
        LevMar.Initialize(self, array([[g] for g in guess]), v)
    def fF(self,a):
        (R,G,C,Rse,df,L0,Linf,fm,b)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0],a[6][0],a[7][0],a[8][0])
        if G==0: G=1e-12
        if R==0: R=1e-12
        self.ffm=self.farr/fm
        self.ffmb=np.power(self.ffm,b)
        self.L=(L0+Linf*self.ffmb)/(1.+self.ffmb)
        self.Z=R+Rse*(1+1j)*self.sqrtfarr+1j*self.p2farr*self.L
        self.Y=G+self.p2farr*C*(1j+df)
        self.gamma=np.sqrt(self.Z*self.Y)
        self.Zc=np.sqrt(self.Z/self.Y)
        self.rho=(self.Zc-self.Z0)/(self.Zc+self.Z0)
        self.rho2=self.rho*self.rho
        self.eg=np.exp(-self.gamma)
        self.e2g=self.eg*self.eg
        self.S11=self.rho*(1-self.e2g)/(1-self.rho2*self.e2g)
        self.S12=(1-self.rho2)*self.eg/(1-self.rho2*self.e2g)
        vS=np.empty((4*len(self.f),1),dtype=complex)
        vS[0::4,0]=self.S11; vS[1::4,0]=self.S12
        vS[2::4,0]=self.S12; vS[3::4,0]=self.S11
        return vS
    def fJ(self,a,Fa=None):
        if self.m_Fa is None: self.m_Fa=self.fF(a)
        (R,G,C,Rse,df,L0,Linf,fm,b)=(a[0][0],a[1][0],a[2][0],a[3][0],a[4][0],a[5][0],a[6][0],a[7][0],a[8][0])
        Z=self.Z; Y=self.Y; gamma=self.gamma; Zc=self.Zc
        rho=self.rho; rho2=self.rho2; eg=self.eg; e2g=self.e2g
        ffm=self.ffm; ffmb=self.ffmb
        dffmbdfm=-ffmb*b/fm
        dffmbdb=ffmb*np.log(np.real(ffm)+1e-15)
        dLdL0=1./(1.+ffmb)
        dLdLinf=ffmb/(1.+ffmb)
        dLdfm=(Linf-L0)/((1.+ffmb)*(1.+ffmb))*dffmbdfm
        dLdb=(Linf-L0)/((1.+ffmb)*(1.+ffmb))*dffmbdb
        dZdL=self.dZdLarr
        dZ=[self.onesarr,self.zerosarr,self.zerosarr,self.dZdRsearr,self.zerosarr,
            dZdL*dLdL0,dZdL*dLdLinf,dZdL*dLdfm,dZdL*dLdb]
        dY=[self.zerosarr,self.onesarr,self.p2farr*(1j+df),self.zerosarr,self.p2farr*C,
            self.zerosarr,self.zerosarr,self.zerosarr,self.zerosarr]
        e3g=eg*e2g; e4g=e2g*e2g; rho3=rho*rho2; rho4=rho2*rho2
        den2=(rho2*e2g-1)*(rho2*e2g-1)
        J=np.empty((4*len(self.f),len(a)),dtype=complex)
        for i in range(len(a)):
            dz=dZ[i]; dy=dY[i]
            dg=(dz*Y+Z*dy)/(2.*gamma)
            dzc=-1./2*(-dz*Y+Z*dy)/(Y*Y*Zc)
            dr=2.*dzc*self.Z0/((Zc+self.Z0)*(Zc+self.Z0))
            dS11=(2*rho*e2g-2.*rho3*e2g)/den2*dg+(-e2g-rho2*e4g+1.+rho2*e2g)/den2*dr
            dS12=(e3g*rho4-eg-e3g*rho2+eg*rho2)/den2*dg+(-2.*eg*rho+2.*e3g*rho)/den2*dr
            J[0::4,i]=dS11; J[1::4,i]=dS12; J[2::4,i]=dS12; J[3::4,i]=dS11
        return J
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
