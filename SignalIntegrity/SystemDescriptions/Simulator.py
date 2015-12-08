from numpy import matrix
from numpy import identity

from SignalIntegrity.SystemDescriptions.SystemSParameters import SystemSParameters
from SignalIntegrity.SystemDescriptions.Device import Device
from SignalIntegrity.Devices import Open
from SignalIntegrity.Devices import Thru
from SignalIntegrity.Devices import Ground
from SignalIntegrity.PySIException import PySIExceptionSimulator

class Simulator(SystemSParameters,object):
    def __init__(self,sd=None):
        SystemSParameters.__init__(self,sd)
        self.m_ol = sd.m_ol if hasattr(sd, 'm_ol') else None
    def Check(self):
        if self.m_ol is None:
            raise PySIExceptionSimulator('no outputs')
        if len(self.StimsPrime()) == 0:
            raise PySIExceptionSimulator('no sources')
    @property
    def pOutputList(self):
        return self.m_ol
    @pOutputList.setter
    def pOutputList(self,ol=None):
        if not ol is None: self.m_ol = ol
        return self
    def AddVoltageSource(self,Name,Ports):
        if Ports == 1: self.AddDevice(Name,Ports,Ground(),'voltage source')
        elif Ports == 2: self.AddDevice(Name,Ports,Thru(),'voltage source')
        stimNumber=len(self.StimsPrime())+1
        for p in range(Ports): self.AssignM(Name,p+1,'m'+str(stimNumber+p))
    def AddCurrentSource(self,Name,Ports):
        if Ports == 1: self.AddDevice(Name,Ports,Open(),'current source')
        elif Ports == 2: self.AddDevice(Name,Ports,[[1.,0.],[0.,1.]],'current source')
        stimNumber=len(self.StimsPrime())+1
        for p in range(Ports): self.AssignM(Name,p+1,'m'+str(stimNumber+p))
    def SourceVector(self):
        sv=[]
        for d in self:
            if d.Type == 'current source' or d.Type == 'voltage source':
                sv.append(d.Name)
        return sv
    def SourceToStimsPrimeMatrix(self,symbolic=False):
        sv=self.SourceVector()
        sp=self.StimsPrime()
        Z0='Z0' if symbolic else 50.
        sm = [[0]*len(sv) for r in range(len(sp))]
        for s in sv:
            d=self[self.IndexOfDevice(s)]
            if d.Type == 'current source':
                if len(d) == 1:
                    sm[sp.index(d[0].M)][sv.index(s)] = Z0
                elif len(d) == 2:
                    sm[sp.index(d[0].M)][sv.index(s)] = Z0
                    sm[sp.index(d[1].M)][sv.index(s)] = Z0
            elif d.Type == 'voltage source':
                if len(d) == 1:
                    sm[sp.index(d[0].M)][sv.index(s)] = 1.
                elif len(d) == 2:
                    sm[sp.index(d[0].M)][sv.index(s)] = -1./2.
                    sm[sp.index(d[1].M)][sv.index(s)] = 1./2.
        return sm
    def StimsPrime(self):
        sv=self.StimulusVector()
        sp=[]
        for s in range(len(sv)):
            sn='m'+str(s+1)
            if sn in sv: sp.append(sn)
            else: return sp
    def SIPrime(self,symbolic=False):
        from numpy.linalg.linalg import LinAlgError
        n=self.NodeVector()
        m=self.StimulusVector()
        mprime=self.StimsPrime()
        if symbolic: SI=Device.SymbolicMatrix('Si',len(n))
        else:
            # pragma: silent exclude
            try:
            # pragma: include outdent
                SI=(matrix(identity(len(n)))-matrix(self.WeightsMatrix())).getI().tolist()
            # pragma: silent exclude indent
            except:
                raise PySIExceptionSimulator('numerical error - cannot invert matrix')
            # pragma: include
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
            result[r][n.index(dp.A)]=1
            result[r][n.index(dp.B)]=1
        return result