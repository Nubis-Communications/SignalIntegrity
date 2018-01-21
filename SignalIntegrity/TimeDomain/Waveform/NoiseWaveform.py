'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
import numpy

class NoiseWaveform(Waveform):
    def __init__(self,td,sigma,mean=0.0):
        Waveform.__init__(self,td,numpy.random.normal(mean,sigma,td.K).tolist())