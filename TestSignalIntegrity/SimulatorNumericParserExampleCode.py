import SignalIntegrity as si

Td=1.23e-9; Zc=55; C=Td/Zc; L=Td*Zc
Rse=0.001; df=.001; R=.1;

netlist=['device T 2 telegrapher'+' r '+str(R)+' rse '+str(Rse)+' l '+str(L)+
         ' c '+str(C)+' df '+str(df),
         'voltagesource Vs 1','voltagesource Vn 2','device Rt 2 R 65',
         'device Rr 1 R 60','connect Vs 1 Vn 1','connect Vn 2 Rt 1',
         'connect Rt 2 T 1','connect T 2 Rr 1','output T 1','output T 2']
for line in netlist: print(line)

Fs=40e9; Ts=1./Fs; irlength=20e-9
fdtm=si.td.wf.TimeDescriptor(0,irlength/Ts,Fs).FrequencyList()
smp=si.p.SimulatorNumericParser(fdtm).AddLines(netlist)
tm=smp.TransferMatrices()
##########################################
outnames=['Vt','Vr']
innames=['Vs','Vn']
tmfr=tm.FrequencyResponses()
import matplotlib.pyplot as plt
for i in range(len(innames)):
    for o in range(len(outnames)):
        plt.subplot(len(outnames),len(innames),o*2+i+1)
        plt.plot(tmfr[o][i].Frequencies('GHz'),tmfr[o][i].Response('dB'),
            label=outnames[o]+' due to '+innames[i],color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('frequency (GHz)');
        plt.ylabel('magnitude (dB)')
plt.show()
plt.cla()

#######################################
tmir=tm.ImpulseResponses()
import matplotlib.pyplot as plt
for i in range(len(innames)):
    for o in range(len(outnames)):
        plt.subplot(len(outnames),len(innames),o*2+i+1)
        plt.plot(tmir[o][i].Times('ns'),tmir[o][i].Values(),
            label=outnames[o]+' due to '+innames[i],color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('time (ns)');
        plt.ylabel('amplitude (V)')
        plt.xlim(-0.05,3);
        plt.ylim(0,0.5)
plt.show()
plt.cla()
##################################################
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
###################################################
tmp=si.td.f.TransferMatricesProcessor(tm)
wfn=si.td.wf.NoiseWaveform(tdi,20e-3)
wfolist=[wf*usf
    for wf in tmp.ProcessWaveforms([wfi,wfn])]

plt.plot(wfolist[0].Times('ns'),
         wfolist[0].Values(),label='Vt',color='black')
plt.plot([t-Td/1e-9 for t in wfolist[1].Times('ns')],
         wfolist[1].Values(),label='Vr',color='gray')
plt.legend(loc='upper right',labelspacing=0.1)
plt.xlim(0 ,10)
plt.ylim(-0.05,0.65)
plt.xlabel('time (ns)')
plt.ylabel('amplitude (V)')
plt.show()
plt.cla()
###################################################
times=[(t-Td/1e-9)%(3*ui/1e-9) for t in wfolist[1].Times('ns')]
values = wfolist[1].Values()

pltt=[]; pltv=[]; tt=[]; vv=[]
for k in range(len(times)):
    if k==0:
        tt=[times[k]]; vv=[values[k]]
    elif times[k]>times[k-1]:
        tt.append(times[k]); vv.append(values[k])
    else:
        pltt.append(tt); pltv.append(vv)
        tt=[times[k]]; vv=[values[k]]

for e in range(len(pltt)):
    plt.plot(pltt[e],pltv[e],color='black')
plt.ylim(-0.00,0.5)
plt.xlim(0.1,0.5)
plt.show()
plt.cla()
