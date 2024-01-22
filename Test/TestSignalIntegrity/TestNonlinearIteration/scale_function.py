from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform

#Code which will be run by a dependent voltage source to perform voltage transformation
#This simple explanation will just scale the input waveform
# inpputs: inputWaveforms - dictionary containing Waveform to utilize
# outputs: outputWaveform - set to transformed Waveform

#Check if scale variable initialized (passed in)
if 'scale' in systemVars:
    scale = float(systemVars['scale'])
    print('Read in scale facto from system var')
else:
    scale = 2
    print('Default scale factor')

if (len(inputWaveforms) > 1):
    print('Undefined behavior for > 1 input waveform!')

inputWaveform = inputWaveforms[list(inputWaveforms.keys())[0]] #Assuming only 1 waveform input, will pick out that waveform
                                                        #if multiple, then will just pick a random one to scale
outputWaveform = inputWaveform*scale
print('RAN IT')


