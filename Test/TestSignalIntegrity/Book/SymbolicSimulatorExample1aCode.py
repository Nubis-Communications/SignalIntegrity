import SignalIntegrity.Lib as si
ss=si.sd.SimulatorSymbolic()
ss.AddDevice('S',2)
ss.AddDevice('\\Gamma_l',1)
ss.ConnectDevicePort('S',2,'\\Gamma_l',1)
ss.AddVoltageSource('V',1)
ss.AddDevice('Z_s',2)
ss.ConnectDevicePort('V',1,'Z_s',1)
ss.ConnectDevicePort('Z_s',2,'S',1)
ss.pOutputList = [('S',1),('S',2)]
ss.AssignSParameters('Z_s',si.sy.SeriesZ('Z_s'))
ss.AssignSParameters('\\Gamma_l',si.sy.ShuntZ(1,'Z_l'))
ss.LaTeXEquations().Emit()
