import SignalIntegrity.Lib as si
ssps = si.sd.SystemSParametersSymbolic()
ssps.AddDevice('S', 2)  # add two-port left device
ssps.AddDevice('\\Gamma t', 1)  # add a termination
ssps.AddPort('S', 1, 1)  # add a port at port 1 of left device
ssps.ConnectDevicePort('S', 2, '\\Gamma t', 1)  # connect the other ports
ssps.LaTeXSystemEquation()
ssps.LaTeXSolution(solvetype='direct')
ssps.LaTeXSolution(solvetype='block').Emit()
