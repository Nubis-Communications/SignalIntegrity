'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform

class StepWaveform(Waveform):
    def __init__(self,td,Amplitude=1.,StartTime=0.):
        t=td.Times()
        x=[0 if t[k] < StartTime else Amplitude for k in range(td.N)]
        Waveform.__init__(self,td,x)