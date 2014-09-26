import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device DC 4',
    'device HIE 2',
    'port 1 HIE 1 2 DC 4 3 DC 3',
    'connect HIE 2 DC 1',
    'connect DC 2 DC 4'])
sd = sdp.SystemDescription()
sd.AssignSParameters('DC',
    [['0','1','0','0'],
    ['1','0','0','0'],
    ['-\\beta','\\beta','1','0'],
    ['\\beta','-\\beta','0','1']])
sd.AssignSParameters('HIE',
    [['\\frac{h_{ie}}{h_{ie}+2\\cdot Z0}','\\frac{2\\cdot Z0}{h_{ie}+2\\cdot Z0}'],
    ['\\frac{2\\cdot Z0}{h_{ie}+2\\cdot Z0}','\\frac{h_{ie}}{h_{ie}+2\\cdot Z0}']])
ssp=si.sd.SystemSParameters(sd)
ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
ssps.LaTeXBigSolution().Emit()
