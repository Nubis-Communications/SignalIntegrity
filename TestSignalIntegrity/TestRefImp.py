import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import array

class TestReferenceImpedanceTransformation(unittest.TestCase):
    def testBasic(self):
        """
        This test tests the s-parameters of the shunt z by building a circuit using the
        system descriptions and computing the s-parameters that way and comparing to
        those computed through the normal calculation
        """
        Z=23+43*1j
        Z01=92-18*1j
        Z02=698+18*1j
        normalResult = array(si.cvt.ReferenceImpedance(si.dev.ShuntZTwoPort(Z),[Z01,Z02]))
        D=si.sd.SystemDescription()
        D.AddDevice('D1',2,si.dev.ShuntZTwoPort(Z))
        D.AddDevice('R1',2,si.dev.ReferenceImpedanceTransformer(Z01))
        D.AddDevice('R2',2,si.dev.ReferenceImpedanceTransformer(Z02))
        D.ConnectDevicePort('D1',1,'R1',1)
        D.ConnectDevicePort('D1',2,'R2',1)
        D.AddPort('R1',2,1)
        D.AddPort('R2',2,2)
        theRealResult=array(si.sd.SystemSParametersNumeric(D).SParameters(solvetype='direct'))
        difference = linalg.norm(normalResult-theRealResult)
        self.assertTrue(difference<1e-10,'Reference Impedance Transformation incorrect')
        #now let's convert it back to 50 Ohms
        D.AssignSParameters('D1',theRealResult.tolist())
        D.AssignSParameters('R1',si.dev.ReferenceImpedanceTransformer(50.0,Z01))
        D.AssignSParameters('R2',si.dev.ReferenceImpedanceTransformer(50.0,Z02))
        theRealResult=array(si.sd.SystemSParametersNumeric(D).SParameters())
        normalResult=array(si.cvt.ReferenceImpedance(normalResult, 50.0, [Z01,Z02]))
        difference = linalg.norm(normalResult-theRealResult)
        self.assertTrue(difference<1e-10,'Reference Impedance Transformation incorrect')
        difference2 = linalg.norm(normalResult-array(si.dev.ShuntZTwoPort(Z)))
        self.assertTrue(difference2<1e-10,'Reference Impedance Transformation incorrect')

if __name__ == '__main__':
    unittest.main()
