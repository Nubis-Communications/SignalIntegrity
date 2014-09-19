import SignalIntegrity as si

D=si.sd.SystemDescription()
D.AddDevice('T',1)
D.AddDevice('C',2)
D.AddDevice('R',1)
D.ConnectDevicePort('T',1,'C',1)
D.ConnectDevicePort('C',2,'R',1)
D.AssignM('T',1,'m1')
D=si.sd.VirtualProbe(D)
D.m_ml=[('T',1)]
D.m_ol=[('R',1)]
D.Print()
W = si.helper.Matrix2LaTeX(si.sd.SystemSParametersCalculator(D).WeightsMatrix())
nv = si.helper.Matrix2LaTeX(si.sd.SystemSParametersCalculator(D).NodeVector())
sv = si.helper.Matrix2LaTeX(si.sd.SystemSParametersCalculator(D).StimulusVector())
line1 = '\\left[ \\identity - ' + W + '\\right]' + nv + '^T' + ' = ' + sv + '^T'
print line1