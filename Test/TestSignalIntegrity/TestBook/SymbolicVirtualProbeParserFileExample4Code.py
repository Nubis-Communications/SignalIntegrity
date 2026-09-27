import SignalIntegrity.Lib as si
vpp=si.p.VirtualProbeParser().File('VirtualProbe4.txt')
vps=si.sd.VirtualProbeSymbolic(vpp.SystemDescription(),size='small')
vps.LaTeXTransferMatrix().Emit()
