"""Mixed mode differential transmission line"""

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

class MixedModeTLine(SParameters):
    """s-parameters of a mixed-mode, balanced transmission line"""
    def __init__(self,f,Zd,Td,Zc,Tc,Z0=50.):
        """Constructor
        The port numbering is ports 1 and 2 are the plus and minus terminals on
        one side of the line and ports 3 and 4 are the plus and minus terminals
        on the other side of the line.
    
        @param f list of float frequencies
        @param Zd float or complex differential mode impedance
        @param Td float differential (or odd-mode) electrical length (the
        differential-mode propagation time.
        @param Zc float or complex common-mode impedance
        @param Tc float common (or even-mode) electrical length (the common-mode
        propagation time.
        @param Z0 (optional) float or complex reference impedance (defaults to 50 Ohms).
        @note The differential mode impedance is twice the odd-mode impedance.\n
        The common-mode impedance is half the even-mode impedance.\n
        @note The model is appropriate for a balanced transmission line.\n
        @note The s-parameters provided are single-ended.
        @note This device builds a model internally and only solves the model
        on each access to __getitem__().
        """
        import SignalIntegrity.Lib.SParameters.Devices as dev
        from SignalIntegrity.Lib.Devices.MixedModeConverter import MixedModeConverter
        from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        self.m_sspn=SystemSParametersNumeric()
        self.m_spdl=[]
        self.m_sspn.AddDevice('MM1',4,MixedModeConverter())
        self.m_sspn.AddDevice('MM2',4,MixedModeConverter())
        self.m_sspn.AddDevice('D',2), self.m_spdl.append(('D',dev.TLineLossless(f,2,Zd/2.,Td,Z0)))
        self.m_sspn.AddDevice('C',2), self.m_spdl.append(('C',dev.TLineLossless(f,2,Zc*2.,Tc,Z0)))
        self.m_sspn.ConnectDevicePort('MM1',3,'D',1)
        self.m_sspn.ConnectDevicePort('MM2',3,'D',2)
        self.m_sspn.ConnectDevicePort('MM1',4,'C',1)
        self.m_sspn.ConnectDevicePort('MM2',4,'C',2)
        self.m_sspn.AddPort('MM1',1,1)
        self.m_sspn.AddPort('MM1',2,2)
        self.m_sspn.AddPort('MM2',1,3)
        self.m_sspn.AddPort('MM2',2,4)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        for ds in self.m_spdl: self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        return self.m_sspn.SParameters()
