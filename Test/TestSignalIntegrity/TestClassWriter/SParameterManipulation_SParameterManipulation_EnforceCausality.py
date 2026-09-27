class SParameterManipulation(object):
...
    def EnforceCausality(self,preserveDC=False):
        self.ResampleToEvenlySpaced()
        for toPort in range(self.m_P):
            for fromPort in range(self.m_P):
                fr=self.FrequencyResponse(toPort+1,fromPort+1)
                ir=fr.ImpulseResponse()
                dc=sum(ir)
                if ir is not None:
                    t=ir.td; Ts=1./ir.td.Fs
                    for k in range(len(t)):
                        if t[k]<=-Ts: ir[k]=0.
                    newdc=sum(ir)
                    if preserveDC and (newdc != 0):
                        ir=ir*(dc/newdc)
                    fr=ir.FrequencyResponse()
                    frv=fr.Response()
                    for n in range(len(frv)): self.m_d[n][toPort][fromPort]=frv[n]
        self.ResampleToUnevenlySpaced()
        return self
...
