"""
 peeled launches
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.ImpedanceProfile.PeeledPortSParameters import PeeledPortSParameters
from SignalIntegrity.Parsers import DeembedderParser
from SignalIntegrity.SystemDescriptions import DeembedderNumeric

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