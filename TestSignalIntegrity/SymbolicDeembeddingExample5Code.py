import SignalIntegrity as si

d=si.sd.Deembedder()
d.AddDevice('D1',2)
d.AddDevice('D2',2)
d.AddDevice('D3',2)
d.AddUnknown('Su',2)
d.AddPort('D1',1,1)
d.AddPort('D2',1,2)
d.ConnectDevicePort('D1',2,'Su',1)
d.ConnectDevicePort('D2',2,'D3',1)
d.ConnectDevicePort('D3',2,'Su',2)
symbolic=si.sd.DeembedderSymbolic(d,size='small')
symbolic.SymbolicSolution().Emit()
