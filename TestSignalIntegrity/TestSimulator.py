import unittest
import SignalIntegrity as si
from TestHelpers import *
import numpy as np

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
        # exclude
        # ss.LaTeXEquations().Emit()
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
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
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
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
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
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
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
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
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
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
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
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        sp = si.p.SimulatorParser()
        sp.AddLine('device X 4')
        sp.AddLine('device P 2')
        sp.AddLine('device M 2')
        sp.AddLine('device \\Gamma_P 1')
        sp.AddLine('device \\Gamma_M 1')
        sp.AddLine('voltagesource V1 1')
        sp.AddLine('voltagesource V2 1')
        sp.AddLine('connect V1 1 P 1')
        sp.AddLine('connect V2 1 M 1')
        sp.AddLine('connect P 2 X 1')
        sp.AddLine('connect M 2 X 2')
        sp.AddLine('connect X 3 \\Gamma_P 1')
        sp.AddLine('connect X 4 \\Gamma_M 1')
        sp.AddLine('output X 3 X 4 X 1 X 2')
        ss=si.sd.SimulatorSymbolic(sp.SystemDescription(),size='small')
        ss._AddEq('P='+ss._LaTeXMatrix(si.sy.SeriesZ('Z')))
        ss._AddEq('M='+ss._LaTeXMatrix(si.sy.SeriesZ('Z')))
        ss._AddEq('\\Gamma_P='+ss._LaTeXMatrix(si.sy.ShuntZ(1,'Z')))
        ss._AddEq('\\Gamma_M='+ss._LaTeXMatrix(si.sy.ShuntZ(1,'Z')))
        ss.LaTeXTransferMatrix().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ss,'SimulatorXRay041Symbolic')
    def testSimulatorXRay041Symbolic2(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        sp = si.p.SimulatorParser()
        sp.AddLine('device X 4')
        sp.AddLine('device P 2')
        sp.AddLine('device M 2')
        sp.AddLine('device \\Gamma_P 1')
        sp.AddLine('device \\Gamma_M 1')
        sp.AddLine('voltagesource V1 1')
        sp.AddLine('voltagesource V2 1')
        sp.AddLine('connect V1 1 P 1')
        sp.AddLine('connect V2 1 M 1')
        sp.AddLine('connect P 2 X 1')
        sp.AddLine('connect M 2 X 2')
        sp.AddLine('connect X 3 \\Gamma_P 1')
        sp.AddLine('connect X 4 \\Gamma_M 1')
        sp.AddLine('output X 3 X 4 X 1 X 2')
        ss=si.sd.SimulatorSymbolic(sp.SystemDescription(),size='small')
        ss.AssignSParameters('P',si.sy.SeriesZ('Z'))
        ss.AssignSParameters('M',si.sy.SeriesZ('Z'))
        ss.AssignSParameters('\\Gamma_P',si.sy.ShuntZ(1,'Z'))
        ss.AssignSParameters('\\Gamma_M',si.sy.ShuntZ(1,'Z'))
        ss.LaTeXTransferMatrix().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),ss,'SimulatorXRay041Symbolic2')
    def testSimulatorXRay041Symbolic2Code(self):
        self.WriteCode('TestSimulator.py','testSimulatorXRay041Symbolic2(self)',self.standardHeader)
    def testSimulatorXRaySparqDemo16(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
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
    def testSimulatorTlineFourPort(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        f=si.fd.EvenlySpacedFrequencyList(40.e9,20*40)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device L 4 tline zc 50. td 0.5e-9')
        sp.AddLine('device R 4 tline zc 50. td 0.5e-9')
        sp.AddLine('device S1 2 R 50.')
        sp.AddLine('device S2 1 R 50.')
        sp.AddLine('device R1 1 R 50.')
        sp.AddLine('device R2 1 R 50.')
        sp.AddLine('device RM 1 R 5e6')
        sp.AddLine('voltagesource V1 1')
        sp.AddLine('connect V1 1 S1 1')
        sp.AddLine('connect S1 2 L 1')
        sp.AddLine('connect S2 1 L 3')
        sp.AddLine('connect L 2 R 1')
        sp.AddLine('connect L 4 RM 1')
        sp.AddLine('connect L 4 R 3')
        sp.AddLine('connect R 2 R1 1')
        sp.AddLine('connect R 4 R2 1')
        sp.AddLine('output L 1 R 2 L 3 R 4 L 2 L 4')
        #sp.SystemDescription().Print()
        tm=sp.TransferMatrices()
        tmsp=tm.SParameters()
        ports=tmsp.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(tmsp,spFileName,spFileName)
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-20e-9,40*80,80e9))
        tmp=si.td.f.TransferMatricesProcessor(tm)
        srs=tmp.ProcessWaveforms([stepin])
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-1e-9,11*80,80e9))
        aw=si.td.wf.AdaptedWaveforms([stepin]+srs)
        if False:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(stepin.Times('ns'),stepin.Values(),label='step input')
            plt.plot(aw[1].Times('ns'),aw[1].Values(),label='port 1 response')
            plt.plot(aw[2].Times('ns'),aw[2].Values(),label='port 2 response')
            plt.plot(aw[3].Times('ns'),aw[3].Values(),label='port 3 response')
            plt.plot(aw[4].Times('ns'),aw[4].Values(),label='port 4 response')
            plt.plot(aw[5].Times('ns'),aw[5].Values(),label='mt response')
            plt.plot(aw[6].Times('ns'),aw[6].Values(),label='mb response')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(aw[0],'Waveform_'+fileNameBase+'_0.txt','Waveform_'+fileNameBase+'_0.txt')
        self.CheckWaveformResult(aw[1],'Waveform_'+fileNameBase+'_1.txt','Waveform_'+fileNameBase+'_1.txt')
        self.CheckWaveformResult(aw[2],'Waveform_'+fileNameBase+'_2.txt','Waveform_'+fileNameBase+'_2.txt')
        self.CheckWaveformResult(aw[3],'Waveform_'+fileNameBase+'_3.txt','Waveform_'+fileNameBase+'_3.txt')
        self.CheckWaveformResult(aw[4],'Waveform_'+fileNameBase+'_4.txt','Waveform_'+fileNameBase+'_4.txt')
        self.CheckWaveformResult(aw[5],'Waveform_'+fileNameBase+'_5.txt','Waveform_'+fileNameBase+'_5.txt')
        self.CheckWaveformResult(aw[6],'Waveform_'+fileNameBase+'_6.txt','Waveform_'+fileNameBase+'_6.txt')
    def testSimulatorTlineFourPort2(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        f=si.fd.EvenlySpacedFrequencyList(40.e9,20*40)
        """
        ssnp2 = si.p.SystemSParametersNumericParser(f)
        ssnp2.AddLine('device T 4 tline zc 25. td 0.5e-9')
        ssnp2.AddLine('device G 1 ground')
        ssnp2.AddLine('connect T 3 T 4 G 1')
        ssnp2.AddLine('port 1 T 1 2 T 2')
        ssnp2.SParameters().WriteToFile('tempTLine.s2p')
        """
        sp = si.p.SimulatorNumericParser(f)
        #sp.AddLine('device TL 2 file tempTLine.s2p')
        sp.AddLine('device TL 2 tline zc 25. td 0.5e-9')
        """
        sp.AddLine('device G 1 ground')
        sp.AddLine('connect TL 3 TL 4 G 1')
        """
        sp.AddLine('device TR 2 tline zc 25. td 0.5e-9')
        sp.AddLine('device MM1 4 mixedmode voltage')
        sp.AddLine('device MM2 4 mixedmode voltage')
        sp.AddLine('device S1 2 R 50.')
        sp.AddLine('device S2 1 R 50.')
        sp.AddLine('device R1 1 R 50.')
        sp.AddLine('device R2 1 R 50.')
        sp.AddLine('device O1 1 open')
        sp.AddLine('device O2 1 open')
        sp.AddLine('voltagesource V1 1')
        sp.AddLine('connect V1 1 S1 1')
        sp.AddLine('connect S1 2 MM1 1')
        sp.AddLine('connect S2 1 MM1 2')
        sp.AddLine('connect MM1 3 TL 1')
        sp.AddLine('connect MM1 4 O1 1')
        sp.AddLine('connect TL 2 TR 1')
        sp.AddLine('connect TR 2 MM2 3')
        sp.AddLine('connect MM2 4 O2 1')
        sp.AddLine('connect MM2 2 R1 1')
        sp.AddLine('connect MM2 1 R2 1')
        sp.AddLine('output MM1 1 MM2 1 MM1 2 MM2 2 TL 2')
        # exclude
        #sp.SystemDescription().Print()
        tm=sp.TransferMatrices()
        tmsp=tm.SParameters()
        ports=tmsp.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(tmsp,spFileName,spFileName)
        # include
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-20e-9,40*80,80e9))
        tmp=si.td.f.TransferMatricesProcessor(tm)
        srs=tmp.ProcessWaveforms([stepin])
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-1e-9,11*80,80e9))
        aw=si.td.wf.AdaptedWaveforms([stepin]+srs)
        if False:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(stepin.Times('ns'),stepin.Values(),label='step input')
            plt.plot(aw[1].Times('ns'),aw[1].Values(),label='port 1 response')
            plt.plot(aw[2].Times('ns'),aw[2].Values(),label='port 2 response')
            plt.plot(aw[3].Times('ns'),aw[3].Values(),label='port 3 response')
            plt.plot(aw[4].Times('ns'),aw[4].Values(),label='port 4 response')
            plt.plot(aw[5].Times('ns'),aw[5].Values(),label='mt response')
            plt.legend(loc='upper right')
            plt.show()
        # exclude
        self.CheckWaveformResult(aw[0],'Waveform_'+fileNameBase+'_0.txt','Waveform_'+fileNameBase+'_0.txt')
        self.CheckWaveformResult(aw[1],'Waveform_'+fileNameBase+'_1.txt','Waveform_'+fileNameBase+'_1.txt')
        self.CheckWaveformResult(aw[2],'Waveform_'+fileNameBase+'_2.txt','Waveform_'+fileNameBase+'_2.txt')
        self.CheckWaveformResult(aw[3],'Waveform_'+fileNameBase+'_3.txt','Waveform_'+fileNameBase+'_3.txt')
        self.CheckWaveformResult(aw[4],'Waveform_'+fileNameBase+'_4.txt','Waveform_'+fileNameBase+'_4.txt')
        self.CheckWaveformResult(aw[5],'Waveform_'+fileNameBase+'_5.txt','Waveform_'+fileNameBase+'_5.txt')
#        self.CheckWaveformResult(aw[6],'Waveform_'+fileNameBase+'_6.txt','Waveform_'+fileNameBase+'_6.txt')
    def testSimulatorTlineFourPortModelCheck(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        f=si.fd.EvenlySpacedFrequencyList(40.e9,20*40)
        ssnp1 = si.p.SystemSParametersNumericParser(f)
        ssnp1.AddLine('device T 2 tline zc 25. td 0.5e-9')
        ssnp1.AddLine('port 1 T 1 2 T 2')
        sp1=ssnp1.SParameters()
        ssnp2 = si.p.SystemSParametersNumericParser(f)
        ssnp2.AddLine('device T 4 tline zc 25. td 0.5e-9')
        ssnp2.AddLine('device G 1 ground')
        ssnp2.AddLine('connect T 3 T 4 G 1')
        ssnp2.AddLine('port 1 T 1 2 T 2')
        sp2=ssnp2.SParameters()
        # exclude
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s2p'
        self.CheckSParametersResult(sp1,fileNameBase+'_1.s2p',fileNameBase+'_1.s2p')
        self.CheckSParametersResult(sp2,fileNameBase+'_2.s2p',fileNameBase+'_2.s2p')
        self.assertTrue(self.SParametersAreEqual(sp1,sp2,0.00001),'SimulatorTlineFourPortModelCheck incorrect')
    def testSimulatorTlineFourPortModelCheck2(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        f=si.fd.EvenlySpacedFrequencyList(40.e9,20*40)
        ssnp1 = si.p.SystemSParametersNumericParser(f)
        ssnp1.AddLine('device T 2 tline zc 25. td 0.5e-9')
        ssnp1.AddLine('device MM1 4 mixedmode voltage')
        ssnp1.AddLine('device MM2 4 mixedmode voltage')
        ssnp1.AddLine('device O1 1 open')
        ssnp1.AddLine('device O2 1 open')
        ssnp1.AddLine('connect MM1 3 T 1')
        ssnp1.AddLine('connect MM1 4 O1 1')
        ssnp1.AddLine('connect T 2 MM2 3')
        ssnp1.AddLine('connect MM2 4 O2 1')
        ssnp1.AddLine('port 1 MM1 1 2 MM2 1 3 MM1 2 4 MM2 2')
        sp1=ssnp1.SParameters()
        ssnp2 = si.p.SystemSParametersNumericParser(f)
        ssnp2.AddLine('device T 4 tline zc 25. td 0.5e-9')
        ssnp2.AddLine('device G 1 ground')
        ssnp2.AddLine('connect T 3 T 4 G 1')
        ssnp2.AddLine('device MM1 4 mixedmode voltage')
        ssnp2.AddLine('device MM2 4 mixedmode voltage')
        ssnp2.AddLine('device O1 1 open')
        ssnp2.AddLine('device O2 1 open')
        ssnp2.AddLine('connect MM1 3 T 1')
        ssnp2.AddLine('connect MM1 4 O1 1')
        ssnp2.AddLine('connect T 2 MM2 3')
        ssnp2.AddLine('connect MM2 4 O2 1')
        ssnp2.AddLine('port 1 MM1 1 2 MM2 1 3 MM1 2 4 MM2 2')
        sp2=ssnp2.SParameters()
        # exclude
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s4p'
        self.CheckSParametersResult(sp1,fileNameBase+'_1.s4p',fileNameBase+'_1.s4p')
        self.CheckSParametersResult(sp2,fileNameBase+'_2.s4p',fileNameBase+'_2.s4p')
        self.assertTrue(self.SParametersAreEqual(sp1,sp2,0.00001),'SimulatorTlineFourPortModelCheck2 incorrect')
    def testSimulatorTlineTwoPort(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        f=si.fd.EvenlySpacedFrequencyList(40.e9,20*40)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device T 2 tline zc 25. td 1.0e-9')
        sp.AddLine('device S 2 R 50.')
        sp.AddLine('device R 1 R 50.')
        sp.AddLine('voltagesource V1 1')
        sp.AddLine('connect V1 1 S 1')
        sp.AddLine('connect S 2 T 1')
        sp.AddLine('connect T 2 R 1')
        sp.AddLine('output T 1 T 2')
        tm=sp.TransferMatrices()
        tmsp=tm.SParameters()
        ports=tmsp.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(tmsp,spFileName,spFileName)
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-20e-9,40*80,80e9))
        tmp=si.td.f.TransferMatricesProcessor(tm)
        srs=tmp.ProcessWaveforms([stepin])
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-1e-9,11*80,80e9))
        aw=si.td.wf.AdaptedWaveforms([stepin]+srs)
        if False:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(stepin.Times('ns'),stepin.Values(),label='step input')
            plt.plot(aw[1].Times('ns'),aw[1].Values(),label='port 1 response')
            plt.plot(aw[2].Times('ns'),aw[2].Values(),label='port 2 response')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(aw[0],'Waveform_'+fileNameBase+'_0.txt','Waveform_'+fileNameBase+'_0.txt')
        self.CheckWaveformResult(aw[1],'Waveform_'+fileNameBase+'_1.txt','Waveform_'+fileNameBase+'_1.txt')
        self.CheckWaveformResult(aw[2],'Waveform_'+fileNameBase+'_2.txt','Waveform_'+fileNameBase+'_2.txt')
    def testSimulatorTlineTwoPort2(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        f=si.fd.EvenlySpacedFrequencyList(40.e9,20*40)
        sp = si.p.SimulatorNumericParser(f)
        sp.AddLine('device T 4 tline zc 25. td 1.0e-9')
        sp.AddLine('device G 1 ground')
        sp.AddLine('connect T 3 T 4 G 1')
        sp.AddLine('device S 2 R 50.')
        sp.AddLine('device R 1 R 50.')
        sp.AddLine('voltagesource V1 1')
        sp.AddLine('connect V1 1 S 1')
        sp.AddLine('connect S 2 T 1')
        sp.AddLine('connect T 2 R 1')
        sp.AddLine('output T 1 T 2')
        tm=sp.TransferMatrices()
        tmsp=tm.SParameters()
        ports=tmsp.m_P
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s'+str(ports)+'p'
        self.CheckSParametersResult(tmsp,spFileName,spFileName)
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-20e-9,40*80,80e9))
        tmp=si.td.f.TransferMatricesProcessor(tm)
        srs=tmp.ProcessWaveforms([stepin])
        stepin=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-1e-9,11*80,80e9))
        aw=si.td.wf.AdaptedWaveforms([stepin]+srs)
        if False:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(stepin.Times('ns'),stepin.Values(),label='step input')
            plt.plot(aw[1].Times('ns'),aw[1].Values(),label='port 1 response')
            plt.plot(aw[2].Times('ns'),aw[2].Values(),label='port 2 response')
            plt.legend(loc='upper right')
            plt.show()
        self.CheckWaveformResult(aw[0],'Waveform_'+fileNameBase+'_0.txt','Waveform_'+fileNameBase+'_0.txt')
        self.CheckWaveformResult(aw[1],'Waveform_'+fileNameBase+'_1.txt','Waveform_'+fileNameBase+'_1.txt')
        self.CheckWaveformResult(aw[2],'Waveform_'+fileNameBase+'_2.txt','Waveform_'+fileNameBase+'_2.txt')
    def testDiabolicalSymbolic(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        f=si.fd.EvenlySpacedFrequencyList(40.e9,20*40)
        ssnp1 = si.p.SystemDescriptionParser()
        ssnp1.AddLine('device O1 1 open')
        ssnp1.AddLine('device O2 1 open')
        ssnp1.AddLine('device T 2 thru')
        ssnp1.AddLine('device O3 1 open')
        ssnp1.AddLine('device O4 1 open')
        ssnp1.AddLine('connect T 1 O3 1')
        ssnp1.AddLine('connect T 2 O4 1')
        ssnp1.AddLine('port 1 O1 1 2 O2 1')
        sps=si.sd.SystemSParametersSymbolic(ssnp1.SystemDescription())
        sps.LaTeXSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),sps,self.id())
    def testDiabolicalNumeric(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        f=si.fd.EvenlySpacedFrequencyList(40.e9,20*40)
        ssp = si.p.SystemSParametersNumericParser(f)
        ssp.AddLine('device O1 1 open')
        ssp.AddLine('device O2 1 open')
        ssp.AddLine('device T 2 thru')
        ssp.AddLine('device O3 1 open')
        ssp.AddLine('device O4 1 open')
        ssp.AddLine('connect T 1 O3 1')
        ssp.AddLine('connect T 2 O4 1')
        ssp.AddLine('port 1 O1 1 2 O2 1')
        sp=ssp.SParameters()
        # exclude
        fileNameBase = self.id().split('.')[2].replace('test','')
        spFileName = fileNameBase +'.s2p'
        self.CheckSParametersResult(sp,spFileName,spFileName)
    def testDiabolicalSymbolic2(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        ssnp1 = si.p.SystemDescriptionParser()
        ssnp1.AddLine('device T1 2 thru')
        ssnp1.AddLine('device T2 2 thru')
        ssnp1.AddLine('device O3 1 open')
        ssnp1.AddLine('device O4 1 open')
        ssnp1.AddLine('connect O3 1 O4 1')
        ssnp1.AddLine('port 1 T1 1 2 T2 2')
        ssnp1.AddLine('connect T1 2 T2 1')
        sd=ssnp1.SystemDescription()
        sd.Print()
        sps=si.sd.SystemSParametersSymbolic(sd)
        sps.Clear().DocStart().LaTeXSystemEquation().LaTeXSolution().DocEnd().Emit().Clear()
        sps.LaTeXSolution().Emit()
        # exclude
        self.CheckSymbolicResult(self.id(),sps,self.id())
    def testDiabolicalNumeric2(self):
        # exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # include
        f=si.fd.EvenlySpacedFrequencyList(40.e9,20*40)
        ssp = si.p.SystemSParametersNumericParser(f)
        ssp.AddLine('device T1 2 thru')
        ssp.AddLine('device T2 2 thru')
        ssp.AddLine('device O3 1 open')
        ssp.AddLine('device O4 1 open')
        ssp.AddLine('connect O3 1 O4 1')
        ssp.AddLine('port 1 T1 1 2 T2 2')
        ssp.AddLine('connect T1 2 T2 1')
        try:
            sp=ssp.SParameters()
            fileNameBase = self.id().split('.')[2].replace('test','')
            spFileName = fileNameBase +'.s2p'
            self.CheckSParametersResult(sp,spFileName,spFileName)
        except np.linalg.linalg.LinAlgError:
            pass
        # exclude

if __name__ == "__main__":
    unittest.main()
