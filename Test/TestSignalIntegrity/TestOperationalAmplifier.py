"""
TestOperationalAmplifier.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import matrix
from TestHelpers import *

class TestOperationalAmplifier(unittest.TestCase,SourcesTesterHelper,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testOperationalAmplifier(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device A 4',
            'device ZI1 2',
            'device ZI2 2',
            'device G 1 ground',
            'port 1 ZI1 1',
            'port 2 ZI2 1',
            'port 3 A 4',
            'connect A 3 G 1',
            'connect ZI1 2 A 1',
            'connect ZI2 2 A 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('ZI1',si.sy.ShuntZ(2,'Zi'))
        ssps.AssignSParameters('ZI2',si.sy.ShuntZ(2,'Zi'))
        ssps.AssignSParameters('A',si.sy.VoltageAmplifier(4, 'G', 'Zd', 'Zo'))
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Operational Amplifier')
    def testOperationalAmplifierNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device A 4',
            'device ZI1 2',
            'device ZI2 2',
            'device G 1 ground',
            'port 1 ZI1 1',
            'port 2 ZI2 1',
            'port 3 A 4',
            'connect A 3 G 1',
            'connect ZI1 2 A 1',
            'connect ZI2 2 A 2'])
        sspn = si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        Zi=34.
        Zd=45.
        G=2.34
        Zo=4.56
        sspn.AssignSParameters('ZI1',si.dev.ShuntZ(2,Zi))
        sspn.AssignSParameters('ZI2',si.dev.ShuntZ(2,Zi))
        sspn.AssignSParameters('A',si.dev.VoltageAmplifier(4, G, Zd, Zo))
        res1=sspn.SParameters()
        res2=si.dev.OperationalAmplifier(Zi,Zd,Zo,G)
        difference = linalg.norm(matrix(res1)-matrix(res2))
        self.assertTrue(difference<1e-10,'Operational Amplifier Numeric incorrect')
    def testOperationalAmplifierNumericParser(self):
        sdp=si.p.SystemDescriptionParser()
        Zi=34.
        Zd=45.
        G=2.34
        Zo=4.56
        sdp.AddLines(['device D 3 opamp zi '+str(Zi)+' zd '+str(Zd)+' zo '+str(Zo)+' gain '+str(G),
                      'port 1 D 1 2 D 2 3 D 3'])
        sspn = si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        res1=sspn.SParameters()
        res2=si.dev.OperationalAmplifier(Zi,Zd,Zo,G)
        difference = linalg.norm(matrix(res1)-matrix(res2))
        self.assertTrue(difference<1e-10,'Operational Amplifier Numeric Parser incorrect')
    def testWriteCodeOperationalAmplifier(self):
        self.WriteCode('TestOperationalAmplifier.py','testOperationalAmplifier(self)',self.standardHeader)
    def testOperationalAmplifierSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3',
            'port 1 D 1 2 D 2 3 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
            eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
        D=si.sy.OperationalAmplifier('Z_i','Z_d','Z_o','G')
        ssps.AssignSParameters('D',D)
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Operational Amplifier Symbolic')

if __name__ == '__main__':
    unittest.main()

