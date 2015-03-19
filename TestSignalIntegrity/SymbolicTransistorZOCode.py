import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DC 4',
    'device HIE 2',
    'device ZO 2',
    'port 1 HIE 1 2 DC 4 3 DC 3',
    'connect HIE 2 DC 1',
    'connect DC 2 DC 4',
    'connect ZO 1 DC 3',
    'connect ZO 2 DC 4'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
ssps.AssignSParameters('HIE',si.sy.SeriesZ('Z_{\\pi}'))
ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
ssps.LaTeXSolution(size='big').Emit()
