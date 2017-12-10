'''
Created on Oct 18, 2017

@author: pete
'''
from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Devices.TLineTwoPort import TLineTwoPort

import math

class Offset(SParameters):
    # offset delay in s, offsetLoss in Ohm/s, offsetZ0 in Ohms
    def __init__(self,fList,offsetDelay,offsetZ0,offsetLoss):
        data=[]
        for f in fList:
            alpha=0. if (f==0) else -1j*offsetLoss*math.sqrt(f/1e9)*offsetDelay/(4.*math.pi*f*offsetZ0)
            beta=offsetDelay
            gamma=alpha+beta
            data.append(TLineTwoPort(offsetZ0,gamma,f,50.0))
        SParameters.__init__(self,fList,data)
