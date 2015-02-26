import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DC 4',
    'device ZI 2',
    'device ZO 2',
    'port 1 ZI 1',
    'port 2 DC 2',
    'port 3 DC 4',
    'port 4 DC 3',
    'connect ZI 2 DC 1',
    'connect ZO 1 DC 4',
    'connect ZO 2 DC 3'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('\\beta'))
ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
ssps.LaTeXBlockSolutionBig().Emit()
