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

class RLGCFitFromFile(object):
    """fits a two-port RLGC model to s-parameters from a file"""
    def __init__(self,f,filename,scale=1,Z0=None):
        """Constructor
        @param f list of float frequencies
        @param filename string name of s-parameter file or project that produces s-parameters
        @param scale float (optional, defaults to 1.0) scaling to be applied on resulting fit
        @param Z0 float (optional, defaults to None) reference impedance
        @note fitting is not performed until an item from the fitted model is requested
        """
        self.scale=scale
        self.Z0=Z0
        self.m_f=f
        self.spfile=filename
        self.RLGC=None
    def Fit(self):
        """Fits a two-port RLGC model for the specified s-parameter file
        @see see RLGC
        """
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
        (R,L,G,C,Rse,df)=fitter.Solve().Results()
#         print "series resistance: "+ToSI(R,'ohm')
#         print "series inductance: "+ToSI(L,'H')
#         print "shunt conductance: "+ToSI(G,'S')
#         print "shunt capacitance: "+ToSI(C,'F')
#         print "skin-effect resistance: "+ToSI(Rse,'ohm/sqrt(Hz)')
#         print "dissipation factor: "+ToSI(df,'')
        s=self.scale
        self.RLGC=TLineTwoPortRLGCAnalytic(self.m_f, R*s, Rse*s, L*s, G*s, C*s, df, Z0=50.)
        return self.RLGC
    def __getitem__(self,item):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        @note if a fit has not yet been performed, it is performed prior to obtaining the element
        """
        if self.RLGC is None:
            self.RLGC = self.Fit()
        return self.RLGC[item]
