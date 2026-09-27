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
