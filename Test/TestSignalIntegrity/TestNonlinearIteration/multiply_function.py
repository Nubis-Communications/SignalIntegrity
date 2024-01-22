from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform

#Code which will be run by a dependent voltage source to perform voltage transformation
#This simple example will multiply all the passed in waveforms and then multiply by a global scale factor
# inpputs: inputWaveforms - Dictionary of waveforms to utilize
# outputs: outputWaveform - set to transformed Waveform

#Check if scale variable initialized (passed in)
if 'scale' in systemVars:
    scale = float(systemVars['scale'])
    print('Read in scale facto from system var')
else:
    scale = 1
    print('Default scale factor')

waveformList = list(inputWaveforms.keys())

outputWaveform = inputWaveforms[waveformList[0]]

for i in range(1, len(waveformList)):
    outputWaveform = outputWaveform * inputWaveforms[waveformList[i]]

outputWaveform = outputWaveform*scale
print('RAN IT')


