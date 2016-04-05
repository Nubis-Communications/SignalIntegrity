import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import array
from numpy import matrix

class TestWavelets(unittest.TestCase):
    def testDWT(self):
        K=16
        x=[k for k in range(K)]
        w=si.wl.WaveletDaubechies4()
        X=w.DWT(x)
        XM=[13.038,29.389,-10.574,1.812,-7.660,-0.000,-0.000,0.732,-5.657,-0.000,-0.000,-0.000,0.000,0.000,-1.776e-15,-1.776e-15]
        difference = linalg.norm([XM[k]-X[k] for k in range(K)])
        self.assertTrue(difference<1e-3,'DWT incorrect')
    def testIDWT(self):
        K=16
        x=[k for k in range(K)]
        w=si.wl.WaveletDaubechies4()
        X=w.DWT(x)
        xc=w.IDWT(X)
        difference = linalg.norm([x[k]-xc[k] for k in range(K)])
        self.assertTrue(difference<1e-3,'DWT incorrect')
