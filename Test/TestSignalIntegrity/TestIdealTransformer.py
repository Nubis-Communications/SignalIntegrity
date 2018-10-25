"""
TestIdealTransformer.py
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

class TestIdealTransformer(unittest.TestCase,si.test.SourcesTesterHelper,si.test.RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testIdealTransformerSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device DV 4',
            'device DC 4',
            'port 1 DC 4',
            'port 2 DC 3',
            'port 3 DC 1',
            'port 4 DV 3',
            'connect DC 2 DV 4',
            'connect DC 4 DV 2',
            'connect DC 3 DV 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('a'))
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('a'))
        ssps.LaTeXSolution(size='big').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Ideal Transformer')
    def testIdealTransformerSymbolic2(self):
        sm = si.sd.Symbolic()
        sm._AddEq(sm._LaTeXMatrix(si.sy.IdealTransformer('a')))
        self.CheckSymbolicResult(self.id(),sm,'Ideal Transformer')
    def testIdealTransformerSymbolic3(self):
        sm = si.sd.Symbolic()
        sm._AddEq(sm._LaTeXMatrix(si.sy.IdealTransformer(10)))
        self.CheckSymbolicResult(self.id(),sm,'Ideal Transformer')
    def testIdealTransformerNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        a=10 #turns ratio for ideal transformer
        sdp.AddLines(['device DV 4 voltagecontrolledvoltagesource '+str(a),
            'device DC 4 currentcontrolledcurrentsource '+str(a),
            'port 1 DC 4',
            'port 2 DC 3',
            'port 3 DC 1',
            'port 4 DV 3',
            'connect DC 2 DV 4',
            'connect DC 4 DV 2',
            'connect DC 3 DV 1'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.IdealTransformer(a)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Ideal Transformer incorrect')
        pass
    def testIdealTransformerNumeric2(self):
        sdp=si.p.SystemDescriptionParser()
        a=10 #turns ratio for ideal transformer
        sdp.AddLines(['device D 4 idealtransformer '+str(a),
            'port 1 D 1',
            'port 2 D 2',
            'port 3 D 3',
            'port 4 D 4'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        rescalc=sspn.SParameters()
        rescorrect=si.dev.IdealTransformer(a)
        difference = linalg.norm(matrix(rescalc)-matrix(rescorrect))
        self.assertTrue(difference<1e-10,'Ideal Transformer incorrect')
    def testIdealTransformerSymbolicCode(self):
        self.WriteCode('TestIdealTransformer.py','testIdealTransformerSymbolic(self)',self.standardHeader)

if __name__ == '__main__':
    unittest.main()

