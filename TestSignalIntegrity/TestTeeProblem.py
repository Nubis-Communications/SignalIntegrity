import unittest

import SignalIntegrity as si

from numpy import linalg
from numpy import matrix
from numpy import identity
from TestHelpers import *

class TestTeeProblem(unittest.TestCase,SourcesTesterHelper,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
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
        regressionFile=open(fileName,'rU')
        regression = regressionFile.read()
        regressionFile.close()
        self.assertTrue(regression==mystdout.getvalue(),'Tee System Description incorrect')
    def testTeeBlockSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 thru','port 1 D 1 2 D 1 3 D 2','connect D 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.LaTeXSolution(size='biggest').Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Shunt Device Four Port Symbolic')
    def testTeeDirectSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 2 thru','port 1 D 1 2 D 1 3 D 2','connect D 2 D 2'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.LaTeXSolution(solvetype='direct').Emit()
        # exclude
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
        regressionFile=open(fileName,'rU')
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
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Simpler Block Symbolic')
    def testTeeSimplerBlockSymbolicUnsafe(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.Tee(3))
        ssps.DocStart().LaTeXSolution().DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Simpler Block Symbolic')
    def testTeeSimplerDirectSymbolic(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.Tee(3))
        ssps.InstallSafeTees()
        ssps.LaTeXSolution(solvetype='direct').Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Simpler Direct Symbolic')
    def testTeeSimplerSystemEquation(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.Tee(3))
        ssps.InstallSafeTees()
        ssps.LaTeXSystemEquation().Emit()
        # exclude
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
        # exclude
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
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee with Z Block Symbolic')
    def testTeeSimplerSystemEquationWithZ2(self):
        sdp=si.p.SystemDescriptionParser()
        sdp.AddLines(['device D 3 tee','port 1 D 1 2 D 2','connect D 2 D 3'])
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
        ssps.AssignSParameters('D',si.sy.TeeWithZ2('Z'))
        ssps.LaTeXSystemEquation().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Tee Simpler with Z2 System Equation')

if __name__ == '__main__':
    unittest.main()

