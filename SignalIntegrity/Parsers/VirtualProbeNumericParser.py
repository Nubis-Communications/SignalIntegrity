from VirtualProbeParser import VirtualProbeParser

class VirtualProbeNumericParser(VirtualProbeParser):
    def __init__(self, f=None, args=None):
        VirtualProbeParser.__init__(self, f, args)
    def VirtualProbe(self,ml=None,ol=None,D=None):
        if not self.m_ml is None:
            ml = self.m_ml
        if not self.m_ol is None:
            ol = self.m_ol
        if not self.m_D is None:
            D = self.m_D
        sd=self.SystemDescription()
        if not sd.CheckConnections():
            return
        spc=self.m_spc
        result=[]
        for n in range(len(self.m_f)):
            for d in range(len(self.m_spc)):
                sd[sd.IndexOfDevice(spc[d][0])].pSParameters=spc[d][1][n]
            result.append((self.m_f[n],VirtualProbe(sd).
                TransferFunction(ml,ol,D)))
        return result