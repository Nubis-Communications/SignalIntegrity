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
