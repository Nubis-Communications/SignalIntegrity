import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DV 4',
    'device ZI 2',
    'device ZO 2',
    'device G 1 ground',
    'port 1 ZI 1',
    'port 2 ZI 2',
    'port 3 ZO 2',
    'connect DV 3 G 1',
    'connect ZI 1 DV 2',
    'connect ZI 2 DV 1',
    'connect ZO 1 DV 4'])
sdp.WriteToFile('VoltageAmplifier3.txt',False)
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
ssps.LaTeXBlockSolutionBig().Emit()
