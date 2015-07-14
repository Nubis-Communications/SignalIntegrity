import SignalIntegrity as si

sd=si.sd.SystemDescription()
sd.AddDevice('S',2)
sd.AddDevice('\\Gamma_l',1)
sd.ConnectDevicePort('S',2,'\\Gamma_l',1)
s=si.sd.Simulator(sd)
s.AddVoltageSource('V',1)
s.AddDevice('Zs',2)
s.ConnectDevicePort('V',1,'Zs',1)
s.ConnectDevicePort('Zs',2,'S',1)
s.pOutputList = [('S',1),('S',2)]
ss=si.sd.SimulatorSymbolic(s)
ss.AssignSParameters('Zs',si.sy.SeriesZ('Zs'))
ss.AssignSParameters('\\Gamma_l',si.sy.ShuntZ(1,'Zl'))
ss.Clear().LaTeXEquations().Emit()
