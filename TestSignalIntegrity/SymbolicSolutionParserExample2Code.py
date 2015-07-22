import SignalIntegrity as si

sdp = si.p.SystemDescriptionParser()
sdp.AddLines(['device L 2','device R 2','port 1 L 1 2 R 2','connect L 2 R 1'])
sdp.WriteToFile('SymbolicSolution2.txt',False)
spc = si.sd.SystemSParameters(sdp.SystemDescription())
symbolic=si.sd.SystemSParametersSymbolic(spc)
symbolic.LaTeXSystemEquation()
symbolic.LaTeXSolution(type='direct')
symbolic.LaTeXSolution(type='block').Emit()
