'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Devices import Mutual
from SignalIntegrity.Devices import SeriesZ
from SignalIntegrity.SParameters.SParameters import SParameters

import math

class SeriesZf(SParameters):
    def __init__(self,f,Z,Z0=50.):
        self.m_Z=Z
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n):
        return SeriesZ(self.m_Z[n],self.m_Z0)
