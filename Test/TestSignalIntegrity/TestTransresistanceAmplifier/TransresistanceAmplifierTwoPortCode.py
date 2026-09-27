import SignalIntegrity.Lib as si
sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 4','device G1 1 ground','device G2 1 ground',
    'port 1 D 1 2 D 3',
    'connect D 2 G1 1','connect D 4 G2 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
D=si.sy.TransresistanceAmplifier(4,'\\gamma','Z_i','Z_o')
ssps.AssignSParameters('D',D)
ssps.LaTeXSolution(size='biggest').Emit()
