import SignalIntegrity as si

d=si.sd.Deembedder()
d.AddDevice('F',4)
d.AddUnknown('?1',1)
d.AddUnknown('?2',1)
d.AddPort('F',1,1)
d.AddPort('F',2,2)
d.ConnectDevicePort('F',3,'?1',1)
d.ConnectDevicePort('F',4,'?2',1)
symbolic=si.sd.DeembedderSymbolic(d,size='small')
symbolic.SymbolicSolution().Emit()
