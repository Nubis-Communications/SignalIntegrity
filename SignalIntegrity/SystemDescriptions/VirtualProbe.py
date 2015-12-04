from SignalIntegrity.SystemDescriptions.Simulator import Simulator

class VirtualProbe(Simulator,object):
    def __init__(self,sd):
        Simulator.__init__(self,sd)
        self.m_ml = sd.m_ml if hasattr(sd, 'm_ml') else None
        self.m_D = sd.m_D if hasattr(sd, 'm_D') else None
    def Check(self):
        if self.m_ml is None:
            raise PySIExceptionVirtualProbe('no outputs')
        try:
            Simulator.Check(self)
        except PySIExceptionSimulator as e:
            raise PySIExceptionVirtualProbe(e.message)
    @property
    def pMeasurementList(self):
        return self.m_ml
    @pMeasurementList.setter
    def pMeasurementList(self,ml=None):
        if not ml is None: self.m_ml = ml
        return self
    @property
    def pStimDef(self):
        return self.m_D
    @pStimDef.setter
    def pStimDef(self,D=None):
        if not D is None: self.m_D = D
        return self
