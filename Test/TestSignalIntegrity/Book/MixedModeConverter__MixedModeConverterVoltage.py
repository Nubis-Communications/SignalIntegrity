def MixedModeConverterVoltage():
    DF=1.; CF=2.
    return [[0.,0.,DF/2.,CF/2.],
            [0.,0.,-DF/2.,CF/2.],
            [1./DF,-1./DF,0.,0.],
            [1./CF,1./CF,0.,0.]]
