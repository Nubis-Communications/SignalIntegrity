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
DS=si.sy.VoltageAmplifierFourPort('\\alpha','Z_i','Z_o')
si.sy.SymbolicMatrix([DS[0][0]],'D_{11}',True).Emit()
si.sy.SymbolicMatrix([DS[0][1]],'D_{12}',True).Emit()
si.sy.SymbolicMatrix([DS[2][0]],'D_{31}',True).Emit()
si.sy.SymbolicMatrix([DS[2][2]],'D_{33}',True).Emit()
si.sy.SymbolicMatrix([DS[2][3]],'D_{34}',True).Emit()
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
FS=si.sy.VoltageAmplifierFourPort('\\beta','Z_{if}','Z_{of}')
si.sy.SymbolicMatrix([FS[0][0]],'F_{11}',True).Emit()
si.sy.SymbolicMatrix([FS[0][1]],'F_{12}',True).Emit()
si.sy.SymbolicMatrix([FS[2][0]],'F_{31}',True).Emit()
si.sy.SymbolicMatrix([FS[2][2]],'F_{33}',True).Emit()
si.sy.SymbolicMatrix([FS[2][3]],'F_{34}',True).Emit()
ssps.LaTeXSolution(size='biggest').Emit()
