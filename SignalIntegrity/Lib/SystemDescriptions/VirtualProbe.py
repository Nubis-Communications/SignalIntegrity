"""
 Virtual Probe Base Class for Housekeeping Functions
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

from SignalIntegrity.Lib.SystemDescriptions.Simulator import Simulator
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSimulator
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionVirtualProbe

class VirtualProbe(Simulator,object):
    """Base class for virtual probing"""
    def __init__(self,sd):
        Simulator.__init__(self,sd)
        self.m_ml = sd.m_ml if hasattr(sd, 'm_ml') else None
        self.m_D = sd.m_D if hasattr(sd, 'm_D') else None
    def Check(self):
        if self.m_ml is None:
            raise SignalIntegrityExceptionVirtualProbe('no measures')
        try:
            Simulator.Check(self)
        except SignalIntegrityExceptionSimulator as e:
            raise SignalIntegrityExceptionVirtualProbe(e.message)
    @property
    def pMeasurementList(self):
        """property containing the list of measurements
        @return list of measurement (input waveforms)
        """
        return self.m_ml
    @pMeasurementList.setter
    def pMeasurementList(self,ml=None):
        if not ml is None: self.m_ml = ml
        return self
    @property
    def pStimDef(self):
        return self.m_D
    @pStimDef.setter
    def pStimDef(self,D=None):
        """property containing the stimdef
        @param D (optional) list of list matrix defining a stimdef
        @return self
        Sets a stimdef to the matrix provided.
        """
        if not D is None: self.m_D = D
        return self
