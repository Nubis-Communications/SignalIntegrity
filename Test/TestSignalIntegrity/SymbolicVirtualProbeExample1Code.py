import SignalIntegrity.Lib as si
vps=si.sd.VirtualProbeSymbolic(size='small')
vps.AddDevice('\\Gamma_T',1)
vps.AddDevice('C',2)
vps.AddDevice('\\Gamma_R',1)
vps.ConnectDevicePort('\\Gamma_T',1,'C',1)
vps.ConnectDevicePort('C',2,'\\Gamma_R',1)
vps.AssignM('\\Gamma_T',1,'m1')
vps.pMeasurementList = [('\\Gamma_T',1)]
vps.pOutputList = [('\\Gamma_R',1)]
vps.LaTeXEquations().Emit()
