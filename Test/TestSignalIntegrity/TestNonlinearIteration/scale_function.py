from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform

#Code which will be run by a dependent voltage source to perform voltage transformation
#This simple explanation will just scale the input waveform
# inpputs: inputWaveforms - dictionary containing Waveform to utilize
# outputs: outputWaveform - set to transformed Waveform

#Check if scale variable initialized (passed in)
try:
    print(f"Scale factor: {scale}")
except NameError:
    print('Scale not passed in!')
    scale = 2

inputWaveform = VO1 

outputWaveform = inputWaveform*scale
print('RAN IT')


