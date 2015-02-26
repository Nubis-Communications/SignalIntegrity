import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device V 4',
              'device F 4',
              'device G 1 ground',
              'port 1 V 1 2 V 3',
              'connect V 2 F 3',
              'connect F 4 G 1',
              'connect V 3 F 1',
              'connect V 4 G 1',
              'connect F 2 G 1'])
si.sy.SymbolicMatrix(si.sy.VoltageAmplifierFourPort('G','Z_i','Z_o'),'V',True).Emit()
si.sy.SymbolicMatrix(si.sy.VoltageAmplifierFourPort('GF','Z_{if}','Z_{of}'),'F',True).Emit()
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),True,True)
ssps.LaTeXBlockSolutionBig().Emit()
