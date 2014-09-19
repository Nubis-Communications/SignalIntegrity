from numpy import matrix
from numpy import empty
from numpy import zeros
from numpy import linalg
from numpy import array
#from numpy import array
import math

import SignalIntegrity as si

#######################################################################################
#
# Tests
#
#######################################################################################

def Test():
    D=si.sd.SystemDescription()
    D.AddDevice('D1',3)
    D.AddDevice('D2',2)
    D.AssignSParameters('D1',si.dev.Tee())
    D.AssignSParameters('D2',si.dev.Thru())
    D.ConnectDevicePort('D1',3,'D2',1)
    D.AddPort('D1',1,1)
    D.AddPort('D1',2,2)
    D.AddPort('D2',2,3)
    return si.sd.SystemSParametersCalculator(D).SParameters()
    
def Test2():
    D=si.sd.SystemDescription()
    D.AddDevice('D1',3)
    D.AssignSParameters('D1',si.dev.Tee())
    D.AddPort('D1',1,1)
    D.AddPort('D1',2,2)
    D.AddPort('D1',3,3)
    return si.sd.SystemSParametersCalculator(D).SParameters()

# This test converts a simply pair of ideal thru transmission lines into mixed mode
# s-parameters
def Test3():
    D=si.sd.SystemDescription()
    D.AddDevice('M1',4)
    D.AddDevice('M2',4)
    D.AddDevice('T1',2)
    D.AddDevice('T2',2)
    # ports 1, 2 are differential mode
    D.AddPort('M1',3,1)
    D.AddPort('M2',3,2)
    # ports 3, 4 are common mode
    D.AddPort('M1',4,3)
    D.AddPort('M2',4,4)
    D.ConnectDevicePort('M1',1,'T1',1)
    D.ConnectDevicePort('M2',1,'T1',2)
    D.ConnectDevicePort('M1',2,'T2',1)
    D.ConnectDevicePort('M2',2,'T2',2)
    D.AssignSParameters('M1',si.dev.MixedModeConverter())
    D.AssignSParameters('M2',si.dev.MixedModeConverter())
    D.AssignSParameters('T1',si.dev.Thru())
    D.AssignSParameters('T2',si.dev.Thru())
    return si.sd.SystemSParametersCalculator(D).SParameters()

def Test4():
    K=100
    f=[(n+1)*10e6 for n in range(1000)]
    #SParametersAproximateTLineModel(f,Rsp,Lsp,Csp,Gsp,Rsm,Lsm,Csm,Gsm,Lm,Cm,Gm,Z0,K)
    SP=si.dev.ApproximateFourPortTLine(
        f,
            10.,5.85e-8,2e-11,0.01,
            10.,5.85e-8,2e-11,0.01,
            1.35e-8,1.111e-12,1e-30,50,100)
    import matplotlib.pyplot as plt
    for r in range(4):
        for c in range(4):
            y=[20*math.log(abs(SP[n][r][c]),10) for n in range(len(f))]
            plt.subplot(4,4,r*4+c+1)
            plt.plot(f,y)
    plt.show()

# in this test, we do a reference impedance transformation and compare
# the result to that obtained through T-parameters and through system
# descriptions.
def Test5(Z0):
    S=[[1.0,2.0],[3.0,4.0]]
    S2=si.cvt.ReferenceImpedance(S,Z0)
    T1=si.cvt.S2T(si.dev.ReferenceImpedanceTransformer(50.,Z0))
    T2=si.cvt.S2T(si.dev.ReferenceImpedanceTransformer(Z0,50.))
    T=si.cvt.S2T(S)
    TR=(matrix(T1)*T*T2).tolist()
    S3=si.cvt.T2S(TR)
    D=si.sd.SystemDescription()
    D.AddDevice('T1',2,si.dev.ReferenceImpedanceTransformer(Z0))
    D.AddDevice('T2',2,si.dev.ReferenceImpedanceTransformer(Z0))
    D.AddDevice('S1',2,S)
    D.AddPort('T1',2,1)
    D.AddPort('T2',2,2)
    D.ConnectDevicePort('S1',1,'T1',1)
    D.ConnectDevicePort('S1',2,'T2',1)
    return matrix(si.sd.SystemSParametersCalculator(D).SParameters())-S2

