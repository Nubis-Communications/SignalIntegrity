import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 4','device ZI 2','device ZO 2',
    'port 1 ZI 1 2 ZI 2 3 ZO 1 4 ZO 2',
    'connect ZI 1 D 2','connect ZI 2 D 1',
    'connect ZO 1 D 4','connect ZO 2 D 3'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
ssps.AssignSParameters('D',si.sy.VoltageControlledCurrentSource('\\delta'))
ssps.AssignSParameters('ZI',si.sy.SeriesZ('Z_i'))
ssps.AssignSParameters('ZO',si.sy.SeriesZ('Z_o'))
ssps.LaTeXBlockSolutionBig().Emit()
