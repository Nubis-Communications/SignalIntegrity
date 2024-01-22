from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform

#Code which will be run by a dependent voltage source to perform voltage transformation
#This simple explanation will just scale the input waveform
# inpputs: inputWaveform - contains Waveform to utilize
# outputs: outputWaveform - set to transformed Waveform


outputWaveform = inputWaveform*2
print('RAN IT')


