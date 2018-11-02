"""
 Impedance Profile Waveform
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

from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.ImpedanceProfile.ImpedanceProfile import ImpedanceProfile

class ImpedanceProfileWaveform(Waveform):
    """Computes the impedance profile waveform from a set of s-parameters using the port specified.

    method is 'exact','estimated' or 'approximate'
    'exact' specifies to use the DFT method to deembed sections of impedance found
    at an interface.  This method is exact in simulation.
    'estimated' and 'approximate' both use the step response of the system computed
    from the s-parameters.  'estimated' calculates the Z exactly, assuming the step
    response contains rho (the reflection coefficient), which is an estimate because
    rho is polluted by multiple reflections.  'approximate' calculates Z using a simple
    offset and scaling like would be employed when viewing a TDR waveform.
    There is no reason to use 'approximate' - except for educational purposes.
    'exact' can be quite unstable.  'Estimated' is actually usually the best method.

    align is either 'middle' or 'interface'
    'middle' means that the impedance for each point produced is at the corresponding time
    representing the the middle of a transmission line section.  
    'interface' means that the time of the impedance is the time of the left edge of a
    transmission line with the corresponding impedance.

    includePortZ is set to True if you want the first point to be the impedance of the
    port used to take the measurement.
    """
    rhoLimit=0.99
    ZLimit=10e3
    def __init__(self,sp,port=1,method='exact',align='middle',includePortZ=True,
                 adjustForDelay=True):
        """Constructor
        @param sp instance of class SParameters of the device
        @param port (optional) integer 1 based port number (defaults to port 1)
        @param method (optional) string method for computation (defaults to 'exact')
        @param align (optional) string alignment of impedancance in waveform (defaults to 'middle')
        @param includePortZ (optional) boolean whether to put the port reference impedance as the first point. (defaults to True)
        @param adjustForDelay (optional) boolean whether to adjust for the delay in the impulse response (defaults to True)
        @remark computation methods include:
        'exact' (default) - calculates  using reflection coefficient of first point computed from DFT and deembedding.
        (this method takes longer and can diverge due to buildup of numerical inaccuracies.)
        'estimated' - calculates the reflection coefficients directly from the step response.
        'approximate' - calculates the reflection coefficients from the step response using an approximation.
        @remark alignment methods include:
        'middle' (default) - shows the impedance in the middle of the sample period distance along the line.
        'front' - shows the impedance measured at the front of the line. 
        """
        tdsp=sp.m_f.TimeDescriptor()
        # assumes middle and no portZ
        tdip=TimeDescriptor(1./(tdsp.Fs*4),tdsp.K/2,tdsp.Fs*2)
        if not align == 'middle':
            tdip.H=tdip.H-1./(tdsp.Fs*4)
        if method == 'exact':
            ip=ImpedanceProfile(sp,tdip.K,port)
            Z=ip.Z()
            delayAdjust=ip.m_fracD
        elif method == 'estimated' or method == 'approximate':
            fr=sp.FrequencyResponse(port,port)
            rho=fr.ImpulseResponse().Integral(addPoint=True,scale=False)
            delayAdjust=fr._FractionalDelayTime()
            finished=False
            for m in range(len(rho)):
                if finished:
                    rho[m]=rho[m-1]
                    continue
                rho[m]=max(-self.rhoLimit,min(self.rhoLimit,rho[m]))
                if abs(rho[m])==self.rhoLimit:
                    finished=True
            if method == 'estimated':
                Z=[max(0.,min(sp.m_Z0*(1+rho[tdsp.K//2+1+k])/
                    (1-rho[tdsp.K//2+1+k]),self.ZLimit)) for k in range(tdip.K)]
            else:
                Z=[max(0.,min(sp.m_Z0+2*sp.m_Z0*rho[tdsp.K//2+1+k],self.ZLimit))
                    for k in range(tdip.K)]
        if includePortZ:
            tdip.H=tdip.H-1./(tdsp.Fs*2)
            tdip.K=tdip.K+1
            Z=[sp.m_Z0]+Z
        if adjustForDelay: tdip.H=tdip.H+delayAdjust/2
        Waveform.__init__(self,tdip,Z)