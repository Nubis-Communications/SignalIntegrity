import SignalIntegrity.Lib as si

vps=si.sd.VirtualProbeSymbolic(size='small')
vps.AddDevice('T',2)
vps.AddDevice('C',4)
vps.AddDevice('R',2)
vps.ConnectDevicePort('T',1,'C',1)
vps.ConnectDevicePort('T',2,'C',2)
vps.ConnectDevicePort('C',3,'R',1)
vps.ConnectDevicePort('C',4,'R',2)
vps.AssignM('T',1,'m1')
vps.AssignM('T',2,'m2')
vps.pMeasurementList = [('T',1),('T',2)]
vps.pOutputList = [('R',1),('R',2)]
vps.LaTeXEquations().Emit()
