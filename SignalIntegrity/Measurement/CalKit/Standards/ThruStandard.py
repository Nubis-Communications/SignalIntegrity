'''
Created on Oct 18, 2017

@author: pete
'''

from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Measurement.CalKit.Standards.Offset import Offset

class ThruStandard(SParameters):
    def __init__(self,f,offsetDelay=0.0,offsetZ0=50.0,offsetLoss=0.0):
        SParameters.__init__(self,f,Offset(f,offsetDelay,offsetZ0,
                                           offsetLoss).m_d)
