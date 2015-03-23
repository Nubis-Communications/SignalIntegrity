import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 3','device G 1 ground',
    'port 1 D 1 2 D 2','connect D 3 G 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
ssps.AssignSParameters('D',si.sy.ShuntZThreePort('Z'))
ssps.LaTeXSolution(size='big').Emit()
