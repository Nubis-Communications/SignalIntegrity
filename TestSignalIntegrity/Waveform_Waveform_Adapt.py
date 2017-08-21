class Waveform(object):
    def Adapt(self,td):
        wf=self
        (upsampleFactor,decimationFactor)=Rat(td.Fs/wf.TimeDescriptor().Fs)
        if upsampleFactor>1:
            wf=wf*(InterpolatorSinX(upsampleFactor) if wf.adaptionStrategy=='SinX'
                else InterpolatorLinear(upsampleFactor))
        ad=td/wf.TimeDescriptor()
        f=ad.D-int(ad.D)
        if not f==0.0:
            wf=wf*(FractionalDelayFilterSinX(f,True) if wf.adaptionStrategy=='SinX'
                else FractionalDelayFilterLinear(f,True))
            ad=td/wf.TimeDescriptor()
        if decimationFactor>1:
            decimationPhase=int(round(ad.TrimLeft())) % decimationFactor
            wf=wf*WaveformDecimator(decimationFactor,decimationPhase)
            ad=td/wf.TimeDescriptor()
        tr=WaveformTrimmer(max(0,int(round(ad.TrimLeft()))),
                           max(0,int(round(ad.TrimRight()))))
        wf=wf*tr
        return wf
...
