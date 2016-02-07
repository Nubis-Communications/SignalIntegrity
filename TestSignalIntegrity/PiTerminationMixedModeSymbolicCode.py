import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser().AddLines([
    'device MM 4 mixedmode',
    'device Z3 2',
    'device Z1 1',
    'device Z2 1',
    'connect MM 1 Z3 2 Z1 1',
    'connect MM 2 Z3 1 Z2 1',
    'port 1 MM 3',
    'port 2 MM 4'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.AssignSParameters('Z3',si.sy.SeriesZ('Z_3'))
ssps.AssignSParameters('Z1',si.sy.ShuntZ(1,'Z_1'))
ssps.AssignSParameters('Z2',si.sy.ShuntZ(1,'Z_2'))
ssps.LaTeXSolution(size='big')
ssps.Emit()
