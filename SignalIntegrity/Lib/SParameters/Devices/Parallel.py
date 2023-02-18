"""two-port device placed in parallel with multiple instances"""

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

import math

from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class Parallel(SParameters):
    """s-parameters of two port device placed in parallel with itself multiple times"""
    def __init__(self,f:list, name: str, numberInParallel: int, Z0:float =50, **kwargs):
        """Constructor
        @param f list of float frequencies
        @param name string file name of s-parameter file to read
        @param numberInParallel int number of instances to place in parallel
        @param Z0 (optional) float reference impedance (defaults to 50 ohms)
        @param **kwargs dict (optional, defaults to {}) dictionary of arguments for the file
        """
        self.m_K=numberInParallel
        # pragma: silent exclude
        from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile
        from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
        from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
        # pragma: include
        sdp=SystemDescriptionParser().AddLines(['device D 2','port 1 D 1 2 D 2 3 D 1 4 D 2'])
        sp=SParameterFile(name,None,**kwargs).Resample(f)
        self.m_sspn1=SystemSParametersNumeric(sdp.SystemDescription())
        self.m_dev=sp
        sdp=SystemDescriptionParser().AddLines(['device D 4','device O1 1 open','device O2 1 open',
                                                'connect O1 1 D 3','connect O2 1 D 4','port 1 D 1 2 D 2'])
        self.m_sspn2=SystemSParametersNumeric(sdp.SystemDescription())
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n: int):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        from numpy import linalg
        from SignalIntegrity.Lib.Conversions import S2T
        from SignalIntegrity.Lib.Conversions import T2S
        from SignalIntegrity.Lib.Conversions import ReferenceImpedance
        # pragma: include
        self.m_sspn1.AssignSParameters('D',self.m_dev[n])
        sp=self.m_sspn1.SParameters()
        lp=[1,2]; rp=[3,4]
        sp=T2S(linalg.matrix_power(S2T(sp,lp,rp),self.m_K),lp,rp)
        self.m_sspn2.AssignSParameters('D', sp)
        sp=self.m_sspn2.SParameters()
        sp=ReferenceImpedance(sp,self.m_Z0,self.m_dev.m_Z0)
        return sp

class Series(SParameters):
    """s-parameters of two port device placed in parallel with itself multiple times"""
    def __init__(self,f: float, name: str, numberInSeries: int, Z0: float =50):
        """Constructor
        @param f list of float frequencies
        @param name string file name of s-parameter file to read
        @param numberInSeries int number of instances to place in parallel
        @param Z0 (optional) float reference impedance (defaults to 50 ohms)
        """
        self.m_K=numberInSeries
        # pragma: silent exclude
        from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile
        # pragma: include
        sp=SParameterFile(name).Resample(f)
        self.m_dev=sp
        SParameters.__init__(self,f,None,Z0)
    def __getitem__(self,n: int):
        """overloads [n]
        @return list of list s-parameter matrix for the nth frequency element
        """
        # pragma: silent exclude
        from numpy import linalg
        from SignalIntegrity.Lib.Conversions import S2T
        from SignalIntegrity.Lib.Conversions import T2S
        from SignalIntegrity.Lib.Conversions import ReferenceImpedance
        # pragma: include
        sp=T2S(linalg.matrix_power(S2T(self.m_dev[n]),self.m_K))
        sp=ReferenceImpedance(sp,self.m_Z0,self.m_dev.m_Z0)
        return sp
