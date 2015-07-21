import unittest
import SignalIntegrity as si
from numpy import matrix
import math
import cmath
from numpy import linalg
from numpy import array
import os
from TestHelpers import *

class TestImpedanceProfile(unittest.TestCase,SParameterCompareHelper):
    def testImpedanceProfileCable(self):
        sp = si.sp.File('cable.s2p')
        ip = si.ip.ImpedanceProfile(sp,100,2)
        Z0 = 50.
        Zc = [-Z0*(rho+1.)/(rho-1) for rho in ip]
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
        pass
    def testImpedanceProfileContrived(self):
        N=1000
        f=[20.e9*n/N for n in range(N+1)]
        Td=1./(2.*f[N])
        gamma=[1j*2.*math.pi*fe*Td for fe in f]
        Zc = [50.,55.,50.,45.,60.,52.,50.,50.,50.]
        Z0=50.
        rho = [(Z-Z0)/(Z+Z0) for Z in Zc]
        Gsp=[]
        for n in range(N+1):
            T = [si.cvt.S2T(si.dev.IdealTransmissionLine(rho[m],gamma[n])) for m in range(len(rho))]
            tacc=matrix([[1.,0.],[0.,1.]])
            for m in range(len(rho)):
                tacc=tacc*matrix(T[m])
            G=si.cvt.T2S(tacc.tolist())
            Gsp.append(G)
        sp = si.sp.SParameters(f,Gsp,Z0)
        ip = si.ip.ImpedanceProfile(sp,len(Zc),1)
        Zc2 = [-Z0*(rho+1.)/(rho-1) for rho in ip]
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
#       print Zc2 # should be equal to Zc
        difference = linalg.norm(array(Zc2)-array(Zc))
        self.assertTrue(difference<1e-4,'contrived impedance profile incorrect')
    def testCableDeembed(self):
        sp = si.sp.File('cable.s2p')
        ip = si.ip.ImpedanceProfile(sp,6,1)
        Z0 = 50.
        Zc = [-Z0*(rho+1.)/(rho-1) for rho in ip]
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
        spls=ip.SParameters(sp.f())
        spls.WriteToFile('cableLeftSide.s2p')
        ip = si.ip.ImpedanceProfile(sp,6,2)
        Zc = [-Z0*(rho+1.)/(rho-1) for rho in ip]
        """
        import matplotlib.pyplot as plt
        plt.plot(Zc)
        plt.show()
        """
        sprs=ip.SParameters(sp.f())
        sprs.WriteToFile('cableRightSide.s2p')
        dp = si.p.DeembedderNumericParser(sp.f())
        dp.AddLines(['unknown ?1 2',
                     'device L 2 file cableLeftSide.s2p',
                     'device R 2 file cableRightSide.s2p',
                     'port 1 L 1 2 R 1',
                     'connect L 2 ?1 1',
                     'connect R 2 ?1 2',
                     'system file cable.s2p'])
        cd = dp.Deembed()
        fileName='cableDeembedded.s2p'
        if not os.path.exists(fileName):
            cd.WriteToFile(fileName)
            self.assertTrue(False,fileName + 'does not exist')
        regression = si.sp.File(fileName)
        self.assertTrue(self.SParametersAreEqual(cd,regression,0.001),self.id()+'result not same')
if __name__ == "__main__":
    unittest.main()