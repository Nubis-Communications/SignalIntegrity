import SignalIntegrity as si

sd=si.sd.SystemDescription()
sd.AddDevice('T',2)
sd.AddDevice('C',4)
sd.AddDevice('R',2)
sd.ConnectDevicePort('T',1,'C',1)
sd.ConnectDevicePort('T',2,'C',2)
sd.ConnectDevicePort('C',3,'R',1)
sd.ConnectDevicePort('C',4,'R',2)
sd.AssignM('T',1,'m1')
sd.AssignM('T',2,'m2')
vp=si.sd.VirtualProbe(sd)
vp.pMeasurementList = [('T',1),('T',2)]
vp.pOutputList = [('R',1),('R',2)]
svp=si.sd.VirtualProbeSymbolic(vp,size='small')
svp.LaTeXEquations().Emit()
