"""
ImpedanceProfile.py
"""

# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from SignalIntegrity.SParameters import SParameters
import math
import cmath
from SignalIntegrity.Devices import IdealTransmissionLine
from SignalIntegrity.Conversions import S2T
from SignalIntegrity.Conversions import T2S
from numpy import matrix

class ImpedanceProfile(list):
    rhoLimit=0.99
    ZLimit=10e3
    def __init__(self,sp,sections,port):
        list.__init__(self,[])
        N = len(sp)-1
        self.m_Td = 1./(4.*sp.f()[N])
        self.m_Z0 = sp.m_Z0
        fr=sp.FrequencyResponse(port,port)
        self.m_fracD=fr._FractionalDelayTime()
        fr=fr._DelayBy(-self.m_fracD)
        S11 = fr.Values()
        zn2 = [cmath.exp(-1j*2.*math.pi*n/N*1/2) for n in range(N+1)]
        finished=False
        rho=0.0
        for _ in range(sections):
            if finished:
                self.append(rho)
                continue
            rho = 1/(2.*N)*(S11[0].real + S11[N].real +
                 sum([2.*S11[n].real for n in range(1,N)]))
            rho=max(-self.rhoLimit,min(rho,self.rhoLimit))
            self.append(rho)
            if abs(rho)==self.rhoLimit:
                finished=True
                continue
            rho2=rho*rho
            S11=[(-S11[n]+S11[n]*rho2*zn2[n]-rho*zn2[n]+rho)/
                (rho2+S11[n]*rho*zn2[n]-S11[n]*rho-zn2[n])
                for n in range(N+1)]
    def Z(self):
        return [max(0.,min(self.m_Z0*(1+rho)/(1-rho),self.ZLimit))
            for rho in self]
    def DelaySection(self):
        return self.m_Td
    def SParameters(self,f):
        N = len(f)-1
        Gsp=[None for n in range(N+1)]
        gamma=[1j*2.*math.pi*f[n]*self.m_Td for n in range(N+1)]
        for n in range(N+1):
            tacc=matrix([[1.,0.],[0.,1.]])
            for m in range(len(self)):
                tacc=tacc*matrix(S2T(IdealTransmissionLine(self[m],gamma[n])))
            Gsp[n]=T2S(tacc.tolist())
        sp = SParameters(f,Gsp,self.m_Z0)
        return sp