import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DV 4','device G 1 ground',
    'port 1 DV 1 2 DV 3',
    'connect DV 2 G 1','connect DV 4 G 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
DV=si.sy.VoltageAmplifierFourPort('\\alpha','Z_i','Z_o')
ssps.AssignSParameters('DV',DV)
ssps.LaTeXBlockSolutionBiggest().Emit()
