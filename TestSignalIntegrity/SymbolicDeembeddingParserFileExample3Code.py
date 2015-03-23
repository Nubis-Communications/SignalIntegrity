import SignalIntegrity as si

dp=si.p.DeembedderParser().File('SymbolicDeembedding3.txt')
spc = si.sd.Deembedder(dp.SystemDescription())
symbolic=si.sd.DeembedderSymbolic(spc,size='small')
symbolic.SymbolicSolution().Emit()
