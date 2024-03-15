"""
TestVirtualProbeNumeric.py
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

class TestVirtualProbeNumeric(unittest.TestCase,si.test.ResponseTesterHelper):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def tearDown(self):
        si.td.wf.Waveform.adaptionStrategy='SinX'
    def testVirtualProbeDC2008(self):
        si.td.wf.Waveform.adaptionStrategy='SinX'
        fileNameBase=self.id().split('.')[0]+'_'+self.id().split('.')[2]
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.//DesignCon2008//')
        Fs=20.e9
        Fe=Fs/2
        N=200
##        si.sp.SParameterFile('XRAY041.s4p',50.).Resample(si.sp.EvenlySpacedFrequencyList(20.0e9,400)).WriteToFile('XRAY041.s4p')
##        return
        vpp=si.p.VirtualProbeNumericParser(si.fd.EvenlySpacedFrequencyList(Fe,N)).File('comparison.txt')
        tm = vpp.TransferMatrices()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.CheckSParametersResult(tm.SParameters(), './/DesignCon2008//VirtualProbeTransferMatrices.s6p', fileNameBase)
        #result.WriteToFile('vptm.s6p')
        #os.remove('vptm.s6p')
        fr=tm.FrequencyResponses()
        ir=tm.ImpulseResponses(Fs)
        ml = [m[0]+'_'+str(m[1]) for m in vpp.SystemDescription().pMeasurementList]
        ol = [o[0]+'_'+str(o[1]) for o in vpp.SystemDescription().pOutputList]
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(fr[o][m].Frequencies('GHz'),fr[o][m].Response('dB'),label=str(ol[o])+' due to '+str(ml[m]))
                #fr[o][m].WriteToFile('FrequencyResponse_'+ol[o]+'_due_to_'+ml[m]+'.txt')
                self.CheckFrequencyResponseResult(fr[o][m],'.//DesignCon2008//FrequencyResponse_'+ol[o]+'_due_to_'+ml[m]+'.txt',fileNameBase)
        plt.legend(loc='upper right')
##        plt.show()
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        for o in range(len(ol)):
            for m in range(len(ml)):
                plt.plot(ir[o][m].Times('ns'),ir[o][m].Values(),label=str(ol[o])+' due to '+str(ml[m]))
                #ir[o][m].WriteToFile('ImpulseResponse_'+str(ol[o])+'_due_to_'+str(ml[m])+'.txt')
                self.CheckWaveformResult(ir[o][m],'.//DesignCon2008//ImpulseResponse_'+ol[o]+'_due_to_'+ml[m]+'.txt',fileNameBase)
        plt.legend(loc='upper right')
##        plt.show()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.chdir('.//DesignCon2008//')
        CableTxPWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxP.txt',si.td.wf.TimeDescriptor(0,2000,20.e9))
        CableTxMWf=si.td.wf.WaveformFileAmplitudeOnly('CableTxM.txt',si.td.wf.TimeDescriptor(0,2000,20.e9))
        CableTxPWf.WriteToFile('Waveform_CableTxPWf.txt')
        CableTxMWf.WriteToFile('Waveform_CableTxMWf.txt')
        ThruBackplaneP=si.td.wf.WaveformFileAmplitudeOnly('ThruBackplaneP.txt',si.td.wf.TimeDescriptor(0,2000,20.e9))
        ThruBackplaneM=si.td.wf.WaveformFileAmplitudeOnly('ThruBackplaneM.txt',si.td.wf.TimeDescriptor(0,2000,20.e9))
        ThruBackplaneDiff=ThruBackplaneP-ThruBackplaneM
        inputWf=[si.td.wf.Waveform().ReadFromFile(fileName) for fileName in ['Waveform_CableTxPWf.txt','Waveform_CableTxMWf.txt']]
        tmp=si.td.f.TransferMatricesProcessor(tm)
        outputWf=tmp.ProcessWaveforms(inputWf)
        DiffIn=(inputWf[0]-inputWf[1])
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self.CheckWaveformResult(DiffIn,'.//DesignCon2008//Waveform_DiffIn.txt',fileNameBase)
        DiffOutTop=(outputWf[ol.index(('D20_2'))]-outputWf[ol.index(('D21_2'))]).DelayBy(-4.7e-9)
        self.CheckWaveformResult(DiffOutTop,'.//DesignCon2008//Waveform_DiffOutTop.txt',fileNameBase)
        DiffOutMid=(outputWf[ol.index(('D11_2'))]-outputWf[ol.index(('D12_2'))]).DelayBy(-4.7e-9)
        self.CheckWaveformResult(DiffOutMid,'.//DesignCon2008//Waveform_DiffOutMid.txt',fileNameBase)
        DiffOutBot=(outputWf[ol.index(('R1_1'))]-outputWf[ol.index(('R2_2'))]).DelayBy(-2.325e-9)
        self.CheckWaveformResult(DiffOutBot,'.//DesignCon2008//Waveform_DiffOutBot.txt',fileNameBase)
        ThruBackplaneDiff.DelayBy(-4.7e-9)
        [DiffIn,ThruBackplaneDiff,DiffOutTop,DiffOutMid,DiffOutBot]=si.td.wf.AdaptedWaveforms([DiffIn*si.td.f.InterpolatorSinX(10),ThruBackplaneDiff,DiffOutTop,DiffOutMid,DiffOutBot])
        self.CheckWaveformResult(DiffIn,'.//DesignCon2008//Waveform_DiffInAdapted.txt',fileNameBase)
        self.CheckWaveformResult(DiffOutTop,'.//DesignCon2008//Waveform_DiffOutTopAdapted.txt',fileNameBase)
        self.CheckWaveformResult(DiffOutMid,'.//DesignCon2008//Waveform_DiffOutMidAdapted.txt',fileNameBase)
        self.CheckWaveformResult(DiffOutBot,'.//DesignCon2008//Waveform_DiffOutBotAdapted.txt',fileNameBase)

        inputWf[0]=inputWf[0]*si.td.f.InterpolatorSinX(2)
        outputWf=tmp.ProcessWaveforms(inputWf)
        DiffIn=(inputWf[0]-inputWf[1])
        DiffOutTop=(outputWf[ol.index(('D20_2'))]-outputWf[ol.index(('D21_2'))]).DelayBy(-4.7e-9)
        DiffOutMid=(outputWf[ol.index(('D11_2'))]-outputWf[ol.index(('D12_2'))]).DelayBy(-4.7e-9)
        DiffOutBot=(outputWf[ol.index(('R1_1'))]-outputWf[ol.index(('R2_2'))]).DelayBy(-2.325e-9)
        ThruBackplaneDiff.DelayBy(-4.7e-9)
        [DiffIn,ThruBackplaneDiff,DiffOutTop,DiffOutMid,DiffOutBot]=si.td.wf.AdaptedWaveforms([DiffIn*si.td.f.InterpolatorSinX(10),ThruBackplaneDiff,DiffOutTop,DiffOutMid,DiffOutBot])

        """
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        plt.plot(DiffIn.Times('ns'),DiffIn.Values(),label='DiffIn')
        plt.plot(DiffOutTop.Times('ns'),DiffOutTop.Values(),label='DiffOutTop')
        plt.plot(DiffOutMid.Times('ns'),DiffOutMid.Values(),label='DiffOutMid')
        plt.plot(DiffOutBot.Times('ns'),DiffOutBot.Values(),label='DiffOutBot')
        plt.legend(loc='upper right')
        plt.show()
        plt.clf()
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude')
        fb=2.501234
        plt.scatter([(t-0.11) % (3./fb) for t in DiffIn.Times('ns')],DiffIn.Values(),label='DiffIn')
        plt.scatter([(t-0.11) % (3./fb) for t in DiffOutTop.Times('ns')],DiffOutTop.Values(),label='DiffOutTop')
        #plt.plot([t % 1./fb for t in DiffOutMid.Times('ns')],DiffOutMid.Values(),label='DiffOutMid')
        #plt.plot([t % 1./fb for t in DiffOutBot.Times('ns')],DiffOutBot.Values(),label='DiffOutBot')
        plt.legend(loc='upper right')
        plt.show()
        """
if __name__ == '__main__':
    unittest.main()
