from numpy import matrix
from numpy import identity

from SignalIntegrity.SystemDescriptions.SystemSParameters import SystemSParameters
from SignalIntegrity.SystemDescriptions.Device import Device

class VirtualProbe(SystemSParameters,object):
    def __init__(self,sd):
        SystemSParameters.__init__(self,sd)
        if hasattr(sd, 'm_ml'):
            self.m_ml = sd.m_ml
        else:
            self.m_ml = None
        if hasattr(sd, 'm_ol'):
            self.m_ol = sd.m_ol
        else:
            self.m_ol = None
        if hasattr(sd, 'm_D'):
            self.m_D = sd.m_D
        else:
            self.m_D = None
    @property
    def pMeasurementList(self):
        return self.m_ml
    @pMeasurementList.setter
    def pMeasurementList(self,ml=None):
        if not ml is None:
            self.m_ml = ml
        return self
    @property
    def pOutputList(self):
        return self.m_ol
    @pOutputList.setter
    def pOutputList(self,ol=None):
        if not ol is None:
            self.m_ol = ol
        return self
    @property
    def pStimDef(self):
        return self.m_D
    @pStimDef.setter
    def pStimDef(self,D=None):
        if not D is None:
            self.m_D = D
        return self
    def StimsPrime(self):
        sv=self.StimulusVector()
        sp=[]
        for s in range(len(sv)):
            sn='m'+str(s+1)
            if sn in sv:
                sp.append(sn)
            else:
                return sp
    def SIPrime(self,symbolic=False):
        n=self.NodeVector()
        m=self.StimulusVector()
        mprime=self.StimsPrime()
        if symbolic:
            SI=Device.SymbolicMatrix('Si',len(n))
        else:
            SI=(matrix(identity(len(n)))-matrix(self.WeightsMatrix())).getI().tolist()
        SiPrime=[[0]*len(mprime) for r in range(len(n))]
        for c in range(len(mprime)):
            for r in range(len(n)):
                SiPrime[r][c]=SI[r][m.index('m'+str(c+1))]
        return SiPrime
    def VoltageExtractionMatrix(self,nl):
        n=self.NodeVector()
        result=[[0]*len(n) for r in range(len(nl))]
        for r in range(len(nl)):
            dp=self[self.DeviceNames().index(nl[r][0])][nl[r][1]-1]
            result[r][n.index(dp.pA)]=1
            result[r][n.index(dp.pB)]=1
        return result