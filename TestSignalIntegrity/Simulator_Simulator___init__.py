class Simulator(SystemSParameters,object):
    def __init__(self,sd=None):
        SystemSParameters.__init__(self,sd)
        self.m_ol = sd.m_ol if hasattr(sd, 'm_ol') else None
...
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
...
