class CalibrationKit(object):
    def __init__(self,filename=None,f=None):
        self.Constants=CalibrationConstants()
        self.m_f=None
        if not filename is None:
            self.ReadFromFile(filename)
        if not f is None:
            self.InitializeFrequency(f)
    def InitializeFrequency(self,f):
        self.m_f=f
        self.openStandard=OpenStandard(self.m_f,self.Constants.openOffsetDelay,
            self.Constants.openOffsetZ0,self.Constants.openOffsetLoss,
            self.Constants.openC0,self.Constants.openC1,self.Constants.openC2,
            self.Constants.openC3)
        self.shortStandard=ShortStandard(self.m_f,self.Constants.shortOffsetDelay,
            self.Constants.shortOffsetZ0,self.Constants.shortOffsetLoss,
            self.Constants.shortL0,self.Constants.shortL1,self.Constants.shortL2,
            self.Constants.shortL3)
        self.loadStandard=LoadStandard(self.m_f,self.Constants.loadOffsetDelay,
            self.Constants.loadOffsetZ0,self.Constants.loadOffsetLoss,
            self.Constants.loadZ)
        self.thruStandard=ThruStandard(self.m_f,self.Constants.thruOffsetDelay,
            self.Constants.thruOffsetZ0,self.Constants.thruOffsetLoss)
        return self
    def ReadFromFile(self,filename):
        self.Constants=CalibrationConstants().ReadFromFile(filename)
        return self
    def WriteToFile(self,filename,calkitname=None):
        self.Constants.WriteToFile(filename, calkitname)
        return self
    def WriteStandardsToFiles(self,filenamePrefix=''):
        self.shortStandard.WriteToFile(filenamePrefix+'Short')
        self.openStandard.WriteToFile(filenamePrefix+'Open')
        self.loadStandard.WriteToFile(filenamePrefix+'Load')
        self.thruStandard.WriteToFile(filenamePrefix+'Thru')
        return self
    def ReadStandardsFromFiles(self,filenamePrefix):
        self.shortStandard=SParameterFile(filenamePrefix+'Short.s1p')
        self.openStandard=SParameterFile(filenamePrefix+'Open.s1p')
        self.loadStandard=SParameterFile(filenamePrefix+'Load.s1p')
        self.thruStandard=SParameterFile(filenamePrefix+'Thru.s2p')
        return self
