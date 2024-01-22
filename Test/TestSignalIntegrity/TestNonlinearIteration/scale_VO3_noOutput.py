from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform

#Code which will be run by a dependent voltage source to perform voltage transformation
#This simple explanation will just scale VO3 probe (if VO3 not there, exception occurs which is not well handled)
# NOTE - This file does not outpu waveform correctly (does not set outputWaveform) and thus is test if this is handled correctly
# inpputs: inputWaveforms - dictionary containing Waveform to utilize
# outputs: outputWaveform - set to transformed Waveform

#Check if scale variable initialized (passed in)
if 'scale' in systemVars:
    scale = float(systemVars['scale'])
    print('Read in scale facto from system var')
else:
    scale = 2
    print('Default scale factor')

inputWaveform = inputWaveforms['VO3'] #Assuming only 1 waveform input, will pick out that waveform
                                                        #if multiple, then will just pick a random one to scale
#outputWaveform = inputWaveform*scale
print('RAN IT')


