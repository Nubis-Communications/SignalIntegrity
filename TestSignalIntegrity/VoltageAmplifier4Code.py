import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DV 4',
    'device ZI 2',
    'device ZO 2',
    'port 1 ZI 1',
    'port 2 ZI 2',
    'port 3 ZO 2',
    'port 4 DV 3',
    'connect ZI 1 DV 2',
    'connect ZI 2 DV 1',
    'connect ZO 1 DV 4'])
sd = sdp.SystemDescription()
sd.AssignSParameters('DV',
    [['1','0','0','0'],
    ['0','1','0','0'],
    ['\\alpha','-\\alpha','0','1'],
    ['-\\alpha','\\alpha','1','0']])
sd.AssignSParameters('ZI',
    [['\\frac{Z_i}{Z_i+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}'],
    ['\\frac{2\\cdot Z0}{Z_i+2\\cdot Z0}','\\frac{Z_i}{Z_i+2\\cdot Z0}']])
sd.AssignSParameters('ZO',
    [['\\frac{Z_o}{Z_o+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}'],
    ['\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}','\\frac{Z_o}{Z_o+2\\cdot Z0}']])
ssp=si.sd.SystemSParameters(sdp.SystemDescription())
ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
ssps.LaTeXBigSolution().Emit()
