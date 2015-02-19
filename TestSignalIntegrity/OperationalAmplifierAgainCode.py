import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device VA 4',
    'device ZI1 2',
    'device ZI2 2',
    'device G 1 ground',
    'port 1 ZI1 1',
    'port 2 ZI2 1',
    'port 3 VA 3',
    'connect VA 4 G 1',
    'connect ZI1 1 VA 1',
    'connect ZI2 1 VA 2',
    'connect ZI1 2 G 1',
    'connect ZI2 2 G 1'])
sd = sdp.SystemDescription()
ssp=si.sd.SystemSParameters(sdp.SystemDescription())
ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
si.sy.SymbolicMatrix(si.sy.SeriesZ('Z_i'),'ZI1 = ZI2',True).Emit()
si.sy.SymbolicMatrix(si.sy.VoltageAmplifierFourPort('G','Z_d','Z_o'),'VA',True).Emit()
ssps.LaTeXBigSolution().Emit()
