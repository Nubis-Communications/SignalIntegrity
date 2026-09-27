import SignalIntegrity.Lib as si
dp=si.p.DeembedderParser()
dp.AddLines(['device L 2','unknown U 2','device R 2',
    'port 1 L 1 2 R 1','connect L 2 U 1','connect R 2 U 2'])
ds = si.sd.DeembedderSymbolic(dp.SystemDescription(),size='small')
ds.SymbolicSolution().Emit()
