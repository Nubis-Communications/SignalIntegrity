'''
Created on Oct 18, 2017

@author: pete
'''
from SignalIntegrity.Measurement.CalKit.Standards.Offset import Offset

class ThruStandard(Offset):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0,f0=1e9):
        Offset.__init__(self,f,offsetDelay,offsetZ0,offsetLoss,f0)
