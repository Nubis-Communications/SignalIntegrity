import SignalIntegrity as si

dp=si.p.DeembedderParser().File('SymbolicDeembedding3.txt')
ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
ds.SymbolicSolution().Emit()
