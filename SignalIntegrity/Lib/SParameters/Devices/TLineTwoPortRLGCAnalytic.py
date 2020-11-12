"""analytic single-ended telegraphers transmission line"""

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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.Devices import SeriesZ

class TLineTwoPortRLGCAnalytic(SParameters):
    """s-parameters of analytic single-ended telegraphers transmission line"""
    def __init__(self,f, R, Rse, L, G, C, df, Z0=50., scale=1.):
        """Constructor
        @param f list of float frequencies
        @param R float DC series resistance (ohms)
        @param Rse float series skin-effect resistance (ohms/sqrt(Hz))
        @param L float series inductance (H)
        @param G float DC conductance to ground (S)
        @param C float capacitance to ground (F)
        @param df float dissipation factor (loss-tangent) of capacitance to ground
        @param Z0 (optional) float reference impedance (defaults to 50 ohms)
        @param scale (optional) float amount to scale the line by (assuming all other values are per unit)
        """
        self.R=R*scale;   self.Rse=Rse*scale; self.L=L*scale
        self.G=G*scale;   self.C=C*scale;     self.df=df
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.Devices.TLineTwoPort import TLineTwoPort
        # pragma: include
        f=self.m_f[n]
        Z=self.R+self.Rse*(1+1j)*math.sqrt(f)+1j*2*math.pi*f*self.L
        Y=self.G+2.*math.pi*f*self.C*(1j+self.df)
        try: Zc=cmath.sqrt(Z/Y)
        except: return SeriesZ(Z)
        gamma=cmath.sqrt(Z*Y)
        return TLineTwoPort(Zc,gamma,self.m_Z0)
