import SignalIntegrity.Lib as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device A 4',
    'device ZI1 2',
    'device ZI2 2',
    'device G 1 ground',
    'port 1 ZI1 1',
    'port 2 ZI2 1',
    'port 3 A 4',
    'connect A 3 G 1',
    'connect ZI1 2 A 1',
    'connect ZI2 2 A 2'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.AssignSParameters('ZI1',si.sy.ShuntZ(2,'Zi'))
ssps.AssignSParameters('ZI2',si.sy.ShuntZ(2,'Zi'))
ssps.AssignSParameters('A',si.sy.VoltageAmplifier(4, 'G', 'Zd', 'Zo'))
ssps.LaTeXSolution(size='biggest').Emit()
