'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
class AdaptedWaveforms(object):
    def __init__(self,wfl):
        from TimeDescriptor import TimeDescriptor
        from SignalIntegrity.TimeDomain.Filters.WaveformTrimmer import WaveformTrimmer
        from SignalIntegrity.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
        from SignalIntegrity.TimeDomain.Filters.InterpolatorSinX import InterpolatorSinX
        from SignalIntegrity.TimeDomain.Filters.InterpolatorSinX import FractionalDelayFilterSinX
        from SignalIntegrity.TimeDomain.Waveform.Waveform import Waveform
        #upsample all of the waveforms first
        ufl=[int(round(wfl[0].TimeDescriptor().Fs/wf.TimeDescriptor().Fs)) for wf in wfl]
        wfl=[wf if uf == 1 else wf*InterpolatorSinX(uf) for (uf,wf) in zip(ufl,wfl)]
        adl=[wfl[0].TimeDescriptor()/wf.TimeDescriptor() for wf in wfl]
        fdl=[ad.D-int(ad.D) for ad in adl]
        wfl=[wf if fd == 0.0 else wf*FractionalDelayFilterSinX(fd,True) for (fd,wf) in zip(fdl,wfl)]
        overlapping=wfl[0].TimeDescriptor()
        for wf in wfl[1:]: overlapping=overlapping.Intersection(wf.TimeDescriptor())
        # overlapping now contains the overlapping waveform
        adl=[overlapping/wf.TimeDescriptor() for wf in wfl]
        trl=[WaveformTrimmer(max(0,int(round(ad.TrimLeft()))),max(0,int(round(ad.TrimRight())))) for ad in adl]
        self.awfl=[wf*tr for (wf,tr) in zip(wfl,trl)]
    def __getitem__(self,item):
        return self.awfl[item]
    def __len__(self):
        return len(self.awfl)