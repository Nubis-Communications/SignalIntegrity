import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 4','device ZI 2','device ZO 2',
    'port 1 ZI 1 2 D 2 3 ZO 2 4 D 3',
    'connect ZI 2 D 1','connect ZO 1 D 4'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.AssignSParameters('D',si.sy.CurrentControlledVoltageSource('\\gamma'))
ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
ssps.LaTeXSolution(size='big').Emit()
