import SignalIntegrity.Lib as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DV 4',
    'device DC 4',
    'port 1 DC 4',
    'port 2 DC 3',
    'port 3 DC 1',
    'port 4 DV 3',
    'connect DC 2 DV 4',
    'connect DC 4 DV 2',
    'connect DC 3 DV 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.AssignSParameters('DV',si.sy.VoltageControlledVoltageSource('a'))
ssps.AssignSParameters('DC',si.sy.CurrentControlledCurrentSource('a'))
ssps.LaTeXSolution(size='big').Emit()
