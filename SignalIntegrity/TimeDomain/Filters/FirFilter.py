'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from numpy import convolve
#from PySICppLib import PySIConvolve

class FirFilter(object):
    def __init__(self,fd,ft):
        self.m_fd = fd
        self.m_ft=ft
    def FilterTaps(self):
        return self.m_ft
    def FilterDescriptor(self):
        return self.m_fd
    def FilterWaveform(self,wf):
        # pragma: silent exclude
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        # pragma: include
        td = wf.TimeDescriptor()*self.FilterDescriptor()
        #filteredwf=PySIConvolve(wf.Values(),self.FilterTaps())
        filteredwf=convolve(wf.Values(),self.FilterTaps(),'valid').tolist()
        return Waveform(td,filteredwf)
    def Print(self):
        self.FilterDescriptor().Print()
        print str(self.FilterTaps())