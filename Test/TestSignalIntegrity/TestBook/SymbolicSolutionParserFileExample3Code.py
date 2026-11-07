import SignalIntegrity.Lib as si
sdp = si.p.SystemDescriptionParser().File('SymbolicSolution3.txt')
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.LaTeXSolution().Emit()
