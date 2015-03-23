import SignalIntegrity as si

sd=si.sd.SystemDescription()
sd.AddDevice('F',4)
sd.AddDevice('?1',1)
sd.AddDevice('?2',1)
sd.AddPort('F',1,1)
sd.AddPort('F',2,2)
sd.ConnectDevicePort('F',3,'?1',1)
sd.ConnectDevicePort('F',4,'?2',1)
spc = si.sd.Deembedder(sd)
symbolic=si.sd.DeembedderSymbolic(spc,size='small')
symbolic.SymbolicSolution().Emit()
