from __future__ import print_function
import SignalIntegrity.Lib as si

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
