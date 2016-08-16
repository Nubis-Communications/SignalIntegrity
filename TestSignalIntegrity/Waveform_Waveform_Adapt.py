class Waveform(object):
    def Adapt(self,td):
        wf=self
        u=int(round(td.Fs/wf.TimeDescriptor().Fs))
        if not u==1:
            wf=wf*(InterpolatorSinX(u) if wf.adaptionStrategy=='SinX'
                else InterpolatorLinear(u))
        ad=td/wf.TimeDescriptor()
        f=ad.D-int(ad.D)
        if not f==0.0:
            wf=wf*(FractionalDelayFilterSinX(f,True) if wf.adaptionStrategy=='SinX'
                else FractionalDelayFilterLinear(f,True))
        ad=td/wf.TimeDescriptor()
        tr=WaveformTrimmer(max(0,int(round(ad.TrimLeft()))),
                           max(0,int(round(ad.TrimRight()))))
        wf=wf*tr
        return wf
...
