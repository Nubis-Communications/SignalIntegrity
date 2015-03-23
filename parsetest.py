import SignalIntegrity as si
lines = [
    'var %T T',
    'device L 2',
    'device R 2',
    'device %T 2',
    'device G 1 ground',
    'port 1 L 1',
    'port 2 R 2',
    'connect L 2 %T 1',
    'connect L 2 R 1',
    'connect %T 2 G 1'
    ]
sp = si.p.DeembedderParser(None,'%T ?')
sp.m_addThru = False
sp.AddLines(lines)
sd = sp.SystemDescription()
de = si.sd.Deembedder(sd)
symbolic = si.sd.SymbolicDeembedder(de,True)
symbolic.EmitLaTeXDeembeddingSolution(True)

sp2 = si.p.SystemSParametersParser(None,'%T T')
sp2.m_addThru = False
sp2.AddLines(lines)
sd2 = sp2.SystemDescription()
sspc = si.sd.SystemSParametersCalculator(sd2)
symbolic2 = si.sd.SymbolicSParameterCalculator(sspc,True)
symbolic2.LaTeXSystemEquation()
symbolic2.LaTeXSolution(type='direct')
symbolic2.LaTeXSolution(type='block').Emit()
