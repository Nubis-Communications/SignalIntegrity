import unittest

import SignalIntegrity as si

import math
import cmath

class TestDescriptors(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
    def testTimesRaw(self):
        K=100
        HO=-1e-9
        Fs=20e9
        td=si.td.wf.TimeDescriptor(HO,K,Fs)
        self.assertEqual(td.Times(), [HO+float(k)/Fs for k in range(K)], 'times incorrect')
    def testTimesps(self):
        K=100
        HO=-1e-9
        Fs=20e9
        td=si.td.wf.TimeDescriptor(HO,K,Fs)
        self.assertEqual(td.Times('ps'), [(HO+float(k)/Fs)/1e-12 for k in range(K)], 'times ps incorrect')
    def testTimesns(self):
        K=100
        HO=-1e-9
        Fs=20e9
        td=si.td.wf.TimeDescriptor(HO,K,Fs)
        self.assertEqual(td.Times('ns'), [(HO+float(k)/Fs)/1e-9 for k in range(K)], 'times ps incorrect')
    def testTimesus(self):
        K=100
        HO=-1e-9
        Fs=20e9
        td=si.td.wf.TimeDescriptor(HO,K,Fs)
        self.assertEqual(td.Times('us'), [(HO+float(k)/Fs)/1e-6 for k in range(K)], 'times ps incorrect')
    def testTimesms(self):
        K=100
        HO=-1e-9
        Fs=20e9
        td=si.td.wf.TimeDescriptor(HO,K,Fs)
        self.assertEqual(td.Times('ms'), [(HO+float(k)/Fs)/1e-3 for k in range(K)], 'times ps incorrect')
    def testTimesFloat(self):
        K=100
        HO=-1e-9
        Fs=20e9
        td=si.td.wf.TimeDescriptor(HO,K,Fs)
        self.assertEqual(td.Times(32.), [(HO+float(k)/Fs)/32. for k in range(K)], 'times ps incorrect')
    def testWaveformDividedByFilter(self):
        K=100
        HO=-1e-9
        Fs=20e9
        output=si.td.wf.TimeDescriptor(HO,K,Fs)
        filter=si.td.f.FilterDescriptor(10,20,20)
        input=output/filter
        self.assertEqual(input*filter, output, 'waveform/filter incorrect')
    def testTimeDescriptorPrint(self):
        K=100
        HO=-1e-9
        Fs=20e9
        td=si.td.wf.TimeDescriptor(HO,K,Fs)
        td.Print()
    def testFilterAfter(self):
        filter1=si.td.f.FilterDescriptor(10,20,20)
        filter2=si.td.f.FilterDescriptor(0.5,30,90)
        res=filter1*filter2
        filter3=filter1.After(filter2)
        reseq=filter2*filter3
        self.assertEqual(res, reseq, 'filter after incorrect')
    def testFilterBefore(self):
        filter1=si.td.f.FilterDescriptor(10,20,20)
        filter2=si.td.f.FilterDescriptor(0.5,30,90)
        res=filter1*filter2
        filter3=filter2.Before(filter1)
        reseq=filter3*filter1
        self.assertEqual(res, reseq, 'filter before incorrect')
    def testFilterDescriptorPrint(self):
        filter=si.td.f.FilterDescriptor(10,20,20).Print()
    def testFrequencyContentSine(self):
        wf=si.td.wf.SineWaveform(si.td.wf.TimeDescriptor(0.,200,2e6),1,30e3,30.)
        fc=wf.FrequencyContent()
        self.assertEqual(fc.Frequencies('kHz')[3],30.,'sine frequency incorrect')
        self.assertEqual(abs(fc[3]), 1., 'sine amplitude incorrect')
        self.assertAlmostEqual(cmath.phase(fc[3])*180./math.pi + 90., 30.,10, 'sine phase incorrect')
    def testFrequencyContentSineAdjustTime(self):
        wf=si.td.wf.SineWaveform(si.td.wf.TimeDescriptor(0.,200,2e6),1,30e3,30.)
        fc=wf.FrequencyContent()
        self.assertEqual(fc.Frequencies('kHz')[3],30.,'sine frequency incorrect')
        self.assertEqual(abs(fc[3]), 1., 'sine amplitude incorrect')
        self.assertAlmostEqual(cmath.phase(fc[3])*180./math.pi + 90., 30.,10, 'sine phase incorrect')

if __name__ == '__main__':
    unittest.main()
        
        
