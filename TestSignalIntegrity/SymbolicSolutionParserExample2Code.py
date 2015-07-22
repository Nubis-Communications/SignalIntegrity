import SignalIntegrity as si

sdp = si.p.SystemDescriptionParser()
sdp.AddLines(['device L 2','device R 2','port 1 L 1 2 R 2','connect L 2 R 1'])
sdp.WriteToFile('SymbolicSolution2.txt',False)
ssps = si.sd.SystemSParametersSymbolic(sdp.SystemDescription())
ssps.LaTeXSystemEquation()
ssps.LaTeXSolution(solvetype='direct')
ssps.LaTeXSolution(solvetype='block').Emit()
