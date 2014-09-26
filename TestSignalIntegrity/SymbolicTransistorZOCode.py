import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DC 4',
    'device HIE 2',
    'device ZO 2',
    'port 1 HIE 1 2 DC 4 3 DC 3',
    'connect HIE 2 DC 1',
    'connect DC 2 DC 4',
    'connect ZO 1 DC 3',
    'connect ZO 2 DC 4'])
sd = sdp.SystemDescription()
sd.AssignSParameters('DC',
    [['0','1','0','0'],
    ['1','0','0','0'],
    ['-\\beta','\\beta','1','0'],
    ['\\beta','-\\beta','0','1']])
sd.AssignSParameters('HIE',
    [['\\frac{Z_{\pi}}{Z_{\pi}+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_{\pi}+2\\cdot Z0}'],
    ['\\frac{2\\cdot Z0}{Z_{\pi}+2\\cdot Z0}','\\frac{Z_{\pi}}{Z_{\pi}+2\\cdot Z0}']])
sd.AssignSParameters('ZO',
    [['\\frac{Z_o}{Z_o+2\\cdot Z0}','\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}'],
    ['\\frac{2\\cdot Z0}{Z_o+2\\cdot Z0}','\\frac{Z_o}{Z_o+2\\cdot Z0}']])
ssp=si.sd.SystemSParameters(sd)
ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
ssps.LaTeXBigSolution().Emit()
