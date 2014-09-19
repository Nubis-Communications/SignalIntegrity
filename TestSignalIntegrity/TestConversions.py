import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import array
from numpy import matrix

class TestConversions(unittest.TestCase):
    def testABCD2SDefault(self):
        R=100
        ABCD=[[1,-R],[0,1]]
        difference = linalg.norm(si.dev.SeriesZ(R)-array(si.cvt.ABCD2S(ABCD)))
        self.assertTrue(difference<1e-10,'100 Ohm ABCD not equal S with default Z0, K')
    def testABCD2S50(self):
        R=20
        ABCD=[[1,-R],[0,1]]
        Z0=50.0
        difference = linalg.norm(si.dev.SeriesZ(R,Z0)-array(si.cvt.ABCD2S(ABCD,Z0)))
        self.assertTrue(difference<1e-10,'20 Ohm ABCD not equal S with  Z0=50 Ohm, default K')
    def testABCD2S150(self):
        R=85
        ABCD=[[1,-R],[0,1]]
        Z0=100.0
        difference = linalg.norm(si.dev.SeriesZ(R,Z0)-array(si.cvt.ABCD2S(ABCD,Z0)))
        self.assertTrue(difference<1e-10,'85 Ohm ABCD not equal S with  Z0=150 Ohm, default K')
    def testABCD2SZ0ListConstant(self):
        R=29
        ABCD=[[1,-R],[0,1]]
        Z0=[45.,45.]
        difference = linalg.norm(si.dev.SeriesZ(R,Z0)-array(si.cvt.ABCD2S(ABCD,Z0)))
        self.assertTrue(difference<1e-10,'29 Ohm ABCD not equal S with  Z0=list same, default K')
    def testABCD2SZ0ListDifferent(self):
        R=134
        ABCD=[[1,-R],[0,1]]
        Z0=[25.,95.]
        difference = linalg.norm(si.dev.SeriesZ(R,Z0)-array(si.cvt.ABCD2S(ABCD,Z0)))
        self.assertTrue(difference<1e-10,'134 Ohm ABCD not equal S with  Z0=list different, default K')
    def testABCD2SComplexZ(self):
        R=23+1j*134
        ABCD=[[1,-R],[0,1]]
        Z0=[25.,95.]
        difference = linalg.norm(si.dev.SeriesZ(R,Z0)-array(si.cvt.ABCD2S(ABCD,Z0)))
        self.assertTrue(difference<1e-10,'Complex Series Z ABCD not equal S with  Z0=list different, default K')
    def testABCD2SComplexZComplexZ0List(self):
        R=23+1j*134
        ABCD=[[1,-R],[0,1]]
        Z0=[25+1j*34,95.-1j*91]
        difference = linalg.norm(si.dev.SeriesZ(R,Z0)-array(si.cvt.ABCD2S(ABCD,Z0)))
        self.assertTrue(difference<0.0001,'Complex Series Z ABCD not equal S with  Z0=list different, default K')
    def testABCD2SComplexZComplexZ0array(self):
        R=23+1j*134
        ABCD=[[1,-R],[0,1]]
        Z0=array([[25+1j*34,0.0],[0.0,95.-1j*91]])
        difference = linalg.norm(si.dev.SeriesZ(R,Z0)-array(si.cvt.ABCD2S(ABCD,Z0)))
        self.assertTrue(difference<1e-10,'Complex Series Z ABCD not equal S with  Z0=list different, default K')
    def testABCD2SComplexZComplexZ0matrix(self):
        R=23+1j*134
        ABCD=[[1,-R],[0,1]]
        Z0=matrix([[25+1j*34,0.0],[0.0,95.-1j*91]])
        difference = linalg.norm(si.dev.SeriesZ(R,Z0)-array(si.cvt.ABCD2S(ABCD,Z0)))
        self.assertTrue(difference<1e-10,'Complex Series Z ABCD not equal S with  Z0=list different, default K')
    def testShuntZ(self):
        """
        This test tests the s-parameters of the shunt z by building a circuit using the system descriptions
        and computing the s-parameters that way and comparing to those computed through the normal calculation
        """
        Z=23+43*1j
        normalResult = array(si.dev.ShuntZ(Z))
        D=si.sd.SystemDescription()
        D.AddDevice('D1',2,si.dev.SeriesZ(Z))
        D.AddDevice('G1',1,si.dev.Ground())
        D.ConnectDevicePort('D1',2,'G1',1)
        D.AddPort('D1',1,1)
        D.AddPort('D1',1,2)
        theRealResult=array(si.sd.SystemSParametersNumeric(D).SParameters())
        difference = linalg.norm(normalResult-theRealResult)
        self.assertTrue(difference<1e-10,'Shunt Z incorrect')
    def testZ2SComplexZComplexZ0matrix(self):
        R=23+1j*134
        Z=[[R,R],[R,R]]
        Z0=matrix([[25+1j*34,0.0],[0.0,95.-1j*91]])
        difference = linalg.norm(si.dev.ShuntZ(R,Z0)-array(si.cvt.Z2S(Z,Z0)))
        self.assertTrue(difference<1e-10,'Complex Series Z Z not equal S with  Z0=list different, default K')
    def testZ2SComplexZComplexZ0List(self):
        R=23+1j*134
        Z=[[R,R],[R,R]]
        Z0=[25+1j*34,95.-1j*91]
        difference = linalg.norm(si.dev.ShuntZ(R,Z0)-array(si.cvt.Z2S(Z,Z0)))
        self.assertTrue(difference<0.0001,'Complex Series Z ABCD not equal S with  Z0=list different, default K')

if __name__ == '__main__':
    unittest.main()

