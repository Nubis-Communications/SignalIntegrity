import SignalIntegrity as si

ds=si.sd.DeembedderSymbolic(size='small')
ds.AddDevice('F',4)
ds.AddUnknown('U_1',1)
ds.AddUnknown('U_2',1)
ds.AddPort('F',1,1)
ds.AddPort('F',2,2)
ds.ConnectDevicePort('F',3,'U_1',1)
ds.ConnectDevicePort('F',4,'U_2',1)
ds.SymbolicSolution().Emit()
