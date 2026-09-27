class TDRWaveformToSParameterConverter(object):
    def Convert(self,wfListProvided,incidentIndex=0):
        if self.step:
            wfList=[wf.Derivative(removePoint=False,scale=False)
                    for wf in wfList]
        if self.inverted:
            wfList=[wf*-1. for wf in wfList]
        if self.denoise:
            wfList=[WaveletDenoiser.DenoisedWaveform(
                wf,isDerivative=self.step,
                mult=self.sigmaMultiple,
                pct=self.denoisePercent)
                    for wf in wfList]
        if self.length!=0:
            lengthSamples=int(self.length*
                wfList[incidentIndex].td.Fs+0.5)
            wfList=[wf*WaveformTrimmer(0,wf.td.K-lengthSamples)
                for wf in wfList]
        incwf=copy.deepcopy(wfList[incidentIndex])
        maxValueIndex=0
        maxValue=incwf[0]
        for k in range(1,len(incwf)):
            if incwf[k]>maxValue:
                maxValue=incwf[k]
                maxValueIndex=k
        forwardSamples=int(self.wfhwt*incwf.td.Fs)
        reverseSamples=int(self.wrhwt*incwf.td.Fs)
        raisedCosineSamples=int(self.wrcdr*incwf.td.Fs)
        (incidentExtractionWindow,reflectExtractionWindow)=self._ExtractionWindows(
            incwf.td,forwardSamples,reverseSamples,raisedCosineSamples,maxValueIndex)
        incwf=Waveform(incwf.td,[x*w 
            for (x,w) in zip(incwf.Values(),incidentExtractionWindow.Values())])
        wfList=[Waveform(wf.td,[x*w
            for (x,w) in zip(wf.Values(),reflectExtractionWindow.Values())])
                for wf in wfList]
        #wfList[incidentIndex]=wfList[incidentIndex]-incwf
        incwffc=incwf.FrequencyContent(self.fd)
        res=[wf.FrequencyContent(self.fd) for wf in wfList]
        for fc in res:
            for n in range(len(fc)):
                fc[n]=fc[n]/incwffc[n]
        return res
...
