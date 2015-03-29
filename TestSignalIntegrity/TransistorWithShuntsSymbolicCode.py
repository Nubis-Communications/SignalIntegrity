import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device T 3','device rb 2','device Cms 4','device Cps 4','device rx 2',
              'device rc 2','device Ccs 3',
              'port 1 rb 1 2 rc 2 3 rx 2 4 Ccs 3',
              'connect rb 2 Cms 1','connect Cms 3 Cps 1','connect Cps 3 T 1',
              'connect T 3 Cps 4','connect Cps 2 rx 1','connect T 2 Ccs 1',
              'connect Ccs 2 Cms 4','connect Cms 2 rc 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps._AddEq('\\mathbf{rb}='+ssps._LaTeXMatrix(si.sy.SeriesZ('r_b')))
ssps._AddEq('\\mathbf{rc}='+ssps._LaTeXMatrix(si.sy.SeriesZ('r_c')))
ssps._AddEq('\\mathbf{rx}='+ssps._LaTeXMatrix(si.sy.SeriesZ('r_ex')))
ssps._AddEq('\\mathbf{Cms}='+ssps._LaTeXMatrix(si.sy.ShuntZ(4,'\\frac{1}{C_{\\mu}\\cdot s}')))
ssps._AddEq('\\mathbf{Ccs}='+ssps._LaTeXMatrix(si.sy.ShuntZ(3,'\\frac{1}{C_{cs}\\cdot s}')))
ssps._AddEq('\\mathbf{Cps}='+ssps._LaTeXMatrix(si.sy.ShuntZ(4,'\\frac{1}{C_{\\pi}\\cdot s}')))
ssps._AddEq('\\mathbf{T}='+ssps._LaTeXMatrix(si.sy.TransconductanceAmplifierThreePort('-g_m', 'r_{\\pi}', 'r_o')))
ssps.m_lines = [line.replace('--','+') for line in ssps.m_lines]
ssps.LaTeXSolution(size='biggest').Emit()
