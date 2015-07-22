import SignalIntegrity as si

ds=si.sd.DeembedderSymbolic(size='small')
ds.AddDevice('F',4)
ds.AddUnknown('?1',1)
ds.AddUnknown('?2',1)
ds.AddPort('F',1,1)
ds.AddPort('F',2,2)
ds.ConnectDevicePort('F',3,'?1',1)
ds.ConnectDevicePort('F',4,'?2',1)
ds.SymbolicSolution().Emit()
