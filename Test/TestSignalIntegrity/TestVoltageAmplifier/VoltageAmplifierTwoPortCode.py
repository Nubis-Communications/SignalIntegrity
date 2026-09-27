import SignalIntegrity.Lib as si
sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DV 4','device G 1 ground','port 1 DV 1 2 DV 3',
    'connect DV 2 G 1','connect DV 4 G 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
DV=si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o')
ssps.AssignSParameters('DV',DV)
ssps.LaTeXSolution(size='biggest').Emit()
