import SignalIntegrity as si

d=si.sd.Deembedder()
d.AddDevice('D',2)
d.AddUnknown('Su',1)
d.ConnectDevicePort('D',2,'Su',1)
d.AddPort('D',1,1)
symbolic=si.sd.DeembedderSymbolic(d,size='small')
symbolic.SymbolicSolution().Emit()
