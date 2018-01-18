import unittest

import SignalIntegrity as si
from numpy import linalg
from numpy import array
from numpy import matrix
import math

class TestWavelets(unittest.TestCase):
    def testDWT(self):
        K=16
        x=[k for k in range(K)]
        w=si.wl.WaveletDaubechies4()
        X=w.DWT(x)
        XM=[13.038,29.389,-10.574,1.812,-7.660,-0.000,-0.000,0.732,-5.657,-0.000,-0.000,-0.000,0.000,0.000,-1.776e-15,-1.776e-15]
        difference = linalg.norm([XM[k]-X[k] for k in range(K)])
        self.assertTrue(difference<1e-3,'DWT incorrect')
    def testIDWT(self):
        K=16
        x=[k for k in range(K)]
        w=si.wl.WaveletDaubechies4()
        X=w.DWT(x)
        xc=w.IDWT(X)
        difference = linalg.norm([x[k]-xc[k] for k in range(K)])
        self.assertTrue(difference<1e-3,'DWT incorrect')
    def testDWTNoiseShapeCalc(self):
        K=pow(2,8)
        h=si.wl.WaveletDaubechies4().h
        N=K/2
        E=[math.sqrt(2.*(1-math.cos(math.pi*n/N))) for n in range(N+1)]
        TS=si.wl.WaveletDenoiser.DWTNoiseShapeCalc(E,h)
        TSCorrect=[0.749999990782253, 1.6677079888241493, 2.8394541449097455, 4.898979445760824, 8.36660021284939, 13.711309143434791, 20.099751216152544]
        for (tsc,ts) in zip(TSCorrect,TS):
            self.assertAlmostEquals(tsc, ts, 8, 'wavelet threshold incorrect')
    def testDerivativeThresholdCalc(self):
        K=pow(2,10)
        Fs=1.
        sigma=0.1
        trys=10
        for _ in range(trys):
            nwf=si.td.wf.NoiseWaveform(si.td.wf.TimeDescriptor(0,K+1,Fs),sigma)
            dnwf=nwf.Derivative()
            w=si.wl.WaveletDaubechies4()
            X=w.DWT(dnwf.Values())
            T=[t*5 for t in si.wl.WaveletDenoiser.DerivativeThresholdCalc(X,w.h,30)]
    #         import matplotlib.pyplot as plt
    #         plt.clf()
    #         plt.title('denoising')
    #         plt.loglog(dnwf.Times(),[abs(x) for x in X],label='dwt')
    #         plt.loglog(dnwf.Times(),T,label='threshold')
    #         plt.xlabel('samples')
    #         plt.ylabel('amplitude')
    #         plt.legend(loc='upper right')
    #         plt.grid(True)
    #         plt.show()
            dnwfDenoised=si.wl.WaveletDenoiser.DenoisedWaveform(dnwf, 30, 5)
            wfDenoised=dnwfDenoised.Integral()*dnwf.TimeDescriptor().Fs
            wfNoisy=nwf
    #         plt.clf()
    #         plt.title('denoising')
    #         plt.plot(wfNoisy.Times(),wfNoisy.Values(),label='noisy')
    #         plt.plot(wfDenoised.Times(),wfDenoised.Values(),label='denoised')
    #         plt.xlabel('time')
    #         plt.ylabel('amplitude')
    #         plt.legend(loc='upper right')
    #         plt.grid(True)
    #         plt.show()
            if all([x==0. for x in wfDenoised.Values()]):
                return # test passed
        self.fail('wavelet denoising didnt work')
    def testDenoiseImpulsive(self):
        K=pow(2,10)
        Fs=1.
        sigma=0.1
        trys=10
        for _ in range(trys):
            nwf=si.td.wf.NoiseWaveform(si.td.wf.TimeDescriptor(0,K,Fs),sigma)
            w=si.wl.WaveletDaubechies4()
            X=w.DWT(nwf.Values())
            T=[t*5 for t in si.wl.WaveletDenoiser.DerivativeThresholdCalc(X,w.h,30,isDerivative=False)]
            import matplotlib.pyplot as plt
    #         plt.clf()
    #         plt.title('denoising')
    #         plt.loglog(nwf.Times(),[abs(x) for x in X],label='dwt')
    #         plt.loglog(nwf.Times(),T,label='threshold')
    #         plt.xlabel('samples')
    #         plt.ylabel('amplitude')
    #         plt.legend(loc='upper right')
    #         plt.grid(True)
    #         plt.show()
            wfDenoised=si.wl.WaveletDenoiser.DenoisedWaveform(nwf, 30, 5,isDerivative=False)
            wfNoisy=nwf
    #         plt.clf()
    #         plt.title('denoising')
    #         plt.plot(wfNoisy.Times(),wfNoisy.Values(),label='noisy')
    #         plt.plot(wfDenoised.Times(),wfDenoised.Values(),label='denoised')
    #         plt.xlabel('time')
    #         plt.ylabel('amplitude')
    #         plt.legend(loc='upper right')
    #         plt.grid(True)
    #         plt.show()
            if all([x==0. for x in wfDenoised.Values()]):
                return # test passed
        self.fail('wavelet denoising didnt work')

    def testDerivativeThresholdCalcHaar(self):
        K=pow(2,10)
        Fs=1.
        sigma=0.1
        trys=10
        for _ in range(trys):
            nwf=si.td.wf.NoiseWaveform(si.td.wf.TimeDescriptor(0,K+1,Fs),sigma)
            dnwf=nwf.Derivative()
            w=si.wl.WaveletHaar()
            X=w.DWT(dnwf.Values())
            T=[t*5 for t in si.wl.WaveletDenoiser.DerivativeThresholdCalc(X,w.h,30)]
#             import matplotlib.pyplot as plt
#             plt.clf()
#             plt.title('denoising')
#             plt.loglog(dnwf.Times(),[abs(x) for x in X],label='dwt')
#             plt.loglog(dnwf.Times(),T,label='threshold')
#             plt.xlabel('samples')
#             plt.ylabel('amplitude')
#             plt.legend(loc='upper right')
#             plt.grid(True)
#             plt.show()
            if all([abs(x) < t for (x,t) in zip(X,T)]):
                return # test passed
        self.fail('wavelet denoising didnt work')
    def testIntegralDerivative(self):
        stepwf=si.td.wf.StepWaveform(si.td.wf.TimeDescriptor(-5.5e-9,100,1e9)).OffsetBy(1.0)
        derivwf=stepwf.Derivative(scale=False,c=stepwf[0])
        integwf=derivwf.Integral(scale=False,c=stepwf[0])
        self.assertTrue(stepwf==integwf,'integral of derivative not same')
#         import matplotlib.pyplot as plt
#         plt.clf()
#         plt.title('compare')
#         plt.plot(stepwf.Times('ns'),stepwf.Values(),label='original step')
#         plt.plot(derivwf.Times('ns'),derivwf.Values(),label='derivative')
#         plt.plot(integwf.Times('ns'),integwf.Values(),label='integral of derivative')        
#         plt.xlabel('time (ns)')
#         plt.ylabel('amplitude')
#         plt.legend(loc='upper right')
#         plt.grid(True)
#         plt.show()
