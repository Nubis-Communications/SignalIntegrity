import SignalIntegrity as si

vps=si.sd.VirtualProbeSymbolic(size='small')
vps.AddDevice('T',1)
vps.AddDevice('C',2)
vps.AddDevice('R',1)
vps.ConnectDevicePort('T',1,'C',1)
vps.ConnectDevicePort('C',2,'R',1)
vps.AssignM('T',1,'m1')
vps.pMeasurementList = [('T',1)]
vps.pOutputList = [('R',1)]
vps.LaTeXEquations().Emit()
