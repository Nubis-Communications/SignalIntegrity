"""
TestTDRFourPortSOLT.py
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

from numpy import array
from numpy.linalg import inv

class TestTDRFourPortTest(unittest.TestCase,si.test.SParameterCompareHelper,
                        si.test.SignalIntegrityAppTestHelper,si.test.RoutineWriterTesterHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    def __init__(self, methodName='runTest'):
        si.test.SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.SignalIntegrityAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        si.test.RoutineWriterTesterHelper.__init__(self)

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
        SignalIntegrity.App.Preferences.SaveToFile()
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        os.chdir(self.cwd)
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App.Project
        pysi=SignalIntegrityAppHeadless()
        SignalIntegrity.App.Preferences['Calculation.UseSinX']=self.UseSinX
        SignalIntegrity.App.Preferences.SaveToFile()
    def GetSimulationResultsCheck(self,filename):
        if not hasattr(TestTDRFourPortTest, 'simdict'):
            TestTDRFourPortTest.simdict=dict()
        if filename in TestTDRFourPortTest.simdict:
            return TestTDRFourPortTest.simdict[filename]
        print("In TestTDRFourPortTest, performing the sim for: "+filename)
        TestTDRFourPortTest.simdict[filename] = self.SimulationResultsChecker(filename)
        return TestTDRFourPortTest.simdict[filename]
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])
    def testResampleCheby(self):
        return
        sp=si.sp.SParameterFile('../../App/Examples/SParameterExample/Sparq_demo_16.s4p')
        sp=si.sp.SParameterFile('FourPortDut20.s4p')
        spresampled=si.sp.SParameters([f/4 for f in sp.f().Frequencies()],[d for d in sp])
        spresampled.WriteToFile('FourPortDUT.s4p')
    def testVNAFourPort(self):
        ports=4
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'.si')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for p in range(ports):
                portName=str(p+1)
                A=fr[outputNames.index('A'+reflectName+portName)][sourceNames.index('VG'+portName)]
                B=fr[outputNames.index('B'+reflectName+portName)][sourceNames.index('VG'+portName)]
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        thruConnections=[[[1,2],[3,4]],[[1,3],[2,4]],[[1,4],[2,3]]]
        for thruConnection in thruConnections:
            thruConnectionName=str(thruConnection[0][0])+str(thruConnection[0][1])+str(thruConnection[1][0])+str(thruConnection[1][1])
            result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+thruConnectionName+'.si')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for thruPorts in thruConnection:
                port1Name=str(thruPorts[0])
                port2Name=str(thruPorts[1])                
                A11=fr[outputNames.index('AThru'+thruConnectionName+'_'+port1Name+port1Name)][sourceNames.index('VG'+port1Name)]
                A21=fr[outputNames.index('AThru'+thruConnectionName+'_'+port2Name+port1Name)][sourceNames.index('VG'+port1Name)]
                B11=fr[outputNames.index('BThru'+thruConnectionName+'_'+port1Name+port1Name)][sourceNames.index('VG'+port1Name)]
                B21=fr[outputNames.index('BThru'+thruConnectionName+'_'+port2Name+port1Name)][sourceNames.index('VG'+port1Name)]
                port2Name=str(thruPorts[1])
                port1Name=str(thruPorts[0])                
                A22=fr[outputNames.index('AThru'+thruConnectionName+'_'+port2Name+port2Name)][sourceNames.index('VG'+port2Name)]
                A12=fr[outputNames.index('AThru'+thruConnectionName+'_'+port1Name+port2Name)][sourceNames.index('VG'+port2Name)]
                B22=fr[outputNames.index('BThru'+thruConnectionName+'_'+port2Name+port2Name)][sourceNames.index('VG'+port2Name)]
                B12=fr[outputNames.index('BThru'+thruConnectionName+'_'+port1Name+port2Name)][sourceNames.index('VG'+port2Name)]
                spDict['Thru'+port1Name+port2Name]=si.sp.SParameters(f,[(array([[B11[n],B12[n]],[B21[n],B22[n]]]).dot(
                                                    inv(array([[A11[n],A12[n]],[A21[n],A22[n]]])))).tolist()
                                                    for n in range(len(f))])

        result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut.si')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        fr=transferMatrices.FrequencyResponses()

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]
        for otherPort in range(ports):
            otherName=str(otherPort+1)
            for drivenPort in range(ports):
                drivenName=str(drivenPort+1)
                DutA[otherPort][drivenPort]=fr[outputNames.index('ADut'+otherName+drivenName)][sourceNames.index('VG'+drivenName)]
                DutB[otherPort][drivenPort]=fr[outputNames.index('BDut'+otherName+drivenName)][sourceNames.index('VG'+drivenName)]

        spDict['Dut']=si.sp.SParameters(f,[(array([[DutB[r][c][n] for c in range(ports)] for r in range(ports)]).dot(
                                            inv(array([[DutA[r][c][n] for c in range(ports)] for r in range(ports)])))).tolist()
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
            if si.test.SignalIntegrityAppTestHelper.plotErrors:
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
                        plt.legend(loc='upper right')
                        plt.grid(True)
                        plt.show()

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-1),'s-parameters not equal')
    def testVNAFourPortTransferThru(self):
        ports=4
        reflectNames=['Short','Open','Load']
        spDict=dict()

        for reflectName in reflectNames:
            result = self.GetSimulationResultsCheck('TDRSimulationFourPort'+reflectName+'.si')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for p in range(ports):
                portName=str(p+1)
                A=fr[outputNames.index('A'+reflectName+portName)][sourceNames.index('VG'+portName)]
                B=fr[outputNames.index('B'+reflectName+portName)][sourceNames.index('VG'+portName)]
                f=A.Frequencies()
                spDict[reflectName+portName]=si.sp.SParameters(f,[[[B[n]/A[n]]] for n in range(len(f))])

        thruConnections=[[[1,2],[3,4]],[[1,3],[2,4]],[[1,4],[2,3]]]
        for thruConnection in thruConnections:
            thruConnectionName=str(thruConnection[0][0])+str(thruConnection[0][1])+str(thruConnection[1][0])+str(thruConnection[1][1])
            result = self.GetSimulationResultsCheck('TDRSimulationFourPortThru'+thruConnectionName+'.si')
            sourceNames=result[0]
            outputNames=result[1]
            transferMatrices=result[2]
            outputWaveforms=result[3]

            fr=transferMatrices.FrequencyResponses()

            for thruPorts in thruConnection:
                port1Name=str(thruPorts[0])
                port2Name=str(thruPorts[1])                
                A11=fr[outputNames.index('AThru'+thruConnectionName+'_'+port1Name+port1Name)][sourceNames.index('VG'+port1Name)]
                A21=fr[outputNames.index('AThru'+thruConnectionName+'_'+port2Name+port1Name)][sourceNames.index('VG'+port1Name)]
                B11=fr[outputNames.index('BThru'+thruConnectionName+'_'+port1Name+port1Name)][sourceNames.index('VG'+port1Name)]
                B21=fr[outputNames.index('BThru'+thruConnectionName+'_'+port2Name+port1Name)][sourceNames.index('VG'+port1Name)]
                port2Name=str(thruPorts[1])
                port1Name=str(thruPorts[0])                
                A22=fr[outputNames.index('AThru'+thruConnectionName+'_'+port2Name+port2Name)][sourceNames.index('VG'+port2Name)]
                A12=fr[outputNames.index('AThru'+thruConnectionName+'_'+port1Name+port2Name)][sourceNames.index('VG'+port2Name)]
                B22=fr[outputNames.index('BThru'+thruConnectionName+'_'+port2Name+port2Name)][sourceNames.index('VG'+port2Name)]
                B12=fr[outputNames.index('BThru'+thruConnectionName+'_'+port1Name+port2Name)][sourceNames.index('VG'+port2Name)]
                spDict['Thru'+port1Name+port2Name]=si.sp.SParameters(f,[(array([[B11[n],B12[n]],[B21[n],B22[n]]]).dot(
                                                    inv(array([[A11[n],A12[n]],[A21[n],A22[n]]])))).tolist()
                                                    for n in range(len(f))])

        result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut.si')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        fr=transferMatrices.FrequencyResponses()

        DutA=[[None for _ in range(ports)] for _ in range(ports)]
        DutB=[[None for _ in range(ports)] for _ in range(ports)]
        for otherPort in range(ports):
            otherName=str(otherPort+1)
            for drivenPort in range(ports):
                drivenName=str(drivenPort+1)
                DutA[otherPort][drivenPort]=fr[outputNames.index('ADut'+otherName+drivenName)][sourceNames.index('VG'+drivenName)]
                DutB[otherPort][drivenPort]=fr[outputNames.index('BDut'+otherName+drivenName)][sourceNames.index('VG'+drivenName)]

        spDict['Dut']=si.sp.SParameters(f,[(array([[DutB[r][c][n] for c in range(ports)] for r in range(ports)]).dot(
                                            inv(array([[DutA[r][c][n] for c in range(ports)] for r in range(ports)])))).tolist()
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
#            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
#            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(1,1),spDict['Thru14'].FrequencyResponse(2,1),calStandards[3],0,3,'Thru141'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru14'].FrequencyResponse(2,2),spDict['Thru14'].FrequencyResponse(1,2),calStandards[3],3,0,'Thru144'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
#            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(1,1),spDict['Thru24'].FrequencyResponse(2,1),calStandards[3],1,3,'Thru242'),
#            si.m.cal.ThruCalibrationMeasurement(spDict['Thru24'].FrequencyResponse(2,2),spDict['Thru24'].FrequencyResponse(1,2),calStandards[3],3,1,'Thru244'),
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
            if si.test.SignalIntegrityAppTestHelper.plotErrors:
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

        self.assertTrue(self.SParametersAreEqual(DUTCalcSp, DUTActualSp, 1e-4),'s-parameters not equal')

if __name__ == "__main__":
    unittest.main()
