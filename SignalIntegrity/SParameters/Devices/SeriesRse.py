'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SParameters.SParameters import SParameters
import SignalIntegrity.Devices as dev

"""
    Series resistance due to skin-effect
    specified as Ohms/sqrt(Hz)
"""
class SeriesRse(SParameters):
    def __init__(self,f,Rse,Z0=50.):
        self.m_Rse=Rse
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return dev.SeriesRse(self.m_f[n],self.m_Rse,self.m_Z0)