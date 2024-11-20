class TransferMatricesProcessor(CallBacker):
    def __init__(self,transferMatrices,callback=None):
        self.TransferMatrices=transferMatrices
...
    def ProcessWaveforms(self,wfl,td=None,adaptToLargest=False):
        if td is None:
            td = [wflm.td.Fs if not isinstance(wflm,DCWaveform) else None
                  for wflm in wfl]
        ir = self.TransferMatrices.ImpulseResponses(td)
        fr = self.TransferMatrices.FrequencyResponses() # for DC inputs
        result=[]
        for o in range(len(ir)):
            acc=[]
            for i in range(len(ir[o])):
                acc.append(ir[o][i].FirFilter().FilterWaveform(wfl[i])
                           if not isinstance(wfl[i],DCWaveform)
                           else DCWaveform((wfl[i].Value()*fr[o][i][0]).real))
            result.append(sum(acc))
        return result