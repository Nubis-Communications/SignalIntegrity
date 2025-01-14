"""
TestDwellTime.py
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

import matplotlib.pyplot as plt

from numpy import matrix

class TestDwellTimeTest(unittest.TestCase,si.test.SParameterCompareHelper,
                    si.test.SignalIntegrityAppTestHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        #self.forceWritePictures=True
    def tearDown(self):
        os.chdir(self.cwd)
        unittest.TestCase.tearDown(self)
    def testDwellTime(self):
        filename='DwellTime.si'
        results=self.SimulationResultsChecker(filename)
        outputNames=results['output waveform labels']
        outputWaveforms=results['output waveforms']
        wfdict=dict([(key,val) for (key,val) in zip(outputNames,outputWaveforms)])
#         import matplotlib.pyplot as plt
#         import matplotlib
#         plt.plot(wfdict['a1'].Values(),wfdict['b1'].Values())
# #        plt.show()
#         
#         plt.cla()
#         startTime=90e-9
#         stopTime=100e-9
#         Fs=wfdict['a1'].td.Fs
#         K=int((stopTime-startTime)*Fs)
#         newtd=si.td.wf.TimeDescriptor(startTime,K,Fs)
#         clippedWf=dict([(key,wfdict[key].Adapt(newtd)) for key in wfdict.keys()])
#         plt.plot(wfdict['a1'].Values(),wfdict['b1'].Values())
#         plt.plot(clippedWf['a1'].Values(),clippedWf['b1'].Values())
# #        plt.show()
        
        plt.cla()
        times=[100e-9*(k) for k in range(4)]
        dur=10e-9
        Fs=wfdict['a1'].td.Fs
        K=int(dur*Fs)
        newtds=[si.td.wf.TimeDescriptor(t-dur,K,Fs) for t in times]
        clippedWfs=[dict([(key,wfdict[key].Adapt(newtd)) for key in wfdict.keys()]) for newtd in newtds]
        plt.plot(wfdict['a1'].Values(),wfdict['b1'].Values(),color='blue',linewidth=0.5)
        plt.plot(clippedWfs[0]['a1'].Values(),clippedWfs[0]['b1'].Values(),color='green',linewidth=3)
        plt.plot(clippedWfs[1]['a1'].Values(),clippedWfs[1]['b1'].Values(),color='red',linewidth=3)
        plt.plot(clippedWfs[2]['a1'].Values(),clippedWfs[2]['b1'].Values(),color='black',linewidth=3)
        plt.plot(clippedWfs[3]['a1'].Values(),clippedWfs[3]['b1'].Values(),color='orange',linewidth=3)
        #plt.show()

        newtds=[si.td.wf.TimeDescriptor(t-dur-70e-9,K,Fs) for t in times]
        clippedWfs=[dict([(key,wfdict[key].Adapt(newtd)) for key in wfdict.keys()]) for newtd in newtds]
        plt.plot(wfdict['a1'].Values(),wfdict['b1'].Values(),color='blue',linewidth=0.5)
        plt.plot(clippedWfs[0]['a1'].Values(),clippedWfs[0]['b1'].Values(),color='green',linewidth=3)
        plt.plot(clippedWfs[1]['a1'].Values(),clippedWfs[1]['b1'].Values(),color='red',linewidth=3)
        plt.plot(clippedWfs[2]['a1'].Values(),clippedWfs[2]['b1'].Values(),color='black',linewidth=3)
        plt.plot(clippedWfs[3]['a1'].Values(),clippedWfs[3]['b1'].Values(),color='orange',linewidth=3)
        #plt.show()

        
