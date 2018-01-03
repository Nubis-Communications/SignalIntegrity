import unittest
import SignalIntegrity as si
from TestSignalIntegrity.TestHelpers import SParameterCompareHelper,RoutineWriterTesterHelper
import os

from numpy import matrix

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
class TestSPARQFourPortScaled(unittest.TestCase,SParameterCompareHelper,si.test.PySIAppTestHelper,RoutineWriterTesterHelper):
    relearn=True
    plot=False
    debug=False
    checkPictures=True
    epsilon=50e-12
    usePickle=False
    def setUp(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    def __init__(self, methodName='runTest'):
        SParameterCompareHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
        si.test.PySIAppTestHelper.__init__(self,os.path.dirname(os.path.realpath(__file__)))
        RoutineWriterTesterHelper.__init__(self)
    def GetSimulationResultsCheck(self,filename):
        if not hasattr(TestSPARQFourPortScaled, 'simdict'):
            TestSPARQFourPortScaled.simdict=dict()
            if TestSPARQFourPortScaled.usePickle:
                try:
                    import pickle
                    TestSPARQFourPortScaled.simdict=pickle.load(open("simresults.p","rb"))
                except:
                    pass
        if filename in TestSPARQFourPortScaled.simdict:
            return TestSPARQFourPortScaled.simdict[filename]
        TestSPARQFourPortScaled.simdict[filename] = self.SimulationResultsChecker(filename)
        return TestSPARQFourPortScaled.simdict[filename]
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

        if TestSPARQFourPortScaled.usePickle:
            if not os.path.exists('simresults.p'):
                import pickle
                pickle.dump(self.simdict,open("simresults.p","wb"))

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
        
        if TestSPARQFourPortScaled.usePickle:
            if not os.path.exists('simresults.p'):
                import pickle
                pickle.dump(self.simdict,open("simresults.p","wb"))

        
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

        cm=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms().WriteToFile('xferNoneTDR')

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

        cm2=si.m.cal.Calibration(2,f)
        cm2.ET=[si.m.cal.ErrorTerms([[cm3.ET[n][r][c] for c in range(ports)] for r in range(ports)]) for n in range(len(f))]
        cm2.WriteToFile('xferThruTDR')

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
                Poly=si.spl.Spline(DutA[r][c].Frequencies(),DutA[r][c].Content())
                newresp=[Poly.Evaluate(fr) for fr in f]
                DutA[r][c]=si.fd.FrequencyContent(f,newresp)
        for r in range(ports):
            for c in range(ports):    
                Poly=si.spl.Spline(DutB[r][c].Frequencies(),DutB[r][c].Content())
                newresp=[Poly.Evaluate(fr) for fr in f]
                DutB[r][c]=si.fd.FrequencyContent(f,newresp)

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
                        for n in range(len(f)):
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

        if TestSPARQFourPortScaled.usePickle:
            if not os.path.exists('simresults.p'):
                import pickle
                pickle.dump(self.simdict,open("simresults.p","wb"))

        for r in range(2):
            for c in range(2):
                for n in range(len(f)):
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

        cm=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms().WriteToFile('xferNoneDiagonalA')

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
                        for n in range(len(f)):
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

        if TestSPARQFourPortScaled.usePickle:
            if not os.path.exists('simresults.p'):
                import pickle
                pickle.dump(self.simdict,open("simresults.p","wb"))

        for r in range(2):
            for c in range(2):
                for n in range(len(f)):
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

        cm=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms().WriteToFile('xferNoneBAInverse')

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
                        for n in range(len(f)):
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
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(1,1),spDict['Thru13'].FrequencyResponse(2,1),calStandards[3],0,2,'Thru131'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru13'].FrequencyResponse(2,2),spDict['Thru13'].FrequencyResponse(1,2),calStandards[3],2,0,'Thru133'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(1,1),spDict['Thru23'].FrequencyResponse(2,1),calStandards[3],1,2,'Thru232'),
            si.m.cal.ThruCalibrationMeasurement(spDict['Thru23'].FrequencyResponse(2,2),spDict['Thru23'].FrequencyResponse(1,2),calStandards[3],2,1,'Thru233'),
            ]

        cm3=si.m.cal.Calibration(ports,f,ml).CalculateErrorTerms()

        ports=2

        cm2=si.m.cal.Calibration(2,f)
        cm2.ET=[si.m.cal.ErrorTerms([[cm3.ET[n][r][c] for c in range(ports)] for r in range(ports)]) for n in range(len(f))]
        cm2.WriteToFile('xferThruDiagonalA')

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

        for r in range(2):
            for c in range(2):
                for n in range(len(f)):
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

        cm2=si.m.cal.Calibration(2,f)
        cm2.ET=[si.m.cal.ErrorTerms([[cm3.ET[n][r][c] for c in range(ports)] for r in range(ports)]) for n in range(len(f))]
        cm2.WriteToFile('xferThruBAInverse')

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

        DUTCalcSp=cm2.DutCalculation(spDict['Dut'])
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

    def testAAATryToFix(self):
        return
        result = self.GetSimulationResultsCheck('TDRSimulationFourPortDut4Scaled.xml')
        sourceNames=result[0]
        outputNames=result[1]
        transferMatrices=result[2]
        outputWaveforms=result[3]

        V4=outputWaveforms[outputNames.index('V4')]
        A4=outputWaveforms[outputNames.index('A4')]
        B4=outputWaveforms[outputNames.index('B4')]
        si.td.wf.Waveform.adaptionStrategy='Linear'
        V4add=A4+B4

        import matplotlib.pyplot as plt
        plt.clf()
        plt.title('A4 and B4 compare')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        plt.plot(V4.Times('ns'),V4.Values(),label='V4')
        plt.plot(A4.Times('ns'),A4.Values(),label='A4')
        plt.plot(B4.Times('ns'),B4.Values(),label='B4')
        plt.legend(loc='upper right')
        plt.grid(True)
        plt.show()

        plt.clf()
        plt.title('V4 compare')
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        plt.plot(V4.Times('ns'),V4.Values(),label='from sim')
        plt.plot(V4add.Times('ns'),V4add.Values(),label='added manually')
        plt.legend(loc='upper right')
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    unittest.main()
