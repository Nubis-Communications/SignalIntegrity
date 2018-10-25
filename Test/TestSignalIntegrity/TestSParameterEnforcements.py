"""
TestSParameterEnforcements.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import unittest

import SignalIntegrity as si
import os

class TestSParameterEnforcements(unittest.TestCase,si.test.RoutineWriterTesterHelper,si.test.ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testPassivityEnforcement(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        pefn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        self.assertTrue(any([sv > 1.+1e-15 for sv in sf._LargestSingularValues()]),' already passive')
        sf.EnforcePassivity(0.99999999999999)
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