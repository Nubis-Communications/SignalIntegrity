"""
TestSParameterEnforcements.py
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import unittest

import SignalIntegrity.Lib as si
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
        self.CheckSParametersResult(sf, pefn, 'passivity enforced s-parameters')
    def testCausalityEnforcement(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        cefn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        self.assertFalse(sf.IsCausal(1e-9),' already causal')
        sf.EnforceCausality()
        self.assertTrue(sf.IsCausal(1e-9),' causality not enforced')
        self.CheckSParametersResult(sf, cefn, 'causality enforced s-parameters')
    def testWaveletDenoising(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        wdfn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        sf.WaveletDenoise()
        self.CheckSParametersResult(sf, wdfn, 'wavelet denoised s-parameters')
    def testImpulseResponseLimitingSingle(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        wdfn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        sf.LimitImpulseResponseLength((-0.5e-12,3e-9))
        self.CheckSParametersResult(sf, wdfn, 'impulse response limited s-parameters')
    def testImpulseResponseLimitingList(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        wdfn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        sf.LimitImpulseResponseLength([[(-0.5e-12,3e-9),(-0.5e-12,5e-9)],[(-0.5e-12,5e-9),(-0.5e-12,3e-9)]])
        self.CheckSParametersResult(sf, wdfn, 'impulse response limited s-parameters')
    def testDetermineImpulseResponseLimits(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        lengths=sf.DetermineImpulseResponseLength(allLengths=True)
        self.assertTrue(lengths==[[(-5e-08, 5e-08), (-5e-08, 5e-08)], [(-5e-08, 4.9975e-08), (-5e-08, 5e-08)]],'initialial impulse response lengths incorrect')
        sf.LimitImpulseResponseLength([[(0,3e-9),(0,5e-9)],[(0,5e-9),(0,3e-9)]])
        lengths=sf.DetermineImpulseResponseLength(allLengths=True)
        self.assertTrue(lengths==[[(0.0, 3e-09),(0.0, 5e-09)],[(0.0, 5e-09),(0.0, 3e-09)]],'limited impulse response lengths incorrect')
        lengths=sf.DetermineImpulseResponseLength()
        self.assertTrue(lengths==(0.0,5.e-9),'limited impulse response lengths incorrect')
    def testDetermineImpulseResponseNoImpulseResponse(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        unevensp=si.sp.SParameters(sf.m_f[1:],sf[1:])
        lengths=unevensp.DetermineImpulseResponseLength(allLengths=True)
        self.assertTrue(lengths==[[(None, None), (None, None)], [(None, None), (None, None)]],'initialial impulse response lengths incorrect')
        unevensp.LimitImpulseResponseLength([[(0,3e-9),(0,5e-9)],[(0,5e-9),(0,3e-9)]])
        lengths=unevensp.DetermineImpulseResponseLength()
        self.assertTrue(lengths==(None,None),'limited impulse response lengths incorrect')
    def testDetermineImpulseReseponseRemoveS11(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        sf.LimitImpulseResponseLength(([[(0,0),(0,5e-9)],[(0,0),(0,3e-9)]]))
        lengths=sf.DetermineImpulseResponseLength(allLengths=True)
        self.assertTrue(lengths==[[(0,0),(0,5e-9)],[(0,0),(0,3e-9)]],'limited impulse response lengths incorrect')
    def testReciprocityEnforcement(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        pefn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        sf.EnforceReciprocity()
        self.CheckSParametersResult(sf, pefn, 'reciprocity enforced s-parameters')
    def testBothPassivityAndCausalityEnforcement(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        pefn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        sf.EnforceBothPassivityAndCausality()
        self.CheckSParametersResult(sf, pefn, 'passivity and reciprocity enforced s-parameters')
    def testAllEnforcement(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('filter.s2p')
        pefn='_'.join(self.id().split('.')[-2:])+'.s'+str(sf.m_P)+'p'
        sf.EnforceAll()
        self.CheckSParametersResult(sf, pefn, 'all enforced s-parameters')
if __name__ == "__main__":
    unittest.main()