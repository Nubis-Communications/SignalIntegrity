import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DV 4',
    'device ZI 2',
    'device ZO 2',
    'port 1 ZI 1',
    'port 2 ZI 2',
    'port 3 ZO 2',
    'port 4 DV 3',
    'connect ZI 1 DV 2',
    'connect ZI 2 DV 1',
    'connect ZO 1 DV 4'])
sd = sdp.SystemDescription()
sd.AssignSParameters('DV',
    si.sy.VoltageControlledVoltageSource('\\alpha'))
sd.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
sd.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
ssp=si.sd.SystemSParameters(sdp.SystemDescription())
ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
ssps.LaTeXBigSolution().Emit()
