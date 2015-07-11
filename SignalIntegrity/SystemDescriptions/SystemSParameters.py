from SignalIntegrity.SystemDescriptions import SystemDescription

class SystemSParameters(SystemDescription):
    def __init__(self,sd):
        self.Data = sd.Data
        self.m_UniqueDevice=sd.m_UniqueDevice
        self.m_UniqueNode=sd.m_UniqueNode
    def PortANames(self):
        return [x[1] for x in sorted
                ([(self[d].pName.strip('P'),self[d][0].pA)
                  for d in range(len(self)) if self[d].pName[0]=='P'])]
    def PortBNames(self):
        return [x[1] for x in sorted
                ([(self[d].pName.strip('P'),self[d][0].pB)
                  for d in range(len(self)) if self[d].pName[0]=='P'])]
    def OtherNames(self,K):
        return list(set(self.NodeVector())-set(K))
    def NodeVector(self):
        return [self[d][p].pB for d in range(len(self)) for p in range(len(self[d]))]
    def StimulusVector(self):
        return [self[d][p].pM for d in range(len(self)) for p in range(len(self[d]))]
    def WeightsMatrix(self,ToN=None,FromN=None):
        if not isinstance(ToN,list):
            nv = self.NodeVector()
            ToN = nv
            FromN = nv
        elif not isinstance(FromN,list):
            FromN=ToN
        PWM = [[0]*len(FromN) for r in range(len(ToN))]
        for d in range(len(self)):
            for p in range(len(self[d])):
                if self[d][p].pB in ToN:
                    r=ToN.index(self[d][p].pB)
                    for c in range(len(self[d])):
                        if self[d][c].pA in FromN:
                            ci=FromN.index(self[d][c].pA)
                            PWM[r][ci]=self[d].pSParameters[p][c]
        return PWM