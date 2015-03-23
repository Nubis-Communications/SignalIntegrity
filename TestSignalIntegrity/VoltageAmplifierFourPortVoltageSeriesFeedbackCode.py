import SignalIntegrity as si

sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 4','device F 4',
    'port 1 D 1 2 F 4 3 D 3 4 F 2',
    'connect D 2 F 3','connect D 3 F 1','connect D 4 F 2'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
DSp=ssps[ssps.IndexOfDevice('D')].pSParameters
DSp[1][1]=DSp[0][0]
DSp[1][0]=DSp[0][1]
DSp[0][2]=0
DSp[0][3]=0
DSp[1][2]=0
DSp[1][3]=0
DSp[2][1]='-'+DSp[2][0]
DSp[3][0]='-'+DSp[2][0]
DSp[3][1]=DSp[2][0]
DSp[3][2]=DSp[2][3]
DSp[3][3]=DSp[2][2]
si.sy.SymbolicMatrix(si.helper.Matrix2Text(DSp),'\\mathbf{D}',True).Emit()
DSp=ssps[ssps.IndexOfDevice('F')].pSParameters
DSp[1][1]=DSp[0][0]
DSp[1][0]=DSp[0][1]
DSp[0][2]=0
DSp[0][3]=0
DSp[1][2]=0
DSp[1][3]=0
DSp[2][1]='-'+DSp[2][0]
DSp[3][0]='-'+DSp[2][0]
DSp[3][1]=DSp[2][0]
DSp[3][2]=DSp[2][3]
DSp[3][3]=DSp[2][2]
si.sy.SymbolicMatrix(si.helper.Matrix2Text(DSp),'\\mathbf{F}',True).Emit()
si.sy.SymbolicMatrix(si.sy.VoltageAmplifierFourPort('\\alpha','Z_i','Z_o'),'\\mathbf{D}',True).Emit()
si.sy.SymbolicMatrix(si.sy.VoltageAmplifierFourPort('\\beta','Z_{if}','Z_{of}'),'\\mathbf{F}',True).Emit()
ssps.LaTeXSolution(size='biggest').Emit()
