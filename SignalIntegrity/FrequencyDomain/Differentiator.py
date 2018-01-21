'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.FrequencyDomain.FrequencyResponse import FrequencyResponse
from SignalIntegrity.TimeDomain.Waveform.ImpulseResponse import ImpulseResponse

class Differentiator(FrequencyResponse):
    def __init__(self,fl):
        td=fl.TimeDescriptor()
        resp=[0 for k in range(td.K)]
        resp[td.K/2]=td.Fs
        resp[td.K/2+1]=-resp[td.K/2]
        ir=ImpulseResponse(td,resp)
        fr=ir.FrequencyResponse()
        FrequencyResponse.__init__(self,fl,fr.Response())