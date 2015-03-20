import SignalIntegrity as si

dp=si.p.DeembedderParser()
dp.AddLines(['device L 2','device ? 2','device R 2','port 1 L 1 2 R 1','connect L 2 ? 1','connect R 2 ? 2'])
spc = si.sd.Deembedder(dp.SystemDescription())
symbolic=si.sd.DeembedderSymbolic(spc,True,True)
symbolic.SymbolicSolution().Emit()
