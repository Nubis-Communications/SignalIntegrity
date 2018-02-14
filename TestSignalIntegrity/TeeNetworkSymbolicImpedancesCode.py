import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device Sl 2','device Sr 2','device Sm 2',
              'connect Sl 2 Sr 2 Sm 2','port 1 Sl 1 2 Sr 1 3 Sm 1'])
sd=sdp.SystemDescription()
sd.AssignSParameters('Sl',si.sy.SeriesZ('Zl'))
sd.AssignSParameters('Sr',si.sy.SeriesZ('Zr'))
sd.AssignSParameters('Sm',si.sy.SeriesZ('Zm'))
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
    eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}')
ssps.LaTeXSolution().Emit()
