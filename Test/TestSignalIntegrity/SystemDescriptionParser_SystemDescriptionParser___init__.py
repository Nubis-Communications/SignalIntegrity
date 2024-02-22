class SystemDescriptionParser(ParserFile,ParserArgs):
    def __init__(self,f=None,args=None,Z0=50.):
        self.m_sd = None
        self.m_f=f
        self.m_lines=[]
        self.m_addThru = False
        self.AssignArguments(args)
        self.known=None
        self.callback=None
        self.m_Z0=Z0
    def SystemDescription(self):
        if self.m_sd is None: self._ProcessLines()
        return self.m_sd
    def AddKnownDevices(self,known):
        self.known=known
        return self
    def AddLine(self,line):
        self.m_sd = None
        if len(line) == 0: return
        self.m_lines.append(line)
        return self
    def AddLines(self,lines):
        self.m_sd = None
        for line in lines:
            self.AddLine(line)
        return self
    def _ProcessLine(self,line,exclusionList):
        lineList=self.ReplaceArgs(LineSplitter(line))
        if len(lineList) == 0: return
        if self.ProcessVariables(lineList): return
        elif lineList[0] in exclusionList: self.m_ul.append(line)
        elif lineList[0] == 'device':
            argList = lineList[3:]
            if [lineList[2]]+argList in self.m_spcl:
                dev = DeviceParser(self.m_f,int(lineList[2]),self.callback,None,
                                   Z0=self.m_Z0)
                dev.m_spf = self.m_spc[self.m_spcl.index([lineList[2]]+argList)][1]
            else: dev=DeviceParser(self.m_f,int(lineList[2]),self.callback,argList,
                                   Z0=self.m_Z0)
            self.m_sd.AddDevice(lineList[1],int(lineList[2]),dev.m_sp)
            if not dev.m_spf is None:
                self.m_spc.append((lineList[1],dev.m_spf))
                self.m_spcl.append([lineList[2]]+argList)
        elif lineList[0] == 'connect':
            for i in range(3,len(lineList),2):
                self.m_sd.ConnectDevicePort(lineList[1],int(lineList[2]),
                    lineList[i],int(lineList[i+1]))
        elif lineList[0] == 'port':
            i=1
            while i < len(lineList):
                port=int(lineList[i])
                dev=lineList[i+1]; devPort=int(lineList[i+2])
                self.m_sd.AddPort(dev,devPort,port,self.m_addThru)
                i=i+3
        else: self.m_ul.append(' '.join(lineList))
    def _ProcessLines(self,exclusionList=[]):
        self.m_sd=SystemDescription()
        self.m_spc=[]; self.m_spcl=[]; self.m_ul=[]
        if not self.known is None:
            for key in self.known.keys():
                self.m_spcl.append(LineSplitter(key))
                self.m_spc.append((None,self.known[key].Resample(self.m_f)))
        for line in self.m_lines: self._ProcessLine(line,exclusionList)
        return self
