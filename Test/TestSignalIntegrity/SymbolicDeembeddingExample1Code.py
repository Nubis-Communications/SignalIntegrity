import SignalIntegrity.Lib as si
ds=si.sd.DeembedderSymbolic(size='small',known='\\Gamma_{msd}')
ds.AddDevice('S',2)
ds.AddUnknown('\\Gamma_{dut}',1)
ds.ConnectDevicePort('S',2,'\\Gamma_{dut}',1)
ds.AddPort('S',1,1)
ds.SymbolicSolution().Emit()
