tmp=si.td.f.TransferMatricesProcessor(tm)
wfolist=[wf*usf for wf in tmp.ProcessWaveforms([wfi,wfn])]

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
plt.ylim(-0.00,0.5); plt.xlim(0.1,0.5)
plt.xlabel('time (ns)'); plt.ylabel('amplitude (V)')
plt.show()
plt.cla()
