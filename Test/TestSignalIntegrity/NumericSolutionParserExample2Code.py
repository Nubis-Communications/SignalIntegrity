import SignalIntegrity as si
sspnp = si.p.SystemSParametersNumericParser([i*100.*1e6 for i in range(100+1)])
sspnp.AddLines(['device L 2 file cable.s2p','device R 2 file filter.s2p',
    'port 1 L 1 2 R 2','connect L 2 R 1']).WriteToFile('example2.txt')
spres=sspnp.SParameters().WriteToFile('result.s2p')
