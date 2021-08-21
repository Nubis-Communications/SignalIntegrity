"""
TestLaplace.py
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
import SignalIntegrity.Lib as si
import os

class TestLaplaceTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper,
        si.test.RoutineWriterTesterHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        #si.test.SignalIntegrityAppTestHelper.forceWritePictures=True
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
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        si.test.RoutineWriterTesterHelper.__init__(self)

    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])

    def testsdomain(self):
        eq='111036345.083127*(s+1043517065940.07)/(s**2+s*(399666919596.745/1.41865904825535)+399666919596.745**2)'
        fd=si.fd.EvenlySpacedFrequencyList(200e9,200)
        sp=si.sp.dev.Laplace(fd,eq)
        self.SParameterRegressionChecker(sp,self.NameForTest()+'.s2p')

    def testwdomain(self):
        eq='111036345.083127*(s+1043517065940.07)/(s**2+s*(399666919596.745/1.41865904825535)+399666919596.745**2)'
        eq=eq.replace('s','(j*w)')
        fd=si.fd.EvenlySpacedFrequencyList(200e9,200)
        sp=si.sp.dev.Laplace(fd,eq)
        self.SParameterRegressionChecker(sp,self.NameForTest()+'.s2p')

    def testfdomain(self):
        eq='111036345.083127*(s+1043517065940.07)/(s**2+s*(399666919596.745/1.41865904825535)+399666919596.745**2)'
        eq=eq.replace('s','(j*2*pi*f)')
        fd=si.fd.EvenlySpacedFrequencyList(200e9,200)
        sp=si.sp.dev.Laplace(fd,eq)
        self.SParameterRegressionChecker(sp,self.NameForTest()+'.s2p')

    def testzdomain(self):
        eq='-0.1*z**(-10)+0.7*z+-0.2*z**10'
        eq=eq.replace('s','(j*2*pi*f)')
        fd=si.fd.EvenlySpacedFrequencyList(200e9,200)
        sp=si.sp.dev.Laplace(fd,eq)
        self.SParameterRegressionChecker(sp,self.NameForTest()+'.s2p')

    def testLaplaceProject(self):
        self.SParameterResultsChecker('LaplaceProject.si')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()