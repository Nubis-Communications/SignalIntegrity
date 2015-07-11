import unittest
import os
from cStringIO import StringIO
import sys
import SignalIntegrity as si
from TestHelpers import *

def AdaptWaveform(wf,td):
        u=int(round(td.Fs/wf.TimeDescriptor().Fs))
        if not u==1:
            wf=wf*si.td.f.InterpolatorSinX(u)
        ad=td/wf.TimeDescriptor()
        f=ad.D-int(ad.D)
        if not f==0.0:
            wf=wf*si.td.f.FractionalDelayFilterSinX(f,True)
        ad=td/wf.TimeDescriptor()
        tr=si.td.f.WaveformTrimmer(max(0,int(round(ad.TrimLeft()))),max(0,int(round(ad.TrimRight()))))
        wf=wf*tr
        return wf

class Test(unittest.TestCase,RoutineWriterTesterHelper,ResponseTesterHelper,SourcesTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testSymbolicSimulatorExample3(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        vp=si.sd.Simulator(sd)
        vp.AddVoltageSource('v1',2)
        vp.ConnectDevicePort('v1',1,'C',1)
        vp.ConnectDevicePort('v1',2,'C',2)
        vp.pOutputList = [('R',1),('R',2)]
        svp=si.sd.SimulatorSymbolic(vp)
        svp.DocStart().LaTeXTransferMatrix().DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),svp,'Symbolic Simulator 1')
    def testSymbolicSimulatorExample3p5(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        vp=si.sd.Simulator(sd)
        vp.AddVoltageSource('v1',2)
        vp.AddDevice('G',1,si.dev.Ground())
        vp.ConnectDevicePort('v1',1,'C',1)
        vp.ConnectDevicePort('v1',2,'C',2)
        vp.ConnectDevicePort('v1',1,'G',1)
        vp.pOutputList = [('R',1),('R',2)]
        svp=si.sd.SimulatorSymbolic(vp)
        svp.DocStart().LaTeXTransferMatrix().DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),svp,'Symbolic Simulator 1')
    def testSymbolicSimulatorExample4(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('C',4)
        sd.AddDevice('R',2)
        sd.ConnectDevicePort('C',3,'R',1)
        sd.ConnectDevicePort('C',4,'R',2)
        vp=si.sd.Simulator(sd)
        vp.AddVoltageSource('v1',1)
        vp.AddCurrentSource('i1',1)
        vp.ConnectDevicePort('v1',1,'C',1)
        vp.ConnectDevicePort('i1',1,'C',2)
        vp.pOutputList = [('R',1),('R',2)]
        svp=si.sd.SimulatorSymbolic(vp)
        svp.DocStart().LaTeXTransferMatrix().DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),svp,'Symbolic Simulator 1')
    def testSimulatorParserVoltageSourceOnePort(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=si.fd.EvenlySpacedFrequencyList(20.e9,200)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device F 2 file filter.s2p')
        sp.AddLine('device S 2 R 50.')
        sp.AddLine('device R 2 R 50.')
        sp.AddLine('device G 1 ground')
        sp.AddLine('voltagesource V 1')
        sp.AddLine('connect V 1 S 1')
        sp.AddLine('connect S 2 F 1')
        sp.AddLine('connect F 2 R 1')
        sp.AddLine('connect R 2 G 1')
        sp.AddLine('output R 1')
        tm=sp.TransferMatrices()
        ports=tm.m_P
        fileName = self.id().split('.')[2].replace('test','')+'.s'+str(ports)+'p'
        self.CheckSParametersResult(sp.TransferMatrices(),fileName,fileName+' incorrect')
    def testSimulatorParserCurrentSourceOnePort(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=si.fd.EvenlySpacedFrequencyList(20.e9,200)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device F 2 file filter.s2p')
        sp.AddLine('device S 2 R 50.')
        sp.AddLine('device R 2 R 50.')
        sp.AddLine('device G 1 ground')
        sp.AddLine('currentsource I 1')
        sp.AddLine('connect I 1 S 1 F 1')
        sp.AddLine('connect S 2 G 1')
        sp.AddLine('connect F 2 R 1')
        sp.AddLine('connect R 2 G 1')
        sp.AddLine('output R 1')
        tm=sp.TransferMatrices()
        ports=tm.m_P
        fileName = self.id().split('.')[2].replace('test','')+'.s'+str(ports)+'p'
        self.CheckSParametersResult(sp.TransferMatrices(),fileName,fileName+' incorrect')
    def testSimulatorParserVoltageSourceTwoPorts(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=si.fd.EvenlySpacedFrequencyList(20.e9,200)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device F 2 file filter.s2p')
        sp.AddLine('device S 2 R 50.')
        sp.AddLine('device R 2 R 50.')
        sp.AddLine('device G 1 ground')
        sp.AddLine('voltagesource V 2')
        sp.AddLine('connect V 2 S 1')
        sp.AddLine('connect V 1 G 1')
        sp.AddLine('connect S 2 F 1')
        sp.AddLine('connect F 2 R 1')
        sp.AddLine('connect R 2 G 1')
        sp.AddLine('output R 1')
        tm=sp.TransferMatrices()
        ports=tm.m_P
        fileName = self.id().split('.')[2].replace('test','')+'.s'+str(ports)+'p'
        self.CheckSParametersResult(sp.TransferMatrices(),fileName,fileName+' incorrect')
    def testSimulatorParserCurrentSourceTwoPorts(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=si.fd.EvenlySpacedFrequencyList(20.e9,200)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device F 2 file filter.s2p')
        sp.AddLine('device S 2 R 50.')
        sp.AddLine('device R 2 R 50.')
        sp.AddLine('device G 1 ground')
        sp.AddLine('currentsource I 2')
        sp.AddLine('connect I 2 S 1 F 1')
        sp.AddLine('connect S 2 G 1 I 1')
        sp.AddLine('connect F 2 R 1')
        sp.AddLine('connect R 2 G 1')
        sp.AddLine('output R 1')
        tm=sp.TransferMatrices()
        ports=tm.m_P
        fileName = self.id().split('.')[2].replace('test','')+'.s'+str(ports)+'p'
        self.CheckSParametersResult(sp.TransferMatrices(),fileName,fileName+' incorrect')
    def testSimulatorXRay041(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=si.fd.EvenlySpacedFrequencyList(20.e9,400)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device X 4 file .\\DesignCon2008\\XRAY041.s4p')
        sp.AddLine('device S1 2 R 50.')
        sp.AddLine('device S2 2 R 50.')
        sp.AddLine('device R1 2 R 50.')
        sp.AddLine('device R2 2 R 50.')
        sp.AddLine('device G 1 ground')
        sp.AddLine('voltagesource V1 1')
        sp.AddLine('voltagesource V2 1')
        sp.AddLine('connect V1 1 S1 1')
        sp.AddLine('connect V2 1 S2 1')
        sp.AddLine('connect S1 2 X 1')
        sp.AddLine('connect S2 2 X 2')
        sp.AddLine('connect X 3 R1 1')
        sp.AddLine('connect X 4 R2 1')
        sp.AddLine('connect R1 2 G 1')
        sp.AddLine('connect R2 2 G 1')
        sp.AddLine('output R1 1 R2 1 X 1 X 2')
        tm=sp.TransferMatrices()
        ports=tm.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(sp.TransferMatrices(),spFileName,spFileName+' incorrect')
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-80e-9,160*40,40e9))
        stepinp=stepin
        stepinm=stepin*-1.
        srs=sp.ProcessWaveforms([stepinp,stepinm])
        sr=srs[0]-srs[1]
        tdr=srs[2]-srs[3]
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-1e-9,21*40,40e9))
        aw=si.td.wf.AdaptedWaveforms([stepin,sr,tdr])
        sr=aw[1]
        tdr=aw[2]
        if False:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(stepin.Times('ns'),stepin.Values(),label='step input')
            plt.plot(sr.Times('ns'),sr.Values(),label='step response')
            plt.plot(tdr.Times('ns'),tdr.Values(),label='tdr response')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(stepin,'Waveform_'+fileNameBase+'_StepIn.txt','Waveform_'+fileNameBase+'_StepIn.txt')
        self.CheckWaveformResult(sr,'Waveform_'+fileNameBase+'_StepResponse.txt','Waveform_'+fileNameBase+'_StepResponse.txt')
        self.CheckWaveformResult(tdr,'Waveform_'+fileNameBase+'_TdrResponse.txt','Waveform_'+fileNameBase+'_TdrResponse.txt')
    def testSimulatorXRay041Symbolic(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sp = si.p.SimulatorParser()
        sp.AddLine('device X 4')
        sp.AddLine('device TP 2')
        sp.AddLine('device TM 2')
        sp.AddLine('device RP 1')
        sp.AddLine('device RM 1')
        sp.AddLine('device G 1 ground')
        sp.AddLine('voltagesource V1 1')
        sp.AddLine('voltagesource V2 1')
        sp.AddLine('connect V1 1 TP 1')
        sp.AddLine('connect V2 1 TM 1')
        sp.AddLine('connect TP 2 X 1')
        sp.AddLine('connect TM 2 X 2')
        sp.AddLine('connect X 3 RP 1')
        sp.AddLine('connect X 4 RM 1')
        sp.AddLine('output RP 1 RM 1 X 1 X 2')
        ss=si.sd.SimulatorSymbolic(sp.SystemDescription())
        ss.DocStart()
        ss._AddEq('TP='+ss._LaTeXMatrix(si.sy.SeriesZ('ZT_p')))
        ss._AddEq('TM='+ss._LaTeXMatrix(si.sy.SeriesZ('ZT_m')))
        ss._AddEq('RP='+ss._LaTeXMatrix(si.sy.ShuntZ(1,'ZT_p')))
        ss._AddEq('RM='+ss._LaTeXMatrix(si.sy.ShuntZ(1,'ZT_m')))
        ss.LaTeXTransferMatrix()
        ss.DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ss,'SimulatorXRay041Symbolic')
    def testSimulatorXRaySparqDemo16(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=si.fd.EvenlySpacedFrequencyList(40.e9,400)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device X 4 file Sparq_demo_16.s4p')
        sp.AddLine('device S1 2 R 50.')
        sp.AddLine('device S2 2 R 50.')
        sp.AddLine('device R1 2 R 50.')
        sp.AddLine('device R2 2 R 50.')
        sp.AddLine('device G 1 ground')
        sp.AddLine('voltagesource V1 1')
        sp.AddLine('voltagesource V2 1')
        sp.AddLine('connect V1 1 S1 1')
        sp.AddLine('connect V2 1 S2 1')
        sp.AddLine('connect S1 2 X 1')
        sp.AddLine('connect S2 2 X 2')
        sp.AddLine('connect X 3 R1 1')
        sp.AddLine('connect X 4 R2 1')
        sp.AddLine('connect R1 2 G 1')
        sp.AddLine('connect R2 2 G 1')
        sp.AddLine('output R1 1 R2 1 X 1 X 2')
        tm=sp.TransferMatrices()
        ports=tm.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(sp.TransferMatrices(),spFileName,spFileName+' incorrect')
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-20e-9,40*80,80e9))
        stepinp=stepin
        stepinm=stepin*-1.
        srs=sp.ProcessWaveforms([stepinp,stepinm])
        sr=srs[0]-srs[1]
        tdr=srs[2]-srs[3]
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-1e-9,11*80,80e9))
        aw=si.td.wf.AdaptedWaveforms([stepin,sr,tdr])
        sr=aw[1]
        tdr=aw[2]
        if False:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(stepin.Times('ns'),stepin.Values(),label='step input')
            plt.plot(sr.Times('ns'),sr.Values(),label='step response')
            plt.plot(tdr.Times('ns'),tdr.Values(),label='tdr response')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(stepin,'Waveform_'+fileNameBase+'_StepIn.txt','Waveform_'+fileNameBase+'_StepIn.txt')
        self.CheckWaveformResult(sr,'Waveform_'+fileNameBase+'_StepResponse.txt','Waveform_'+fileNameBase+'_StepResponse.txt')
        self.CheckWaveformResult(tdr,'Waveform_'+fileNameBase+'_TdrResponse.txt','Waveform_'+fileNameBase+'_TdrResponse.txt')

if __name__ == "__main__":
    unittest.main()
