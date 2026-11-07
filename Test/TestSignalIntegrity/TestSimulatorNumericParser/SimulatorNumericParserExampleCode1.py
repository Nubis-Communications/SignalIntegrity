outnames=['Vt','Vr']
innames=['Vs','Vn']
tmfr=tm.FrequencyResponses()
import matplotlib.pyplot as plt
for i in range(len(innames)):
    for o in range(len(outnames)):
        plt.subplot(len(outnames),len(innames),o*len(innames)+i+1)
        plt.plot(tmfr[o][i].Frequencies('GHz'),tmfr[o][i].Response('dB'),
            label=outnames[o]+' due to '+innames[i],color='black')
        plt.legend(loc='upper right',labelspacing=0.1)
        plt.xlabel('frequency (GHz)');
        plt.ylabel('magnitude (dB)')
plt.show()
plt.cla()

