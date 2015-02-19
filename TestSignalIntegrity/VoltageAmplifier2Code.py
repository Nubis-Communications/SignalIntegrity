import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DV 4',
    'device ZI 2',
    'device ZO 2',
    'device G 1 ground',
    'port 1 ZI 1',
    'port 2 ZO 2',
    'connect ZI 1 DV 2',
    'connect ZI 2 G 1',
    'connect DV 1 G 1',
    'connect ZO 1 DV 4',
    'connect DV 3 G 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
ssps.LaTeXBigSolution().Emit()
