import unittest

import SignalIntegrity as si
import math
import os

class TestTline(unittest.TestCase):
    def testTline(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=[(n+1)*20e6 for n in range(100)]
        #SParametersAproximateTLineModel(f,Rsp,Lsp,Csp,Gsp,Rsm,Lsm,Csm,Gsm,Lm,Cm,Gm,Z0,K)
        SP=si.dev.ApproximateFourPortTLine(
            f,
                10.,5.85e-8,2e-11,0.01,
                10.,5.85e-8,2e-11,0.01,
                1.35e-8,1.111e-12,1e-30,50,100)
        sf=si.sp.SParameters(f,SP)
        fileName='_'.join(self.id().split('.'))+'.s'+str(sf.m_P)+'p'
        if not os.path.exists(fileName):
            sf.WriteToFile(fileName)
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.File(fileName)
        self.assertTrue(sf.AreEqual(regression,0.001),self.id()+'result not same')
        """
        import matplotlib.pyplot as plt
        for r in range(4):
            for c in range(4):
                y=[20*math.log(abs(SP[n][r][c]),10) for n in range(len(f))]
                plt.subplot(4,4,r*4+c+1)
                plt.plot(f,y)
        plt.show()
        """

if __name__ == '__main__':
    unittest.main()
