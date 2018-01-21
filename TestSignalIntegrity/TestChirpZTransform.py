import unittest
import SignalIntegrity as si
import os
from TestHelpers import SParameterCompareHelper

class TestChirpZTransform(unittest.TestCase,SParameterCompareHelper):
    def testCZTResampleSame(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        sf2=sf.Resample(si.fd.EvenlySpacedFrequencyList(20.e9,200))
        sf2.WriteToFile('TestDutCmp.s4p')
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testCZTResampleHigherFreq(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        sf2=sf.Resample(si.fd.EvenlySpacedFrequencyList(40.e9,400)).Resample(si.fd.EvenlySpacedFrequencyList(20.e9,200))
        sf2.WriteToFile('TestDutCmp.s4p')
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testCZTResampleHigherRes(self):
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        sf2=sf.Resample(si.fd.EvenlySpacedFrequencyList(20.e9,400)).Resample(si.fd.EvenlySpacedFrequencyList(20.e9,200))
        sf2.WriteToFile('TestDutCmp.s4p')
        os.remove('TestDutCmp.s4p')
        self.assertTrue(self.SParametersAreEqual(sf2,sf,0.001),self.id()+'result not same')
    def testNewResamplerSpline(self):
        Fe=20.e9
        Np=400
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        sf=si.sp.SParameterFile('TestDut.s4p',50.)
        f2=[Fe/Np*n for n in range(Np+1)]
        sf2=sf.Resample(f2)
        sf3=sf.Resample(si.fd.EvenlySpacedFrequencyList(Fe,Np))
        self.assertTrue(self.SParametersAreEqual(sf2,sf3,0.001),self.id()+'result not same')
    def testFrequencyContentCZT(self):
        td=si.td.wf.TimeDescriptor(-1e-9,1000,20e9)
        wf=si.td.wf.PulseWaveform(td,PulseWidth=1e9)
        fd=td.FrequencyList()
        fc1=wf.FrequencyContent()
        fc2=wf.FrequencyContent(fd)
        self.assertEqual(fc1, fc2, 'frequency content not correct')
    def testFrequencyContentNormalizationDFTEven(self):
        td=si.td.wf.TimeDescriptor(-1e-9,10,10e9)
        fd=td.FrequencyList()
        for n in range(fd.N+1):
            wf=si.td.wf.SineWaveform(td,Amplitude=5.0,Frequency=fd[n],Phase=90.)
            fc=wf.FrequencyContent()
            self.assertAlmostEqual(fc.Values('mag')[n],5.)
            wf2=fc.Waveform()
            self.assertEquals(wf,wf2,'waveform not equal from frequency content')
    def testFrequencyContentNormalizationCZTEven(self):
        td=si.td.wf.TimeDescriptor(-1e-9,10,10e9)
        fd=td.FrequencyList()
        for n in range(fd.N+1):
            wf=si.td.wf.SineWaveform(td,Frequency=fd[n],Phase=90.)
            fc=wf.FrequencyContent()
            self.assertAlmostEqual(fc.Values('mag')[n],1.)
            wf2=fc.Waveform()
            self.assertEquals(wf,wf2,'waveform not equal from frequency content')
    def testFrequencyContentNormalizationDFTOdd(self):
        td=si.td.wf.TimeDescriptor(-1e-9,11,10e9)
        fd=td.FrequencyList()
        for n in range(fd.N+1):
            wf=si.td.wf.SineWaveform(td,Amplitude=5.0,Frequency=fd[n],Phase=90.)
            fc=wf.FrequencyContent()
            self.assertAlmostEqual(fc.Values('mag')[n],5.)
            wf2=fc.Waveform()
            self.assertEquals(wf,wf2,'waveform not equal from frequency content')
    def testFrequencyContentNormalizationCZTOdd(self):
        td=si.td.wf.TimeDescriptor(-1e-9,11,10e9)
        fd=td.FrequencyList()
        for n in range(fd.N+1):
            wf=si.td.wf.SineWaveform(td,Frequency=fd[n],Phase=90.)
            fc=wf.FrequencyContent()
            self.assertAlmostEqual(fc.Values('mag')[n],1.)
            wf2=fc.Waveform()
            self.assertEquals(wf,wf2,'waveform not equal from frequency content')
    def testFrequencyContentStepEven(self):
        td=si.td.wf.TimeDescriptor(-1e-9,10,1e9)
        wf=si.td.wf.StepWaveform(td)
        fc=wf.FrequencyContent()
        wf2=fc.Waveform()
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('step magnitude')
#         resp=fc
#         plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label='step')
#         plt.xlabel('frequency (GHz)')
#         plt.ylabel('magnitude (dB)')
#         plt.legend(loc='upper right')
#         plt.grid(True)
#         plt.show()
    def testFrequencyContentStepOdd(self):
        td=si.td.wf.TimeDescriptor(-1e-9,11,1e9)
        wf=si.td.wf.StepWaveform(td)
        fc=wf.FrequencyContent()
        wf2=fc.Waveform()
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('step magnitude')
#         resp=fc
#         plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label='step')
#         plt.xlabel('frequency (GHz)')
#         plt.ylabel('magnitude (dB)')
#         plt.legend(loc='upper right')
#         plt.grid(True)
#         plt.show()
    def testFrequencyContentImpulse(self):
        td=si.td.wf.TimeDescriptor(-1e-9,10,1e9)
        wf=si.td.wf.Waveform(td)
        wf[2]=1.0
        fc=wf.FrequencyContent()
        wf2=fc.Waveform()
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('impulse magnitude')
#         resp=fc
#         plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label='step')
#         plt.xlabel('frequency (GHz)')
#         plt.ylabel('magnitude (dB)')
#         plt.legend(loc='upper right')
#         plt.grid(True)
#         plt.show()
    def testSumOfSines(self):
        td=si.td.wf.TimeDescriptor(-1e-9,10,10e9)
        fd=td.FrequencyList()
        wf=si.td.wf.Waveform(td)
        for n in range(fd.N+1):
            wf=wf+si.td.wf.SineWaveform(td,Frequency=fd[n],Phase=90.)
        fc=wf.FrequencyContent()
        wf2=fc.Waveform()
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('sum of sines')
#         plt.plot(wf.Times('ns'),wf.Values(),label='sum')
#         plt.xlabel('time (ns)')
#         plt.ylabel('amplitude')
#         plt.legend(loc='upper right')
#         plt.grid(True)
#         plt.show()
    def testSumOfSines2(self):
        td=si.td.wf.TimeDescriptor(-1e-9,10,10e9)
        fd=td.FrequencyList()
        wf=si.td.wf.Waveform(td)
        for n in range(fd.N+1):
            amplitude = (1. if 0 < n < fd.N else 0.5)*2./td.K
            wf=wf+si.td.wf.SineWaveform(td,Amplitude=amplitude,Frequency=fd[n],Phase=90.)
        fc=wf.FrequencyContent()
        wf2=fc.Waveform()
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
        wfImpulse=si.td.wf.PulseWaveform(td,StartTime=-1.05e-9,PulseWidth=100e-12)
        self.assertEquals(wf2,wfImpulse,'not equal to impulse')
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('sum of sines scaled')
#         plt.plot(wf.Times('ns'),wf.Values(),label='sum')
#         plt.plot(wf2.Times('ns'),wf2.Values(),label='from content')
#         plt.plot(wfImpulse.Times('ns'),wfImpulse.Values(),label='impulse')
#         plt.xlabel('time (ns)')
#         plt.ylabel('amplitude')
#         plt.legend(loc='upper right')
#         plt.grid(True)
#         plt.show()
    def testSumOfSines3(self):
        td=si.td.wf.TimeDescriptor(-1e-9,10,10e9)
        fd=td.FrequencyList()
        wf=sum([si.td.wf.SineWaveform(td,Frequency=fd[n],Phase=90.) for n in range(fd.N+1)])
        fc=wf.FrequencyContent()
        wf2=fc.Waveform()
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
    def testSumOfSines4(self):
        td=si.td.wf.TimeDescriptor(-1e-9,10,10e9)
        fd=td.FrequencyList()
        wf=si.td.wf.Waveform(td)
        for n in range(fd.N+1):
            wf=si.td.wf.SineWaveform(td,Frequency=fd[n],Phase=90.).__radd__(wf)
        fc=wf.FrequencyContent()
        wf2=fc.Waveform()
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
    def testSumOfSinesByDefinition(self):
        td=si.td.wf.TimeDescriptor(-1e-9,10,10e9)
        fd=td.FrequencyList()
        wf=si.td.wf.Waveform(td)
        for n in range(fd.N+1):
            amplitude = (1. if 0 < n < fd.N else 0.5)*2./td.K
            wf=wf+si.td.wf.SineWaveform(td,Amplitude=amplitude,Frequency=fd[n],Phase=90.)
        fc=wf.FrequencyContent()
        wf2=fc.WaveformFromDefinition()
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
        wfImpulse=si.td.wf.PulseWaveform(td,StartTime=-1.05e-9,PulseWidth=100e-12)
        self.assertEquals(wf2,wfImpulse,'not equal to impulse')
    def testNoiseWaveform(self):
        td=si.td.wf.TimeDescriptor(-1e-9,100,10e9)
        wf=si.td.wf.NoiseWaveform(td,.1)
        fc=wf.FrequencyContent()
        wf2=fc.Waveform(td)
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('impulse magnitude')
#         resp=fc
#         plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label='noise')
#         plt.xlabel('frequency (GHz)')
#         plt.ylabel('magnitude (dB)')
#         plt.legend(loc='upper right')
#         plt.grid(True)
#         plt.show()
    def testNoiseWaveformByDefinition(self):
        td=si.td.wf.TimeDescriptor(-1e-9,100,10e9)
        wf=si.td.wf.NoiseWaveform(td,.1)
        fc=wf.FrequencyContent()
        wf2=fc.WaveformFromDefinition(td)
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('impulse magnitude')
#         resp=fc
#         plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label='noise')
#         plt.xlabel('frequency (GHz)')
#         plt.ylabel('magnitude (dB)')
#         plt.legend(loc='upper right')
#         plt.grid(True)
    def testNoiseWaveformByDefinitionOdd(self):
        td=si.td.wf.TimeDescriptor(-1e-9,11,10e9)
        wf=si.td.wf.NoiseWaveform(td,1)
        fc=wf.FrequencyContent()
        wf2=fc.WaveformFromDefinition(td)
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('impulse magnitude')
#         resp=fc
#         plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label='noise')
#         plt.xlabel('frequency (GHz)')
#         plt.ylabel('magnitude (dB)')
#         plt.legend(loc='upper right')
#         plt.grid(True)
#         plt.show()
    def testDCWaveform(self):
        td=si.td.wf.TimeDescriptor(-1e-9,100,10e9)
        fd=td.FrequencyList()
        wf=si.td.wf.Waveform(td,.1)
        fc=wf.FrequencyContent()
        wf2=fc.Waveform()
        self.assertEquals(wf,wf2,'waveform not equal from frequency content')
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('impulse magnitude')
#         resp=fc
#         plt.plot(resp.Frequencies('GHz'),resp.Values('dB'),label='noise')
#         plt.xlabel('frequency (GHz)')
#         plt.ylabel('magnitude (dB)')
#         plt.legend(loc='upper right')
#         plt.grid(True)
#         plt.show()



if __name__ == '__main__':
    unittest.main()