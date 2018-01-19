'''
Created on Jan 18, 2018

@author: pete
'''
import unittest
import SignalIntegrity as si
from TestSignalIntegrity.TestHelpers import SParameterCompareHelper,RoutineWriterTesterHelper
import os

from numpy import matrix,mean
import math
import xlrd

from SignalIntegrity.Measurement import CalKit

class TestSequidTest(unittest.TestCase,SParameterCompareHelper,si.test.PySIAppTestHelper,RoutineWriterTesterHelper):
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
    def NameForTest(self):
        return '_'.join(self.id().split('.')[-2:])
    def testSequidSOLOnePort(self):
        ports=1
        reflectNames=['Short','Open','Load']
        dutNames=['BPFilter','LPFilter']

        spDict=dict()
        tdr=si.m.tdr.TDRWaveformToSParameterConverter(Length=50e-9,
                                                      WindowHalfWidthTime=1e-9,
                                                      WindowRaisedCosineDuration=1e-9,
                                                      Sigma=1.
                                                      )

        for reflectName in reflectNames+dutNames:
            book=xlrd.open_workbook(reflectName+'200.xls',encoding_override='ascii')
            sheet=book.sheet_by_index(0)
            (rows,cols)=(sheet.nrows,sheet.ncols)
            times=[c.value for c in sheet.col_slice(0,2,rows-2)]
            volts=[c.value for c in sheet.col_slice(3,2,rows-2)]
            Fs=1./mean([times[k]-times[k-1] for k in range(1,len(times))])
            wf=si.td.wf.Waveform(si.td.wf.TimeDescriptor(times[0],len(times),Fs),volts)
            rmf=tdr.RawMeasuredSParameters(wf)

            limit=16.e9
            for n in range(len(rmf)):
                if rmf.m_f[n]<=limit:
                    nlimit=n

            rmf=si.sp.SParameters([rmf.m_f[nn] for nn in range(nlimit)],[rmf.m_d[nn] for nn in range(nlimit)])

            spDict[reflectName]=rmf
            spDict[reflectName+'wf']=wf

        plotthem=False
        if plotthem:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.title('waveforms')
            for reflectName in reflectNames:
                wf=spDict[reflectName+'wf']
                plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.legend(loc='upper right')
            plt.grid(True)
            plt.show()

            import matplotlib.pyplot as plt
            plt.clf()
            plt.title('derivatives')
            for reflectName in reflectNames:
                wf=spDict[reflectName+'wf'].Derivative(scale=False)
                plt.plot(wf.Times('ns'),wf.Values(),label=reflectName)
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.legend(loc='upper right')
            plt.grid(True)
            plt.show()

            import matplotlib.pyplot as plt
            plt.clf()
            plt.title('s11 magnitude')
            for reflectName in reflectNames:
                resp=spDict[reflectName].FrequencyResponse(1,1)
                plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label=reflectName)
            plt.xlabel('frequency (GHz)')
            plt.ylabel('magnitude (dB)')
            plt.legend(loc='upper right')
            plt.grid(True)
            plt.show()

            import matplotlib.pyplot as plt
            plt.clf()
            plt.title('s11 phase')
            for reflectName in reflectNames:
                resp=spDict[reflectName].FrequencyResponse(1,1)
                plt.plot(resp.Frequencies('GHz'),resp.Values('deg'),label=reflectName)
            plt.xlabel('frequency (GHz)')
            plt.ylabel('phase (deg)')
            plt.legend(loc='upper right')
            plt.grid(True)
            plt.show()

        dutName='LPFilter'

        f=spDict[dutName].f()

        ck=si.m.calkit.CalibrationKit('CalKitFile.cstd',f)
#         calStandards=[si.m.calkit.std.ShortStandard(f),
#               si.m.calkit.OpenStandard(f),
#               si.m.calkit.LoadStandard(f),
#               si.m.calkit.ThruStandard(f,100e-12)]

        calStandards=[ck.shortStandard,ck.openStandard,ck.loadStandard]

        ml=[si.m.cal.ReflectCalibrationMeasurement(spDict['Short'].FrequencyResponse(1,1),calStandards[0],0,'Short1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Open'].FrequencyResponse(1,1),calStandards[1],0,'Open1'),
            si.m.cal.ReflectCalibrationMeasurement(spDict['Load'].FrequencyResponse(1,1),calStandards[2],0,'Load1'),
            ]

        cm=si.m.cal.Calibration(ports,f,ml)
        Fixture=cm.Fixtures()
        for p in range(ports):
            self.SParameterRegressionChecker(Fixture[p],'sequidTDR'+str(p+1)+'.s'+str(ports*2)+'p')

        DUTCalcSp=cm.DutCalculation(spDict[dutName])
        return


        self.SParameterRegressionChecker(DUTCalcSp, self.NameForTest()+'_Calc.s1p')
        #DUTActualSp=si.sp.dev.TLine(f,2,40,300e-12)
        #self.SParameterRegressionChecker(DUTActualSp, self.NameForTest()+'_Actual.s1p')
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

if __name__ == "__main__":
    unittest.main()
