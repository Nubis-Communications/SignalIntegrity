import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DV 4',
    'device ZI1 2',
    'device ZI2 2',
    'device ZO 2',
    'device G 1 ground',
    'port 1 ZI1 1',
    'port 2 ZI2 1',
    'port 3 ZO 2',
    'connect DV 3 G 1',
    'connect ZI1 1 DV 2',
    'connect ZI2 1 DV 1',
    'connect ZI1 2 G 1',
    'connect ZI2 2 G 1',
    'connect ZO 1 DV 4'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('\\alpha'))
ssps.AssignSParameters('ZI1',si.sy.SeriesZ('Z_i'))
ssps.AssignSParameters('ZI2',si.sy.SeriesZ('Z_i'))
ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
ssps.LaTeXSolution(size='big').Emit()
