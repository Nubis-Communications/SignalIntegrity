import SignalIntegrity.Lib as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device Sl 2','device Sr 2','device Sm 1',
              'connect Sl 2 Sr 2 Sm 1','port 1 Sl 1 2 Sr 1'])
sd=sdp.SystemDescription()
sd.AssignSParameters('Sl',si.sy.SeriesZ('Zl'))
sd.AssignSParameters('Sr',si.sy.SeriesZ('Zr'))
sd.AssignSParameters('Sm',si.sy.ShuntZ(1,'Zm'))
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),
    eqprefix='\\begin{equation} ',eqsuffix=' \\end{equation}',
    size='small')
ssps.LaTeXSolution(size='big').Emit()
