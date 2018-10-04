"""
TestSPARQFourPortScaled.py
"""

# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import unittest
import SignalIntegrity as si
from TestSignalIntegrity.TestHelpers import SParameterCompareHelper,RoutineWriterTesterHelper
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
class TestSPARQFourPortScaledTest(unittest.TestCase,
        SParameterCompareHelper,si.test.PySIAppTestHelper,RoutineWriterTesterHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12
    usePickle=False
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def tearDown(self):
        si.m.tdr.TDRWaveformToSParameterConverter.taper=True
        si.wl.WaveletDenoiser.wavelet=si.wl.WaveletDaubechies16()
        si.td.wf.Waveform.adaptionStrategy='SinX'
    def __init__(self, methodName='runTest'):
        SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.PySIAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        RoutineWriterTesterHelper.__init__(self)
    def GetSimulationResultsCheck(self,filename):
        if not hasattr(TestSPARQFourPortScaledTest, 'simdict'):
            TestSPARQFourPortScaledTest.simdict=dict()
            if TestSPARQFourPortScaledTest.usePickle:
                try:
                    import pickle
                    TestSPARQFourPortScaledTest.simdict=pickle.load(open("simresults.p","rb"))
                except:
                    pass
        if filename in TestSPARQFourPortScaledTest.simdict:
            return TestSPARQFourPortScaledTest.simdict[filename]
        TestSPARQFourPortScaledTest.simdict[filename] = self.SimulationResultsChecker(filename)
        return TestSPARQFourPortScaledTest.simdict[filename]
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])
    def testVNAFourPort(self):
        ports=4
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for p in range(ports):
                portName=str(p+1)
                A=fr[outputNames.index('A'+portName)][sourceNames.index('VG'+portName)]
                B=fr[outputNames.index('B'+portName)][sourceNames.index('VG'+portName)]
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
#                 13
#                 [[131_A1,133_A1],
#                  [131_A3,133_A3]]
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    fr=transferMatrices.FrequencyResponses()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        A[o][d]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        B[o][d]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        f=A[o][d].Frequencies()

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                DutA[otherPort][drivenPort]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                DutB[otherPort][drivenPort]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]

        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short4'].FrequencyResponse(1,1),calStandards[0],3,'Short4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open4'].FrequencyResponse(1,1),calStandards[1],3,'Open4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load4'].FrequencyResponse(1,1),calStandards[2],3,'Load4'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(1,1),spDict['Thru14'].FrequencyResponse(2,1),calStandards[3],0,3,'Thru141'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(2,2),spDict['Thru14'].FrequencyResponse(1,2),calStandards[3],3,0,'Thru144'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(1,1),spDict['Thru24'].FrequencyResponse(2,1),calStandards[3],1,3,'Thru242'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(2,2),spDict['Thru24'].FrequencyResponse(1,2),calStandards[3],3,1,'Thru244'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(1,1),spDict['Thru34'].FrequencyResponse(2,1),calStandards[3],2,3,'Thru343'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(2,2),spDict['Thru34'].FrequencyResponse(1,2),calStandards[3],3,2,'Thru344')
            ]

        cm=si.m.cal.Calibration(4,f,ml)

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s4p')
        DUTActualSp=si.sp.SParameterFile('FourPortDUT.s4p').Resample(f)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s4p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-1),'s-parameters not equal')
    def testVNAFourPortAssumeDiagonalA(self):
        ports=4
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for p in range(ports):
                portName=str(p+1)
                A=fr[outputNames.index('A'+portName)][sourceNames.index('VG'+portName)]
                B=fr[outputNames.index('B'+portName)][sourceNames.index('VG'+portName)]
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
#                 13
#                 [[131_A1,133_A1],
#                  [131_A3,133_A3]]
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    fr=transferMatrices.FrequencyResponses()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        A[o][d]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        B[o][d]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        f=A[o][d].Frequencies()

                for r in range(2):
                    for c in range(2):
                        if r != c:
                            for n in range(len(A[r][c])):
                                A[r][c][n]=0.

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                DutA[otherPort][drivenPort]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                DutB[otherPort][drivenPort]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]

        for r in range(ports):
            for c in range(ports):
                if r != c:
                    for n in range(len(DutA[r][c])):
                        DutA[r][c][n]=0.

        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short4'].FrequencyResponse(1,1),calStandards[0],3,'Short4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open4'].FrequencyResponse(1,1),calStandards[1],3,'Open4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load4'].FrequencyResponse(1,1),calStandards[2],3,'Load4'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(1,1),spDict['Thru14'].FrequencyResponse(2,1),calStandards[3],0,3,'Thru141'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(2,2),spDict['Thru14'].FrequencyResponse(1,2),calStandards[3],3,0,'Thru144'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(1,1),spDict['Thru24'].FrequencyResponse(2,1),calStandards[3],1,3,'Thru242'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(2,2),spDict['Thru24'].FrequencyResponse(1,2),calStandards[3],3,1,'Thru244'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(1,1),spDict['Thru34'].FrequencyResponse(2,1),calStandards[3],2,3,'Thru343'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(2,2),spDict['Thru34'].FrequencyResponse(1,2),calStandards[3],3,2,'Thru344')
            ]

        cm=si.m.cal.Calibration(4,f,ml)

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s4p')
        DUTActualSp=si.sp.SParameterFile('FourPortDUT.s4p').Resample(f)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s4p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-1),'s-parameters not equal')    
    def testVNAFourPortTransferThru(self):
        ports=4
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for p in range(ports):
                portName=str(p+1)
                A=fr[outputNames.index('A'+portName)][sourceNames.index('VG'+portName)]
                B=fr[outputNames.index('B'+portName)][sourceNames.index('VG'+portName)]
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
#                 13
#                 [[131_A1,133_A1],
#                  [131_A3,133_A3]]
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    fr=transferMatrices.FrequencyResponses()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        A[o][d]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        B[o][d]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        f=A[o][d].Frequencies()

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                DutA[otherPort][drivenPort]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                DutB[otherPort][drivenPort]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]

#         import pickle
#         pickle.dump(self.simdict,open("simresults.p","wb"))


        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short4'].FrequencyResponse(1,1),calStandards[0],3,'Short4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open4'].FrequencyResponse(1,1),calStandards[1],3,'Open4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load4'].FrequencyResponse(1,1),calStandards[2],3,'Load4'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            #si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            #si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            #si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(1,1),spDict['Thru14'].FrequencyResponse(2,1),calStandards[3],0,3,'Thru141'),
            #si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(2,2),spDict['Thru14'].FrequencyResponse(1,2),calStandards[3],3,0,'Thru144'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            #si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(1,1),spDict['Thru24'].FrequencyResponse(2,1),calStandards[3],1,3,'Thru242'),
            #si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(2,2),spDict['Thru24'].FrequencyResponse(1,2),calStandards[3],3,1,'Thru244'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(1,1),spDict['Thru34'].FrequencyResponse(2,1),calStandards[3],2,3,'Thru343'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(2,2),spDict['Thru34'].FrequencyResponse(1,2),calStandards[3],3,2,'Thru344')
            ]

        cm=si.m.cal.Calibration(4,f,ml)

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s4p')
        DUTActualSp=si.sp.SParameterFile('FourPortDUT.s4p').Resample(f)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s4p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-1),'s-parameters not equal')

    def testTDRFourPort(self):
        ports=4
        reflectNames=['Short','Open','Load']
        spDict=dict()
        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for p in range(ports):
                portName=str(p+1)

                wf=outputWaveforms[outputNames.index('V'+portName)]
                a1=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                A=a1.FrequencyContent()
                b1=wf-a1
                B=b1.FrequencyContent()
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
#                 13
#                 [[131_A1,133_A1],
#                  [131_A3,133_A3]]
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    wf=outputWaveforms[outputNames.index('V'+drivenPortName)]
                    ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                    AD=ad.FrequencyContent()
                    bd=wf-ad
                    BD=bd.FrequencyContent()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        wf=outputWaveforms[outputNames.index('V'+otherPortName)]
                        if o==d:
                            ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                            A[o][d]=ad.FrequencyContent()
                            bd=wf-ad
                            B[o][d]=bd.FrequencyContent()
                        else:
                            A[o][d]=(wf-wf).FrequencyContent()
                            B[o][d]=wf.FrequencyContent()

                        f=A[o][d].Frequencies()

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                wf=outputWaveforms[outputNames.index('V'+otherPortName)]
                if otherPort==drivenPort:
                    ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                    DutA[otherPort][drivenPort]=ad.FrequencyContent()
                    bd=wf-ad
                    DutB[otherPort][drivenPort]=bd.FrequencyContent()
                else:
                    DutA[otherPort][drivenPort]=(wf-wf).FrequencyContent()
                    DutB[otherPort][drivenPort]=wf.FrequencyContent()

#         import pickle
#         pickle.dump(self.simdict,open("simresults.p","wb"))


        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short4'].FrequencyResponse(1,1),calStandards[0],3,'Short4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open4'].FrequencyResponse(1,1),calStandards[1],3,'Open4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load4'].FrequencyResponse(1,1),calStandards[2],3,'Load4'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(1,1),spDict['Thru14'].FrequencyResponse(2,1),calStandards[3],0,3,'Thru141'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(2,2),spDict['Thru14'].FrequencyResponse(1,2),calStandards[3],3,0,'Thru144'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(1,1),spDict['Thru24'].FrequencyResponse(2,1),calStandards[3],1,3,'Thru242'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(2,2),spDict['Thru24'].FrequencyResponse(1,2),calStandards[3],3,1,'Thru244'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(1,1),spDict['Thru34'].FrequencyResponse(2,1),calStandards[3],2,3,'Thru343'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(2,2),spDict['Thru34'].FrequencyResponse(1,2),calStandards[3],3,2,'Thru344')
            ]

        cm=si.m.cal.Calibration(4,f,ml)

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s4p')
        DUTActualSp=si.sp.SParameterFile('FourPortDUT.s4p').Resample(f)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s4p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

    def testTDRFourPortTransferThru(self):
        ports=4
        reflectNames=['Short','Open','Load']
        spDict=dict()
        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for p in range(ports):
                portName=str(p+1)

                wf=outputWaveforms[outputNames.index('V'+portName)]
                a1=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                A=a1.FrequencyContent()
                b1=wf-a1
                B=b1.FrequencyContent()
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
#                 13
#                 [[131_A1,133_A1],
#                  [131_A3,133_A3]]
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    wf=outputWaveforms[outputNames.index('V'+drivenPortName)]
                    ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                    AD=ad.FrequencyContent()
                    bd=wf-ad
                    BD=bd.FrequencyContent()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        wf=outputWaveforms[outputNames.index('V'+otherPortName)]
                        if o==d:
                            ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                            A[o][d]=ad.FrequencyContent()
                            bd=wf-ad
                            B[o][d]=bd.FrequencyContent()
                        else:
                            A[o][d]=(wf-wf).FrequencyContent()
                            B[o][d]=wf.FrequencyContent()

                        f=A[o][d].Frequencies()

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                wf=outputWaveforms[outputNames.index('V'+otherPortName)]
                if otherPort==drivenPort:
                    ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                    DutA[otherPort][drivenPort]=ad.FrequencyContent()
                    bd=wf-ad
                    DutB[otherPort][drivenPort]=bd.FrequencyContent()
                else:
                    DutA[otherPort][drivenPort]=(wf-wf).FrequencyContent()
                    DutB[otherPort][drivenPort]=wf.FrequencyContent()

#         import pickle
#         pickle.dump(self.simdict,open("simresults.p","wb"))


        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short4'].FrequencyResponse(1,1),calStandards[0],3,'Short4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open4'].FrequencyResponse(1,1),calStandards[1],3,'Open4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load4'].FrequencyResponse(1,1),calStandards[2],3,'Load4'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
#             si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
#             si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
#             si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(1,1),spDict['Thru14'].FrequencyResponse(2,1),calStandards[3],0,3,'Thru141'),
#             si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(2,2),spDict['Thru14'].FrequencyResponse(1,2),calStandards[3],3,0,'Thru144'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(1,1),spDict['Thru24'].FrequencyResponse(2,1),calStandards[3],1,3,'Thru242'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(2,2),spDict['Thru24'].FrequencyResponse(1,2),calStandards[3],3,1,'Thru244'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(1,1),spDict['Thru34'].FrequencyResponse(2,1),calStandards[3],2,3,'Thru343'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(2,2),spDict['Thru34'].FrequencyResponse(1,2),calStandards[3],3,2,'Thru344')
            ]

        cm=si.m.cal.Calibration(4,f,ml)

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s4p')
        DUTActualSp=si.sp.SParameterFile('FourPortDUT.s4p').Resample(f)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s4p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

    def testTDRTwoPort(self):
        ports=2
        reflectNames=['Short','Open','Load']
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=False)

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for p in range(ports):
                portName=str(p+1)
                fc=tdr.Convert(outputWaveforms[outputNames.index('V'+portName)])
                spDict[reflectName+portName]=si.sp.SParameters(fc.Frequencies(),[[[fc[n]]] for n in range(len(fc.Frequencies()))])

                wf=outputWaveforms[outputNames.index('V'+portName)]
                a1=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                A=a1.FrequencyContent()
                b1=wf-a1
                B=b1.FrequencyContent()
                f=A.Frequencies()
                spDict[reflectName+portName+'old']=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

                self.assertTrue(self.SParametersAreEqual(spDict[reflectName+portName], spDict[reflectName+portName+'old'], 1e-4))

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)               
#                 13
#                 [[131_A1,133_A1],
#                  [131_A3,133_A3]]
                portNames=[firstPortName,secondPortName]

                S=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]

                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    wfList=[outputWaveforms[outputNames.index('V'+name)] for name in portNames]
                    fc=tdr.Convert(wfList,d)

                    for o in range(len(portNames)):
                        S[o][d]=fc[o]

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[[[S[0][0][n],S[0][1][n]],[S[1][0][n],S[1][1][n]]]
                                                    for n in range(len(f))])

                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    wf=outputWaveforms[outputNames.index('V'+drivenPortName)]
                    ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                    AD=ad.FrequencyContent()
                    bd=wf-ad
                    BD=bd.FrequencyContent()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        wf=outputWaveforms[outputNames.index('V'+otherPortName)]
                        if o==d:
                            ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                            A[o][d]=ad.FrequencyContent()
                            bd=wf-ad
                            B[o][d]=bd.FrequencyContent()
                        else:
                            A[o][d]=(wf-wf).FrequencyContent()
                            B[o][d]=wf.FrequencyContent()

                        f=A[o][d].Frequencies()

                spDict['Thru'+firstPortName+secondPortName+'old']=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

                self.assertTrue(self.SParametersAreEqual(spDict['Thru'+firstPortName+secondPortName], spDict['Thru'+firstPortName+secondPortName+'old'], 1e-4))

        S=[[None for _ in range(ports)] for _ in range(ports)]
        portNames=[str(p+1) for p in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            wfList=[outputWaveforms[outputNames.index('V'+name)] for name in portNames]
            fc=tdr.Convert(wfList,drivenPort)

            for otherPort in range(ports):
                S[otherPort][drivenPort]=fc[otherPort]

        spDict['Dut']=si.sp.SParameters(f,[[[S[r][c][n] for c in range(ports)] for r in range(ports)]
                                            for n in range(len(f))])

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                wf=outputWaveforms[outputNames.index('V'+otherPortName)]
                if otherPort==drivenPort:
                    ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                    DutA[otherPort][drivenPort]=ad.FrequencyContent()
                    bd=wf-ad
                    DutB[otherPort][drivenPort]=bd.FrequencyContent()
                else:
                    DutA[otherPort][drivenPort]=(wf-wf).FrequencyContent()
                    DutB[otherPort][drivenPort]=wf.FrequencyContent()


        spDict['Dutold']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        self.assertTrue(self.SParametersAreEqual(spDict['Dut'], spDict['Dutold'], 1e-4))

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLineLossless(f,2,40,300e-12)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')


    def testTDRTwoPortRefined(self):
        ports=2
        reflectNames=['Short','Open','Load']
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=False,Length=20e-9,WindowRaisedCosineDuration=100e-12)

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for p in range(ports):
                portName=str(p+1)
                spDict[reflectName+portName]=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('V'+portName)])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)               
                portNames=[firstPortName,secondPortName]

                wfl=[]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]

                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    wfl.append([outputWaveforms[outputNames.index('V'+name)] for name in portNames])

                spDict['Thru'+firstPortName+secondPortName]=tdr.RawMeasuredSParameters(wfl)

        wfl=[]
        portNames=[str(p+1) for p in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            wfl.append([outputWaveforms[outputNames.index('V'+name)] for name in portNames])

        spDict['Dut']=tdr.RawMeasuredSParameters(wfl)

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'xferNoneTDR'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLineLossless(f,2,40,300e-12)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

    def testTDRTwoPortRefinedTransferThru(self):
        ports=3
        reflectNames=['Short','Open','Load']
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=False,Length=20e-9,WindowRaisedCosineDuration=100e-12)

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for p in range(ports):
                portName=str(p+1)
                spDict[reflectName+portName]=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('V'+portName)])
                f=spDict[reflectName+portName].m_f

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
                portNames=[firstPortName,secondPortName]

                wfl=[]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]

                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    wfl.append([outputWaveforms[outputNames.index('V'+name)] for name in portNames])

                spDict['Thru'+firstPortName+secondPortName]=tdr.RawMeasuredSParameters(wfl)


        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            ]

        cm3=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms()

        ports=2

        cm2=si.m.cal.Calibration(ports,f)
        cm2.ET=[si.m.cal.ErrorTerms([[cm3.ET[n][r][c] for c in range(ports)] for r in range(ports)]) for n in range(len(f))]
        Fixture=cm2.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'xferThruTDR'+str(p+1)+'.s'+str(ports*2)+'p')

        wfl=[]
        portNames=[str(p+1) for p in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            wfl.append([outputWaveforms[outputNames.index('V'+name)] for name in portNames])

        spDict['Dut']=tdr.RawMeasuredSParameters(wfl)

        f=spDict['Dut'].f()

        DUTCalcSp=cm2.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLineLossless(f,2,40,300e-12)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

    def testTDRFourPortManualVoltageWaveforms(self):
        si.td.wf.Waveform.adaptionStrategy='Linear'
        ports=4
        reflectNames=['Short','Open','Load']
        spDict=dict()
        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for p in range(ports):
                portName=str(p+1)

                wf=outputWaveforms[outputNames.index('A'+portName)]+outputWaveforms[outputNames.index('B'+portName)]
                a1=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                A=a1.FrequencyContent()
                b1=wf-a1
                B=b1.FrequencyContent()
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    wf=outputWaveforms[outputNames.index('A'+drivenPortName)]+outputWaveforms[outputNames.index('B'+drivenPortName)]
                    ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                    AD=ad.FrequencyContent()
                    bd=wf-ad
                    BD=bd.FrequencyContent()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        wf=outputWaveforms[outputNames.index('A'+otherPortName)]+outputWaveforms[outputNames.index('B'+otherPortName)]
                        if o==d:
                            ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                            A[o][d]=ad.FrequencyContent()
                            bd=wf-ad
                            B[o][d]=bd.FrequencyContent()
                        else:
                            A[o][d]=(wf-wf).FrequencyContent()
                            B[o][d]=wf.FrequencyContent()

                        f=A[o][d].Frequencies()

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                wf=outputWaveforms[outputNames.index('A'+otherPortName)]+outputWaveforms[outputNames.index('B'+otherPortName)]
                if otherPort==drivenPort:
                    ad=si.td.wf.Waveform(wf.TimeDescriptor(),[v if abs(t)<self.epsilon else 0. for (t,v) in zip(wf.Times(),wf.Values())])
                    DutA[otherPort][drivenPort]=ad.FrequencyContent()
                    bd=wf-ad
                    DutB[otherPort][drivenPort]=bd.FrequencyContent()
                else:
                    DutA[otherPort][drivenPort]=(wf-wf).FrequencyContent()
                    DutB[otherPort][drivenPort]=wf.FrequencyContent()

#         import pickle
#         pickle.dump(self.simdict,open("simresults.p","wb"))

        for r in range(ports):
            for c in range(ports):    
                Poly=si.spl.Spline(DutA[r][c].Frequencies(),DutA[r][c].Values())
                newresp=[Poly.Evaluate(fr) for fr in f]
                DutA[r][c]=si.fd.FrequencyDomain(f,newresp)
        for r in range(ports):
            for c in range(ports):    
                Poly=si.spl.Spline(DutB[r][c].Frequencies(),DutB[r][c].Values())
                newresp=[Poly.Evaluate(fr) for fr in f]
                DutB[r][c]=si.fd.FrequencyDomain(f,newresp)

        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short4'].FrequencyResponse(1,1),calStandards[0],3,'Short4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open4'].FrequencyResponse(1,1),calStandards[1],3,'Open4'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load4'].FrequencyResponse(1,1),calStandards[2],3,'Load4'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(1,1),spDict['Thru14'].FrequencyResponse(2,1),calStandards[3],0,3,'Thru141'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(2,2),spDict['Thru14'].FrequencyResponse(1,2),calStandards[3],3,0,'Thru144'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(1,1),spDict['Thru24'].FrequencyResponse(2,1),calStandards[3],1,3,'Thru242'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(2,2),spDict['Thru24'].FrequencyResponse(1,2),calStandards[3],3,1,'Thru244'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(1,1),spDict['Thru34'].FrequencyResponse(2,1),calStandards[3],2,3,'Thru343'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru34'].FrequencyResponse(2,2),spDict['Thru34'].FrequencyResponse(1,2),calStandards[3],3,2,'Thru344')
            ]

        cm=si.m.cal.Calibration(4,f,ml)

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s4p')
        DUTActualSp=si.sp.SParameterFile('FourPortDUT.s4p').Resample(f)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s4p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-2)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')

    def testVNATwoPortDiagonalA(self):
        ports=2
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for p in range(ports):
                portName=str(p+1)
                A=fr[outputNames.index('A'+portName)][sourceNames.index('VG'+portName)]
                B=fr[outputNames.index('B'+portName)][sourceNames.index('VG'+portName)]
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)

                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    fr=transferMatrices.FrequencyResponses()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        A[o][d]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        B[o][d]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        f=A[o][d].Frequencies()

                for r in range(2):
                    for c in range(2):
                        if r!=c:
                            A[r][c]=si.fd.FrequencyResponse(f,[0. for _ in range(len(f))])

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                DutA[otherPort][drivenPort]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                DutB[otherPort][drivenPort]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]

        for r in range(2):
            for c in range(2):
                if r!=c:
                    DutA[r][c]=si.fd.FrequencyResponse(f,[0. for _ in range(len(f))])

        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'xferNoneDiagonalA'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLineLossless(f,2,40,300e-12)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-4)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(SpAreEqual,'s-parameters not equal')

    def testVNATwoPortBAInverse(self):
        ports=2
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for p in range(ports):
                portName=str(p+1)
                A=fr[outputNames.index('A'+portName)][sourceNames.index('VG'+portName)]
                B=fr[outputNames.index('B'+portName)][sourceNames.index('VG'+portName)]
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    fr=transferMatrices.FrequencyResponses()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        A[o][d]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        B[o][d]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        f=A[o][d].Frequencies()

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                DutA[otherPort][drivenPort]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                DutB[otherPort][drivenPort]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]

        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        cm.WriteToFile('testFixtureWrite')
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'testFixtureWrite'+str(p+1)+'.s'+str(ports*2)+'p')
            os.remove('testFixtureWrite'+str(p+1)+'.s'+str(ports*2)+'p')
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'xferNoneBAInverse'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLineLossless(f,2,40,300e-12)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-4)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(SpAreEqual,'s-parameters not equal')

    @unittest.expectedFailure
    def testVNATwoPortTransferThruDiagonalA(self):
        ports=3
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for p in range(ports):
                portName=str(p+1)
                A=fr[outputNames.index('A'+portName)][sourceNames.index('VG'+portName)]
                B=fr[outputNames.index('B'+portName)][sourceNames.index('VG'+portName)]
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    fr=transferMatrices.FrequencyResponses()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        A[o][d]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        B[o][d]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        f=A[o][d].Frequencies()

                for r in range(2):
                    for c in range(2):
                        if r!=c:
                            A[r][c]=si.fd.FrequencyResponse(f,[0. for _ in range(len(f))])

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
#             si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
#             si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            ]

        cm3=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms()

        ports=2

        cm2=si.m.cal.Calibration(ports,f)
        cm2.ET=[si.m.cal.ErrorTerms([[cm3.ET[n][r][c] for c in range(ports)] for r in range(ports)]) for n in range(len(f))]
        Fixture=cm2.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'xferThruDiagonalA'+str(p+1)+'.s'+str(ports*2)+'p')

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                DutA[otherPort][drivenPort]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                DutB[otherPort][drivenPort]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]

        for r in range(2):
            for c in range(2):
                if r!=c:
                    DutA[r][c]=si.fd.FrequencyResponse(f,[0. for _ in range(len(f))])

        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        DUTCalcSp=cm2.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLine(f,2,40,300e-12)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-4)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors and False:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(SpAreEqual,'this is a known failure - cannot do VNA transfer thru assuming diagonal A')

    def testVNATwoPortTransferThruBAInv(self):
        ports=3
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for p in range(ports):
                portName=str(p+1)
                A=fr[outputNames.index('A'+portName)][sourceNames.index('VG'+portName)]
                B=fr[outputNames.index('B'+portName)][sourceNames.index('VG'+portName)]
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    fr=transferMatrices.FrequencyResponses()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        A[o][d]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        B[o][d]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        f=A[o][d].Frequencies()

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            ]

        cm3=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms()

        ports=2

        cm2=si.m.cal.Calibration(ports,f)
        cm2.ET=[si.m.cal.ErrorTerms([[cm3.ET[n][r][c] for c in range(ports)] for r in range(ports)]) for n in range(len(f))]
        Fixture=cm2.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'xferThruBAInverse'+str(p+1)+'.s'+str(ports*2)+'p')

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                DutA[otherPort][drivenPort]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                DutB[otherPort][drivenPort]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]

        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        DUTCalcSp=cm2.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLineLossless(f,2,40,300e-12)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-4)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(SpAreEqual,'s-parameters not equal')

    def ConvertToNoGain(self):
        ports=4
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            from PySIApp.PySIAppHeadless import PySIAppHeadless
            pysi=PySIAppHeadless()
            filename='TDRSimulationFourPort'+reflectName+'Scaled.xml'
            self.assertTrue(pysi.OpenProjectFile(os.path.realpath(filename)),filename + ' couldnt be opened')

            #change gains of probes to unity
            for device in pysi.Drawing.schematic.deviceList:
                from PySIApp.Device import DeviceOutput
                if isinstance(device,DeviceOutput):
                    for prop in device.propertiesList:
                        if prop.keyword=='gain':
                            prop._value=1.0
            newfilename='TDRSimulationFourPort'+reflectName+'.xml'
            pysi.SaveProjectToFile(newfilename)

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    filename='TDRSimulationFourPortThru'+simulationName+'Scaled.xml'
                    from PySIApp.PySIAppHeadless import PySIAppHeadless
                    pysi=PySIAppHeadless()
                    self.assertTrue(pysi.OpenProjectFile(os.path.realpath(filename)),filename + ' couldnt be opened')

                    #change gains of probes to unity
                    for device in pysi.Drawing.schematic.deviceList:
                        from PySIApp.Device import DeviceOutput
                        if isinstance(device,DeviceOutput):
                            for prop in device.propertiesList:
                                if prop.keyword=='gain':
                                    prop._value=1.0
                    newfilename='TDRSimulationFourPortThru'+simulationName+'.xml'
                    pysi.SaveProjectToFile(newfilename)

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)
            filename='TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml'
            from PySIApp.PySIAppHeadless import PySIAppHeadless
            pysi=PySIAppHeadless()
            self.assertTrue(pysi.OpenProjectFile(os.path.realpath(filename)),filename + ' couldnt be opened')

            #change gains of probes to unity
            for device in pysi.Drawing.schematic.deviceList:
                from PySIApp.Device import DeviceOutput
                if isinstance(device,DeviceOutput):
                    for prop in device.propertiesList:
                        if prop.keyword=='gain':
                            prop._value=1.0
            newfilename='TDRSimulationFourPortDut'+drivenPortName+'.xml'
            pysi.SaveProjectToFile(newfilename)

    def testTDRTwoPortNoGain(self):
        return unittest.skip('this test doesnt test anything special - I just want to keep it')
        self.ConvertToNoGain()
        ports=2
        reflectNames=['Short','Open','Load']
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=False,Length=20e-9,WindowRaisedCosineDuration=100e-12)

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            for p in range(ports):
                portName=str(p+1)
                spDict[reflectName+portName]=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('V'+portName)])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
                portNames=[firstPortName,secondPortName]

                wfl=[]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]

                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    wfl.append([outputWaveforms[outputNames.index('V'+name)] for name in portNames])

                spDict['Thru'+firstPortName+secondPortName]=tdr.RawMeasuredSParameters(wfl)

        wfl=[]
        portNames=[str(p+1) for p in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            wfl.append([outputWaveforms[outputNames.index('V'+name)] for name in portNames])

        spDict['Dut']=tdr.RawMeasuredSParameters(wfl)

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'xferNoneTDRNoGain'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLine(f,2,40,300e-12)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')
    def testVNATwoPortBAInverseNoGain(self):
        return unittest.SkipTest('this test doesnt test anything special - I just want to keep it')
        self.ConvertToNoGain()
        ports=2
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for p in range(ports):
                portName=str(p+1)
                A=fr[outputNames.index('A'+portName)][sourceNames.index('VG'+portName)]
                B=fr[outputNames.index('B'+portName)][sourceNames.index('VG'+portName)]
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
                portNames=[firstPortName,secondPortName]
                A=[[None for _ in range(2)] for _ in range(2)]
                B=[[None for _ in range(2)] for _ in range(2)]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]
                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=result[3]

                    fr=transferMatrices.FrequencyResponses()

                    for o in range(len(portNames)):
                        otherPortName=portNames[o]
                        A[o][d]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        B[o][d]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                        f=A[o][d].Frequencies()

                spDict['Thru'+firstPortName+secondPortName]=si.sp.SParameters(f,[(matrix([[B[0][0][n],B[0][1][n]],[B[1][0][n],B[1][1][n]]])*
                                                    matrix([[A[0][0][n],A[0][1][n]],[A[1][0][n],A[1][1][n]]]).getI()).tolist()
                                                    for n in range(len(f))])

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for otherPort in range(ports):
                otherPortName=str(otherPort+1)
                DutA[otherPort][drivenPort]=fr[outputNames.index('A'+otherPortName)][sourceNames.index('VG'+drivenPortName)]
                DutB[otherPort][drivenPort]=fr[outputNames.index('B'+otherPortName)][sourceNames.index('VG'+drivenPortName)]

        spDict['Dut']=si.sp.SParameters(f,[(matrix([[DutB[r][c][n] for c in range(ports)] for r in range(ports)])*
                                            matrix([[DutA[r][c][n] for c in range(ports)] for r in range(ports)]).getI()).tolist()
                                            for n in range(len(f))])

        f=spDict['Dut'].f()

        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(1,1),spDict['Thru12'].FrequencyResponse(2,1),calStandards[3],0,1,'Thru121'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru12'].FrequencyResponse(2,2),spDict['Thru12'].FrequencyResponse(1,2),calStandards[3],1,0,'Thru122'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'xferNoneBAInverseNoGain'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTCalcSp=cm.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLine(f,2,40,300e-12)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-4)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(SpAreEqual,'s-parameters not equal')
    def testTDRTwoPortStepsTransferThru(self):
        ports=3
        reflectNames=['Short','Open','Load']
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Step=True,Inverted=True,Length=20e-9,WindowRaisedCosineDuration=100e-12,WindowForwardHalfWidthTime=40e-12)
        sigma=707e-6/math.sqrt(100.)
        sigma=1e-18
        si.td.wf.Waveform.adaptionStrategy='Linear'
        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=[r.Integral()*r.TimeDescriptor().Fs*-0.2+si.td.wf.NoiseWaveform(r.TimeDescriptor(),sigma) for r in result[3]]

            for p in range(ports):
                portName=str(p+1)
                spDict[reflectName+portName]=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('V'+portName)])
                f=spDict[reflectName+portName].m_f

                plotthem=False
                if plotthem:
                    wf=outputWaveforms[outputNames.index('V'+portName)]
                    import matplotlib.pyplot as plt
                    plt.clf()
                    plt.title('waveform')
                    plt.plot(wf.Times('ns'),wf.Values(),label='V'+portName)
                    plt.xlabel('time (s)')
                    plt.ylabel('amplitude')
                    plt.legend(loc='upper right')
                    plt.grid(True)
                    plt.show()


        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
                portNames=[firstPortName,secondPortName]

                wfl=[]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]

                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=[r.Integral()*r.TimeDescriptor().Fs*-0.2+si.td.wf.NoiseWaveform(r.TimeDescriptor(),sigma) for r in result[3]]

                    wfl.append([outputWaveforms[outputNames.index('V'+name)] for name in portNames])

                spDict['Thru'+firstPortName+secondPortName]=tdr.RawMeasuredSParameters(wfl)


        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            ]

        cm3=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms()

        ports=2

        cm2=si.m.cal.Calibration(ports,f)
        cm2.ET=[si.m.cal.ErrorTerms([[cm3.ET[n][r][c] for c in range(ports)] for r in range(ports)]) for n in range(len(f))]
        Fixture=cm2.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'xferThruTDRStep'+str(p+1)+'.s'+str(ports*2)+'p')

        wfl=[]
        portNames=[str(p+1) for p in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=[r.Integral()*r.TimeDescriptor().Fs*-0.2+si.td.wf.NoiseWaveform(r.TimeDescriptor(),sigma) for r in result[3]]

            wfl.append([outputWaveforms[outputNames.index('V'+name)] for name in portNames])

        spDict['Dut']=tdr.RawMeasuredSParameters(wfl)

        f=spDict['Dut'].f()

        DUTCalcSp=cm2.DutCalculation(spDict['Dut'])
        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLineLossless(f,2,40,300e-12)
        self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-3)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-3),'s-parameters not equal')
    def NoisyWaveforms(self,wfList):
        sigma=707e-6/math.sqrt(10000.)
        newwfList=[r*si.td.f.WaveformTrimmer(0,-2000) for r in wfList]
        newwfList=[r.Integral()*r.TimeDescriptor().Fs*-0.2+si.td.wf.NoiseWaveform(r.TimeDescriptor(),sigma) for r in newwfList]
        return newwfList
    def testTDRTwoPortStepsNoiseTransferThru(self):
        ports=3
        reflectNames=['Short','Open','Load']
        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(
            Step=True,Inverted=True,Length=100e-9,
            WindowRaisedCosineDuration=100e-12,
            WindowReverseHalfWidthTime=5e-9,
            WindowForwardHalfWidthTime=40e-12,Denoise=True)
        tdr.taper=False
        si.wl.WaveletDenoiser.wavelet=si.wl.WaveletDaubechies4()

        #sigma=1e-18
        si.td.wf.Waveform.adaptionStrategy='Linear'
        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=self.NoisyWaveforms(result[3])

            for p in range(ports):
                portName=str(p+1)
                spDict[reflectName+portName]=tdr.RawMeasuredSParameters(outputWaveforms[outputNames.index('V'+portName)])
                f=spDict[reflectName+portName].m_f

                plotthem=False
                if plotthem:
                    wf=outputWaveforms[outputNames.index('V'+portName)]
                    import matplotlib.pyplot as plt
                    plt.clf()
                    plt.title('waveform')
                    plt.plot(wf.Times('ns'),wf.Values(),label='V'+portName)
                    plt.xlabel('time (s)')
                    plt.ylabel('amplitude')
                    plt.legend(loc='upper right')
                    plt.grid(True)
                    plt.show()


        for firstPort in range(ports):
            firstPortName=str(firstPort+1)
            for secondPort in range(firstPort+1,ports):
                secondPortName=str(secondPort+1)
                portNames=[firstPortName,secondPortName]

                wfl=[]

                for d in range(len(portNames)):
                    drivenPortName=portNames[d]

                    simulationName=firstPortName+secondPortName+drivenPortName
                    result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+simulationName+'Scaled.xml')
                    sourceNames=result[0]
                    outputNames=result[1]
                    transferMatrices=result[2]
                    outputWaveforms=self.NoisyWaveforms(result[3])

                    wfl.append([outputWaveforms[outputNames.index('V'+name)] for name in portNames])

                spDict['Thru'+firstPortName+secondPortName]=tdr.RawMeasuredSParameters(wfl)


        calStandards=[si.m.calkit.std.ShortStandard(f),
              si.m.calkit.OpenStandard(f),
              si.m.calkit.LoadStandard(f),
              si.m.calkit.ThruStandard(f,100e-12)]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short1'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short2'].FrequencyResponse(1,1),calStandards[0],1,'Short2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Short3'].FrequencyResponse(1,1),calStandards[0],2,'Short3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open1'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open2'].FrequencyResponse(1,1),calStandards[1],1,'Open2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open3'].FrequencyResponse(1,1),calStandards[1],2,'Open3'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load1'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load2'].FrequencyResponse(1,1),calStandards[2],1,'Load2'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load3'].FrequencyResponse(1,1),calStandards[2],2,'Load3'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            ]

        cm3=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms()

        ports=2

        cm2=si.m.cal.Calibration(ports,f)
        cm2.ET=[si.m.cal.ErrorTerms([[cm3.ET[n][r][c] for c in range(ports)] for r in range(ports)]) for n in range(len(f))]
        Fixture=cm2.Fixtures()
#         for p in range(ports):
#             self.SParameterRegressionChecker(Fixture[p],'xferThruTDRStepNoisy'+str(p+1)+'.s'+str(ports*2)+'p')

        wfl=[]
        portNames=[str(p+1) for p in range(ports)]

        for drivenPort in range(ports):
            drivenPortName=str(drivenPort+1)

            result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut'+drivenPortName+'Scaled.xml')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=self.NoisyWaveforms(result[3])

            wfl.append([outputWaveforms[outputNames.index('V'+name)] for name in portNames])

        spDict['Dut']=tdr.RawMeasuredSParameters(wfl)

        f=spDict['Dut'].f()

        DUTCalcSp=cm2.DutCalculation(spDict['Dut'])
#         self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s2p')
        DUTActualSp=si.sp.dev.TLineLossless(f,2,40,300e-12)
#         self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s2p')
        SpAreEqual=self.SParametersAreEqual(DUTCalcSp, DUTActualSp,1e-2)

        if not SpAreEqual:
            if si.test.PySIAppTestHelper.plotErrors:
                import matplotlib.pyplot as plt
                plt.clf()
                plt.title('s-parameter compare')
                plt.xlabel('frequency (Hz)')
                plt.ylabel('amplitude')
                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.semilogy(DUTActualSp.f(),[abs(DUTCalcSp[n][r][c]-DUTActualSp[n][r][c]) for n in range(len(DUTActualSp))],label='S'+str(r+1)+str(c+1))
                plt.legend(loc='upper right')
                plt.grid(True)
                plt.show()

                for r in range(DUTActualSp.m_P):
                    for c in range(DUTActualSp.m_P):
                        plt.clf()
                        plt.title('S'+str(r+1)+str(c+1))
                        plt.plot(DUTCalcSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTCalcSp.FrequencyResponse(r+1,c+1).Values('dB'),label='calculated')
                        plt.plot(DUTActualSp.FrequencyResponse(r+1,c+1).Frequencies(),DUTActualSp.FrequencyResponse(r+1,c+1).Values('dB'),label='actual')
                        plt.xlabel('frequency (Hz)')
                        plt.ylabel('amplitude (dB)')
                        plt.ylim(ymin=-60,ymax=30)
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(SpAreEqual,'s-parameters not equal')
    def testZZZZRunAfterAllTestsCompleted(self):
        if TestSPARQFourPortScaledTest.usePickle:
            if not os.path.exists('simresults.p'):
                import pickle
                pickle.dump(self.simdict,open("simresults.p","wb"))
    def testWriteTDRWaveformToSParameterConverterClassCodeExceptConvert(self):
        fileName='../SignalIntegrity/Measurement/TDR/TDRWaveformToSParameterConverter.py'
        className='TDRWaveformToSParameterConverter'
        firstDef='__init__'
        allfuncs=self.EntireListOfClassFunctions(fileName,className)
        allfuncs.remove(firstDef)
        allfuncs.remove('Convert')
        allfuncs.remove('_ExtractionWindows')
        defName=[firstDef]+allfuncs
        self.WriteClassCode(fileName,className,defName)
    def testWriteTDRWaveformToSParameterConverterClassCodeConvert(self):
        fileName='../SignalIntegrity/Measurement/TDR/TDRWaveformToSParameterConverter.py'
        className='TDRWaveformToSParameterConverter'
        defName=['Convert']
        self.WriteClassCode(fileName,className,defName)

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
