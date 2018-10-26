import SignalIntegrity.Lib as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DV 4',
    'port 1 DV 1 2 DV 3 3 DV 2',
    'connect DV 2 DV 4'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.AssignSParameters('DV',si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o'))
ssps.LaTeXSolution(size='biggest').Emit()
