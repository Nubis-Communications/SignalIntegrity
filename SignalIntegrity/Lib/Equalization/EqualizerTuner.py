import SignalIntegrity.Lib as si
import SignalIntegrity.App as siapp
from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
from SignalIntegrity.Lib.TimeDomain.Filters.FirFilter import FirFilter

import numpy as np
import os
from scipy import signal
import scipy.optimize
import matplotlib.pyplot as plt
import math


class EqualizerTuner():
    def __init__(self,num_ffe_taps, num_precursor_taps, use_dfe, num_dfe_taps, DFE_max_tap = np.inf, use_floating = False, num_floating_tap_banks = 4, num_floating_taps_per_bank = 3, max_ui_floating_taps = 80):

        self._NUM_FFE_TAPS = num_ffe_taps
        self._NUM_PRECURSOR = num_precursor_taps
        self._USE_DFE = use_dfe
        self._NUM_DFE_TAPS = num_dfe_taps


        #(Vo, Vref_up) = si.td.wf.AdaptedWaveforms([Vo, Vref])
        #Aligning waveforms
        self._maxDelay = 20E-9
        self._uiForCorrelation = 750
        self._samplesPerUI = 4
        self._upsampleFactorDelay = 5
        self._UpsampleFactorReclock = 5

        self.DFE_max_tap = DFE_max_tap

        self.optimal_taps = np.zeros((num_ffe_taps))
        if (use_dfe):
            self.optimal_dfe_taps = np.zeros((num_dfe_taps))

        self._use_floating_taps = use_floating
        self._num_floating_tap_banks = num_floating_tap_banks
        self._num_floating_taps_per_bank = num_floating_taps_per_bank
        self._max_ui_floating_taps = max_ui_floating_taps

    def TuneupTrained(self, Vo, Vref, Wvfm_type, init_index, num_samples, invert = False, noise = 0, upsampleFinalWaveform = 1, jitter = 0):
        """
        Performs trained tuneup of Receiver DSP
        """
        #Todo - check if target waveform is long enough for init index and num samples, and init index large enoguh for given number of taps

        def CalculateDelay(refWf, delayedWf, maxDelay, refSegmentStart, refSegmentLength, upsampleFactor=1, subtractMeanDelayed=True):
                if upsampleFactor != 1:
                    us = si.td.f.InterpolatorSinX(upsampleFactor)
                    arefWf = refWf * us
                    adelayedWf = delayedWf * us
                else:
                    arefWf = refWf
                    adelayedWf = delayedWf

                (arefWf, adelayedWf) = si.td.wf.AdaptedWaveforms([arefWf, adelayedWf])
                refSegmentStart = adelayedWf.td.H
                timeOfFirstPointReferenceSegment = arefWf.td.TimeOfPoint(arefWf.td.IndexOfTime(refSegmentStart))
                arefWf = arefWf.Adapt(si.td.wf.TimeDescriptor(timeOfFirstPointReferenceSegment,
                                                            int(math.ceil(refSegmentLength * arefWf.td.Fs)),
                                                            arefWf.td.Fs))
                adelayedWf = adelayedWf.Adapt(si.td.wf.TimeDescriptor(timeOfFirstPointReferenceSegment,
                                                                    int(math.ceil((maxDelay) * adelayedWf.td.Fs)) + arefWf.td.K,
                                                                    adelayedWf.td.Fs))

        #         adelayedWf.WriteToFile('DelayExperiment_delayed.txt')
        #         arefWf.WriteToFile('DelayExperiment_ref.txt')

                stDelayed = np.std(adelayedWf)
                stRef = np.std(arefWf)

                if stDelayed == 0.0:
                    return 0.0
                if stRef == 0.0:
                    return 0.0

                try:
                    stDelayedReciprocal = 1. / np.std(adelayedWf)
                    stRefReciprocal = 1. / np.std(arefWf)
                except:
                    return 0.0

                if stDelayedReciprocal == np.inf:
                    return 0.0
                if stRefReciprocal == np.inf:
                    return 0.0

                meanDelayedWf = np.mean(adelayedWf)
                meanRefWf = np.mean(arefWf)

                if not subtractMeanDelayed:
                    meanDelayedWf = 0.

                corr = np.correlate((adelayedWf - meanDelayedWf) * stDelayedReciprocal, (arefWf - meanRefWf) * stRefReciprocal).tolist()
                corrWf = si.td.wf.Waveform(si.td.wf.TimeDescriptor(adelayedWf.td.H - arefWf.td.H, len(corr), adelayedWf.td.Fs), corr)
        #         corrWf.WriteToFile('DelayExperiment_corr.txt')

                indexOfMax = corrWf.index(max(corrWf))

                side = 2
                x = [corrWf.td.TimeOfPoint(indexOfMax - side + k) for k in range(side * 2 + 1)]
                y = [corrWf[indexOfMax - side + k] for k in range(side * 2 + 1)]
                res = np.polynomial.polynomial.polyfit(x, y, 2)
                return -res[1] / (2.*res[2]), np.max(corr)

        self._samplesPerUI = int(Vo.td.Fs/Vref.td.Fs)
        us = si.td.f.InterpolatorLinear(self._samplesPerUI)
        Vref_up = Vref * us 


        #if (invert):
        #    Vo = Vo*-1 #Inversion due to type of fwaveform

        #Apply jitter
        #Vo_jitter = self._ApplyJitter(Vo, upsampleFactor=50, jitter=90E-15, detJitter = 180E-15)
        scale = np.std(Vref) / np.std(Vo)

        #Scaling "Data" waveform to match that input scale
        Vo = Vo - np.mean(Vo)
        Vo = Vo*scale

        self._scale = scale

        #Now retiming Vo down to sample clock

        #First upsampling waveform and trim excess of ref waveform 

        #Figuring out the delay - check both inverted and not inverted cases to handle both types of channels

        delay, corr = CalculateDelay(Vref_up, Vo, self._maxDelay, Vo.td.H, self._uiForCorrelation * self._samplesPerUI / Vref_up.td.Fs, self._upsampleFactorDelay)
        delay_inver, corr_inver = CalculateDelay(Vref_up, Vo*-1, self._maxDelay, Vo.td.H, self._uiForCorrelation * self._samplesPerUI / Vref_up.td.Fs, self._upsampleFactorDelay)
        if (corr > corr_inver):
            Vo = Vo.DelayBy(-delay)
        else:

            Vo = Vo*-1
            Vo = Vo.DelayBy(-delay_inver)

        
        self._delay = delay
        Nbphases = int(self._UpsampleFactorReclock*self._samplesPerUI)     

        Vo_orig = Vo
        Vref_orig = Vref
        #Try out different phases find where can get best fit
        #This is done since we found that slight changes in clock phase can lead to drastically different results

        best_residual = np.inf
        best_phase = 0 
        all_residuals = np.zeros(Nbphases)
        for i in range(Nbphases):
            phase = (-i/Nbphases + 0.5)/Vref.td.Fs
            Vo = Vo_orig.DelayBy(phase)
            VoUSWf = Vo.Adapt(si.td.wf.TimeDescriptor(Vo.td.H, Vo.td.K * self._UpsampleFactorReclock, Vo.td.Fs * self._UpsampleFactorReclock))

            #Vref=Vref*si.td.f.WaveformTrimmer(int(np.ceil((VoUSWf.td/Vref.td).TrimLeft())) + UpsampleFactorReclock,0) #Cut reference waveform so that first sample is after rightmost
            numClkSamples = math.floor(len(VoUSWf)/Nbphases) #Number of clocked samples in data waveform

            Vref=Vref_orig*si.td.f.WaveformTrimmer(int(np.ceil((VoUSWf.td/Vref_orig.td).TrimLeft())),0)
            VoWfdec=VoUSWf.Adapt(td = si.td.wf.TimeDescriptor(Vref.td.H, numClkSamples, Vref.td.Fs)) #Clocked version of waveform that we will use for equalization. 
            
            #Need to do final trimming to line up waveform, unsure why exactly - maybe bug in SI? 

            if (Vref.td.H > VoWfdec.td.H):
                VoWfdec=VoWfdec*si.td.f.WaveformTrimmer(int(np.ceil((Vref.td/VoWfdec.td).TrimLeft())),0)
            else:
                Vref=Vref*si.td.f.WaveformTrimmer(int(np.ceil((VoWfdec.td/Vref.td).TrimLeft())),0)


            self._PerformTuneup(Vo, VoWfdec, Vref, Wvfm_type, init_index, num_samples, noise=noise*scale, use_floating = self._use_floating_taps)

            all_residuals[i] = self._residual
            print(f"Phase: {phase}, residual: {self._residual}")
            #Check if residual is best AND cursor tap is in corect position - note this is kinda gross I thin we should make it more robust so this does not happen
            #Got rid of cursor tap requirement b/c it was leadin to issues on some waveforms - I was a whole sample off - decided to keep it simple for onw
            if (self._residual < best_residual):
                best_residual = self._residual
                best_phase = phase

        #if (best_residual == np.inf):
        #    raise Exception('Cursor tap is bad')
        #TODO: This is ugly - should not rerun whole thing again feels kinda silly
        self._best_phase = best_phase
        self._scale = scale
        Vo = Vo_orig.DelayBy(best_phase)
        VoUSWf = Vo.Adapt(si.td.wf.TimeDescriptor(Vo.td.H, Vo.td.K * self._UpsampleFactorReclock, Vo.td.Fs * self._UpsampleFactorReclock))

        #Vref=Vref*si.td.f.WaveformTrimmer(int(np.ceil((VoUSWf.td/Vref.td).TrimLeft())) + UpsampleFactorReclock,0) #Cut reference waveform so that first sample is after rightmost
        numClkSamples = math.floor(len(VoUSWf)/Nbphases) #Number of clocked samples in data waveform

        Vref=Vref_orig*si.td.f.WaveformTrimmer(int(np.ceil((VoUSWf.td/Vref_orig.td).TrimLeft())),0)
        VoWfdec=VoUSWf.Adapt(td = si.td.wf.TimeDescriptor(Vref.td.H, numClkSamples, Vref.td.Fs)) #Clocked version of waveform that we will use for equalization. 


        self._VoWfdec = VoWfdec  
        #Need to do final trimming to line up waveform, unsure why exactly - maybe bug in SI? 

        if (Vref.td.H > VoWfdec.td.H):
            VoWfdec=VoWfdec*si.td.f.WaveformTrimmer(int(np.ceil((Vref.td/VoWfdec.td).TrimLeft())),0)
        else:
            Vref=Vref*si.td.f.WaveformTrimmer(int(np.ceil((VoWfdec.td/Vref.td).TrimLeft())),0)

        #self._PerformTuneup(Vo, VoWfdec, Vref, Wvfm_type, init_index, num_samples)
        #Manually undo scale factor so waveform matches input - note this is also doesnt make me happy
        return self._PerformTuneup(Vo, VoWfdec, Vref, Wvfm_type, init_index, num_samples, noise = noise*scale, upsampleFinalWaveform=upsampleFinalWaveform, use_floating = self._use_floating_taps) / scale

    def TuneupBlind(self, Vo, Wvfm_type, init_index, num_samples, BaudRate, clkRecovery=False, noise = 0):
        """
        Performs blind tuneup of receiver DSP
        """
        def LockFreqPhase(waveform, nomSignalRateGuess, clkRecovery = True, freqSearchWindow = 0.5):
            #Clocok recovery

            if (clkRecovery):

                #First perform "edge detection"
                edge_det_fft = np.abs(np.fft.fft(np.abs(np.diff(waveform))))
                fft_freqs = np.fft.fftfreq(n = len(waveform)-1, d = 1/waveform.td.Fs)

                #Now find max value of FFT aorund "guess frequency" which will be clock
                #Have  +/- 50% threshold around nomFreqGuess, think its reasonable
                freqMin = nomSignalRateGuess*(1 - freqSearchWindow)
                freqMax = nomSignalRateGuess*(1 + freqSearchWindow)
                mask = np.logical_and(fft_freqs > freqMin, fft_freqs < freqMax)
                max_ind = np.argmax(np.abs((edge_det_fft[mask]))) #Todo, could try some smooth fitting here to get a more accurate max value
                signalRate = fft_freqs[mask][max_ind]

                #Now have absolute signalRate, I will "round" signalRate so that it is not a weird value and interpolation is not impossible
                signalRateFactor = waveform.td.Fs / signalRate
                signalRateFactor = np.round(signalRateFactor, decimals=1)
                signalRate = waveform.td.Fs / signalRateFactor
            else:
                signalRate = nomSignalRateGuess

            def overlap(waveform, freq, phase):
                period_samples = waveform.td.Fs / freq 
                x_ax = np.arange(len(waveform))
                osc = np.cos(2*np.pi*(x_ax / period_samples) + phase )
                return np.sum(osc*(waveform))
            
            overlap_wrapper = lambda x: -overlap(waveform, signalRate/2, x[0])

            result = scipy.optimize.minimize(overlap_wrapper, x0 = [np.pi/2], bounds=[(0, np.pi)])
            return result.x, signalRate

        Vo = Vo - np.mean(Vo)
        if (Wvfm_type == "PAM4"):
            #PAM4 scale matters - so apply initial scale factor
            scale =np.sqrt((5/9)/np.mean(np.abs(Vo)**2))
            Vo = Vo*scale 
        self._scale = scale
        VoUSWf = Vo.Adapt(si.td.wf.TimeDescriptor(Vo.td.H, Vo.td.K * self._UpsampleFactorReclock, Vo.td.Fs * self._UpsampleFactorReclock))

        phase, signalFreq  = LockFreqPhase(VoUSWf, BaudRate, clkRecovery=clkRecovery)

        phases = np.linspace(-np.pi, np.pi)
        all_residuals = np.zeros(phases.shape)
        best_residual = np.inf
        for i in range(len(phases)):
            offset_time = phases[i]/(2*np.pi)/(signalFreq/2)
            VoWfdec=VoUSWf.Adapt(td = si.td.wf.TimeDescriptor(Vo.td.H + offset_time, len(Vo) - 1, signalFreq))

            self._PerformTuneup(Vo, VoWfdec, None, Wvfm_type, init_index, num_samples, noise=noise*scale, use_floating = self._use_floating_taps)
            all_residuals[i] = self._residual

            if (best_residual > self._residual):
                best_residual = self._residual
                best_phase = phases[i]

        
        offset_time = best_phase/(2*np.pi)/(signalFreq/2)
        VoWfdec=VoUSWf.Adapt(td = si.td.wf.TimeDescriptor(Vo.td.H + offset_time, len(Vo) - 1, signalFreq))
        
        return self._PerformTuneup(Vo, VoWfdec, None, Wvfm_type, init_index, num_samples, noise=noise*scale)/scale
    
    def _PerformTuneup(self, Vo, VoWfdec, Vref, Wvfm_Type, init_index, num_samples, noise = 0, upsampleFinalWaveform = 1, use_floating = False):
        """
        Internal function which actually does the tuneup.
        """
        def setupFFEFilter(taps, num_precursor, tap_upsample_factor = 1, floating_taps = None, ft_pos = None):
            if (floating_taps is None or len(floating_taps) == 0):
                tap_len = len(taps)
            else:
                tap_len = self._max_ui_floating_taps + self._NUM_PRECURSOR #Is it better style if this method doesnt use any class variables? 
            taps_adjust = np.zeros(tap_upsample_factor*(tap_len-1) + 1)
            for i in range(len(taps)):
                taps_adjust[tap_upsample_factor*i] = taps[i]

            if (floating_taps is not None and len(floating_taps) > 0):
                for i in range(len(ft_pos)):
                    for j in range(self._num_floating_taps_per_bank):
                        taps_adjust[int(tap_upsample_factor*(ft_pos[i] + j))] = floating_taps[j + int(i*self._num_floating_taps_per_bank)]
            
            fd = FilterDescriptor(UpsampleFactor=1, DelaySamples=num_precursor*tap_upsample_factor, StartupSamples=len(taps_adjust)-1)
            return FirFilter(fd, taps_adjust)


        def CalculateEqualized(init_waveform, ffe_filt):
            return init_waveform*ffe_filt

        def CalculateDFEEqualizer(init_waveform, DFEtaps, ideal_wvfm, Wvfm_type='NRZ'):
            #Calculates "correction waveform" which should be added to the signal waveform
            #Does not do addition to allow for upsampling to higher sample frequency as desired
            #Assumes init waveform is clocked at decision clock frequency

            if (ideal_wvfm is None):
                decision_array = Decision(init_waveform, Wvfm_Type=Wvfm_type)
            else:
                #Populate decision array with corresponding decisions from ideal training waveform
                decision_array = np.zeros(len(init_waveform))
                for i in range(len(decision_array)):
                    decision_array[i] = ideal_wvfm.Measure(init_waveform.td.TimeOfPoint(i))
            decision_wvfm = si.td.wf.Waveform(init_waveform.td, [x for x in decision_array])
            taps_adjust = np.concatenate(([0], DFEtaps))#Added initial 0 cursor tap for DFE
            filt = setupFFEFilter(taps_adjust, 0)
            return decision_wvfm*filt

        def CalculateError(init_waveform, ideal_waveform, taps, num_precursor, init_index, num_samples, DFEtaps = None, Wvfm_type='NRZ', noise=0, floating_taps = [], ft_pos = [], bias_offset=0):

            FFE_Filt = setupFFEFilter(taps, num_precursor, floating_taps=floating_taps, ft_pos=ft_pos)
            equalizedWfm = CalculateEqualized(init_waveform, FFE_Filt)


            if (DFEtaps is not None):
                dfeEqArray = CalculateDFEEqualizer(equalizedWfm, DFEtaps, ideal_wvfm=ideal_waveform, Wvfm_type=Wvfm_Type)
                #Have to pre trim since adapt seems to cut off a ton of waveform unnecesaraily in addition
                equalizedWfm = equalizedWfm*si.td.f.WaveformTrimmer(int(np.ceil((dfeEqArray.td/equalizedWfm.td).TrimLeft()))-1,0)
                equalizedWfm = equalizedWfm + dfeEqArray
                #Issue - when addition, excss waveform seems to get cut off for some rason


            #Now cut waveform to just region we want to compare
            def IndexOfTime(td, time):
                return int(np.round((time - td.H)*td.Fs)) #Implemented manual index of time function due to issue with truncating in SignalIntegrity
            adjStartIndex = IndexOfTime(equalizedWfm.td, init_waveform.td.TimeOfPoint(init_index))
            if (adjStartIndex < 0 ):
                raise Exception('Start index not big enough')
            equalizedWfm = np.array(equalizedWfm[adjStartIndex:adjStartIndex+num_samples]) #Todo - can prob get rid of this and just use adapted waaveforms - might be less error prone

            #Subtract from ideal waveform in limited region
            if (ideal_waveform is not None):
                return equalizedWfm + bias_offset - ideal_waveform[init_index:init_index+num_samples]
            else:
                idealized_em = Decision(equalizedWfm, Wvfm_type)
                return equalizedWfm + bias_offset - idealized_em

        def CalculateJacobian(init_waveform, taps, num_precursor, init_index, num_samples, DFEtaps = None, ideal_waveform = None, Wvfm_type='NRZ', floating_taps = [], ft_pos = []):
            if (len(floating_taps) == 0):
                tap_len = len(taps)
            else:
                tap_len = len(taps) + len(floating_taps)
            
            if DFEtaps is None:
                jacobian = np.zeros(shape=(num_samples, tap_len + 1))
            else:
                jacobian = np.zeros(shape=(num_samples, tap_len + len(DFEtaps) + 1))
                if (ideal_waveform is None):
                    #For DFE, either use ideal waveform (training data) in Jacobian calc or make decision off of current waveform for "blind" Jacobian 
                    ideal_waveform = Decision(init_waveform, Wvfm_type)
            for i in range(len(taps)):
                jacobian[:, i] = init_waveform[init_index - (i - num_precursor):init_index - (i - num_precursor) + num_samples]
            if (len(floating_taps) > 0):
                for i in range(len(ft_pos)):
                    for j in range(self._num_floating_taps_per_bank):
                        jacobian[:, len(taps) + int(i*self._num_floating_taps_per_bank) + j] = init_waveform[init_index - (int(ft_pos[i]) + j - num_precursor):init_index - (int(ft_pos[i]) + j - num_precursor) + num_samples]
            if DFEtaps is not None:
                for j in range(len(DFEtaps)):
                    jacobian[:, tap_len + j] = ideal_waveform[init_index - (1 + j):init_index - (1 + j) + num_samples]

            #Hardcoded bias term for jacobian (its always 1)
            jacobian[:, -1] = 1
            return jacobian

        def Decision(waveform, Wvfm_Type):
            waveform = waveform - np.mean(waveform)
            #For NRZ
            if (Wvfm_Type == "NRZ"):
                return [-1 if sample < 0 else 1 for sample in waveform]
            elif (Wvfm_Type == "PAM4"):
                #scales input to input power of 5/9 - unsure if I should include or not? 
                decision_wvfm = np.zeros(len(waveform))
                for i in range(len(waveform)):
                    if (waveform[i] < 0):
                        if (waveform[i] < -2/3):
                            decision_wvfm[i] = -1
                        else:
                            decision_wvfm[i] = -1/3
                    else:
                        if (waveform[i] > 2/3):
                            decision_wvfm[i] = 1
                        else: 
                            decision_wvfm[i] = 1/3
                return decision_wvfm
            return None
        
        if (use_floating):
            _EFF_NUM_TAPS = self._max_ui_floating_taps + self._NUM_PRECURSOR
        else:
            _EFF_NUM_TAPS = self._NUM_FFE_TAPS
        taps = np.zeros(shape=_EFF_NUM_TAPS + 1)
        taps[self._NUM_PRECURSOR] = 1 #Send in identity tap initially

        VoWfdec_train = VoWfdec

        #Add noise onto VoWfdec for training purposes - should this not be computed every time - maybe adding too much crap here? 

        if (isinstance(noise, si.td.Waveform.Waveform)):
                if (noise.td.Fs != VoWfdec_train.td.Fs):
                    raise Exception('Noise waveform needs to be at clock sampling rate!')
                else:
                    waveform_w_noise = [a + b for a,b in zip(VoWfdec_train, noise)]
                    VoWfdec_train = si.td.Waveform.Waveform(si.td.Waveform.TimeDescriptor(VoWfdec_train.td.H, len(waveform_w_noise), VoWfdec_train.td.Fs), waveform_w_noise)
        elif (noise > 0):
                noiseWvfm = si.td.Waveform.NoiseWaveform(VoWfdec.td, noise)
                VoWfdec_train = VoWfdec_train + noiseWvfm

        #First optimization on just FFE
        #Add in optiization of "Phase" or fractional delay -
        #Todo (in future?): Add cosntraint on tap size
        error_wrapper = lambda x: CalculateError(VoWfdec_train, Vref, x[0:_EFF_NUM_TAPS], self._NUM_PRECURSOR, init_index, num_samples, Wvfm_type=Wvfm_Type, noise=noise, bias_offset=x[-1])
        jacobian_wrapper = lambda x: CalculateJacobian(VoWfdec_train, x[0:_EFF_NUM_TAPS], self._NUM_PRECURSOR, init_index, num_samples)  
        result = scipy.optimize.least_squares(error_wrapper, taps, jacobian_wrapper, method='lm') #Perform optimization of taps via Levenberg-Marquardt algorithm
        #print(f"Intermediate Taps: {result.x}")
        int_taps = result.x[0:-1]
        print(f"error: {np.sum(np.abs(result.fun)**2)}")

        self.optimal_taps = result.x[0:_EFF_NUM_TAPS]

        if (use_floating and self._num_floating_tap_banks > 0):
            print("Handling floating taps")
            self.ft_pos = self._determineFloatTapLocation(self.optimal_taps)
            num_ft = self._num_floating_tap_banks*self._num_floating_taps_per_bank
            num_taps = num_ft + self._NUM_FFE_TAPS
            init_taps = np.zeros(num_taps + 1)
            error_wrapper = lambda x: CalculateError(VoWfdec_train, Vref, x[0:self._NUM_FFE_TAPS], self._NUM_PRECURSOR, init_index, num_samples, Wvfm_type=Wvfm_Type, noise=noise, floating_taps = x[self._NUM_FFE_TAPS:num_taps], ft_pos = self.ft_pos, bias_offset=x[-1])
            jacobian_wrapper = lambda x: CalculateJacobian(VoWfdec_train, x[0:self._NUM_FFE_TAPS], self._NUM_PRECURSOR, init_index, num_samples, floating_taps = x[self._NUM_FFE_TAPS:num_taps], ft_pos = self.ft_pos)  
            result = scipy.optimize.least_squares(error_wrapper, init_taps, jacobian_wrapper, method='lm') #Perform optimization of taps via Levenberg-Marquardt algorithm
            print(f"error: {np.sum(np.abs(result.fun)**2)}")
            self.optimal_taps = result.x[0:self._NUM_FFE_TAPS]
            self.floating_taps = result.x[self._NUM_FFE_TAPS:num_taps] 

        else:
            num_ft = 0
            self.ft_pos = None
            num_taps = self._NUM_FFE_TAPS
            self.floating_taps = []

        if (self._USE_DFE):
            #Now optimize all taps including dfe taps, starting from optimal ffe taps 
            dfeTaps = np.zeros(shape=self._NUM_DFE_TAPS)
            total_taps = np.concatenate((result.x[0:-1], dfeTaps))
            total_taps = np.append(total_taps, result.x[-1])
            error_wrapper = lambda x: CalculateError(VoWfdec_train, Vref, x[0:self._NUM_FFE_TAPS], self._NUM_PRECURSOR, init_index, num_samples, DFEtaps=x[num_taps:-1], Wvfm_type=Wvfm_Type, noise=noise, floating_taps = x[self._NUM_FFE_TAPS:num_taps], ft_pos = self.ft_pos, bias_offset=x[-1])
            jacobian_wrapper = lambda x: CalculateJacobian(VoWfdec_train, x[0:self._NUM_FFE_TAPS], self._NUM_PRECURSOR, init_index, num_samples, DFEtaps=x[num_taps:-1], ideal_waveform=Vref, Wvfm_type=Wvfm_Type, floating_taps = x[self._NUM_FFE_TAPS:num_taps], ft_pos = self.ft_pos)  
            print(f"New init error: {np.sum(np.abs(error_wrapper(total_taps))**2)}")

            result = scipy.optimize.least_squares(error_wrapper, total_taps, jacobian_wrapper, method='lm') #Perform optimization of taps via Levenberg-Marquardt algorithm

        #result = scipy.optimize.least_squares(error_wrapper, total_taps, jacobian_wrapper, method='lm') #Perform optimization of taps via Levenberg-Marquardt algorithm
            self.optimal_taps = result.x[0:self._NUM_FFE_TAPS]
            self.optimal_DFE_taps = result.x[num_taps:-1]
            self.floating_taps = result.x[self._NUM_FFE_TAPS:num_taps] 
            self.offset_bias = result.x[-1]

            DFE_taps_larger = np.abs(self.optimal_DFE_taps) > self.DFE_max_tap
            if (DFE_taps_larger.any()):
                #DFE taps larger than supposed to be, cap them at maximum and rerun optimizatoin
                print('CAPPING DFE')
                self.optimal_DFE_taps[DFE_taps_larger] = np.sign(self.optimal_DFE_taps[DFE_taps_larger])*self.DFE_max_tap
                #self.optimal_DFE_taps = [-0.85]

                #Rerunning final optimization on the noiseless data but with a fixed DFE
                total_taps = result.x[0:num_taps]
                total_taps = np.append(total_taps, result.x[-1])

                error_wrapper = lambda x: CalculateError(VoWfdec_train, Vref, x[0:self._NUM_FFE_TAPS], self._NUM_PRECURSOR, init_index, num_samples, DFEtaps=self.optimal_DFE_taps, Wvfm_type=Wvfm_Type, noise=noise, floating_taps = x[self._NUM_FFE_TAPS:num_taps], ft_pos = self.ft_pos, bias_offset=x[-1])
                jacobian_wrapper = lambda x: CalculateJacobian(VoWfdec_train, x[0:self._NUM_FFE_TAPS], self._NUM_PRECURSOR, init_index, num_samples, ideal_waveform=Vref, Wvfm_type=Wvfm_Type, floating_taps = x[self._NUM_FFE_TAPS:num_taps], ft_pos = self.ft_pos)  
                print(f"New init error: {np.sum(np.abs(result.fun)**2)}")

                result = scipy.optimize.least_squares(error_wrapper, total_taps, jacobian_wrapper, method='lm')
                self.optimal_taps = result.x[0:self._NUM_FFE_TAPS]
                self.floating_taps = result.x[self._NUM_FFE_TAPS:num_taps] 
                self.offset_bias = result.x[-1]
            print(f"DFE Tap: {self.optimal_DFE_taps}")

        #print(f"Taps: {result.x}")
    
        print('done')
        print(f"error: {np.sum(np.abs(result.fun)**2)}")
        
        


        
        print('Applying optimal tap')
        FFE_Filt = setupFFEFilter(self.optimal_taps, self._NUM_PRECURSOR, floating_taps=self.floating_taps, ft_pos = self.ft_pos)
        VoWfdec_eq = CalculateEqualized(VoWfdec, FFE_Filt) + self.offset_bias

        #Upsampling equalized waveform to original sample rate
        Upsample_factor_final = int(np.round(Vo.td.Fs/VoWfdec_eq.td.Fs))

        FFE_Filt_upsampled = setupFFEFilter(self.optimal_taps, self._NUM_PRECURSOR, Upsample_factor_final, floating_taps=self.floating_taps, ft_pos = self.ft_pos) #For upsampled, use normalized taps
        Vo_eq = CalculateEqualized(Vo, FFE_Filt_upsampled) + self.offset_bias


        us = si.td.f.InterpolatorSinX(upsampleFinalWaveform)
        Vo_eq = Vo_eq * us
        if (self._USE_DFE):
            dfeEqWvfm = CalculateDFEEqualizer(VoWfdec_eq, self.optimal_DFE_taps, ideal_wvfm=Vref, Wvfm_type=Wvfm_Type)
            #Manually upsample in a "repeat" fashion as for each symbol we want a constant DFE output
            VoWfdec_eq= VoWfdec_eq + dfeEqWvfm + self.offset_bias


            #Apply DFE correction to upsampled waveform - do thi smanually on a point by point basis since problem is SI addition does too much interpolation

            #First trip Vo_eq to be within the defined DFE window
            excessLeft = int(np.ceil((dfeEqWvfm.td/Vo_eq.td).TrimLeft()))
            excessRight = int(np.ceil(((Vo_eq.td.H + (Vo_eq.td.K-1)/Vo_eq.td.Fs) - (dfeEqWvfm.td.H + (dfeEqWvfm.td.K-1)/dfeEqWvfm.td.Fs))*Vo_eq.td.Fs)) + 1
            Vo_eq=Vo_eq*si.td.f.WaveformTrimmer(excessLeft,excessRight)
            Vo_eq = Vo_eq + self.offset_bias
            for i in range(len(Vo_eq)):
                correspondingIndex = np.round(dfeEqWvfm.td.IndexOfTime(Vo_eq.td.TimeOfPoint(i), Integer=False)) #Matching correction index of current Vo index
                Vo_eq[i] += dfeEqWvfm[int(correspondingIndex)] #Apply correction
        print(f"error: {np.sum(np.abs(result.fun)**2)}")


        #Calculate equalized noise 

        if (isinstance(noise, si.td.Waveform.Waveform)):
            self._noise_eq = CalculateEqualized(noise, FFE_Filt)
        elif (noise > 0):
            self._noise_eq = si.td.Waveform.NoiseWaveform(VoWfdec.td, noise)
        self._residual = np.sum(np.abs(result.fun)**2)
        self._VoWfdec_eq = VoWfdec_eq
        self._ideal_data = Vref
        self._noise = noise
        return Vo_eq


    def _ApplyJitter(self, Vo, upsampleFactor, jitter, detJitter):
            us = si.td.f.InterpolatorSinX(upsampleFactor)
            Vo_up = Vo * us

            time_points = upsampleFactor*20 + 1 #Implicit assumption that waveform is not oversmapled by 20x, not iddeal should fix here
            all_times = np.linspace(start=-time_points/2/Vo_up.td.Fs, stop=time_points/2/Vo_up.td.Fs, num=time_points)
            gauss_filter = np.exp(-((all_times-detJitter/2)/jitter)**2/2) + np.exp(-((all_times+detJitter/2)/jitter)**2/2) #Two dirac jitter method


            fd = FilterDescriptor(UpsampleFactor=1, DelaySamples=(len(all_times)-1)/2, StartupSamples=len(all_times)-1)
            fullFilt =  FirFilter(fd, [x for x in gauss_filter])
            Vo_filt = Vo_up * fullFilt
            dec_wvfm = Vo_filt[0::upsampleFactor]
            full_wvfm = si.td.Waveform.Waveform(si.td.wf.TimeDescriptor(Vo_filt.td.H,
                                                            len(dec_wvfm),
                                                            Vo.td.Fs), dec_wvfm)
            return full_wvfm

    def _determineFloatTapLocation(self, taps):
        #Determines ideal location of floating taps based on a long optimized FFE
        #Finds optimal position which maximizes the total absolute sum of the optimized FFE taps
        if (len(taps) < self._max_ui_floating_taps):
            raise Exception('Not big enouh tap to calculate floating tap')
        best_value, best_pos = self._determineFloatTapLocation_rec(taps, self._num_floating_tap_banks, self._num_floating_taps_per_bank, self._max_ui_floating_taps + self._NUM_PRECURSOR, self._NUM_FFE_TAPS)
        print(f"Floating tap: best val: {best_value}, best position: {best_pos}")
        return best_pos
    def _determineFloatTapLocation_rec(self, taps, num_floating_tap_banks, num_taps_per_bank, max_ui, minimum_offset):
        if (num_floating_tap_banks == 0):
            return 0, np.array([])
        else:
            max_offset = max_ui - num_floating_tap_banks*num_taps_per_bank
            best_value = -1
            best_pos = -1
            for i in range(minimum_offset, max_offset+1):
                value_add = np.sum(np.abs(taps[i:i+num_taps_per_bank]))
                value_rec, pos_rec = self._determineFloatTapLocation_rec(taps, num_floating_tap_banks-1, num_taps_per_bank, max_ui, i + num_taps_per_bank)
                if (best_value < (value_rec + value_add)):
                    best_value = value_rec + value_add
                    best_pos = np.append([i], pos_rec)
            return best_value, best_pos

    def _generate_full_linear_taps_array(self, upsample=1):
        if (not self._use_floating_taps):
            tap_len = len(self.optimal_taps)*upsample
        else:
            tap_len = (self._max_ui_floating_taps + self._NUM_PRECURSOR)*upsample  #Is it better style if this method doesnt use any class variables? 
        taps_adjust = np.zeros(tap_len)
        for i in range(len(self.optimal_taps)):
            taps_adjust[i*upsample] = self.optimal_taps[i]

        if (self._use_floating_taps):
            for i in range(len(self.ft_pos)):
                for j in range(self._num_floating_taps_per_bank):
                    taps_adjust[int((self.ft_pos[i] + j))*upsample] = self.floating_taps[j + int(i*self._num_floating_taps_per_bank)]
        return taps_adjust





if __name__ == "__main__":
    target_fn = "ACC/ACCOut2"
    ref_fn = 'ACC/ACCIdeal'
    invert = False
    blind = False

    Wvfm_Type = 'PAM4'

    #Info for equalization
    INIT_INDEX = 100 #Todo - shouldnt be specified
    NUM_SAMPLES = 1000
    NUM_FFE_TAPS = 10
    NUM_PRECURSOR = 0

    #DFE_settings
    USE_DFE = False
    NUM_DFE_TAPS = 3

    #For blind
    BaudRate = 56E9
    clkRecovery = True

    tuner = DaRxEqTuner(NUM_FFE_TAPS, NUM_PRECURSOR, USE_DFE, NUM_DFE_TAPS, 0.85, 4, 3, 30)
    taps = np.zeros(30)
    taps[27:30] = 1
    taps[0:5] = 1
    taps[15:18] = 1

    loc = tuner._determineFloatTapLocation(taps)

    Vo = si.td.wf.Waveform().ReadFromFile(os.path.abspath(f"Projects/{target_fn}.txt"))

    if (not blind):
        Vref = si.td.wf.Waveform().ReadFromFile(os.path.abspath(f"Projects/{ref_fn}.txt"))
        
        #Scale and center ideal waveform
        scale = 1/((np.max(Vref) - np.min(Vref))/2)
        Vref = si.td.wf.Waveform(Vref.td, [(x - np.mean(Vref))*scale for x in Vref])
        Vequalized = tuner.TuneupTrained(Vo, Vref, Wvfm_Type, INIT_INDEX, NUM_SAMPLES, invert)
    else:
        Vequalized = tuner.TuneupBlind(Vo, Wvfm_Type, INIT_INDEX, NUM_SAMPLES, BaudRate, clkRecovery)

    Vequalized.WriteToFile(f"{target_fn}_eq.txt")


    
