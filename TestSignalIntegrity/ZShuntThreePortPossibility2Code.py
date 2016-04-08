import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 4','device O 1 open','port 1 D 1 2 D 3 3 D 2',
    'connect D 4 O 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.AssignSParameters('D',si.sy.ShuntZ(4,'Z'))
ssps.LaTeXSolution(size='big').Emit()
