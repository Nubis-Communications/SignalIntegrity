import SignalIntegrity.Lib as si
sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device T 3','device rb 2','device Cm 2','device Cp 2','device rx 2',
              'device rc 2','device Cc 2',
              'port 1 rb 1 2 rc 2 3 rx 2 4 Cc 2',
              'connect rb 2 Cp 1 Cm 1 T 1','connect T 2 rc 1 Cm 2 Cc 1',
              'connect Cp 2 T 3 rx 1'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
ssps.LaTeXSolution(size='biggest').Emit()
