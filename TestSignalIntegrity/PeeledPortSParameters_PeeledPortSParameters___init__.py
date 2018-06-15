class PeeledPortSParameters(SParameters):
    def __init__(self,sp,port,timelen):
        ip=ImpedanceProfileWaveform(sp,port,
            method='estimated',includePortZ=False)
        Ts=1./ip.td.Fs; sections=int(math.floor(timelen/Ts+0.5))
        tp1=[identity(2) for n in range(len(sp.f()))]
        for k in range(sections):
            tp1=[tp1[n]*matrix(S2T(TLineTwoPortLossless(ip[k],Ts,sp.m_f[n])))
                for n in range(len(sp.m_f))]
        SParameters.__init__(self,sp.m_f,[T2S(tp.tolist()) for tp in tp1])