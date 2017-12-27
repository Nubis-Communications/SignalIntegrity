import unittest

import SignalIntegrity as si
from TestHelpers import RoutineWriterTesterHelper,ResponseTesterHelper
import os

class TestSParameterEnforcements(unittest.TestCase,RoutineWriterTesterHelper,ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testPassivityEnforcement(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        pefn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        self.assertTrue(any([sv > 1.+1e-15 for sv in sf._LargestSingularValues()]),' already passive')
        sf.EnforcePassivity()
        self.assertFalse(any([sv > 1.+1.e-15 for sv in sf._LargestSingularValues()]),' passivity not enforced')
        self.CheckSParametersResult(sf, pefn, 'passivity enforced s-parameters incorrect')
    def testCausalityEnforcement(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        cefn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        self.assertFalse(sf.IsCausal(1e-9),' already causal')
        sf.EnforceCausality()
        self.assertTrue(sf.IsCausal(1e-9),' causality not enforced')
        self.CheckSParametersResult(sf, cefn, 'causality enforced s-parameters incorrect')
    def testWaveletDenoising(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        wdfn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        sf.WaveletDenoise()
        self.CheckSParametersResult(sf, wdfn, 'wavelet denoised s-parameters incorrect')

if __name__ == "__main__":
    unittest.main()