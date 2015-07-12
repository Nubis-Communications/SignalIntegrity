import SignalIntegrity as si

sd=si.sd.SystemDescription()
sd.AddDevice('S',2)
sd.AddDevice('\\Gamma_l',1)
sd.AddDevice('\\Gamma_s',1)
sd.ConnectDevicePort('\\Gamma_s',1,'S',1)
sd.ConnectDevicePort('S',2,'\\Gamma_l',1)
sd.AssignM('\\Gamma_s',1,'m1')
ssp=si.sd.SystemSParametersSymbolic(sd)
ssp.LaTeXSystemEquation().Emit()
ssp.AssignSParameters('\\Gamma_s',si.sy.ShuntZ(1,'Zs'))
ssp.AssignSParameters('\\Gamma_l',si.sy.ShuntZ(1,'Zl'))
ssp.Clear().LaTeXSystemEquation().Emit()
