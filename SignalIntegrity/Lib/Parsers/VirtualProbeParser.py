"""
 base class for virtual probe netlist handling
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

from SignalIntegrity.Lib.SystemDescriptions import VirtualProbe
from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
import copy

class VirtualProbeParser(SystemDescriptionParser):
    """base class for netlist based virtual probing solutions"""
    def __init__(self, f=None, args=None):
        """Constructor

        frequencies may be provided at construction time (or not for symbolic solutions).

        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.

        Arguments are provided on a line as pairs of names and values separated by a space.
        """
        SystemDescriptionParser.__init__(self, f, args)
    def _ProcessVirtualProbeLine(self,line):
        """processes a line of a netlist, handing virtual probe specific commands

        Lines that can be processed at this level are processed and lines that
        are unknown are place in a list of unknown lines for upstream processing.  This
        enables derived classes to benefit from what this class knows how to process and
        to simply add specific functionality.  As a simple example, a derived simulator class
        needs to add output probes, and this simple system description class knows nothing of
        this.

        netlist lines that are handled at this level are:
        - 'output' - addition of an output probe
        - 'meas' - addition of a measurement probe.
        - 'stim' - addition of a stimulus source.
        - 'stimdef' - definition of a stimdef (the relationship between stims).

        """
        lineList=self.ReplaceArgs(line.split())
        if len(lineList) == 0: # pragma: no cover
            return
        if lineList[0] == 'meas':
            if self.m_sd.pMeasurementList is None:
                self.m_sd.pMeasurementList = []
            for i in range(1,len(lineList),2):
                self.m_sd.pMeasurementList.append((lineList[i],int(lineList[i+1])))
        elif lineList[0] == 'output':
            if self.m_sd.pOutputList is None:
                self.m_sd.pOutputList = []
            for i in range(1,len(lineList),2):
                self.m_sd.pOutputList.append((lineList[i],int(lineList[i+1])))
        elif lineList[0] == 'stim':
            for i in range((len(lineList)-1)//3):
                self.m_sd.AssignM(lineList[i*3+2],int(lineList[i*3+3]),lineList[i*3+1])
        elif lineList[0] == 'stimdef':
            self.m_sd.pStimDef = [[float(e) for e in r] for r in [s.split(',')
                for s in ''.join(lineList[1:]).strip(' ').strip('[[').
                    strip(']]').split('],[') ]]
        else:
            self.m_ul.append(line)
    def _ProcessLines(self):
        """processes all of the lines in a netlist
        @see _ProcessLine() for explanation of parameters and functionality.
        """
        SystemDescriptionParser._ProcessLines(self)
        self.m_sd = VirtualProbe(self.m_sd)
        lines=copy.deepcopy(self.m_ul)
        self.m_ul=[]
        for line in lines:
            self._ProcessVirtualProbeLine(line)
        return self
