import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 3','device G 1 ground',
    'port 1 D 1 2 D 2',
    'connect D 3 G 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
D=si.sy.TransresistanceAmplifier(3,'\\gamma','Z_i','Z_o')
ssps.AssignSParameters('D',D)
ssps.LaTeXBlockSolutionBiggest().Emit()
