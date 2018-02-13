class TDRWaveformToSParameterConverter(object):
    def __init__(self,
                 WindowHalfWidthTime=0,
                 WindowRaisedCosineDuration=0,
                 Step=True,
                 Length=0,
                 Denoise=False,
                 DenoisePercent=30.,
                 Inverted=False,
                 fd=None
                 ):
        self.whwt=WindowHalfWidthTime
        self.wrcdr=WindowRaisedCosineDuration
        self.step=Step
        self.length=Length
        self.denoise=Denoise
        self.denoisePercent=DenoisePercent
        self.inverted=Inverted
        self.fd=fd
    def RawMeasuredSParameters(self,wfList):
        ports=len(wfList)
        S=[[None for _ in range(ports)] for _ in range(ports)]
        for d in range(ports):
            fc=self.Convert(wfList[d],d)
            for o in range(ports):
                S[o][d]=fc[o]
        f=S[0][0].Frequencies()
        return SParameters(f,
            [[[S[r][c][n] for c in range(ports)] for r in range(ports)]
            for n in range(len(f))])
...
