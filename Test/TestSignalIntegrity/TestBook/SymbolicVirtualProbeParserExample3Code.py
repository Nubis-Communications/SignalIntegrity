import SignalIntegrity.Lib as si
vpp=si.p.VirtualProbeParser()
vpp.AddLines(['device T 2','device C 4','device R 2','connect T 1 C 1',
    'connect T 2 C 2','connect C 3 R 1','connect C 4 R 2','stim m1 T 1',
    'stim m2 T 2','meas T 1 T 2','output R 1 R 2','stimdef [[1],[-1]]'])
vps=si.sd.VirtualProbeSymbolic(vpp.SystemDescription(),size='small')
vps.LaTeXEquations().Emit()
