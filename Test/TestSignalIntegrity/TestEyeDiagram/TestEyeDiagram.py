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
    def Hits(self,r,c,R,C):
        lowestr=r-0.5
        rl=int(math.floor(lowestr))
        highestr=r+0.5
        rh=int(math.floor(highestr))
        lrh=lowestr-rl
        lrl=1-lrh
        lowestc=c-0.5
        cl=int(math.floor(lowestc))
        highestc=c+0.5
        ch=int(math.floor(highestc))
        lch=lowestc-cl
        lcl=1-lch
        rlValid=(0<=rl<R)
        rhValid=(0<=rh<R)
        cl=cl%C
        if cl<0: cl=cl+C
        ch=ch%C
        if ch<0: ch=ch+C
        clValid=(0<=cl<C)
        chValid=(0<=ch<C)
        results=[]
        if rlValid and clValid: results+=[((rl,cl),(lrl,lcl),lrl*lcl)]
        if rhValid and clValid: results+=[((rh,cl),(lrh,lcl),lrh*lcl)]
        if rlValid and chValid: results+=[((rl,ch),(lrl,lch),lrl*lch)]
        if rhValid and chValid: results+=[((rh,ch),(lrh,lch),lrh*lch)]
        return results
    def testLocations(self):
        R,C=(200,200)
        r=1.8
        c=1.7
        results=self.Hits(r, c, R, C)
        for result in results:
            print(f"({result[0][0]},{result[0][1]}) = {result[1][0]}*{result[1][1]}={result[2]}")
    def testSteps(self):
        R,C=(4,4)
        steps=1
        ri,ci=(0.2,3.7)
        rf,cf=(2.6,1.3)
        if ci>cf:
            cf=cf+C
        m=(rf-ri)/(cf-ci)
        # solve y=mx+b for ci to produce ri:  ri=m*ci+b
        b=ri-m*ci
        # so now, r=m*c+b

        cspan=cf-ci
        rspan=rf-ri
        c=[n/steps*cspan+ci for n in range(steps+1)]
        r=[n/steps*rspan+ri for n in range(steps+1)]
        results=[]
        useFirst=True
        for n in range(steps+1):
            if n!=0 or useFirst:
                results.extend(self.Hits(r[n],c[n],R,C))
        for result in results:
            print(f"({result[0][0]},{result[0][1]}) = {result[1][0]}*{result[1][1]}={result[2]}")

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
