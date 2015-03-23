import SignalIntegrity as si

sdp = si.p.SystemDescriptionParser().File('SymbolicSolution3.txt')
spc = si.sd.SystemSParameters(sdp.SystemDescription())
symbolic=si.sd.SystemSParametersSymbolic(spc,size='small')
symbolic.LaTeXSolution().Emit()
