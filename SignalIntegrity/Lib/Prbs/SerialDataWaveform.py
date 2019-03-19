"""
  serial data waveform
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
import math
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.Prbs.PseudoRandomPolynomial import PseudoRandomPolynomial
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionWaveform,SignalIntegrityException
from SignalIntegrity.App.ToSI import ToSI

class SerialDataWaveform(Waveform):
    """a serial data NRZ waveform"""
    rtvsT=0.5903445
    def __init__(self,pattern,bitRate,amplitude=1.0,risetime=0.,delay=0.,tdOrFs=None):
        """constructor
        @param pattern list of bits in pattern which must be 0 or 1
        @param bitrate float bitrate in bits/s
        @param amplitude (optional, defaults to 1.0) float amplitude of zero centered serial data waveform (pk-pk amplitude is twice this value)
        @param risetime (optional, defaults to 0.0) float risetime of a 1/2 cosine response.
        @param delay (optional, defaults to 0,0) float delay in time into the pattern.
        @param tdOrFs (optional, defaults to None) time descriptor or float sample rate.  If None is specified, then
        the descriptor is generated for one pattern length with a sample rate of 10x the bitrate.  Otherwise, if a float
        is specified, then a time descriptor for one pattern length is generated with the sample rate specified.  Otherwise
        the time descriptor specified is used.
        @return self, a waveform.
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
        T=max(risetime/self.rtvsT,1/td.Fs)
        patternTimeLength=len(pattern)/bitRate
        unitInterval=1./bitRate
        if T>unitInterval:
            # todo: would like to handle this case in the future
            raise SignalIntegrityExceptionWaveform('PRBS risetime too high\nfor waveform generation. '+\
                   'Limit is '+ToSI(unitInterval*self.rtvsT,'s')+' for given bitrate')
        v=[0. for _ in range(len(td))]
        for k in range(len(td)):
            t=td[k]
            timeInPattern=((t-delay)%patternTimeLength+patternTimeLength)%patternTimeLength
            thisBit=int(math.floor(timeInPattern/unitInterval))
            timeInBit=timeInPattern-thisBit*unitInterval
            thisBitValue=pattern[thisBit]
            if timeInBit>=T/2. and (timeInBit-unitInterval)<=-T/2.:
                v[k]=2.*amplitude*(thisBitValue-0.5)
            elif timeInBit<T/2.:
                previousBit=(thisBit-1+len(pattern))%len(pattern)
                previousBitTransition=thisBitValue-pattern[previousBit]
                if previousBitTransition==0:
                    v[k]=2.*amplitude*(thisBitValue-0.5)
                else:
                    v[k]=amplitude*previousBitTransition*math.cos(math.pi*(timeInBit/T+3./2.))
            elif (timeInBit-unitInterval)>-T/2.:
                nextBit=(thisBit+1)%len(pattern)
                nextBitTransition=pattern[nextBit]-thisBitValue
                if nextBitTransition==0:
                    v[k]=2.*amplitude*(thisBitValue-0.5)
                else:
                    v[k]=amplitude*nextBitTransition*math.cos(math.pi*((timeInBit-unitInterval)/T+3./2.))
        Waveform.__init__(self,Waveform(td,v))
    @staticmethod
    def TimeDescriptor(bitRate,sampleRate,patternLength):
        timeLength=patternLength/bitRate
        numPoints=int(math.floor(timeLength*sampleRate+0.5))
        return TimeDescriptor(0.,numPoints,sampleRate)
