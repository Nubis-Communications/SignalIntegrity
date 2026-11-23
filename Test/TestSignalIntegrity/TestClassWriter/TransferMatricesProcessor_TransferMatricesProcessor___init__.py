class TransferMatricesProcessor(CallBacker):
    def __init__(self,transferMatrices,callback=None):
        self.TransferMatrices=transferMatrices
...
    def ProcessWaveforms(self,wfl,td=None,adaptToLargest=False,time_before_0=None):

        #Replace any 1 sample waveforms with floats - so they are handled as DC values 
        wfl = [wflm[0] if isinstance(wflm,(list,Waveform)) and len(wflm) == 1
               else wflm for wflm in wfl]
        if td is None:
            td = [wflm.td.Fs if isinstance(wflm,Waveform) else None for wflm in wfl]
        ir = self.TransferMatrices.ImpulseResponses(td,time_before_0=time_before_0)
        fr = self.TransferMatrices.FrequencyResponses() # for DC inputs
        result=[]
        for o in range(len(ir)):
            acc=[]
            for i in range(len(ir[o])):
                if isinstance(wfl[i],Waveform):
                    # Disconnected sources must not constrain the output time span.
                    acc.append(0. if all(value == 0. for value in fr[o][i])
                               else ir[o][i].FirFilter().FilterWaveform(wfl[i]))
                else:
                    acc.append((wfl[i]*fr[o][i][0]).real)
            result.append(sum(acc))
        return result
