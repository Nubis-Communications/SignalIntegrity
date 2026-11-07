"""
  serial data waveform
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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
import math
import numpy as np
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.Prbs.PseudoRandomPolynomial import PseudoRandomPolynomial
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionWaveform,SignalIntegrityException
from SignalIntegrity.Lib.ToSI import ToSI

class SerialDataWaveform(Waveform):
    """a serial data NRZ waveform"""
    rtvsT=0.5903445
    def __init__(self,pattern,bitRate,amplitude=1.0,risetime=0.,delay=0.,tdOrFs=None):
        """constructor
        @param pattern list of bits in pattern which must be 0 or 1
        @param bitRate float bitrate in bits/s
        @param amplitude (optional, defaults to 1.0) float amplitude of zero centered serial data waveform (pk-pk amplitude is twice this value)
        @param risetime (optional, defaults to 0.0) float risetime of a 1/2 cosine response.
        @param delay (optional, defaults to 0,0) float delay in time into the pattern.
        @param tdOrFs (optional, defaults to None) time descriptor or float sample rate.  If None is specified, then
        the descriptor is generated for one pattern length with a sample rate of 10x the bitrate.  Otherwise, if a float
        is specified, then a time descriptor for one pattern length is generated with the sample rate specified.  Otherwise
        the time descriptor specified is used.
        @throw SignalIntegrityExceptionWaveform exception is raised if the risetime exceeds 59% of the unit interval as this causes
        the calculation to fail.
        @todo the failure for a given risetime is due to the simplicity of the algorithm which should be improved at some point.
        this simplicity is that it only looks at adjacent bits to determine the intersymbol effect of the risetime.
        @note the left edge of the first bit in the pattern is at the delay time.  But because a cosine is used for
        the risetime emulation, the 50% point of the cosine is reached at this edge.
        @note the risetime is adjusted if it is too low relative to the sample period.
        """
        if tdOrFs is None:
            sampleRate=10.*bitRate
            td=self.TimeDescriptor(bitRate, sampleRate, len(pattern))
        elif isinstance(tdOrFs,float):
            sampleRate=tdOrFs
            td=self.TimeDescriptor(bitRate, sampleRate, len(pattern))
        else:
            td=tdOrFs
        v=SerialDataWaveform._Render(td,bitRate,[pattern],[amplitude],risetime,delay)
        Waveform.__init__(self,Waveform(td,v))
    @staticmethod
    def _Render(td,bitRate,patterns,amplitudes,risetime,delay):
        """vectorized serial-data renderer
        @param td instance of TimeDescriptor for the output waveform.
        @param bitRate float bit (symbol) rate.
        @param patterns list of equal-length binary patterns (one per bit position).
        @param amplitudes list of float amplitudes, one for each pattern.
        @param risetime float risetime of a 1/2 cosine response.
        @param delay float delay in time into the pattern.
        @return list of float sample values equal to the sum of the serial-data
        waveforms for each (pattern,amplitude) pair.
        @throw SignalIntegrityExceptionWaveform if the risetime exceeds the unit interval.
        @note this reproduces the per-bit SerialDataWaveform algorithm exactly while
        computing the shared sample geometry only once.  Multi-level waveforms are the
        sum of several single-bit waveforms, so rendering them in a single pass (rather
        than building and summing a separate waveform per bit) is what makes them fast.
        """
        N=len(td)
        unitInterval=1./bitRate
        if td.Fs == bitRate and risetime == 0.:
            acc=np.zeros(N)
            for pattern,amplitude in zip(patterns,amplitudes):
                acc=acc+2.*amplitude*(np.asarray(pattern,dtype=float)-0.5)
            return acc.tolist()
        T=max(risetime/SerialDataWaveform.rtvsT,1/td.Fs)
        if T>unitInterval:
            # todo: would like to handle this case in the future
            raise SignalIntegrityExceptionWaveform('PRBS risetime too high\nfor waveform generation. '+\
                   'Limit is '+ToSI(unitInterval*SerialDataWaveform.rtvsT,'s')+' for given bitrate')
        patternLength=len(patterns[0])
        patternTimeLength=patternLength*unitInterval
        t=np.arange(N)/td.Fs+td.H
        timeInPattern=np.mod(np.mod(t-delay,patternTimeLength)+patternTimeLength,patternTimeLength)
        thisBit=np.floor(timeInPattern/unitInterval).astype(np.int64)
        np.clip(thisBit,0,patternLength-1,out=thisBit)
        timeInBit=timeInPattern-thisBit*unitInterval
        risingEdge=timeInBit<T/2.
        fallingEdge=(timeInBit-unitInterval)>-T/2.
        previousBit=(thisBit-1)%patternLength
        nextBit=(thisBit+1)%patternLength
        cosRising=np.cos(np.pi*(timeInBit/T+3./2.))
        cosFalling=np.cos(np.pi*((timeInBit-unitInterval)/T+3./2.))
        acc=np.zeros(N)
        for pattern,amplitude in zip(patterns,amplitudes):
            p=np.asarray(pattern,dtype=float)
            thisBitValue=p[thisBit]
            v=2.*amplitude*(thisBitValue-0.5)
            previousBitTransition=thisBitValue-p[previousBit]
            v=np.where(risingEdge & (previousBitTransition!=0.),
                       amplitude*previousBitTransition*cosRising,v)
            nextBitTransition=p[nextBit]-thisBitValue
            v=np.where(fallingEdge & (nextBitTransition!=0.),
                       amplitude*nextBitTransition*cosFalling,v)
            acc=acc+v
        return acc.tolist()
    @staticmethod
    def TimeDescriptor(bitRate,sampleRate,patternLength):
        timeLength=patternLength/bitRate
        numPoints=int(math.floor(timeLength*sampleRate+0.5))
        return TimeDescriptor(0.,numPoints,sampleRate)
