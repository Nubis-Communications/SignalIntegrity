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
from App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
import SignalIntegrity.App.Project

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
    def testEyeCentering(self):
        app=SignalIntegrityAppHeadless()
        app.OpenProjectFile('/home/petep/Work/NubisSystemSim/Projects/Receiver.si')
        SignalIntegrity.App.Project['EyeDiagram.Mode']='JitterNoise'
        SignalIntegrity.App.Project['EyeDiagram.JitterNoise.LogIntensity.LogIntensity']=False
        Exponent=-3
        deltaExponent=0.00001
        (sourceNames,
         outputWaveformLabels,
         transferMatrices,
         outputWaveformList,
         eyeDiagramLabels,
         eyeDiagramImages,
         eyeDiagramBitmaps)=app.Simulate(EyeDiagrams=True)
        bitmap=eyeDiagramBitmaps[eyeDiagramLabels.index('Vo')]
        (R,C)=bitmap.shape
        darkCounts=[]
        darkExtents=[]
        minValueLog=pow(10.,-20)
        minSat=0
        maxSat=1.

        minBER=Exponent; maxBER=Exponent+1
        m=(maxSat-minSat)/(maxBER-minBER)
        b=minSat-minBER*m
        bitmapLog=np.array([[math.log10(max(bitmap[r][c],minValueLog)) for c in range(C)] for r in range(R)])
        bitmapLog=bitmapLog*m+b
        bitmapLog=np.array([[0. if bitmapLog[r][c] < minSat else (1 if bitmapLog[r][c] > maxSat else bitmapLog[r][c]) for c in range(C)] for r in range(R)])

        for c in range(C):
            counter=None
            thisCounts=[]
            thisExtents=[]
            for r in range(1,R):
                if bitmapLog[r][c]==0. and bitmapLog[r-1][c]!=0.:
                    counter=r
                elif bitmapLog[r][c]!=0 and bitmapLog[r-1][c]==0:
                    if counter != None:
                        thisCounts.append(r-counter)
                        thisExtents.append((counter,r))
            darkExtents.append(thisExtents)
            darkCounts.append(thisCounts)
        bestOpenings=None
        indexOfBestOpening=None
        for c in range(C):
            dc=darkCounts[c]
            if len(dc)!=3:
                continue
            if bestOpenings is None:
                bestOpenings=np.sort(dc)
            else:
                dc=np.sort(dc)
                if dc[0]>bestOpenings[0]:
                    bestOpenings=dc; indexOfBestOpening=c
                elif dc[0]==bestOpenings[0]:
                    if dc[1]> bestOpenings[1]:
                        bestOpenings=dc; indexOfBestOpening=c
                    elif dc[1]==bestOpenings[1]:
                        if dc[2]>bestOpenings[2]:
                            bestOpenings=dc; indexOfBestOpening=c
        # These are the three largest eye openings at the best index in order of appearance
        # remember that the eye is upside down (we're looking from the bottom up
        eyeExtents=sorted(sorted(darkExtents[indexOfBestOpening],key = lambda x: x[1]-x[0])[0:3],key = lambda y:y[0])
        # now, for each eye, walk backwards and forwards at each row slice within these extents
        # to find the extents of each eye opening
        rowOfMaxEyeWidth=None
        startColumnofMaxEyeWidth=None
        endColumnofMaxEyeWidth=None
        maxEyeWidth=0
        for eye in eyeExtents:
            for r in range(eye[0],eye[1]+1):
                c=indexOfBestOpening
                count=1 # count the pixel we're on
                startColumn=c
                endColumn=c
                found=False
                while count != C and not found:
                    c=(c-1)%C
                    if bitmapLog[r][c]!=0:
                        found=True
                    else:
                        count+=1
                        startColumn=c
                found=False
                while count != C and not found:
                    c=(c+1)%C
                    if bitmapLog[r][c]!=0:
                        found=True
                    else:
                        count+=1
                        endColumn=c
                if count > maxEyeWidth:
                    maxEyeWidth=count
                    rowOfMaxEyeWidth=r
                    startColumnofMaxEyeWidth=startColumn
                    endColumnofMaxEyeWidth=endColumn
        # should check these for None
        if endColumnofMaxEyeWidth<startColumnofMaxEyeWidth:
            endColumnofMaxEyeWidth+=C
        columnAtEyeCenter=((startColumnofMaxEyeWidth+endColumnofMaxEyeWidth)//2)%C
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()