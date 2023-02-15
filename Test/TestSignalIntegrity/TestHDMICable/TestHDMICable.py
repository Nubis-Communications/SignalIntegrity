"""
TestHDMICable.py
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

from numpy import matrix
import math

#------------------------------------------------------------------------------ 
# this class tries to speed things up a bit using a pickle containing the simulation
# results from a simulation that is used for every test.  If the pickle 'simresults.p'
# exists, it will load this pickle as the complete set of simulation results - you must
# delete this pickle if you change any of the schematics and expect them to produce
# different results.  This pickle will get rewritten by one of the classes as the simulation
# results are produced only once by the first test to produce them so it doesn't really matter
# who writes the pickle.
# you must set usePickle to True for it to perform this caching.  It cuts the time from about
# 1 minute to about 20 seconds
#------------------------------------------------------------------------------ 
class TestHDMICableTest(unittest.TestCase,
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
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=self.UseSinX
        SignalIntegrity.App.Preferences.SaveToFile()
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation'].ApplyPreferences()
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        si.test.RoutineWriterTesterHelper.__init__(self)
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])
    def testPRBSTest(self):
        self.SimulationResultsChecker('PRBSTest.si')
    def testPRBSTestArchive(self):
        self.SimulationResultsChecker('PRBSTest.si',archive=True)
    def testPRBSTestCompare(self):
        self.SimulationResultsChecker('PRBSTestCompare.si')
    def testFFE(self):
        self.SParameterResultsChecker('FFE.si')
    def testHDMIThru(self):
        self.SParameterResultsChecker('HDMIThru.si')
    def testHDMIThruPort1(self):
        self.DeembeddingResultsChecker('HDMIThruPort1.si')
    def testHDMIThruPort2(self):
        self.DeembeddingResultsChecker('HDMIThruPort2.si')
    def testHDMICableRawMM(self):
        self.SParameterResultsChecker('HDMICableRawMM.si')
    def testHDMIThruMiddle(self):
        self.SParameterResultsChecker('HDMIThruMiddle.si')
    def testHDMIThruMiddleModel(self):
        self.SParameterResultsChecker('HDMIThruMiddleModel.si')
    def testHDMIThruPort1Peeled(self):
        self.SParameterResultsChecker('HDMIThruPort1Peeled.si')
    def testHDMIThruPort2Peeled(self):
        self.SParameterResultsChecker('HDMIThruPort2Peeled.si')
    def testHDMIThruPortsPeeled(self):
        self.SParameterResultsChecker('HDMIThruPortsPeeled.si')
    def testHDMICableDeembeddedMM(self):
        self.SParameterResultsChecker('HDMICableDeembeddedMM.si')
    def testHDMICableDeembeddedSE(self):
        self.DeembeddingResultsChecker('HDMICableDeembeddedSE.si')
    def testHDMICableSENoDeembedding(self):
        self.SParameterResultsChecker('HDMICableSENoDeembedding.si')
    def testHDMICableDeembeddedSEPeeled(self):
        self.DeembeddingResultsChecker('HDMICableDeembeddedSEPeeled.si')
    def testHDMIThruDeembeddingStructure(self):
        self.SParameterResultsChecker('HDMIThruDeembeddingStructure.si')
    def testHDMIDeembeddingStructureEvaluation(self):
        self.DeembeddingResultsChecker('HDMIDeembeddingStructureEvaluation.si')
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
