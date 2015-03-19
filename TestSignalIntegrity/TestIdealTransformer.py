import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import matrix
from TestHelpers import *

class TestIdealTransformer(unittest.TestCase,SourcesTesterHelper,RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
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
        ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
        ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('a'))
        ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('a'))
        ssps.LaTeXSolution(size='big').Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ssps,'Ideal Transformer')
    def testIdealTransformerSymbolic2(self):
        sm = si.sy.SymbolicMatrix(si.sy.IdealTransformer('a'))
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

