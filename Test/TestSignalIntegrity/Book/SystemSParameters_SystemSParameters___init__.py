class SystemSParameters(SystemDescription):
    def __init__(self,sd=None):
        SystemDescription.__init__(self,sd)
    def PortANames(self):
        pref=SystemDescription.port_refdes
        return [x[1] for x in sorted
                ([(int(self[d].Name.strip(pref)),self[d][0].A)
                  for d in range(len(self)) if self[d].Name[0:len(pref)]==pref])]
    def PortBNames(self):
        pref=SystemDescription.port_refdes
        return [x[1] for x in sorted
                ([(int(self[d].Name.strip(SystemDescription.port_refdes)),self[d][0].B)
                  for d in range(len(self)) if self[d].Name[0:len(pref)]==pref])]
    def OtherNames(self,K):
        other=[]
        for item in self.NodeVector():
            if not item in K: other.append(item)
        return other
    def NodeVector(self):
        return [self[d][p].B for d in range(len(self)) for p in range(len(self[d]))]
    def StimulusVector(self):
        return [self[d][p].M for d in range(len(self)) for p in range(len(self[d]))]
    def WeightsMatrix(self,ToN=None,FromN=None):
        if not isinstance(ToN,list):
            nv = self.NodeVector()
            ToN = nv
        if not isinstance(FromN,list):
            FromN=ToN
        PWM = [[0]*len(FromN) for r in range(len(ToN))]
        for d in range(len(self)):
            for p in range(len(self[d])):
                if self[d][p].B in ToN:
                    r=ToN.index(self[d][p].B)
                    for c in range(len(self[d])):
                        if self[d][c].A in FromN:
                            ci=FromN.index(self[d][c].A)
                            PWM[r][ci]=self[d].SParameters[p][c]
        return PWM
