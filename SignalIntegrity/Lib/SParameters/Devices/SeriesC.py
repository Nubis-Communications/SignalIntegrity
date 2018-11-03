"""Series capacitance"""

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


class SeriesC(SParameters):
    """s-parameters of a series capacitance"""
    def __init__(self,f,C,Z0=50.,df=0.,esr=0.):
        """Constructor
        @param f list of float frequencies
        @param C float capacitance
        @param Z0 (optional) float of complex reference impedance (defaults to 50 Ohms)
        @param df (optional) float dissipation factor (or loss-tangent) (defaults to 0)
        @param esr (optional) float effective-series-resistance (defaults to 0)
        @remark The s-parameters are evaluated using the single-frequency device
        SignalIntegrity.Lib.Devices.SeriesC
        """
        self.m_C=C
        self.m_df=df
        self.m_esr=esr
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        import SignalIntegrity.Lib.Devices as dev
        # pragma: include
        return dev.SeriesC(self.m_C,self.m_f[n],self.m_Z0,self.m_df,self.m_esr)
