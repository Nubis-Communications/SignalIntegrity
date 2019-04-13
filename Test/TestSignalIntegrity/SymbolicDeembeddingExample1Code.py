import SignalIntegrity.Lib as si
ds=si.sd.DeembedderSymbolic(size='small',known='\\Gamma_{msd}')
ds.AddDevice('D',2)
ds.AddUnknown('\\Gamma_{dut}',1)
ds.ConnectDevicePort('D',2,'\\Gamma_{dut}',1)
ds.AddPort('D',1,1)
ds.SymbolicSolution().Emit()
