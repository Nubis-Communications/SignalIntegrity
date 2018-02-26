# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform

class StepWaveform(Waveform):
    """step waveform"""
    def __init__(self,td,Amplitude=1.,StartTime=0.):
        """Constructor

        constructs a step waveform.

        @param td instance of class TimeDescriptor containing time axis of waveform.
        @param Amplitude (optional) float amplitude of step (defaults to unity).
        @param StartTime (optional) float starting time of the pulse (defaults to zero).

        @note The amplitude can be positive or negative, with negative providing a negative
        pulse.
        @note The step starts at the first sample point after the start time specified.
        """
        x=[0 if t < StartTime else Amplitude for t in td.Times()]
        Waveform.__init__(self,td,x)