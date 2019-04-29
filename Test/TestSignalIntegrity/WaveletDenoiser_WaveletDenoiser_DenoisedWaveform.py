class WaveletDenoiser(object):
    def DenoisedWaveform(wf,pct=30.,mult=5.,isDerivative=True):
        w=WaveletDenoiser.wavelet
        Ki=wf.td.K
        Kf=int(pow(2,math.ceil(log2(wf.td.K))))
        PadLeft=Kf-Ki
        pct=pct*Ki/Kf
        pwf=wf*WaveformTrimmer(-PadLeft,0)
        X=w.DWT(pwf.Values())
        T=WaveletDenoiser.DerivativeThresholdCalc(X,w.h,pct,isDerivative)
        dwf=Waveform(pwf.td,w.IDWT(
            [0 if abs(x) < t*mult else x for (x,t) in zip(X,T)]))
        dwf=dwf*WaveformTrimmer(PadLeft,0)
        return dwf
...
...
