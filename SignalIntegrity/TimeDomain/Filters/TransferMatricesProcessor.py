class TransferMatricesProcessor(object):
    def __init__(self,transferMatrices):
        self.TransferMatrices=transferMatrices
    def ProcessWaveforms(self,wfl,td=None):
        if td is None:
            td = [wflm.TimeDescriptor().Fs for wflm in wfl]
        ir = self.TransferMatrices.ImpulseResponses(td)
        return [sum([iro[m].FirFilter().FilterWaveform(wfl[m])
            for m in range(len(iro))]) for iro in ir]