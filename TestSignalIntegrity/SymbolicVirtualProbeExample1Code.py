import SignalIntegrity as si

sd=si.sd.SystemDescription()
sd.AddDevice('T',1)
sd.AddDevice('C',2)
sd.AddDevice('R',1)
sd.ConnectDevicePort('T',1,'C',1)
sd.ConnectDevicePort('C',2,'R',1)
sd.AssignM('T',1,'m1')
vp=si.sd.VirtualProbe(sd)
vp.pMeasurementList = [('T',1)]
vp.pOutputList = [('R',1)]
svp=si.sd.VirtualProbeSymbolic(vp,True,True)
svp.LaTeXEquations().Emit()
