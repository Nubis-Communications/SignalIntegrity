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
