class ImpedanceProfileWaveform(Waveform):
    def __init__(self,sp,port=1,method='exact',align='middle',includePortZ=True):
        tdsp=sp.m_f.TimeDescriptor()
        # assumes middle and no portZ
        tdip=TimeDescriptor(1./(tdsp.Fs*4),tdsp.K/2,tdsp.Fs*2)
        if not align == 'middle':
            tdip.H=tdip.H-1./(tdsp.Fs*4)
        if method == 'exact':
            Z=ImpedanceProfile(sp,tdip.K,port).Z()
        elif method == 'estimated' or method == 'approximate':
            rho=sp.FrequencyResponse(port,port).ImpulseResponse().\
                Integral(addPoint=True,scale=False)
            if method == 'estimated':
                Z=[sp.m_Z0*(1+rho[tdsp.K/2+1+k])/(1-rho[tdsp.K/2+1+k])
                   for k in range(tdip.K)]
            else:
                Z=[sp.m_Z0+2*sp.m_Z0*rho[tdsp.K/2+1+k] for k in range(tdip.K)]
        if includePortZ:
            tdip.H=tdip.H-1./(tdsp.Fs*2)
            tdip.K=tdip.K+1
            Z=[sp.m_Z0]+Z
        Waveform.__init__(self,tdip,Z)