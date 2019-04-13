import SignalIntegrity.Lib as si
sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device Sl 2','device Sr 2','device Sm 2','device g 1 ground',
              'connect Sl 2 Sr 2 Sm 2','connect Sm 1 g 1','port 1 Sl 1 2 Sr 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
    eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}',
    size='small')
ssps.LaTeXSolution(size='big').Emit()
