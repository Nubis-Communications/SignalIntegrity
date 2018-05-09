import unittest
import SignalIntegrity as si
from TestSignalIntegrity.TestHelpers import SParameterCompareHelper
import os

class TestYuriyNormalizationTest(unittest.TestCase,SParameterCompareHelper):
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def __init__(self, methodName='runTest'):
        SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testNormalization(self):
        regular=si.sp.SParameterFile('Project1_t-line_Simulation_same.s2p')
        different=si.sp.SParameterFile('Project1_t-line_Simulation_diff.s2p')
        # The different file, is actually touchstone 2 and has reference impedance
        # of 50 Ohms on port 1 and 25 Ohms on port 2
        converted=si.sp.SParameters(different.f(),
            [si.cvt.ReferenceImpedance(S, 50.0, [50.0,25.0]) for S in different])
        self.assertTrue(self.SParametersAreEqual(regular, converted, 1e-9))

if __name__ == "__main__":
    runProfiler=False
    if runProfiler:
        import cProfile
        cProfile.run('unittest.main()','stats')
        import pstats
        p = pstats.Stats('stats')
        p.strip_dirs().sort_stats('cumulative').print_stats(30)
    else:
        unittest.main()
