import SignalIntegrity.Lib as si
import SignalIntegrity.App as siapp
import numpy as np
from SignalIntegrity.Lib.TimeDomain.Filters.FilterDescriptor import FilterDescriptor
from SignalIntegrity.Lib.TimeDomain.Filters.FirFilter import FirFilter

def applyNL(input_waveform, NLfilters, MaxHarm = 5, Debug=False):
    '''
    Function which applies given simplified Votlera series based nonlinear filters to the given waveform

    input_waveform: the input waveform
    @param NLfilters: dictionary of nonlinear filters. Keys are Eitehr NLxI which refers to the filter for the xth harmonic, or 'NL3Lag1' or 'NL3Lag2' which is the memory based Lag 1 and
    2 terms of the 3rd order (see X for definition). Each element of the dictionary should either be a float (implying a broadband harmonic distortion) or a ImpulseResponse 
    (implying a frequency dependent harmonic distortion)
    @param MaxHarm: integer referring to the max instaneous harmonic to evaluate.
    '''


    output_wvfm = input_waveform
    avg = np.mean(input_waveform)
    input_waveform = si.td.wf.Waveform(input_waveform.td, [x - avg for x in input_waveform])

    if (Debug):
        print(f"Signal std: {np.std(input_waveform)}")
    for i in range(MaxHarm+1):
        key = f"NL{i}I"
        
        #Applying memoryless nonlinearities
        if (key in NLfilters and NLfilters[key] is not None):
            if (i == 0):
                wvfm_power = 1
            else:
                wvfm_power = si.td.wf.Waveform(input_waveform.td, [x**i for x in input_waveform])
            if (isinstance(NLfilters[key], si.td.wf.ImpulseResponse)):
                #If filter is provided, apply the filter ot the waveform
                output_wvfm = output_wvfm + wvfm_power * NLfilters[key].FirFilter()

                if (Debug):
                    print(f"Harm: {i}, std: {np.std(wvfm_power * NLfilters[key].FirFilter())}")
            else:
                output_wvfm = output_wvfm + wvfm_power * NLfilters[key]

                if (Debug):
                    print(f"Harm: {i}, std: {np.std(wvfm_power * NLfilters[key])}")

    #Apply nonlinearity with memory
    #Currently only 3rd order "Lag 1" and "Lag 2" terms are supported
    if ('NL3Lag1' in NLfilters and NLfilters['NL3Lag1'] is not None):
        input_waveform_lag1_vals = np.square(input_waveform[0:-1])*np.array(input_waveform[1:])
        input_waveform_lag1 = si.td.wf.Waveform(si.td.wf.TimeDescriptor(input_waveform.td.H, len(input_waveform_lag1_vals), input_waveform.td.Fs), [x for x in input_waveform_lag1_vals])
        output_wvfm = output_wvfm + input_waveform_lag1 * NLfilters['NL3Lag1'].FirFilter()
        if (Debug):
            print(f"3Lag1: std: {np.std(input_waveform_lag1 * NLfilters['NL3Lag1'].FirFilter())}")

    if ('NL3Lag2' in NLfilters and NLfilters['NL3Lag2'] is not None):
        input_waveform_lag2_vals = np.array(input_waveform[0:-2])*np.array(input_waveform[2:])*np.array(input_waveform[1:-1])
        input_waveform_lag2 = si.td.wf.Waveform(si.td.wf.TimeDescriptor(input_waveform.Times()[1], len(input_waveform_lag2_vals), input_waveform.td.Fs), [x for x in input_waveform_lag2_vals])
        output_wvfm = output_wvfm + input_waveform_lag2 * NLfilters['NL3Lag2'].FirFilter()
        if (Debug):
            print(f"3Lag2: std: {np.std(input_waveform_lag2 * NLfilters['NL3Lag2'].FirFilter())}")

    if (Debug):
        diff = output_wvfm - input_waveform
        print(f"Total: std: {np.std(diff)}")

    return output_wvfm


if __name__ == "__main__":
        #Todo - make this an explicit test case
        import os 
        dir_path = os.path.dirname(os.path.realpath(__file__))
        test_file_directory = f"{dir_path}/../../../Test/TestSignalIntegrity/TestNonlinear"
        VoTIA_wvfm = si.td.wf.Waveform().ReadFromFile(f'{test_file_directory}/WaveformIn.txt')
        ref_wvfm = si.td.wf.Waveform().ReadFromFile(f'{test_file_directory}/WaveformOut.txt')
        
        NL3rdONL_filter = si.td.wf.ImpulseResponse()
        NL3rdONL_filter.ReadFromFile(f'{test_file_directory}/3rdONLTest.txt')

        NL3rdONLLag2_filter = si.td.wf.ImpulseResponse()
        NL3rdONLLag2_filter.ReadFromFile(f'{test_file_directory}/3rdONLLag1Test.txt')

        NL3rdONLLag1_filter = si.td.wf.ImpulseResponse()
        NL3rdONLLag1_filter.ReadFromFile(f'{test_file_directory}/3rdONLLag2Test.txt')

        a0 = 0.000105308133343
        a2 = 0.033653825068386

        NLFilters = {'NL3I': NL3rdONL_filter, 'NL0I':a0, 'NL2I':a2, 'NL3Lag1':NL3rdONLLag1_filter, 'NL3Lag2':NL3rdONLLag2_filter}

        output_wvfm = applyNL(input_waveform=VoTIA_wvfm, NLfilters = NLFilters)

        diff = output_wvfm - ref_wvfm

        print(f"SNDR: {20*np.log10(np.std(output_wvfm)/np.std(diff))}dB")