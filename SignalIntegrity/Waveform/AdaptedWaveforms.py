from TimeDescriptor import TimeDescriptor
from SignalIntegrity.Filters.WaveformTrimmer import WaveformTrimmer
from SignalIntegrity.Filters.FilterDescriptor import FilterDescriptor
from SignalIntegrity.Filters.UpsamplerLinear import Upsampler
from SignalIntegrity.Filters.UpsamplerLinear import FractionalDelayFilter

class AdaptedWaveforms(object):
    def __init__(self,wfl):
        wfcdl=[wf.TimeDescriptor()*WaveformTrimmer(0,0)*
        FractionalDelayFilter(0,True).FilterDescriptor()*
        Upsampler(1).FilterDescriptor() for wf in wfl]
        overlapping=wfcdl[0]
        for wfcd in wfcdl[1:]:
            overlapping=overlapping.Intersection(wfcd)
        # overlapping now contains the overlapping waveform
        usl=[Upsampler(int(round(overlapping.Fs/wfcd.Fs))) for wfcd in wfcdl]
        wfcdbul=[overlapping/us.FilterDescriptor() for us in usl]
        adl=[wfcdbu/wf.TimeDescriptor() for (wfcdbu,wf) in zip(wfcdbul,wfl)]
        fdl=[FractionalDelayFilter(ad.D-int(ad.D),True) for ad in adl]
        adl=[FilterDescriptor(ad.U,int(ad.D),ad.S) for ad in adl]
        trl=[WaveformTrimmer(int(round(ad.TrimLeft())),int(round(ad.TrimRight()))) for ad in adl]
        #self.awfl=[usl[k].FilterWaveform(fdl[k].FilterWaveform(trl[k].TrimWaveform(wfl[k]))) for k in range(len(wfl))]
        #self.awfl=[wfl[k]*trl[k]*fdl[k]*usl[k] for k in range(len(wfl))]
        self.awfl=[wf*tr*fd*us for (wf,tr,fd,us) in zip(wfl,trl,fdl,usl)]
    def __getitem__(self,item):
        return self.awfl[item]
    def __len__(self):
        return len(self.awfl)