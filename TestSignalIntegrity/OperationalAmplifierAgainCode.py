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
sd = sdp.SystemDescription()
sd.AssignSParameters('VA',si.sd.Device.SymbolicMatrix('VA',4))
sd.AssignSParameters('ZI1',si.sd.Device.SymbolicMatrix('ZI1',2))
sd.AssignSParameters('ZI2',si.sd.Device.SymbolicMatrix('ZI2',2))
ssp=si.sd.SystemSParameters(sdp.SystemDescription())
ssps=si.sd.SystemSParametersSymbolic(ssp,True,True)
print '\[ ZI1 = ZI2 = '+ si.helper.Matrix2LaTeX(si.sy.SeriesZ('Z_i')) + ' \]'
print '\[ VA = ' + si.helper.Matrix2LaTeX(si.sy.VoltageAmplifierFourPort('G','Z_d','Z_o')) + ' \]'
ssps.LaTeXBigSolution().Emit()
