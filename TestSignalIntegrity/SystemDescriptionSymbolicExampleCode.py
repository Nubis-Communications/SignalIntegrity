import SignalIntegrity as si

ssps = si.sd.SystemSParametersSymbolic()
ssps.AddDevice('L', 2)  # add two-port left device
ssps.AddDevice('R', 2)  # add two-port right device
ssps.AddPort('L', 1, 1)  # add a port at port 1 of left device
ssps.AddPort('R', 2, 2)  # add a port at port 2 of right device
ssps.ConnectDevicePort('L', 2, 'R', 1)  # connect the other ports
ssps.LaTeXSystemEquation().Emit()
