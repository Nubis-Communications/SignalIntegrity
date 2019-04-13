import SignalIntegrity.Lib as si
sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 4',
    'port 1 D 1 2 D 3 3 D 2',
    'connect D 2 D 4'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.AssignSParameters('D',si.sy.TransresistanceAmplifier(4,'\\gamma','Z_i','Z_o'))
ssps.LaTeXSolution(size='biggest').Emit()
