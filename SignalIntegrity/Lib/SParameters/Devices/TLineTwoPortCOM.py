"""single-ended COM transmission line"""

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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class TLineTwoPortCOM(SParameters):
    """s-parameters of COM transmission line"""
    def __init__(self,f,gamma_0,a_1,a_2,tau,Zc,d,Z0=50.):
        """Constructor
        COM Two-port Transmission Line
        @param f frequency list in Hz
        @param gamma_0 float transmission line gamma_0 in units 1/mm
        @param a_1 float transmission line parameter in units sqrt(ns)/mm
        @param a_2 float transmission line parameter in units ns/mm
        @param tau float transmission line parameter in units ns/mm
        @param Z_c float differential mode characterisitic impedance in units of ohms
        @param d float length in units mm 
        @param Z0 (optional) float or complex reference impedance Z0 (defaults to 50 ohms).
        @return the s-parameter matrix of a COM defined two-port transmission line  
        """
        self.gamma_0=gamma_0;   self.a_1=a_1; self.a_2=a_2
        self.tau=tau;   self.Zc=Zc;     self.d=d
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.Devices.TLineTwoPortCOM import TLineTwoPortCOM
        # pragma: include
        return TLineTwoPortCOM(self.m_f[n],self.gamma_0,self.a_1,self.a_2,self.tau,self.Zc,self.d,self.m_Z0)
