class ImpedanceProfile(object):
    def __init__(self,sp,sections,port):
        N = len(sp)-1
        self.m_Td = 1./(4.*sp.f()[N])
        self.m_rho = []
        self.m_Z0 = sp.m_Z0
        S11 = sp.Response(port,port)
        zn2 = [cmath.exp(-1j*2.*math.pi*n/N*1/2) for n in range(N+1)]
        for _ in range(sections):
            rho = 1/(2.*N)*(S11[0].real + S11[N].real +
                 sum([2.*S11[n].real for n in range(1,N)]))
            self.m_rho.append(rho)
            rho2=rho*rho
            S11=[(-S11[n]+S11[n]*rho2*zn2[n]-rho*zn2[n]+rho)/
                (rho2+S11[n]*rho*zn2[n]-S11[n]*rho-zn2[n])
                for n in range(N+1)]
    def __getitem__(self,item):
        return self.m_rho[item]
    def __len__(self):
        return len(self.m_rho)
    def Z(self):
        return [self.m_Z0*(1+rho)/(1-rho) for rho in self]
    def DelaySection(self):
        return self.m_Td
    def SParameters(self,f):
        N = len(f)-1
        Gsp=[None for n in range(N+1)]
        gamma=[1j*2.*math.pi*f[n]*self.m_Td for n in range(N+1)]
        for n in range(N+1):
            tacc=matrix([[1.,0.],[0.,1.]])
            for m in range(len(self)):
                tacc=tacc*matrix(S2T(IdealTransmissionLine(self[m],gamma[n])))
            Gsp[n]=T2S(tacc.tolist())
        sp = SParameters(f,Gsp,self.m_Z0)
        return sp