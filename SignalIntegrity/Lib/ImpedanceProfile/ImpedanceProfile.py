"""
Impedance Profile generated through the peeling method
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

from SignalIntegrity.Lib.SParameters import SParameters
import math
import cmath
from SignalIntegrity.Lib.Devices import IdealTransmissionLine
from SignalIntegrity.Lib.Conversions import S2T
from SignalIntegrity.Lib.Conversions import T2S
from numpy import matrix

class ImpedanceProfile(list):
    """ Impedance profile generated using the peeling algorithm.  After construction, it is
    a list of rho values"""
    rhoLimit=0.99
    ZLimit=10e3
    def __init__(self,sp,sections,port):
        """ Constructor\n
        Generates a list of rho values for a specified number of sections by peeling the
        s-parameters provided from the port provided.
        @param sp instance of class SParameters
        @param sections integer number of sections to compute
        @param port port of the SParameters instance to peel from
        """
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
        """impedance list
        @return list of impedances, in ohms, for each section.
        """
        return [max(0.,min(self.m_Z0*(1+rho)/(1-rho),self.ZLimit))
            for rho in self]
    def DelaySection(self):
        """time length of each section
        @return float time length of each section.
        """
        return self.m_Td
    def SParameters(self,f):
        """s-parameters
        @param f list of frequencies for the s-parameters
        @return instance of class SParameters calculated by aggregating the list of rho
        values using lossless transmission line sections with the rho calculated for each
        section.
        """
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
    # pragma: silent exclude
    ##
    # @var rhoLimit
    # static float upper limit on absolute value of rho before the impedance profile
    # measurement stops.
    # it defaults to 0.99
    # it stops at this limit because this is effectively an open or short and continuing
    # would be fruitless and cause the algorithm to blow up.
    # @var ZLimit
    # static float upper limit on Z when rho is converted to Z.  Values higher than this
    # Z are clipped to this value so it doesn't go to infinity.
    # @var m_Td
    # float time length of each section.
    # @var m_Z0
    # reference impedance corresponding to the rho values taken from the s-parameters
    # supplied.
    # @var m_fracD
    # float fractional delay time determined while converting the s-parameter file
    # to impulse response.
