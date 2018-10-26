import SignalIntegrity.Lib as si

ss=si.sd.SimulatorSymbolic()
ss.AddDevice('S',2)
ss.AddDevice('\\Gamma_l',1)
ss.ConnectDevicePort('S',2,'\\Gamma_l',1)
ss.AddVoltageSource('V',1)
ss.AddDevice('Zs',2)
ss.ConnectDevicePort('V',1,'Zs',1)
ss.ConnectDevicePort('Zs',2,'S',1)
ss.pOutputList = [('S',1),('S',2)]
ss.AssignSParameters('Zs',si.sy.SeriesZ('Zs'))
ss.AssignSParameters('\\Gamma_l',si.sy.ShuntZ(1,'Zl'))
ss.LaTeXEquations().Emit()
