"""
TestMixedModeTermination.py
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

import unittest

import SignalIntegrity.Lib as si
import math
import os
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless

class TestMixedModeTermination(unittest.TestCase,si.test.RoutineWriterTesterHelper,si.test.ResponseTesterHelper,si.test.SourcesTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testTerminationMixedModeSymbolic(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device MM 4 mixedmode','device S 2','connect S 1 MM 1',
            'connect MM 2 S 2','port 1 MM 3 2 MM 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(), ssps, self.id())
    def testTerminationMixedModeSymbolicCode(self):
        self.WriteCode('TestMixedModeTermination.py','testTerminationMixedModeSymbolic(self)',self.standardHeader)
    def testTeeTerminationMixedModeSymbolic(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device MM 4 mixedmode','device R1 2','device R2 2','device R3 1','connect MM 1 R1 2',
            'connect R1 1 R2 2 R3 1','connect MM 2 R2 1','port 1 MM 3 2 MM 4',])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('R1',si.sy.SeriesZ('Z_1'))
        ssps.AssignSParameters('R2',si.sy.SeriesZ('Z_2'))
        ssps.AssignSParameters('R3',si.sy.ShuntZ(1,'Z_3'))
        ssps.LaTeXSolution(size='big')
        ssps.Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(), ssps, self.id())
    def testTeeTerminationSymbolicCode(self):
        self.WriteCode('TestMixedModeTermination.py','testTeeTerminationMixedModeSymbolic(self)',self.standardHeader)
    def testPiTerminationMixedModeSymbolic(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        sdp=si.p.SystemDescriptionParser().AddLines([
            'device MM 4 mixedmode','device Z3 2','device Z1 1','device Z2 1',
            'connect MM 1 Z3 2 Z1 1','connect MM 2 Z3 1 Z2 1','port 1 MM 3 2 MM 4'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('Z3',si.sy.SeriesZ('Z_3'))
        ssps.AssignSParameters('Z1',si.sy.ShuntZ(1,'Z_1'))
        ssps.AssignSParameters('Z2',si.sy.ShuntZ(1,'Z_2'))
        ssps.LaTeXSolution(size='big')
        ssps.Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(), ssps, self.id())
    def testPiTerminationSymbolicCode(self):
        self.WriteCode('TestMixedModeTermination.py','testPiTerminationMixedModeSymbolic(self)',self.standardHeader)
    def testMixedModeConversion(self):
        import SignalIntegrity.App as siapp
        pysi=siapp.SignalIntegrityAppHeadless()
        pysi.OpenProjectFile('MixedMode.si')
        netlist=[line.replace(' file None','') for line in pysi.Drawing.schematic.NetList().Text()]
        sd=si.p.SystemDescriptionParser().AddLines(netlist).SystemDescription()
        sd.AssignSParameters('MM1',si.dev.MixedModeConverter())
        sd.AssignSParameters('MM2',si.dev.MixedModeConverter())
        ssps=si.sd.SystemSParametersSymbolic(sd,size='small')
        ssps.DocStart().LaTeXSolution().DocEnd().WriteToFile('mixedmode.tex')
        
if __name__ == '__main__':
    unittest.main()