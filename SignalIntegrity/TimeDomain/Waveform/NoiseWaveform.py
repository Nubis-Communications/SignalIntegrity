# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
import numpy

class NoiseWaveform(Waveform):
    """noise waveform"""
    def __init__(self,td,sigma,mean=0.0):
        """Constructor

        constructs a waveform with mean and normally distributed noise.

        @param td instance of class TimeDescriptor containing time axis of waveform.
        @param sigma float non-zero value of the rms value of the noise
        @param mean (optional) float containing the mean value of the waveform
        """
        Waveform.__init__(self,td,numpy.random.normal(mean,sigma,td.K).tolist())