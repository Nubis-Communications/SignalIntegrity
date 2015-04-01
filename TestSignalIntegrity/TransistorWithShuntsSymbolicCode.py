import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device T 3','device rb 2','device Cms 4','device Cps 4','device rx 2',
              'device rc 2','device Ccs 3',
              'port 1 rb 1 2 rc 2 3 rx 2 4 Ccs 3',
              'connect rb 2 Cms 1','connect Cms 3 Cps 1','connect Cps 3 T 1',
              'connect T 3 Cps 4','connect Cps 2 rx 1','connect T 2 Ccs 1',
              'connect Ccs 2 Cms 4','connect Cms 2 rc 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
symbolic=si.sd.Symbolic(size='small')
rb=si.sy.SeriesZ('r_b')
symbolic._AddEq('\\mathbf{rb}='+ssps._LaTeXMatrix(rb))
rc=si.sy.SeriesZ('r_c')
symbolic._AddEq('\\mathbf{rc}='+ssps._LaTeXMatrix(rc))
rx=si.sy.SeriesZ('r_ex')
symbolic._AddEq('\\mathbf{rx}='+ssps._LaTeXMatrix(rx))
Cms=si.sy.ShuntZ(4,'\\frac{1}{C_{\\mu}\\cdot s}')
symbolic._AddEq('\\mathbf{Cms}='+ssps._LaTeXMatrix(Cms))
Ccs=si.sy.ShuntZ(3,'\\frac{1}{C_{cs}\\cdot s}')
symbolic._AddEq('\\mathbf{Ccs}='+ssps._LaTeXMatrix(Ccs))
Cps=si.sy.ShuntZ(4,'\\frac{1}{C_{\\pi}\\cdot s}')
symbolic._AddEq('\\mathbf{Cps}='+ssps._LaTeXMatrix(Cps))
T=si.sy.TransconductanceAmplifierThreePort('-g_m', 'r_{\\pi}', 'r_o')
symbolic._AddEq('\\mathbf{T}=\\ldots')
symbolic._AddEq(ssps._LaTeXMatrix(T))
symbolic.m_lines = [line.replace('--','+') for line in symbolic.m_lines]
symbolic.Emit()
ssps.LaTeXSolution(size='biggest').Emit()
