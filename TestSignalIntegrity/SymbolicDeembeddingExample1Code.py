import SignalIntegrity as si

sd=si.sd.SystemDescription()
sd.AddDevice('D',2)
sd.AddDevice('?',1)
sd.ConnectDevicePort('D',2,'?',1)
sd.AddPort('D',1,1)
spc = si.sd.Deembedder(sd)
symbolic=si.sd.DeembedderSymbolic(spc,True,True)
symbolic.SymbolicSolution().Emit()
