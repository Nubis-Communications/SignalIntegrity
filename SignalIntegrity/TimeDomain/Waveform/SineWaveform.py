'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
import math

from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform

class SineWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,Frequency=1e6,Phase=0.):
        times=td.Times()
        x=[Amplitude*math.sin(2.*math.pi*Frequency*t+Phase/2./math.pi) for t in times]
        Waveform.__init__(self,td,x)