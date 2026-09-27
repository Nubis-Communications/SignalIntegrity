import SignalIntegrity.Lib as si
sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 4','device ZI 4','device ZO 4',
    'port 1 ZI 1 2 ZI 2 3 ZO 1 4 ZO 2',
    'connect ZI 3 D 2','connect ZI 4 D 1','connect ZO 3 D 4','connect ZO 4 D 3'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.AssignSParameters('D',si.sy.VoltageControlledCurrentSource('\\delta'))
ssps.AssignSParameters('ZI',si.sy.ShuntZ(4,'Z_i'))
ssps.AssignSParameters('ZO',si.sy.ShuntZ(4,'Z_o'))
ssps.LaTeXSolution(size='biggest').Emit()
