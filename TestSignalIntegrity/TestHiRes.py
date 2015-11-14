import unittest
import SignalIntegrity as si
from TestHelpers import *
import numpy as np
import math

class TestSimulator(unittest.TestCase,RoutineWriterTesterHelper,ResponseTesterHelper,SourcesTesterHelper):
    def __init__(self, methodName='runTest'):
        RoutineWriterTesterHelper.__init__(self)
        unittest.TestCase.__init__(self,methodName)


    def testHiRes2(self):
        # pragma: exclude
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        # pragma: include
        Fsa=40e9    # assumed analog sample rate
        NoiseBandwidth=10e9
        snrdB = 42.5
        #snrdB = 100

        # Make a filter with bandwidth equal to the noise bandwidth from 6 GHz filter s-parameters
        OriginalFilterBandwidth = 6e9
        sp = si.sp.File('filter.s2p')
        sp.m_f=si.fd.EvenlySpacedFrequencyList(NoiseBandwidth/OriginalFilterBandwidth*sp.f()[-1],len(sp.f())-1)
        sp.WriteToFile('filterNBW.s2p')
        del OriginalFilterBandwidth
        del sp
        del NoiseBandwidth

        # make a simulator system to filter the noise according to the noise bandwidth
        snp=si.p.SimulatorNumericParser(si.fd.EvenlySpacedFrequencyList(Fsa/2,2000))
        snp.AddLine('device F 2 file filterNBW.s2p')
        snp.AddLine('device S 2 R 50.')
        snp.AddLine('device R 1 R 50.')
        snp.AddLine('voltagesource V 1')
        snp.AddLine('connect V 1 S 1')
        snp.AddLine('connect S 2 F 1')
        snp.AddLine('connect F 2 R 1')
        snp.AddLine('output R 1')
        tmp=si.td.f.TransferMatricesProcessor(snp.TransferMatrices())
        del snp

        # make the analog waveforms
        K=2000
        KaddBothSides=8000
        fin=100e6
        vdiv=50e-3
        Amplitude=4*vdiv
        sigmafe=4.*Amplitude/math.sqrt(2.)*math.pow(10.,-snrdB/20.)
        td=si.td.wf.TimeDescriptor(-KaddBothSides/Fsa,K+KaddBothSides*2,Fsa)
        wfa=si.td.wf.Waveform(td,[Amplitude*math.sin(2.*math.pi*fin*t) for t in td.Times()])
        wfna=si.td.wf.Waveform(td,np.random.normal(0,sigmafe,td.N).tolist())
        del KaddBothSides
        del fin
        del vdiv
        del td
        del t

        # wfa and wfna are analog and noise waveforms
        # process these waveforms through the noise filter
        wfa=tmp.ProcessWaveforms([wfa*2.])[0]
        wfna=tmp.ProcessWaveforms([wfna*2.])[0]
        del tmp

        # now we need to measure the noise waveform and adjust the noise to match
        # what is stated
        sigmafeActual =np.std(wfna.Values())
        wfna=si.td.wf.Waveform(wfna.TimeDescriptor(),[wfna.Values()[k]*sigmafe/sigmafeActual for k in range(len(wfna.Values()))])
        sigmafeActual=np.std(wfna.Values())
        del sigmafeActual
        del k

        # wfa and wfna are analog waveforms
        # wfa is the analog input waveform
        # wfna is an analog noise waveform that meets the noise characteristics
        # measured without a hardware filter

        # adapt both waveforms to a desired scale
        #td=si.td.wf.TimeDescriptor(0,K,Fsa)
        #wfna=wfna.Adapt(td)
        #wfa=wfa.Adapt(td)

        HWFilterBandwidth = 4e9 # what we want the bandwidth to be

        # 6 GHz filter s-parameters
        OriginalFilterBandwidth = 6e9
        sp = si.sp.File('filter.s2p')
        sp.m_f=si.fd.EvenlySpacedFrequencyList(HWFilterBandwidth/OriginalFilterBandwidth*sp.f()[-1],len(sp.f())-1)
        sp.WriteToFile('filterBWL.s2p')
        del OriginalFilterBandwidth
        del sp
        del HWFilterBandwidth

        # make a simulator system to filter the noise according to the noise bandwidth
        snp=si.p.SimulatorNumericParser(si.fd.EvenlySpacedFrequencyList(Fsa/2,2000))
        snp.AddLine('device F 2 file filterBWL.s2p')
        snp.AddLine('device S 2 R 50.')
        snp.AddLine('device R 1 R 50.')
        snp.AddLine('voltagesource V 1')
        snp.AddLine('connect V 1 S 1')
        snp.AddLine('connect S 2 F 1')
        snp.AddLine('connect F 2 R 1')
        snp.AddLine('output R 1')
        tmp=si.td.f.TransferMatricesProcessor(snp.TransferMatrices())
        del snp

        wfnafe=tmp.ProcessWaveforms([wfna*2.])[0]
        wf=tmp.ProcessWaveforms([wfa*2.])[0]
        del tmp

        # wfnafe and wf are analog waveforms
        # wfnafe is now the noise waveform that has been filtered by a hardware
        # filter
        # wf is the analog input waveform filtered by the hardware filter

        Fs=40e9 # system sample rate

        snrdBadc=46
        #snrdBadc=90

        sigmaadc=4.*Amplitude/math.sqrt(2.)*math.pow(10.,-snrdBadc/20.)
        wfnadc=si.td.wf.Waveform(wfnafe.TimeDescriptor(),np.random.normal(0,sigmaadc,wfnafe.TimeDescriptor().N).tolist())
        sigmaadcActual = np.std(wfnadc.Values())
        wfnadc=si.td.wf.Waveform(wfnafe.TimeDescriptor(),[wfnadc.Values()[k]*sigmaadc/sigmaadcActual for k in range(len(wfnadc.Values()))])
        sigmaadcActual = np.std(wfnadc.Values())
        del sigmaadc
        del sigmaadcActual
        del k

        # now we have wf, wfnafe, and wfnadc
        # these are the analog waveform, the analog front-end noise and
        # the adc noise (assumed white)

        wfn=wfnafe+wfnadc
        wfs=wf+wfn

        # form the decimated waveforms
        VILV=4

        wfd = [si.td.wf.Waveform(si.td.wf.TimeDescriptor(wf.Times()[d],len(wf)/VILV,wf.TimeDescriptor().Fs/VILV),[wf.Values()[kd*VILV+d] for kd in range(len(wf)/VILV)]) for d in range(VILV)]
        wfnd = [si.td.wf.Waveform(si.td.wf.TimeDescriptor(wfn.Times()[d],len(wfn)/VILV,wfn.TimeDescriptor().Fs/VILV),[wfn.Values()[kd*VILV+d] for kd in range(len(wfn)/VILV)]) for d in range(VILV)]
        wfsd = [si.td.wf.Waveform(si.td.wf.TimeDescriptor(wfs.Times()[d],len(wfs)/VILV,wfs.TimeDescriptor().Fs/VILV),[wfs.Values()[kd*VILV+d] for kd in range(len(wfs)/VILV)]) for d in range(VILV)]

        wfavg=wfd[0]*(1./VILV)
        wfnavg=wfnd[0]*(1./VILV)
        wfsavg=wfsd[0]*(1./VILV)
        for d in range(1,VILV):
            wfavg=wfavg+wfd[d]*(1./VILV)
            wfnavg=wfnavg+wfnd[d]*(1./VILV)
            wfsavg=wfsavg+wfsd[d]*(1./VILV)

        us=si.td.f.InterpolatorSinX(VILV)

        wfavgus = us.FilterWaveform(wfavg)
        wfnavgus = us.FilterWaveform(wfnavg)
        wfsavgus = us.FilterWaveform(wfsavg)

        #adapt all of the waveform results
        wf=wf.Adapt(si.td.wf.TimeDescriptor(0.,K/Fs*wf.TimeDescriptor().Fs,wf.TimeDescriptor().Fs))
        wfs=wfs.Adapt(si.td.wf.TimeDescriptor(0.,K/Fs*wfs.TimeDescriptor().Fs,wfs.TimeDescriptor().Fs))
        wfsavgus=wfsavgus.Adapt(si.td.wf.TimeDescriptor(0.,K/Fs*wfsavgus.TimeDescriptor().Fs,wfsavgus.TimeDescriptor().Fs))

        wfnavgus=wfnavgus.Adapt(si.td.wf.TimeDescriptor(0.,K/Fs*wfnavgus.TimeDescriptor().Fs,wfnavgus.TimeDescriptor().Fs))
        wfn=wfn.Adapt(si.td.wf.TimeDescriptor(0.,K/Fs*wfn.TimeDescriptor().Fs,wfn.TimeDescriptor().Fs))

        if True:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(wf.Times('ns'),wf.Values(),label='input waveform')
            plt.plot(wfs.Times('ns'),wfs.Values(),label='acquired at 40 GS/s input')
            #for d in range(VILV):
            #    plt.plot(wfad[d].Times('ns'),wfad[d].Values(),label='10 GS/s stream '+str(d))
            #plt.plot(wfavg.Times('ns'),wfavg.Values(),label='averaged 10 GS/s streams')
            plt.plot(wfsavgus.Times('ns'),wfsavgus.Values(),label='upsampled averaged streams')
            plt.legend(loc='upper right')
            plt.show()

        if True:
            import matplotlib.pyplot as plt
            plt.clf()
            plt.xlabel('time (ns)')
            plt.ylabel('amplitude')
            plt.plot(wfn.Times('ns'),wfn.Values(),label='noise acquired at 40 GS/s input')
            plt.plot(wfnavgus.Times('ns'),wfnavgus.Values(),label='noise after averaging and upsampling')
            plt.legend(loc='upper right')
            plt.show()

        sigmai=np.std(wfn.Values())
        snri=20*math.log10(4.*Amplitude/math.sqrt(2.)/sigmai)
        enobi=(snri-1.76)/6.02
        print snri,enobi
        sigmaf=np.std(wfnavgus.Values())
        snrf=20*math.log10(4.*Amplitude/math.sqrt(2.)/sigmaf)
        enobf=(snrf-1.76)/6.02
        print snrf,enobf

if __name__ == "__main__":
    unittest.main()