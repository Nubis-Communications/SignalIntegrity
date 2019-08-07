"""
 RLGC fit from file
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

from SignalIntegrity.Lib.SParameters.Devices.TLineTwoPortRLGCAnalytic import TLineTwoPortRLGCAnalytic
from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile
from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.Fit.RLGC import RLGCFitter
from SignalIntegrity.Lib.ResultsCache import LinesCache

class RLGCFitFromFile(LinesCache):
    def __init__(self,f,filename,cacheFileName=None,Z0=None):
        self.m_lines='device D1 2 file '+filename
        self.Z0=Z0
        self.m_args=None
        self.m_f=f
        self.spfile=filename
        self.RLGC=None
        LinesCache.__init__(self,'RLGC',cacheFileName)
    def Fit(self):
        if self.CheckCache():
            return self.RLGC
        sp=SParameterFile(self.spfile,self.Z0)
        stepResponse=sp.FrequencyResponse(2,1).ImpulseResponse().Integral()
        threshold=(stepResponse[len(stepResponse)-1]+stepResponse[0])/2.0
        for k in range(len(stepResponse)):
            if stepResponse[k]>threshold: break
        dly=stepResponse.Times()[k]
        rho=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(scale=False).Measure(dly)
        Z0=sp.m_Z0*(1.+rho)/(1.-rho)
        L=dly*Z0; C=dly/Z0; guess=[0.,L,0.,C,0.,0.]
        fitter=RLGCFitter(sp,guess)
        (R,L,G,C,Rse,df)=[r[0] for r in fitter.Solve().Results()]
        print(fitter.Results())
        self.RLGC=TLineTwoPortRLGCAnalytic(self.m_f, R, Rse, L, G, C, df, Z0=50.)
        self.CacheResult()
        return self.RLGC
