import math

# Ports 1 2 3 4 are + - D C
def MixedModeConverter():
    MMCM=matrix([[0,0,1,1],[0,0,-1,1],[1,-1,0,0],[1,1,0,0]])/math.sqrt(2.0)
    return array(MMCM).tolist()

# this one has the right definition for differential and common mode voltage
def MixedModeConverterVoltage():
    DF=1.; CF=2.
    return [[0.,0.,DF/2.,CF/2.],
            [0.,0.,-DF/2.,CF/2.],
            [1./DF,-1./DF,0.,0.],
            [1./CF,1./CF,0.,0.]]

# this is an alternate form of the standard mixed-mode converter
def MixedModeConverter():
    DF=math.sqrt(2.0); CF=math.sqrt(2.0)
    return [[0.,0.,DF/2.,CF/2.],
            [0.,0.,-DF/2.,CF/2.],
            [1./DF,-1./DF,0.,0.],
            [1./CF,1./CF,0.,0.]]
