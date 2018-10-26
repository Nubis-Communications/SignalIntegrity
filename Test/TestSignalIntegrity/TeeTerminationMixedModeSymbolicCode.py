import SignalIntegrity.Lib as si

sdp=si.p.SystemDescriptionParser().AddLines([
    'device MM 4 mixedmode',
    'device R1 2',
    'device R2 2',
    'device R3 1',
    'connect MM 1 R1 2',
    'connect MM 2 R2 1',
    'port 1 MM 3',
    'port 2 MM 4',
    'connect R1 1 R2 2 R3 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.AssignSParameters('R1',si.sy.SeriesZ('Z_1'))
ssps.AssignSParameters('R2',si.sy.SeriesZ('Z_2'))
ssps.AssignSParameters('R3',si.sy.ShuntZ(1,'Z_3'))
ssps.LaTeXSolution(size='big')
ssps.Emit()
