"""
 base class for netlist deembedding solutions
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

from SignalIntegrity.Lib.SystemDescriptions.Deembedder import Deembedder
from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
from SignalIntegrity.Lib.Parsers.Devices.DeviceParser import DeviceParser
import copy

class DeembedderParser(SystemDescriptionParser):
    """base class for netlist based deembedding solutions"""
    def __init__(self, f=None, args=None):
        """Constructor

        frequencies may be provided at construction time (or not for symbolic solutions).

        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.

        Arguments are provided on a line as pairs of names and values separated by a space.
        """
        SystemDescriptionParser.__init__(self, f, args)
    def _ProcessDeembedderLine(self,line):
        """processes a line of a netlist, handing deembedding specific commands

        Lines that can be processed at this level are processed and lines that
        are unknown are place in a list of unknown lines for upstream processing.  This
        enables derived classes to benefit from what this class knows how to process and
        to simply add specific functionality.  As a simple example, a derived simulator class
        needs to add output probes, and this simple system description class knows nothing of
        this.

        netlist lines that are handled at this level are:
        - 'system' - addition of the system
        - 'unknown' - addition of a device whose s-parameters are unknown.

        Calls SystemDescriptionParser._ProcessLines()
        exludes 'connect' and 'port' in first call, then processes simulator lines, then
        calls upstream one more time for the device connections, again excluding 'port'.
        """
        lineList=self.ReplaceArgs(line.split())
        if len(lineList) == 0: # pragma: no cover
            return
        if lineList[0] == 'system':
            dev=DeviceParser(self.m_f,None,lineList[1:])
            if not dev.m_spf is None:
                self.m_spc.append(('system',dev.m_spf))
        elif lineList[0] == 'unknown':
            self.m_sd.AddUnknown(lineList[1],int(lineList[2]))
        else:
            self.m_ul.append(line)
    def _ProcessLines(self):
        """processes all of the lines in a netlist
        @see _ProcessLine() for explanation of parameters and functionality.
        """
        SystemDescriptionParser._ProcessLines(self,['connect','port'])
        self.m_sd = Deembedder(self.m_sd)
        lines=copy.deepcopy(self.m_ul)
        self.m_ul=[]
        for line in lines:
            self._ProcessDeembedderLine(line)
        lines=copy.deepcopy(self.m_ul)
        self.m_ul=[]
        for line in lines:
            SystemDescriptionParser._ProcessLine(self,line,[])
        return self
