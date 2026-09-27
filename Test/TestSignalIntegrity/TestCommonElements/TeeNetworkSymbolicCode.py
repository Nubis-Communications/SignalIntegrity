import SignalIntegrity.Lib as si
sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device Sl 2','device Sr 2','device Sm 2',
              'connect Sl 2 Sr 2 Sm 2','port 1 Sl 1 2 Sr 1 3 Sm 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
    eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}',
    size='small')
ssps.LaTeXSolution(size='big').Emit()
