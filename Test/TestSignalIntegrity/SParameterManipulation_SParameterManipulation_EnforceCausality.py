class SParameterManipulation(object):
    def EnforceCausality(self):
        for toPort in range(self.m_P):
            for fromPort in range(self.m_P):
                fr=self.FrequencyResponse(toPort+1,fromPort+1)
                ir=fr.ImpulseResponse()
                if ir is not None:
                    t=ir.td
                    Ts=1./ir.td.Fs
                    for k in range(len(t)):
                        if t[k]<=-Ts:
                            ir[k]=0.
                    fr=ir.FrequencyResponse()
                    frv=fr.Response()
                    for n in range(len(frv)):
                        self.m_d[n][toPort][fromPort]=frv[n]
        return self
...
