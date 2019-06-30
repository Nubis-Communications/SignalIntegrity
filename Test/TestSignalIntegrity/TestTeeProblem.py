"""
TestTeeProblem.py
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
import os

import sys
if sys.version_info.major < 3:
    from cStringIO import StringIO
else:
    from io import StringIO

import SignalIntegrity.Lib as si

from numpy import linalg
from numpy import matrix
from numpy import identity

class TestTeeProblem(unittest.TestCase,si.test.SourcesTesterHelper,si.test.RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def id(self):
        return 'TestTeeProblem.'+'.'.join(unittest.TestCase.id(self).split('.')[-2:])
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        si.sd.Numeric.trySVD=True
        unittest.TestCase.setUp(self)
    def tearDown(self):
        si.sd.Numeric.trySVD=True
        unittest.TestCase.tearDown(self)
    def testTeeSystemDescription(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 thru','port 1 D 1 2 D 1 3 D 2','connect D 2 D 2'])
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        sdp.SystemDescription().Print()
        sys.stdout = old_stdout
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName='_'.join(self.id().split('.'))+'.txt'
        if not os.path.exists(fileName):
            resultFile=open(fileName,'w')
            resultFile.write(mystdout.getvalue())
            resultFile.close()
            self.assertTrue(False,fileName+ ' not found')
        regressionFile=open(fileName,'rU' if sys.version_info.major < 3 else 'r')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression==mystdout.getvalue(),'Tee System Description incorrect')
    def testTeeBlockSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 thru','port 1 D 1 2 D 1 3 D 2','connect D 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Device Four Port Symbolic')
    def testTeeDirectSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 thru','port 1 D 1 2 D 1 3 D 2','connect D 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.LaTeXSolution(solvetype='direct').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Device Four Port Symbolic')
    def testTeeNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 thru','port 1 D 1 2 D 1 3 D 2','connect D 2 D 2'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.InstallSafeTees()
        rescalc1=sspn.SParameters()
        rescalc2=sspn.SParameters(solvetype='direct')
        rescorrect=si.dev.Tee()
        difference = linalg.norm(matrix(rescalc1)-matrix(rescalc2))
        self.assertTrue(difference<1e-6,'Tee Numeric incorrect')
    def testTeeSimplerSystemDescription(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        sdp.SystemDescription().Print()
        sys.stdout = old_stdout
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        fileName='_'.join(self.id().split('.'))+'.txt'
        if not os.path.exists(fileName):
            resultFile=open(fileName,'w')
            resultFile.write(mystdout.getvalue())
            resultFile.close()
            self.assertTrue(False,fileName+ ' not found')
        regressionFile=open(fileName,'rU' if sys.version_info.major < 3 else 'r')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression==mystdout.getvalue(),'Tee Simpler System Description incorrect')
    def testTeeSimplerBlockSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.Tee(3))
        ssps.InstallSafeTees()
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Simpler Block Symbolic')
    def testTeeSimplerBlockSymbolicUnsafe(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.Tee(3))
        sdp.SystemDescription().Print()
        ssps.DocStart().LaTeXSolution().DocEnd().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Simpler Block Symbolic')
    def testTeeSimplerDirectSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.Tee(3))
        ssps.InstallSafeTees()
        ssps.LaTeXSolution(solvetype='direct').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Simpler Direct Symbolic')
    def testTeeSimplerSystemEquation(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.Tee(3))
        ssps.InstallSafeTees()
        ssps.LaTeXSystemEquation().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Simpler System Equation')
    def testTeeSimplerNumeric(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        sspn=si.sd.SystemSParametersNumeric(sdp.SystemDescription())
        sspn.InstallSafeTees()
        rescalc2=sspn.SParameters(solvetype='direct')
        rescalc1=sspn.SParameters()
        rescorrect=si.dev.Tee()
        difference = linalg.norm(matrix(rescalc1)-matrix(rescalc2))
        self.assertTrue(difference<1e-10,'Tee Simpler Numeric incorrect')
    def testTeeWithZBlockSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','device Z 2',
            'port 1 D 1 2 D 2 3 Z 2','connect D 3 Z 1'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.Tee(3))
        ssps.AssignSParameters('Z',si.sy.SeriesZ('Z'))
        ssps.LaTeXSolution().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee with Z Block Symbolic')
    def testTeeWithZAllAroundBlockSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3','device Z1 2','device Z2 2','device Z3 2',
            'port 1 Z1 1 2 Z2 1 3 Z3 1','connect Z1 2 D 1','connect Z2 2 D 2','connect Z3 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.Tee(3))
        ssps.AssignSParameters('Z1',si.sy.SeriesZ('Z_1'))
        ssps.AssignSParameters('Z2',si.sy.SeriesZ('Z_2'))
        ssps.AssignSParameters('Z3',si.sy.SeriesZ('Z_3'))
        ssps.LaTeXSolution(size='biggest').Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee with Z Block Symbolic')
    def testTeeSimplerSystemEquationWithZ2(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.TeeWithZ2('Z'))
        ssps.LaTeXSystemEquation().Emit()
        # pragma: exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Simpler with Z2 System Equation')
    def testTeeZAllAroundComprehensive(self):
        sym=si.sd.Symbolic()
        sym.DocStart()
        sym._AddEq('\\mathbf{S} = '+sym._LaTeXMatrix(si.sy.TeeThreePortZ1Z2Z3('Z_1', 'Z_2', 'Z_3')))
        sym.DocEnd()
        sym.Emit()
        self.CheckSymbolicResult(self.id(),sym,'Tee Z1 Z2 Z3')
if __name__ == '__main__':
    unittest.main()

