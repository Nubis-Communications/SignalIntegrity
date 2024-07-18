import SignalIntegrity.Lib as si
from SignalIntegrity.Lib.Equalization.EqualizerTuner import EqualizerTuner
import SignalIntegrity.Lib.Equalization.ClockSNRCalc

import numpy as np

if __name__ == "__main__":
    folder = "C:\\Users\\danie\\Documents\\GitHub\\SignalIntegrity\\Test\\TestSignalIntegrity\\TestEqualizer"

    useLaurentWaveform = False
    useDanielNoise = True
    if (useLaurentWaveform):
        ideal_wvfm = si.td.wf.Waveform().ReadFromFile(f'C:\\Users\\danie\\Documents\\GitHub\\SignalIntegrity\\Test\\TestSignalIntegrity\\TestEqualizer\\ViWf.txt')
        sig_wvfm = si.td.wf.Waveform().ReadFromFile(f'C:\\Users\\danie\\Documents\\GitHub\\SignalIntegrity\\Test\\TestSignalIntegrity\\TestEqualizer\\SIGUSWf.txt')
        if (useDanielNoise):
            noise_wvfm = si.td.wf.Waveform().ReadFromFile(f'{folder}\\NoiseExport_Daniel.txt')
            
            noise_wvfm_clk = noise_wvfm.Adapt(si.td.wf.TimeDescriptor(noise_wvfm.td.H, 5*len(ideal_wvfm), ideal_wvfm.td.Fs))
            noise_wvfm_clk = si.td.wf.Waveform(noise_wvfm_clk.td, [x*(490/180) for x in noise_wvfm_clk])
        else:
            phase = 5
            noise_wvfm = si.td.wf.Waveform().ReadFromFile(f'C:\\Users\\danie\\Documents\\GitHub\\SignalIntegrity\\Test\\TestSignalIntegrity\\TestEqualizer\\NoiseUSWf.txt')
            
            noise_wvfm_clk = noise_wvfm.Adapt(si.td.wf.TimeDescriptor(noise_wvfm.td.H + phase/ideal_wvfm.td.Fs, 5*len(ideal_wvfm), ideal_wvfm.td.Fs))


        rxTuner = EqualizerTuner(45, 6, use_dfe=True, num_dfe_taps=1, DFE_max_tap = 0.85)
        rxTuner._UpsampleFactorReclock = 1

        tuneup_wvfm = rxTuner.TuneupTrained(sig_wvfm, ideal_wvfm, 'PAM4', 200, 1000, invert=False, noise=noise_wvfm_clk, upsampleFinalWaveform=1)

    else: 
        ideal_wvfm = si.td.wf.Waveform().ReadFromFile(f'{folder}\\ViWvfm_Daniel.txt')
        sig_wvfm = si.td.wf.Waveform().ReadFromFile(f'{folder}\\WvfmExport_Daniel.txt')
        noise_wvfm = si.td.wf.Waveform().ReadFromFile(f'{folder}\\NoiseExport_Daniel.txt')
        
        noise_wvfm_clk = noise_wvfm.Adapt(si.td.wf.TimeDescriptor(noise_wvfm.td.H, 5*len(ideal_wvfm), ideal_wvfm.td.Fs))


        rxTuner = EqualizerTuner(45, 6, use_dfe=True, num_dfe_taps=1, DFE_max_tap = 0.85)

        tuneup_wvfm = rxTuner.TuneupTrained(sig_wvfm, ideal_wvfm, 'PAM4', 200, 1000, invert=False, noise=noise_wvfm_clk, upsampleFinalWaveform=8)


    tuneup_wvfm.WriteToFile(f'{folder}/VoEq.txt')
    noise_final = np.std(rxTuner._noise_eq)/rxTuner._scale
    print(f"Noise: {noise_final}")
    a = si.Equalization.ClockSNRCalc.CalcSNR(rxTuner._VoWfdec_eq, rxTuner._noise_eq)
    error_vec = si.Equalization.ClockSNRCalc.CalcErrorVector(rxTuner._VoWfdec_eq)
    print('done')