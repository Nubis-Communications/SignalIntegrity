import SignalIntegrity.Lib as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 4','device F 2','device G 1 ground',
    'port 1 D 1 2 D 3',
    'connect D 2 F 2','connect D 3 F 1','connect D 4 G 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.AssignSParameters('D',si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o'))
ssps.AssignSParameters('F',si.sy.VoltageAmplifier(2,'\\beta','Z_{if}','Z_{of}'))
ssps.LaTeXSolution(size='biggest').Emit()
