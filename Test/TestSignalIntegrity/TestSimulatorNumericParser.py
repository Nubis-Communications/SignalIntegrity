"""
TestSimulatorNumericParser.py
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
import copy
import sys

class TestSimulatorNumericParserExample(unittest.TestCase,si.test.RoutineWriterTesterHelper):
    def __init__(self, methodName='runTest'):
        si.test.RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testSimulatorNumericParserExample(self):
        Td=1.23e-9; Zc=55; C=Td/Zc; L=Td*Zc
        Rse=0.001; df=.001; R=.1;

        netlist=['device T 2 telegrapher'+' r '+str(R)+' rse '+str(Rse)+' l '+str(L)+
                 ' c '+str(C)+' df '+str(df),
                 'voltagesource Vs 1','voltagesource Vn 2','device Rt 2 R 65',
                 'device Rr 1 R 60','connect Vs 1 Vn 1','connect Vn 2 Rt 1',
                 'connect Rt 2 T 1','connect T 2 Rr 1','output T 1','output T 2']
        for line in netlist: print(line)

        # pragma: silent exclude
        with open('SimulatorNumericParserExampleNetlist.txt','w') as f:
            for line in netlist:
                f.write(line+'\n')
        # pragma: include
        Fs=40e9; Ts=1./Fs; irlength=20e-9
        fdtm=si.td.wf.TimeDescriptor(0,irlength/Ts,Fs).FrequencyList()
        smp=si.p.SimulatorNumericParser(fdtm).AddLines(netlist)
        tm=smp.TransferMatrices()
        ##########################################
        outnames=['Vt','Vr']
        innames=['Vs','Vn']
        tmfr=tm.FrequencyResponses()
        import matplotlib.pyplot as plt
        for i in range(len(innames)):
            for o in range(len(outnames)):
                plt.subplot(len(outnames),len(innames),o*len(innames)+i+1)
                plt.plot(tmfr[o][i].Frequencies('GHz'),tmfr[o][i].Response('dB'),
                    label=outnames[o]+' due to '+innames[i],color='black')
                plt.legend(loc='upper right',labelspacing=0.1)
                plt.xlabel('frequency (GHz)');
                plt.ylabel('magnitude (dB)')
        #plt.show()
        plt.cla()

        # pragma: silent exclude
        plt.plot(tmfr[0][0].Frequencies('GHz'),tmfr[0][0].Response('dB'),label='Vt due to Vs',color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        #plt.xlim(0,20)
        #plt.ylim(-25,5)
        #si.test.PlotTikZ('SimulatorNumericParserExampleFrequencyResponse00.tex',plt)
        plt.cla()

        plt.plot(tmfr[1][0].Frequencies('GHz'),tmfr[1][0].Response('dB'),label='Vr due to Vs',color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        #plt.xlim(0,20)
        #plt.ylim(-25,5)
        #si.test.PlotTikZ('SimulatorNumericParserExampleFrequencyResponse10.tex',plt)
        plt.cla()

        plt.plot(tmfr[0][1].Frequencies('GHz'),tmfr[0][1].Response('dB'),label='Vt due to Vn',color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        #plt.xlim(0,20)
        #plt.ylim(-25,5)
        #si.test.PlotTikZ('SimulatorNumericParserExampleFrequencyResponse01.tex',plt)
        plt.cla()

        plt.plot(tmfr[1][1].Frequencies('GHz'),tmfr[1][1].Response('dB'),label='Vr due to Vn',color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dB)')
        #plt.xlim(0,20)
        #plt.ylim(-25,5)
        #si.test.PlotTikZ('SimulatorNumericParserExampleFrequencyResponse11.tex',plt)
        plt.cla()
        # pragma: include
        #######################################
        tmir=tm.ImpulseResponses()
        import matplotlib.pyplot as plt
        for i in range(len(innames)):
            for o in range(len(outnames)):
                plt.subplot(len(outnames),len(innames),o*2+i+1)
                plt.plot(tmir[o][i].Times('ns'),tmir[o][i].Values(),
                    label=outnames[o]+' due to '+innames[i],color='black')
                plt.legend(loc='upper right',labelspacing=0.1)
                plt.xlabel('time (ns)');
                plt.ylabel('amplitude (V)')
                plt.xlim(-0.05,3);
                plt.ylim(0,0.5)
        #plt.show()
        plt.cla()
        # pragma: silent exclude
        plt.plot(tmir[0][0].Times('ns'),tmir[0][0].Values(),label='Vt due to Vs',color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        plt.xlim(-0.05,3)
        plt.ylim(0,0.5)
        #si.test.PlotTikZ('SimulatorNumericParserExampleImpulseResponse00.tex',plt)
        plt.cla()

        plt.plot(tmir[1][0].Times('ns'),tmir[1][0].Values(),label='Vr due to Vs',color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        plt.xlim(-0.05,3)
        plt.ylim(0,0.5)
        #si.test.PlotTikZ('SimulatorNumericParserExampleImpulseResponse10.tex',plt)
        plt.cla()

        plt.plot(tmir[0][1].Times('ns'),tmir[0][1].Values(),label='Vt due to Vn',color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        plt.xlim(-0.05,3)
        plt.ylim(0,0.5)
        #si.test.PlotTikZ('SimulatorNumericParserExampleImpulseResponse01.tex',plt)
        plt.cla()

        plt.plot(tmir[1][1].Times('ns'),tmir[1][1].Values(),label='Vr due to Vn',color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        plt.xlim(-0.05,3)
        plt.ylim(0,0.5)
        #si.test.PlotTikZ('SimulatorNumericParserExampleImpulseResponse11.tex',plt)
        plt.cla()
        # pragma: include
        ##################################################
        bitRate=5e9; ui=1./bitRate

        rcf=si.td.f.RaisedCosineFilter(int(0.3*ui/Ts))

        uf=2
        usf=si.td.f.InterpolatorSinX(uf)
        fdf=si.td.f.FractionalDelayFilterSinX(0,False)

        bitsResult=300
        lengthResult=bitsResult*ui
        tdr=si.td.wf.TimeDescriptor(0.,lengthResult/Ts*uf,Fs*uf)
        tdi=((((tdr/usf.FilterDescriptor())/
                tmir[0][0].FirFilter().FilterDescriptor())/
                    rcf.FilterDescriptor())/
                        fdf.FilterDescriptor())
        import random
        bits=[1 if random.random()>0.5 else 0
            for _ in range(bitsResult+1)]; bits[0]=0
        a=[(bits[k]-bits[k-1]) for k in range(1,bitsResult+1)]
        import numpy
        jitter=numpy.random.normal(0.,10.e-12,bitsResult).tolist()
        wfi=sum([si.td.wf.StepWaveform(tdi,a[b],b*ui)*
                 si.td.f.FractionalDelayFilterSinX(jitter[b]/Ts,False)
                    for b in range(len(a))])
        wfi=wfi*rcf
        # pragma: silent exclude
        wfi.WriteToFile('SimulatorNumericParserExampleWaveform.txt')

        tdt=si.td.wf.TimeDescriptor(0.0,10e-9*Fs,Fs)
        trimmerfd=tdt/wfi.TimeDescriptor()
        trimmer=si.td.f.WaveformTrimmer(int(trimmerfd.TrimLeft()),int(trimmerfd.TrimRight()))
        wfiplot=wfi*trimmer

        plt.plot(wfiplot.Times('ns'),
                 wfiplot.Values(),label='Vs',color='black')
        #plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlim(0 ,10)
        plt.ylim(-0.05,1.05)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        si.test.PlotTikZ('SimulatorNumericParserExampleInputWaveform.tex',plt)
        #plt.show()
        plt.cla()

        # pragma: include
        fci=wfi.FrequencyContent()

        plt.plot(fci.Frequencies('GHz'),
            [v+90 for v in fci.Values('dBmPerHz')],color='black')
        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude (dBm/GHz)')
        plt.xlim(0,15)
        plt.ylim(-60,30)
        # pragma: silent exclude
        si.test.PlotTikZ('SimulatorNumericParserExampleFrequencyContent.tex',plt)
        # pragma: include
        #plt.show()
        plt.cla()

        wfn=si.td.wf.NoiseWaveform(tdi,20e-3)
        ###################################################
        tmp=si.td.f.TransferMatricesProcessor(tm)
        wfolist=[wf*usf for wf in tmp.ProcessWaveforms([wfi,wfn])]

        # pragma: silent exclude
        wfotemp=copy.deepcopy(wfolist)

        Fso=wfolist[0].TimeDescriptor().Fs
        tdt=[si.td.wf.TimeDescriptor(0.0,10e-9*Fso,Fso),
             si.td.wf.TimeDescriptor(Td,10e-9*Fso,Fso)]
        trimmerfd=[td/wf.TimeDescriptor()
                   for (td,wf) in zip(tdt,wfolist)]
        trimmer=[si.td.f.WaveformTrimmer(int(fd.TrimLeft()),int(fd.TrimRight()))
                    for fd in trimmerfd]
        wfolist=[wf*tr for (wf,tr) in zip(wfolist,trimmer)]
        # pragma: include
        plt.plot(wfolist[0].Times('ns'),
                 wfolist[0].Values(),label='Vt',color='black')
        plt.plot([t-Td/1e-9 for t in wfolist[1].Times('ns')],
                 wfolist[1].Values(),label='Vr',color='gray')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlim(0 ,10)
        plt.ylim(-0.05,0.65)
        plt.xlabel('time (ns)')
        plt.ylabel('amplitude (V)')
        # pragma: silent exclude
        si.test.PlotTikZ('SimulatorNumericParserExampleOutputWaveforms.tex',plt)
        wfolist=wfotemp
        # pragma: include
        #plt.show()
        plt.cla()

        times=[(t-Td/1e-9)%(3*ui/1e-9) for t in wfolist[1].Times('ns')]
        values = wfolist[1].Values()

        pltt=[]; pltv=[]; tt=[]; vv=[]
        for k in range(len(times)):
            if k==0:
                tt=[times[k]]; vv=[values[k]]
            elif times[k]>times[k-1]:
                tt.append(times[k]); vv.append(values[k])
            else:
                pltt.append(tt); pltv.append(vv)
                tt=[times[k]]; vv=[values[k]]

        for e in range(len(pltt)):
            plt.plot(pltt[e],pltv[e],color='black')
        plt.ylim(-0.00,0.5); plt.xlim(0.1,0.5)
        plt.xlabel('time (ns)'); plt.ylabel('amplitude (V)')
        # pragma: silent exclude
        si.test.PlotTikZ('SimulatorNumericParserExampleEyeDiagram.tex',plt)
        # pragma: include
        #plt.show()
        plt.cla()
    def testWriteSimulationExample(self):
        return
        self.WriteCode('TestSimulatorNumericParser.py','testSimulatorNumericParserExample(self)',self.standardHeader)
    def testXXXSplitItUp(self):
        filename='SimulatorNumericParserExampleCode'
        if not os.path.exists(filename+'.py'):
            self.testWriteSimulationExample()
        with open(filename+'.py', 'rU' if sys.version_info.major < 3 else 'r') as totalFile:
            total = totalFile.readlines()
        index=0
        writing = False
        for line in total:
            if not writing:
                writing = True
                outputFile = open(filename+str(index)+'.py','w')
            if '##############' in line:
                outputFile.close()
                writing=False
                index=index+1
            else:
                outputFile.write(line)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
