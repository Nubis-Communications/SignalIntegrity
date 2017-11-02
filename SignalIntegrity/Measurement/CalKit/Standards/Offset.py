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
            alpha=offsetLoss*math.sqrt(f/1e9)*offsetDelay/offsetZ0*4*math.pi*f
            beta=offsetDelay
            gamma=alpha+1j*beta
            data.append(TLineTwoPort(self.Z0,gamma,f))
        SParameters.__init__(self,fList,data)
