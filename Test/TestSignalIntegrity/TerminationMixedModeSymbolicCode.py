import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser().AddLines([
    'device MM 4 mixedmode',
    'device S 2',
    'connect S 1 MM 1',
    'connect MM 2 S 2',
    'port 1 MM 3',
    'port 2 MM 4'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.LaTeXSolution().Emit()
