"""skin-effect resistance"""

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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class SeriesRse(SParameters):
    """s-parameters of series skin-effect Resistance"""
    def __init__(self,f,Rse,Z0=50.):
        """Constructor
        @param f list of float frequencies
        @param Rse float resistance specified as Ohms/sqrt(Hz)
        @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
        @note a skin-effect resistance is simply a resistance that is proportional to 
        the square-root of the frequency."""
        self.m_Rse=Rse
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        import SignalIntegrity.Lib.Devices as dev
        # pragma: include
        return dev.SeriesRse(self.m_f[n],self.m_Rse,self.m_Z0)
