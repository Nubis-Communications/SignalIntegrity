'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import linalg
import math

from SignalIntegrity.Conversions import S2T
from SignalIntegrity.Conversions import T2S
from SignalIntegrity.SParameters.SParameters import SParameters

class MixedModeTLine(SParameters):
    def __init__(self,f,Zd,Td,Zc,Tc,Z0=50.):
        import SignalIntegrity.SParameters.Devices as dev
        from SignalIntegrity.Devices.MixedModeConverter import MixedModeConverter
        from SignalIntegrity.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        self.m_sspn=SystemSParametersNumeric()
        self.m_spdl=[]
        self.m_sspn.AddDevice('MM1',4,MixedModeConverter())
        self.m_sspn.AddDevice('MM2',4,MixedModeConverter())
        self.m_sspn.AddDevice('D',2), self.m_spdl.append(('D',dev.TLine(f,2,Zd/2.,Td,Z0)))
        self.m_sspn.AddDevice('C',2), self.m_spdl.append(('C',dev.TLine(f,2,Zc*2.,Tc,Z0)))
        self.m_sspn.ConnectDevicePort('MM1',3,'D',1)
        self.m_sspn.ConnectDevicePort('MM2',3,'D',2)
        self.m_sspn.ConnectDevicePort('MM1',4,'C',1)
        self.m_sspn.ConnectDevicePort('MM2',4,'C',2)
        self.m_sspn.AddPort('MM1',1,1)
        self.m_sspn.AddPort('MM2',1,3)
        self.m_sspn.AddPort('MM1',2,2)
        self.m_sspn.AddPort('MM2',2,4)
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        for ds in self.m_spdl: self.m_sspn.AssignSParameters(ds[0],ds[1][n])
        return self.m_sspn.SParameters()