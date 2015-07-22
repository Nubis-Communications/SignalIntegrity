import SignalIntegrity as si

sd = si.sd.SystemDescription()
sd.AddDevice('S', 2)  # add two-port left device
sd.AddDevice('\\Gamma t', 1)  # add a termination
sd.AddPort('S', 1, 1)  # add a port at port 1 of left device
sd.ConnectDevicePort('S', 2, '\\Gamma t', 1)  # connect the other ports
spc = si.sd.SystemSParameters(sd)
symbolic=si.sd.SystemSParametersSymbolic(spc)
symbolic.LaTeXSystemEquation()
symbolic.LaTeXSolution(solvetype='direct')
symbolic.LaTeXSolution(solvetype='block').Emit()
