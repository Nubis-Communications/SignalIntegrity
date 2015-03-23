import SignalIntegrity as si

sd = si.sd.SystemDescription()
sd.AddDevice('L', 2)  # add two-port left device
sd.AddDevice('R', 2)  # add two-port right device
sd.AddPort('L', 1, 1)  # add a port at port 1 of left device
sd.AddPort('R', 2, 2)  # add a port at port 2 of right device
sd.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
ssps = si.sd.SystemSParametersSymbolic(sd)
ssps.LaTeXSystemEquation().Emit()
