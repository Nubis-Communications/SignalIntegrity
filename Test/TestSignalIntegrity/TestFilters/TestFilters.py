"""
TestFilters.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
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
import os

import SignalIntegrity.Lib as si

class TestFiltersTest(unittest.TestCase,si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    relearn=True
    debug=False
    checkPictures=True
    keepNewFormats=False
    def __init__(self, methodName='runTest'):
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=False
        SignalIntegrity.App.Preferences.SaveToFile()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=self.UseSinX
        SignalIntegrity.App.Preferences.SaveToFile()
    def testName(self):
        return '_'.join(unittest.TestCase.id(self).split('.')[-1:])
    def testBesselLowPassFilter(self):
        f=si.fd.EvenlySpacedFrequencyList(100e9,100)
        sp=si.sp.dev.BesselLowPassFilter(f,4,0.6*56e9)
        self.SParameterRegressionChecker(sp,self.testName()+'.s2p')
    def testButterworthLowPassFilter(self):
        f=si.fd.EvenlySpacedFrequencyList(100e9,100)
        sp=si.sp.dev.ButterworthLowPassFilter(f,12,1.25*56e9)
        self.SParameterRegressionChecker(sp,self.testName()+'.s2p')
    def testFFE(self):
        Fbaud=56e9
        samplesPerUI=5
        Fe=Fbaud*samplesPerUI/2
        ResponseLength=1e-9
        Td=1./Fbaud
        taps=[-0.1,1.2,-0.1]
        numPreCursorTaps=1
        f=si.fd.EvenlySpacedFrequencyList(Fe,Fe*ResponseLength)
        sp=si.sp.dev.FFE(f,Td,taps,numPreCursorTaps,Z0=50.)
        self.SParameterRegressionChecker(sp,self.testName()+'.s2p')
    def testCTLE(self):
        Fbaud=56e9
        samplesPerUI=5
        Fe=Fbaud*samplesPerUI/2
        ResponseLength=1e-9
        gDC=-2 # can be -8 to 0
        gDC2=0 # can be -2 to 0
        fz=Fbaud/2.5
        fp1=Fbaud/2.5
        fp2=Fbaud
        fLF=Fbaud/80.
        f=si.fd.EvenlySpacedFrequencyList(Fe,Fe*ResponseLength)
        sp=si.sp.dev.CTLE(f,gDC,gDC2,fz,fLF,fp1,fp2,Z0=50.)
        self.SParameterRegressionChecker(sp,self.testName()+'.s2p')
    def testBesselLowPassFilterStepResponse(self):
        self.SimulationResultsChecker(self.testName().replace('test',''))
    def testButterworthLowPassFilterStepResponse(self):
        self.SimulationResultsChecker(self.testName().replace('test',''))
    def testFFEStepResponse(self):
        self.SimulationResultsChecker(self.testName().replace('test',''))
    def testCTLEStepResponse(self):
        self.SimulationResultsChecker(self.testName().replace('test',''))
