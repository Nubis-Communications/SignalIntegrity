import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device VA 4',
    'device ZI1 2',
    'device ZI2 2',
    'device G 1 ground',
    'port 1 ZI1 1',
    'port 2 ZI2 1',
    'port 3 VA 3',
    'connect VA 4 G 1',
    'connect ZI1 1 VA 1',
    'connect ZI2 1 VA 2',
    'connect ZI1 2 G 1',
    'connect ZI2 2 G 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps._AddEq('ZI1=ZI2='+ssps._LaTeXMatrix(si.sy.SeriesZ('Z_i')))
ssps._AddEq('VA='+ssps._LaTeXMatrix(si.sy.VoltageAmplifier(4,'G','Z_d','Z_o')))
ssps.LaTeXSolution(size='big').Emit()
