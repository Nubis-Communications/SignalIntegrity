import SignalIntegrity.Lib as si
import SignalIntegrity.App as siapp
import numpy as np

class NoisePropagtor:
    def __init__(self, maxFreq, RandomSeed=None) :
        self.maxFreq = maxFreq
        self.noiseSources = {}
        self._randomSeed = RandomSeed

    def addNoiseSource(self, NSName, NSV2Hz, NSInputNode, NSPropNodes = None, NSInputForTransfer = 1, sourceNames = None):
        self.noiseSources[NSName] = {}
        self.noiseSources[NSName]['NSV2Hz'] = NSV2Hz
        self.noiseSources[NSName]['NSInputNode'] = NSInputNode
        self.noiseSources[NSName]['NSPropNodes'] = NSPropNodes
        if (isinstance(NSInputForTransfer, str)):
            if (sourceNames == None):
                raise Exception('If specifying source node by string need to provide source names!')
            else:
                self.noiseSources[NSName]['NSInputForTransfer'] = sourceNames.index(NSInputForTransfer) + 1
        else:

            self.noiseSources[NSName]['NSInputForTransfer'] = NSInputForTransfer




    def calculateNoiseAtNode(self, currOutputProbe, outputWaveformLabels, transferMatrices, maxFreq = None, extraFilter = None):
        """
        Returns noise at Node in V^2/Hz
        """

        if (maxFreq == None):
            maxFreq = self.maxFreq
        allNoises = np.zeros(len(self.noiseSources.keys()))
        noisesSummarized = {}
        for i, key in zip(range(len(self.noiseSources.keys())), self.noiseSources.keys()):
            currNS = self.noiseSources[key]
            noiseSourcePropNodes = currNS['NSPropNodes']
            if (noiseSourcePropNodes is None or currOutputProbe in noiseSourcePropNodes):
                transfer_func = self._calculate_effective_frequency_response(currNS['NSInputNode'], currOutputProbe, outputWaveformLabels, transferMatrices, currNS['NSInputForTransfer'], extraFilter)
                freqMask = np.array(transfer_func.Frequencies()) < maxFreq
                if (isinstance(currNS['NSV2Hz'], si.fd.FrequencyResponse)):
                    noiseFreqContent = currNS['NSV2Hz']
                    noiseFreqContent_new = noiseFreqContent.Resample(transfer_func.FrequencyList())
                    noiseFreqContent_arr = np.array(noiseFreqContent_new.Values('mag'))
                    freq_mask = np.max(noiseFreqContent.Frequencies()) <= noiseFreqContent_new.Frequencies()
                    noiseFreqContent_arr[freq_mask] = 0


                    magnoise = noiseFreqContent_arr
                    allNoises[i] = np.trapz(y=np.abs(np.array(transfer_func)[freqMask]*np.array(magnoise)[freqMask])**2, x=np.array(transfer_func.Frequencies())[freqMask])#Integrate magnitude of transfer function, get V^2
                else:
                    allNoises[i] = np.trapz(y=np.abs(np.array(transfer_func)[freqMask])**2, x=np.array(transfer_func.Frequencies())[freqMask]) * (currNS['NSV2Hz'])#Integrate magnitude of transfer function, get V^2
            else:
                allNoises[i] = 0 

            noisesSummarized[key] = allNoises[i]

        return np.sum(allNoises), noisesSummarized

    def propagateNoiseToEyeDiagrams(self, app, currOutputProbe, outputWaveformLabels, transferMatrices, referenceOutputProbe = None, extraFilter = None):
        if (referenceOutputProbe == None):
            referenceOutputProbe = currOutputProbe #In most cases, reference probe to compute noise from is same as output probe whose eye we want to set
            #Only exception is DFE one
        totalNoise, noisesSummarized = self.calculateNoiseAtNode(referenceOutputProbe, outputWaveformLabels, transferMatrices, extraFilter=extraFilter)
        self.setEyeDiagramNoise(app, currOutputProbe, totalNoise)
        return totalNoise, noisesSummarized
    
    def setEyeDiagramNoise(self, app, currOutputProbe, totalNoise):
        probe=app.Device(currOutputProbe)
        if (type(probe) is siapp.Device.DeviceEyeProbe or type(probe) is siapp.Device.DeviceDifferentialEyeProbe or type(probe) is siapp.Device.DeviceEyeWaveform): #If eye diagram - update the eye
            probe.configuration['JitterNoise']['Noise'] = np.sqrt(totalNoise)


    def calculateNoiseWaveformsAtNode(self, currOutputProbe, outputWaveformLabels, transferMatrices, sampleFrequency = None, extraFilter = None):
            outputWaveforms = {}

            if (self._randomSeed is not None):
                np.random.seed(seed=self._randomSeed)
            if (sampleFrequency == None):
                sampleFrequency = self.maxFreq
            for i, key in zip(range(len(self.noiseSources.keys())), self.noiseSources.keys()):
                #Generate white noise waveform first
                if (isinstance(self.noiseSources[key]['NSV2Hz'], si.fd.FrequencyResponse)):
                    noiseFreqContent = self.noiseSources[key]['NSV2Hz']
                    effectiveMagn = 1
                    #Todo: check if this is correct!!!!
                else:
                    noiseFreqContent = None
                    effectiveMagn = self.noiseSources[key]['NSV2Hz']
                
                
                noiseWvfm = si.td.Waveform.NoiseWaveform(si.td.wf.TimeDescriptor(0, 10**6, sampleFrequency*2), np.sqrt(sampleFrequency * effectiveMagn)) #Baud Rate and total sample size are arbitrarily picked
                transfer_func = self._calculate_effective_frequency_response(self.noiseSources[key]['NSInputNode'], currOutputProbe, outputWaveformLabels, transferMatrices, self.noiseSources[key]['NSInputForTransfer'])

                if (noiseFreqContent is not None):
                    #If noise is shaped, add it as a prefactor to the transfer function
                    noiseFreqContent_new = noiseFreqContent.Resample(transfer_func.FrequencyList())
                    noiseFreqContent_arr = np.array(noiseFreqContent_new)
                    freq_mask = np.max(noiseFreqContent.Frequencies()) <= noiseFreqContent_new.Frequencies()
                    noiseFreqContent_arr[freq_mask] = 0
                    transfer_func = si.fd.FrequencyResponse(transfer_func.Frequencies(), [x*y for x,y in zip(transfer_func, noiseFreqContent_arr)])

                if (extraFilter is not None):
                    extraFilter_new = extraFilter.Resample(transfer_func.FrequencyList)
                    extraFilter_arr = np.array(extraFilter_new)
                    freq_mask = np.max(extraFilter_arr.Frequencies()) <= extraFilter_arr.Frequencies()
                    extraFilter_arr[freq_mask] = 0
                    transfer_func = si.fd.FrequencyResponse(transfer_func.Frequencies(), [x*y for x,y in zip(transfer_func, extraFilter_arr)])

                #Need to mask down tranfer function to match bandwidth of our noise "sources"
                #Note - chance of some numerical error here in the case that maxfrequency is not an exact frequency? 
                transfer_func_freq_mask = np.array(transfer_func.Frequencies()) <= sampleFrequency
                tf_freq_mask = np.array(transfer_func.Frequencies())[transfer_func_freq_mask]
                tf_resp_mask = np.array(transfer_func)[transfer_func_freq_mask]
                transfer_func_mask = si.fd.FrequencyResponse([x for x in tf_freq_mask], [x for x in tf_resp_mask])

                #Apply transform filter and output waveform
                fir_filter=transfer_func_mask.ImpulseResponse().FirFilter()
                noiseWvfmTfm = noiseWvfm * fir_filter
                outputWaveforms[key] = noiseWvfmTfm
            return outputWaveforms

    def _calculate_effective_frequency_response(self, targetInput, targetOutput, outputWaveformLabels, transferMatrices, sourceInput, extraFilter = None):
            """calculates effective frequency response between targetInput and targetOutput probes
                Assumes VP1 and VS1 are only inputs in simulation
            @param targetInput string name of input probe
            @param targetOutput string name of output probes
            @param outputWaveformLabels list of labeled output waveforms from Signal Integrity
            @param transferMatrices list of transfer matrices from signal integrity
            @return instance of FrequencyResponse with the frequency respones between targetInput and targetOutput
            """
            #Todo - add some error handling
            OutputDueToVP1 = transferMatrices.FrequencyResponse(outputWaveformLabels.index(targetOutput) + 1, sourceInput)
            InputDueToVP1 = transferMatrices.FrequencyResponse(outputWaveformLabels.index(targetInput) + 1, sourceInput)

            newFR = [(DVoVP1) / (DViVP1) for DVoVP1, DViVP1 in zip(OutputDueToVP1.Values(), InputDueToVP1.Values())]
            newFR = np.nan_to_num(newFR) #To handle divide by 0 case due to finite bandwidth data for certain S parameters

            if (extraFilter is not None):
                extraFilter = extraFilter.Resample(InputDueToVP1.FrequencyList())
                newFR = [x * y for x,y in zip(newFR, extraFilter.Values())]
            OutputDueToInput =  si.fd.FrequencyResponse(InputDueToVP1.Frequencies(), newFR)

            return OutputDueToInput