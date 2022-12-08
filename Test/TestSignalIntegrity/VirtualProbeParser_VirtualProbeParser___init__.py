class VirtualProbeParser(SystemDescriptionParser):
    def __init__(self, f=None, args=None, Z0=50.):
        SystemDescriptionParser.__init__(self, f, args, Z0=Z0)
    def _ProcessVirtualProbeLine(self,line):
        lineList=self.ReplaceArgs(line.split())
        if len(lineList) == 0: return
        if lineList[0] == 'meas':
            if self.m_sd.pMeasurementList is None: self.m_sd.pMeasurementList = []
            for i in range(1,len(lineList),2):
                self.m_sd.pMeasurementList.append((lineList[i],int(lineList[i+1])))
        elif lineList[0] == 'output':
            if self.m_sd.pOutputList is None: self.m_sd.pOutputList = []
            for i in range(1,len(lineList),2):
                self.m_sd.pOutputList.append((lineList[i],int(lineList[i+1])))
        elif lineList[0] == 'stim':
            for i in range((len(lineList)-1)//3):
                self.m_sd.AssignM(lineList[i*3+2],int(lineList[i*3+3]),lineList[i*3+1])
        elif lineList[0] == 'stimdef':
            self.m_sd.pStimDef = [[float(e) for e in r] for r in [s.split(',')
                for s in ''.join(lineList[1:]).strip(' ').strip('[[').
                    strip(']]').split('],[') ]]
        else: self.m_ul.append(line)
    def _ProcessLines(self):
        SystemDescriptionParser._ProcessLines(self)
        self.m_sd = VirtualProbe(self.m_sd)
        lines=copy.deepcopy(self.m_ul); self.m_ul=[]
        for line in lines: self._ProcessVirtualProbeLine(line)
        return self
