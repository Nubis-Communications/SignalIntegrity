"""
TestEyeDiagram.py
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
import math
import SignalIntegrity as si
import numpy as np
import os

class TestEyeDiagramTest(unittest.TestCase,
        si.test.SParameterCompareHelper,si.test.SignalIntegrityAppTestHelper):
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
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=True
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
    def testEyeDiagram(self):
        self.SimulationEyeDiagramResultsChecker('EyeDiagramTest.si')
    def testEyeDiagramTransferMatrices(self):
        self.SimulationTransferMatricesResultsChecker('EyeDiagramTest.si')
    def testEyeDiagramJitterNoise(self):
        self.SimulationEyeDiagramResultsChecker('EyeDiagramTestJitterNoise.si')
    def testEyeDiagramJitterNoiseTransferMatrices(self):
        self.SimulationTransferMatricesResultsChecker('EyeDiagramTestJitterNoise.si')
    def testEyeDiagramJitterNoiseLog(self):
        self.SimulationEyeDiagramResultsChecker('EyeDiagramTestJitterNoiseLog.si')
    def testEyeDiagramJitterNoiseLogTransferMatrices(self):
        self.SimulationTransferMatricesResultsChecker('EyeDiagramTestJitterNoiseLog.si')
    def testMatPlotLib(self):
        result=self.SimulationEyeDiagramResultsChecker('EyeDiagramTest.si')
        eyeDiagrams=result[5]
        eyeDiagramImages=[ed.Image() for ed in eyeDiagrams]
        eyeDiagramBitmaps=[ed.BitMap() for ed in eyeDiagrams]
    def testEyeDiagramNonlinear(self):
        self.SimulationEyeDiagramResultsChecker('EyeDiagramNonLinear.si')
    def testPRBSTest(self):
        self.SimulationEyeDiagramResultsChecker('../../../SignalIntegrity/App/Examples/HDMICable/PRBSTest.si')

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
