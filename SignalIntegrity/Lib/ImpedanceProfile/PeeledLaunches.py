"""
 peeled launches
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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.ImpedanceProfile.PeeledPortSParameters import PeeledPortSParameters
from SignalIntegrity.Lib.Parsers import DeembedderParser
from SignalIntegrity.Lib.SystemDescriptions import DeembedderNumeric

class PeeledLaunches(SParameters):
    """S-parameters with launches peeled from them.
    Calculates the impedance profile looking into each port for various time lengths,
    assembles these impedance profiles into s-parameters and deembeds them from the ports.
    """
    def __init__(self,sp,timelen,method='estimated'):
        """Constructor
        @param sp instance of class SParameters of the device
        @param timelen list of float times to peel, one for each port
        @param method string determining method for computing impedance profile
        @remark methods include:
        'estimated' (default) estimate the impedance profile from simulated step response.
        'approximate' use the approximation based on the simulated step response.
        'exact' use the impedance peeling algorithm.
        """
        spp=[PeeledPortSParameters(sp,p+1,timelen[p],method) for p in range(sp.m_P)]
        sddp=DeembedderParser().AddLine('unknown S '+str(sp.m_P))
        for ps in [str(p+1) for p in range(sp.m_P)]:
            sddp.AddLines(['device D'+ps+' 2','connect D'+ps+' 2 S '+ps,
                           'port '+ps+' D'+ps+' 1'])
        sddn=DeembedderNumeric(sddp.SystemDescription()); spd=[]
        for n in range(len(sp)):
            for p in range(sp.m_P): sddn.AssignSParameters('D'+str(p+1),spp[p][n])
            spd.append(sddn.CalculateUnknown(sp[n]))
        SParameters.__init__(self,sp.m_f,spd)
