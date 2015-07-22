import SignalIntegrity as si

ds=si.sd.DeembedderSymbolic(size='small')
ds.AddDevice('D1',2)
ds.AddDevice('D2',2)
ds.AddDevice('D3',2)
ds.AddUnknown('Su',2)
ds.AddPort('D1',1,1)
ds.AddPort('D2',1,2)
ds.ConnectDevicePort('D1',2,'Su',1)
ds.ConnectDevicePort('D2',2,'D3',1)
ds.ConnectDevicePort('D3',2,'Su',2)
ds.SymbolicSolution().Emit()
