"""
TestCOMModels.py
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

class TestCOMModelsTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12
    def removeFile(self,filename):
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        #si.test.SignalIntegrityAppTestHelper.forceWritePictures=True
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=True
        self.Caching=SignalIntegrity.App.Preferences['Cache.CacheResults']
        SignalIntegrity.App.Preferences['Cache.CacheResults']=False
        self.TextLimit=SignalIntegrity.App.Preferences['Appearance.LimitText']
        SignalIntegrity.App.Preferences['Appearance.LimitText']=60
        self.RoundDisplayedValues=SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']
        SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']=4
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=self.UseSinX
        SignalIntegrity.App.Preferences['Cache.CacheResults']=self.Caching
        SignalIntegrity.App.Preferences['Appearance.LimitText']=self.TextLimit
        SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']=self.RoundDisplayedValues
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
    #@unittest.expectedFailure
    def testCOMTransmissionLineModel_Package_12(self):
        gamma_0 = 0 # units 1/mm
        a_1 = 1.734e-3 # units sqrt(ns)/mm
        a_2 = 1.455e-4 # units ns/mm
        tau = 6.141e-3 # units ns/mm
        Z_c = 78.2 # units ohms
        d=12. # units mm
        fl=si.fd.EvenlySpacedFrequencyList(60e9,6000)
        sp_tline=si.sp.dev.TLineTwoPortCOM(fl,gamma_0,a_1,a_2,tau,Z_c,d,Z0=50.)
        spFileName=self.NameForTest()+'.s2p'
        if not os.path.exists(spFileName):
            sp_tline.WriteToFile(spFileName)
        sp=si.sp.SParameterFile(spFileName)
        self.assertTrue(self.SParametersAreEqual(sp_tline,sp,.001),spFileName+' result not same')
    def testCOMTransmissionLineModel_Package_30(self):
        gamma_0 = 0 # units 1/mm
        a_1 = 1.734e-3 # units sqrt(ns)/mm
        a_2 = 1.455e-4 # units ns/mm
        tau = 6.141e-3 # units ns/mm
        Z_c = 78.2 # units ohms
        d=30. # units mm
        fl=si.fd.EvenlySpacedFrequencyList(60e9,6000)
        sp_tline=si.sp.dev.TLineTwoPortCOM(fl,gamma_0,a_1,a_2,tau,Z_c,d,Z0=50.)
        spFileName=self.NameForTest()+'.s2p'
        if not os.path.exists(spFileName):
            sp_tline.WriteToFile(spFileName)
        sp=si.sp.SParameterFile(spFileName)
        self.assertTrue(self.SParametersAreEqual(sp_tline,sp,.001),spFileName+' result not same')
    def testCOMTransmissionLineModel_Host_68(self):
        gamma_0 = 0 # units 1/mm
        a_1 = 4.114e-4 # units sqrt(ns)/mm
        a_2 = 2.547e-4 # units ns/mm
        tau = 6.191e-3 # units ns/mm
        Z_c = 109.8 # units ohms
        d=68. # units mm
        fl=si.fd.EvenlySpacedFrequencyList(60e9,6000)
        sp_tline=si.sp.dev.TLineTwoPortCOM(fl,gamma_0,a_1,a_2,tau,Z_c,d,Z0=50.)
        spFileName=self.NameForTest()+'.s2p'
        if not os.path.exists(spFileName):
            sp_tline.WriteToFile(spFileName)
        sp=si.sp.SParameterFile(spFileName)
        self.assertTrue(self.SParametersAreEqual(sp_tline,sp,.001),spFileName+' result not same')
    def testCOMTransmissionLineModel_Host_141(self):
        gamma_0 = 0 # units 1/mm
        a_1 = 4.114e-4 # units sqrt(ns)/mm
        a_2 = 2.547e-4 # units ns/mm
        tau = 6.191e-3 # units ns/mm
        Z_c = 109.8 # units ohms
        d=141. # units mm
        fl=si.fd.EvenlySpacedFrequencyList(60e9,6000)
        sp_tline=si.sp.dev.TLineTwoPortCOM(fl,gamma_0,a_1,a_2,tau,Z_c,d,Z0=50.)
        spFileName=self.NameForTest()+'.s2p'
        if not os.path.exists(spFileName):
            sp_tline.WriteToFile(spFileName)
        sp=si.sp.SParameterFile(spFileName)
        self.assertTrue(self.SParametersAreEqual(sp_tline,sp,.001),spFileName+' result not same')
    def testCOMTransmissionLineModel_Package_30_Netlist(self):
        gamma_0 = 0 # units 1/mm
        a_1 = 1.734e-3 # units sqrt(ns)/mm
        a_2 = 1.455e-4 # units ns/mm
        tau = 6.141e-3 # units ns/mm
        Z_c = 78.2 # units ohms
        d=30. # units mm
        netlistLines=['device F1 2 tlinecom '+'gamma0 '+str(gamma_0)+' a1 '+str(a_1)+' a2 '+\
                      str(a_2)+' tau '+str(tau)+' zc '+str(Z_c)+' d '+str(d*1e-3),
                      'port 1 F1 1 2 F1 2']
        fl=si.fd.EvenlySpacedFrequencyList(60e9,6000)
        ssnp=si.p.SystemSParametersNumericParser(fl).AddLines(netlistLines)
        sp=ssnp.SParameters()
        self.SParameterRegressionChecker(sp,self.NameForTest().replace('_Netlist','')+'.s2p')
    def testTransmissionLineModel1Project(self):
        self.SParameterResultsChecker('COMTransmissionLineModel_Package_12.si')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
