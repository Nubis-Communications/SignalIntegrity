import SignalIntegrity as si

vpp=si.p.VirtualProbeParser().File('VirtualProbe4.txt')
vp=si.sd.VirtualProbe(vpp.SystemDescription())
svp=si.sd.VirtualProbeSymbolic(vp,size='small')
svp.LaTeXTransferFunctions().Emit()
