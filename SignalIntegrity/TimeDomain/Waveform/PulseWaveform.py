# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.TimeDomain.Waveform.StepWaveform import StepWaveform

class PulseWaveform(Waveform):
    """pulse waveform"""
    def __init__(self,td,Amplitude=1.,StartTime=0.,PulseWidth=0):
        """Constructor

        constructs a waveform with mean and normally distributed noise.

        @param td instance of class TimeDescriptor containing time axis of waveform.
        @param Amplitude (optional) float amplitude of pulse (defaults to unity).
        @param StartTime (optional) float starting time of the pulse (defaults to zero).
        @param PulseWidth (optional) float the width of the pulse (defaults to zero).

        @note The amplitude can be positive or negative, with negative providing a negative
        pulse.
        @note if the pulse appears entirely within the samples, then the waveform will be all zero.
        """
        StopTime=StartTime+PulseWidth
        stepup=StepWaveform(td,Amplitude,StartTime)
        stepdown=StepWaveform(td,Amplitude,StopTime)
        Waveform.__init__(self,td,[stepup[k]-stepdown[k] for k in range(len(stepup))])