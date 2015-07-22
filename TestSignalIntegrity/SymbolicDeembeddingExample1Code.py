import SignalIntegrity as si

ds=si.sd.DeembedderSymbolic(size='small')
ds.AddDevice('D',2)
ds.AddUnknown('Su',1)
ds.ConnectDevicePort('D',2,'Su',1)
ds.AddPort('D',1,1)
ds.SymbolicSolution().Emit()
