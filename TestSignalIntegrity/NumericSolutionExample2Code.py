import SignalIntegrity as si

sspn = si.sd.SystemSParametersNumeric()
sspn.AddDevice('L', 2)  # add two-port left device
sspn.AddDevice('R', 2)  # add two-port right device
sspn.AddPort('L', 1, 1)  # add a port at port 1 of left device
sspn.AddPort('R', 2, 2)  # add a port at port 2 of right device
sspn.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
fl=[i*100.*1e6 for i in range(100+1)]
spl=si.sp.SParameterFile('cable.s2p',50.).Resample(fl)
spr=si.sp.SParameterFile('filter.s2p',50.).Resample(fl)
sp=[]
for n in range(len(fl)):
    sspn.AssignSParameters('L',spl[n])
    sspn.AssignSParameters('R',spr[n])
    sp.append(sspn.SParameters())
spres=si.sp.SParameters(fl,sp).WriteToFile('result.s2p')
