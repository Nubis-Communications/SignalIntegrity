from SignalIntegrity.SystemDescriptions.VirtualProbe import VirtualProbe

from SignalIntegrity.Devices import Open
from SignalIntegrity.Devices import Thru
from SignalIntegrity.Devices import Ground

class Simulator(VirtualProbe,object):
    def __init__(self,sd):
        VirtualProbe.__init__(self,sd)
    def _NextStimNumber(self):
        return len(self.StimsPrime())+1
    def AddVoltageSource(self,Name,Ports):
        if Ports == 1:
            self.AddDevice(Name,Ports,Ground(),'voltage source')
        elif Ports == 2:
            self.AddDevice(Name,Ports,Thru(),'voltage source')
        stimNumber=self._NextStimNumber()
        for p in range(Ports):
            self.AssignM(Name,p+1,'m'+str(stimNumber+p))
    def AddCurrentSource(self,Name,Ports):
        if Ports == 1:
            self.AddDevice(Name,Ports,Open(),'current source')
        elif Ports == 2:
            self.AddDevice(Name,Ports,[[1.,0.],[0.,1.]],'current source')
        stimNumber=self._NextStimNumber()
        for p in range(Ports):
            self.AssignM(Name,p+1,'m'+str(stimNumber+p))
    def SourceVector(self):
        sv=[]
        for d in self:
            if d.pType == 'current source' or d.pType == 'voltage source':
                sv.append(d.pName)
        return sv
    def SourceToStimsPrimeMatrix(self,symbolic=False):
        sv=self.SourceVector()
        sp=self.StimsPrime()
        Z0='Z0' if symbolic else 50.
        sm = [[0]*len(sv) for r in range(len(sp))]
        for s in sv:
            d=self[self.IndexOfDevice(s)]
            if d.pType == 'current source':
                if len(d) == 1:
                    sm[sp.index(d[0].pM)][sv.index(s)] = Z0
                elif len(d) == 2:
                    sm[sp.index(d[0].pM)][sv.index(s)] = Z0
                    sm[sp.index(d[1].pM)][sv.index(s)] = Z0
            elif d.pType == 'voltage source':
                if len(d) == 1:
                    sm[sp.index(d[0].pM)][sv.index(s)] = 1.
                elif len(d) == 2:
                    sm[sp.index(d[0].pM)][sv.index(s)] = -1./2.
                    sm[sp.index(d[1].pM)][sv.index(s)] = 1./2.
        return sm