"""
TestVNACalibrationObject.py
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
import SignalIntegrity.App.SignalIntegrityAppHeadless as siapp

import os

class TestVNACalibrationObjectTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
    relearn=True
    debug=False
    checkPictures=True
    keepNewFormats=False
    deleteCache=True
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        self.SPCompareResolution=1e-2
        #si.test.SignalIntegrityAppTestHelper.plotErrors=True
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        #self.forceWritePictures=True
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        self.UseSinX=SignalIntegrity.App.Preferences['Calculation.UseSinX']
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=False
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
        SignalIntegrity.App.Preferences['Appearance.LimitText']=self.TextLimit
        SignalIntegrity.App.Preferences['Appearance.RoundDisplayedValues']=self.RoundDisplayedValues
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def DeleteCache(self):
        import glob
        # Get a list of all cached files
        fileList = glob.glob('*_cache*')
        # Iterate over the list of filepaths & remove each file.
        for filePath in fileList:
            try:
                os.remove(filePath)
            except:
                print("Error while deleting file : ", filePath)
    def testAAAADoThisFirst(self):
        if self.deleteCache:
            self.DeleteCache()
    def testSIUnits(self):
        unit='e-27 F/Hz'
        number=-310.13
        self.assertEqual(number,si.ToSI.FromSI(si.ToSI.ToSI(number,unit),unit),'si with exponent converted incorrectly')
    def Args(self):
        return {'Noise':0.0}
    def TestCal(self,testid):
        filename=testid.split('.')[-1].replace('test','')+'.si'
        self.SParameterResultsChecker(filename,args=self.Args())
        self.SimulationResultsChecker(filename,args=self.Args())
        if self.deleteCache:
            # checks caching
            self.SParameterResultsChecker(filename,args=self.Args())
            self.SimulationResultsChecker(filename,args=self.Args())
    def testTDRShort1(self):
        self.TestCal(self.id())
    def testTDROpen1(self):
        self.TestCal(self.id())
    def testTDRLoad1(self):
        self.TestCal(self.id())
    def testTDRShort2(self):
        self.TestCal(self.id())
    def testTDROpen2(self):
        self.TestCal(self.id())
    def testTDRLoad2(self):
        self.TestCal(self.id())
    def testTDRShort3(self):
        self.TestCal(self.id())
    def testTDROpen3(self):
        self.TestCal(self.id())
    def testTDRLoad3(self):
        self.TestCal(self.id())
    def testTDRShort4(self):
        self.TestCal(self.id())
    def testTDROpen4(self):
        self.TestCal(self.id())
    def testTDRLoad4(self):
        self.TestCal(self.id())
    def testTDRThru12(self):
        self.TestCal(self.id())
    def testTDRThru13(self):
        self.TestCal(self.id())
    def testTDRThru14(self):
        self.TestCal(self.id())
    def testTDRThru23(self):
        self.TestCal(self.id())
    def testTDRThru24(self):
        self.TestCal(self.id())
    def testTDRThru34(self):
        self.TestCal(self.id())
    def testTDRCalibration(self):
        self.CalibrationResultsChecker('TDRCalibration.si',args=self.Args())
    def testTDRCalculation(self):
        self.SParameterResultsChecker('TDRCalculation.si',args=self.Args())
    def testTDRCalculationArchive(self):
        self.SParameterResultsChecker('TDRCalculation.si',args=self.Args(),archive=True)

if __name__ == "__main__": # pragma: no cover
    runProfiler=False

    if runProfiler:
        import cProfile
        cProfile.run('unittest.main()','stats')

        import pstats
        p = pstats.Stats('stats')
        p.strip_dirs().sort_stats('cumulative').print_stats(30)
    else:
        unittest.main()
