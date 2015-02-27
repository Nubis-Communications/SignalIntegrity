import unittest

import SignalIntegrity as si
import os

class TestRLGC(unittest.TestCase):            
    def testRLGC(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        spf=si.spf.File('cable.s2p')
        rlgc = si.spf.RLGC(spf)
        pass

if __name__ == '__main__':
    unittest.main()
