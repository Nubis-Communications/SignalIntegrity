import SignalIntegrity.Lib as si
sdp=si.p.SystemDescriptionParser()
sdp.AddLines(['device D 4','device F 4',
    'port 1 D 1 2 F 4 3 D 3 4 F 2',
    'connect D 2 F 3','connect D 3 F 1','connect D 4 F 2'])
ssps=si.sd.SystemSParametersSymbolic(sdp.SystemDescription(),size='small')
DSp=ssps[ssps.IndexOfDevice('D')].SParameters
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
DS=si.sy.VoltageAmplifier(4,'\\alpha','Z_i','Z_o')
ssps._AddEq('D_{11}={\\scriptstyle '+DS[0][0]+'}')
ssps._AddEq('D_{12}={\\scriptstyle '+DS[0][1]+'}')
ssps._AddEq('D_{31}={\\scriptstyle '+DS[2][0]+'}')
ssps._AddEq('D_{33}={\\scriptstyle '+DS[2][2]+'}')
ssps._AddEq('D_{34}={\\scriptstyle '+DS[2][3]+'}')
DSp=ssps[ssps.IndexOfDevice('F')].SParameters
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
FS=si.sy.VoltageAmplifier(4,'\\beta','Z_{if}','Z_{of}')
ssps._AddEq('F_{11}={\\scriptstyle '+FS[0][0]+'}')
ssps._AddEq('F_{12}={\\scriptstyle '+FS[0][1]+'}')
ssps._AddEq('F_{31}={\\scriptstyle '+FS[2][0]+'}')
ssps._AddEq('F_{33}={\\scriptstyle '+FS[2][2]+'}')
ssps._AddEq('F_{34}={\\scriptstyle '+FS[2][3]+'}')
ssps.LaTeXSolution(size='biggest').Emit()
