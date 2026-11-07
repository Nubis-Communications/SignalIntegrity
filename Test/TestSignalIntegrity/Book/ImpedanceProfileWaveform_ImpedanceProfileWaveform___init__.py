class ImpedanceProfileWaveform(Waveform):
    def __init__(self,sp,port=1,method='exact',align='middle',includePortZ=True,
                 adjustForDelay=True):
        tdsp=sp.m_f.TimeDescriptor()
        # assumes middle and no portZ
        tdip=TimeDescriptor(1./(tdsp.Fs*4),tdsp.K/2,tdsp.Fs*2)
        if not align == 'middle':
            tdip.H=tdip.H-1./(tdsp.Fs*4)
        if method == 'exact':
            ip=ImpedanceProfile(sp,tdip.K,port)
            Z=ip.Z()
            delayAdjust=ip.m_fracD
        elif method == 'estimated' or method == 'approximate':
            fr=sp.FrequencyResponse(port,port)
            rho=fr.ImpulseResponse().Integral(addPoint=True,scale=False)
            delayAdjust=fr._FractionalDelayTime()
            finished=False
            for m in range(len(rho)):
                if finished:
                    rho[m]=rho[m-1]
                    continue
                rho[m]=max(-self.rhoLimit,min(self.rhoLimit,rho[m]))
                if abs(rho[m])==self.rhoLimit:
                    finished=True
            if method == 'estimated':
                Z=[max(0.,min(sp.m_Z0*(1+rho[tdsp.K//2+1+k])/
                    (1-rho[tdsp.K//2+1+k]),self.ZLimit)) for k in range(tdip.K)]
            else:
                Z=[max(0.,min(sp.m_Z0+2*sp.m_Z0*rho[tdsp.K//2+1+k],self.ZLimit))
                    for k in range(tdip.K)]
        if includePortZ:
            tdip.H=tdip.H-1./(tdsp.Fs*2)
            tdip.K=tdip.K+1
            Z=[sp.m_Z0]+Z
        if adjustForDelay: tdip.H=tdip.H+delayAdjust/2
        Waveform.__init__(self,tdip,Z)