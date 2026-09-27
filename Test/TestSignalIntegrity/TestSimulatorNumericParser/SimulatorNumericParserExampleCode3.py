bitRate=5e9; ui=1./bitRate

rcf=si.td.f.RaisedCosineFilter(int(0.3*ui/Ts))

uf=2
usf=si.td.f.InterpolatorSinX(uf)
fdf=si.td.f.FractionalDelayFilterSinX(0,False)

bitsResult=300
lengthResult=bitsResult*ui
tdr=si.td.wf.TimeDescriptor(0.,lengthResult/Ts*uf,Fs*uf)
tdi=((((tdr/usf.FilterDescriptor())/
        tmir[0][0].FirFilter().FilterDescriptor())/
            rcf.FilterDescriptor())/
                fdf.FilterDescriptor())
import random
bits=[1 if random.random()>0.5 else 0
    for _ in range(bitsResult+1)]; bits[0]=0
a=[(bits[k]-bits[k-1]) for k in range(1,bitsResult+1)]
import numpy
jitter=numpy.random.normal(0.,10.e-12,bitsResult).tolist()
wfi=sum([si.td.wf.StepWaveform(tdi,a[b],b*ui)*
         si.td.f.FractionalDelayFilterSinX(jitter[b]/Ts,False)
            for b in range(len(a))])
wfi=wfi*rcf
fci=wfi.FrequencyContent()

plt.plot(fci.Frequencies('GHz'),
    [v+90 for v in fci.Values('dBmPerHz')],color='black')
plt.xlabel('frequency (GHz)')
plt.ylabel('magnitude (dBm/GHz)')
plt.xlim(0,15)
plt.ylim(-60,30)
plt.show()
plt.cla()

wfn=si.td.wf.NoiseWaveform(tdi,20e-3)
