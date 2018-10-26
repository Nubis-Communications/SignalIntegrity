import SignalIntegrity.Lib as si

fl=[i*100.*1e6 for i in range(100+1)]
sspnp = si.p.SystemSParametersNumericParser(fl).File('SubCircuitExample2.txt')
spres=sspnp.SParameters().WriteToFile('result.s2p')
