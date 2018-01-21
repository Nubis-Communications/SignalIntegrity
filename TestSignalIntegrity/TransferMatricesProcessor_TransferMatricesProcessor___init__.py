class TransferMatricesProcessor(CallBacker):
    def __init__(self,transferMatrices,callback=None):
        self.TransferMatrices=transferMatrices
    def ProcessWaveforms(self,wfl,td=None):
        if td is None:
            td = [wflm.td.Fs for wflm in wfl]
        ir = self.TransferMatrices.ImpulseResponses(td)
        result=[]
        for o in range(len(ir)):
            acc=[]
            for i in range(len(ir[o])):
                acc.append(ir[o][i].FirFilter().FilterWaveform(wfl[i]))
            result.append(sum(acc))
        return result
