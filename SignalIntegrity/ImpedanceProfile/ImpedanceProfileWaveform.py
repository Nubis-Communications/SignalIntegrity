# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.
import math
from numpy import matrix,identity

from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.ImpedanceProfile.ImpedanceProfile import ImpedanceProfile
from SignalIntegrity.Conversions import S2T,T2S
from SignalIntegrity.SParameters.SParameters import SParameters
from SignalIntegrity.Devices.TLineTwoPortLossless import TLineTwoPortLossless
"""
    computes the impedance profile waveform from a set of s-parameters using the
    port specified.

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
class ImpedanceProfileWaveform(Waveform):
    rhoLimit=0.99
    ZLimit=10e3
    def __init__(self,sp,port=1,method='exact',align='middle',includePortZ=True,
                 adjustForDelay=True):
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
                Z=[max(0.,min(sp.m_Z0*(1+rho[tdsp.K/2+1+k])/
                    (1-rho[tdsp.K/2+1+k]),self.ZLimit)) for k in range(tdip.K)]
            else:
                Z=[max(0.,min(sp.m_Z0+2*sp.m_Z0*rho[tdsp.K/2+1+k],self.ZLimit))
                    for k in range(tdip.K)]
        if includePortZ:
            tdip.H=tdip.H-1./(tdsp.Fs*2)
            tdip.K=tdip.K+1
            Z=[sp.m_Z0]+Z
        if adjustForDelay: tdip.H=tdip.H+delayAdjust/2
        Waveform.__init__(self,tdip,Z)
    def PeeledSParameters(self,timelen,f):
        Ts=1./self.td.Fs; sections=int(math.floor(timelen/Ts+0.5))
        tp1=[identity(2) for n in range(len(f))]
        for k in range(sections):
            tp1=[tp1[n]*matrix(S2T(TLineTwoPortLossless(self[k],Ts,f[n])))
                for n in range(len(f))]
        return SParameters(f,[T2S(tp.tolist()) for tp in tp1])
