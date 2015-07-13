import unittest
import os
from cStringIO import StringIO
import sys
import SignalIntegrity as si
from TestHelpers import *

class TestSimulator(unittest.TestCase,RoutineWriterTesterHelper,ResponseTesterHelper,SourcesTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)
    def testSymbolicSimulatorExample1(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('S',2)
        sd.AddDevice('\\Gamma_l',1)
        sd.AddDevice('\\Gamma_s',1)
        sd.ConnectDevicePort('\\Gamma_s',1,'S',1)
        sd.ConnectDevicePort('S',2,'\\Gamma_l',1)
        sd.AssignM('\\Gamma_s',1,'m1')
        ssp=si.sd.SystemSParametersSymbolic(sd)
        ssp.LaTeXSystemEquation().Emit()
        # exclude
        self.CheckSymbolicResult(self.id()+'_1',ssp,self.id())
        # include
        ssp.AssignSParameters('\\Gamma_s',si.sy.ShuntZ(1,'Zs'))
        ssp.AssignSParameters('\\Gamma_l',si.sy.ShuntZ(1,'Zl'))
        ssp.Clear().LaTeXSystemEquation().Emit()
        # exclude
        self.CheckSymbolicResult(self.id()+'_2',ssp,self.id())
    def testSymbolicSimulatorExample1Code(self):
        self.WriteCode('TestSimulator.py','testSymbolicSimulatorExample1(self)',self.standardHeader)
    def testSymbolicSimulatorExample1a(self):
        sd=si.sd.SystemDescription()
        sd.AddDevice('S',2)
        sd.AddDevice('\\Gamma_l',1)
        sd.ConnectDevicePort('S',2,'\\Gamma_l',1)
        s=si.sd.Simulator(sd)
        s.AddVoltageSource('V',1)
        s.AddDevice('Zs',2)
        s.ConnectDevicePort('V',1,'Zs',1)
        s.ConnectDevicePort('Zs',2,'S',1)
        s.pOutputList = [('S',1),('S',2)]
        ss=si.sd.SimulatorSymbolic(s)
        ss.LaTeXEquations().Emit()
        # exclude
        self.CheckSymbolicResult(self.id()+'_1',ss,self.id())
        # include
        ss.AssignSParameters('Zs',si.sy.SeriesZ('Zs'))
        ss.AssignSParameters('\\Gamma_l',si.sy.ShuntZ(1,'Zl'))
        ss.Clear().LaTeXEquations().Emit()
        # exclude
        self.CheckSymbolicResult(self.id()+'_2',ss,self.id())
    def testSymbolicSimulatorExample1aCode(self):
        self.WriteCode('TestSimulator.py','testSymbolicSimulatorExample1a(self)',self.standardHeader)
    def testWriteSimulator_Basic(self):
        fileName="../SignalIntegrity/SystemDescriptions/Simulator.py"
        className='Simulator'
        defName=['__init__','pOutputList','AddVoltageSource','AddCurrentSource']
        self.WriteClassCode(fileName,className,defName)
    def testWriteSimulator_Other(self):
        fileName="../SignalIntegrity/SystemDescriptions/Simulator.py"
        className='Simulator'
        defName=['SourceVector','SourceToStimsPrimeMatrix','StimsPrime','SIPrime','VoltageExtractionMatrix']
        self.WriteClassCode(fileName,className,defName)
    def testWriteTransferMatrices_Basic(self):
        fileName="../SignalIntegrity/FrequencyDomain/TransferMatrices.py"
        className='TransferMatrices'
        defName=['__init__','SParameters','__len__','__getitem__']
        self.WriteClassCode(fileName,className,defName)
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
        self.CheckSymbolicResult(self.id(),svp,self.id())
    def testSimulatorParserVoltageSourceOnePortSymbolic(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sp = si.p.SimulatorParser()
        sp.AddLine('device F 2')
        sp.AddLine('device S 2')
        sp.AddLine('device R 1')
        sp.AddLine('voltagesource V 1')
        sp.AddLine('connect V 1 S 1')
        sp.AddLine('connect S 2 F 1')
        sp.AddLine('connect F 2 R 1')
        sp.AddLine('output F 1 F 2')
        ss=si.sd.SimulatorSymbolic(sp.SystemDescription(),size='small')
        ss.AssignSParameters('S',si.sy.SeriesZ('Z'))
        ss.AssignSParameters('R',si.sy.ShuntZ(1,'Z'))
        ss.DocStart().LaTeXEquations().DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ss,self.id())
    def testSimulatorParserVoltageSourceOnePort(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=si.fd.EvenlySpacedFrequencyList(20.e9,10*20)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device F 2 file filter.s2p')
        sp.AddLine('device S 2 R 50.')
        sp.AddLine('device R 1 R 50.')
        sp.AddLine('voltagesource V 1')
        sp.AddLine('connect V 1 S 1')
        sp.AddLine('connect S 2 F 1')
        sp.AddLine('connect F 2 R 1')
        sp.AddLine('output F 1 F 2')
        tm=sp.TransferMatrices()
        tmsp=tm.SParameters()
        ports=tmsp.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(tmsp,spFileName,spFileName+' incorrect')
        # check theory for filter response based on s-parameters
        spf=si.sp.File('filter.s2p').Resample(f)
        # theory is that thru response is 1/2 of S21 and return loss is 1/2 S11 + 1/2
        tm2m=[[[0.5*m[0][0]+0.5,0.],[0.5*m[1][0],0.]] for m in spf]
        tm2=si.sp.SParameters(spf.f(),tm2m)
        # compare these resampled s-parameters to regression
        self.CheckSParametersResult(tm2,fileNameBase+'2'+'.s'+str(ports)+'p',spFileName+' incorrect')
        # compare them directly to the previous result
        self.CheckSParametersResult(tm2,spFileName,spFileName+' incorrect')
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-80e-9,160*40,40e9),Amplitude=2.0)
        tmp=si.td.f.TransferMatricesProcessor(tm)
        srs=tmp.ProcessWaveforms([stepin])
        sr=srs[1]
        tdr=srs[0]
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
        sp.AddLine('output F 1 F 2')
        tm=sp.TransferMatrices()
        tmsp=tm.SParameters()
        ports=tmsp.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(tmsp,spFileName,spFileName+' incorrect')
    def testSimulatorParserVoltageSourceTwoPorts(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=si.fd.EvenlySpacedFrequencyList(20.e9,20*20)
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
        sp.AddLine('output F 1 F 2')
        tm=sp.TransferMatrices()
        tmsp=tm.SParameters()
        ports=tmsp.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(tmsp,spFileName,spFileName+' incorrect')
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-80e-9,160*40,40e9))
        tmp=si.td.f.TransferMatricesProcessor(tm)
        srs=tmp.ProcessWaveforms([stepin])
        sr=srs[0]
        tdr=srs[1]
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
        tmsp=tm.SParameters()
        ports=tmsp.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(tmsp,spFileName,spFileName+' incorrect')
    def testSimulatorXRay041(self):
        path=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        f=si.fd.EvenlySpacedFrequencyList(20.e9,400)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device X 4 file .//DesignCon2008//XRAY041.s4p')
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
        sp.AddLine('output X 3 X 4 X 1 X 2')
        tm=sp.TransferMatrices()
        tmsp=tm.SParameters()
        ports=tmsp.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(tmsp,spFileName,spFileName+' incorrect')
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-80e-9,160*40,40e9))
        stepinp=stepin
        stepinm=stepin*-1.
        tmp=si.td.f.TransferMatricesProcessor(tm)
        srs=tmp.ProcessWaveforms([stepinp,stepinm])
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
        sp.AddLine('output X 3 X 4 X 1 X 2')
        ss=si.sd.SimulatorSymbolic(sp.SystemDescription(),size='small')
        ss.DocStart()
        ss._AddEq('TP='+ss._LaTeXMatrix(si.sy.SeriesZ('ZT_p')))
        ss._AddEq('TM='+ss._LaTeXMatrix(si.sy.SeriesZ('ZT_m')))
        ss._AddEq('RP='+ss._LaTeXMatrix(si.sy.ShuntZ(1,'ZR_p')))
        ss._AddEq('RM='+ss._LaTeXMatrix(si.sy.ShuntZ(1,'ZR_m')))
        ss.LaTeXTransferMatrix()
        ss.DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ss,'SimulatorXRay041Symbolic')
    def testSimulatorXRay041Symbolic2(self):
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
        sp.AddLine('output X 3 X 4 X 1 X 2')
        ss=si.sd.SimulatorSymbolic(sp.SystemDescription(),size='small')
        ss.AssignSParameters('TP',si.sy.SeriesZ('Z'))
        ss.AssignSParameters('TM',si.sy.SeriesZ('Z'))
        ss.AssignSParameters('RP',si.sy.ShuntZ(1,'Z'))
        ss.AssignSParameters('RM',si.sy.ShuntZ(1,'Z'))
        ss.DocStart().LaTeXTransferMatrix().DocEnd().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ss,'SimulatorXRay041Symbolic2')
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
        sp.AddLine('output X 3 X 4 X 1 X 2')
        tm=sp.TransferMatrices()
        tmsp=tm.SParameters()
        ports=tmsp.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(tmsp,spFileName,spFileName+' incorrect')
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-20e-9,40*80,80e9))
        stepinp=stepin
        stepinm=stepin*-1.
        tmp=si.td.f.TransferMatricesProcessor(tm)
        srs=tmp.ProcessWaveforms([stepinp,stepinm])
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
