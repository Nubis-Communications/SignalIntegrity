import SignalIntegrity as si

dp=si.p.DeembedderParser()
dp.AddLines(['device L 2','unknown Su 2','device R 2',
    'port 1 L 1 2 R 1','connect L 2 Su 1','connect R 2 Su 2'])
ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
ds.SymbolicSolution().Emit()
