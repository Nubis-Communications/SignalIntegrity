class Calibration(object):
    def __init__(self,ports,f,calibrationList=[]):
        self.ports=ports
        self.f=f
        self.ET=None
        self.calibrationMatrix=[[[] for _ in range(self.ports)]
                                for _ in range(self.ports)]
        self.AddMeasurements(calibrationList)
...
    def AddMeasurements(self,calibrationList=[]):
        self.ET=None
        for calibrationMeasurement in calibrationList:
            if calibrationMeasurement.type=='reflect':
                portDriven=calibrationMeasurement.port
                otherPort=portDriven
                self.calibrationMatrix[otherPort][portDriven].\
                    append(calibrationMeasurement)
            elif (calibrationMeasurement.type=='thru') or\
                (calibrationMeasurement.type=='xtalk') or\
                (calibrationMeasurement.type=='reciprocal'):
                portDriven=calibrationMeasurement.portDriven
                otherPort=calibrationMeasurement.otherPort
                self.calibrationMatrix[otherPort][portDriven].\
                    append(calibrationMeasurement)
        return self
...
    def CalculateErrorTerms(self,force=False):
        if (not self.ET is None) and (not force): return self
        self.ET=[ErrorTerms().Initialize(self.ports) for _ in range(len(self))]
        measurements=copy.deepcopy(self.calibrationMatrix)
        self._CalculateReflectErrorTerms(measurements)
        self._CalculateXtalkErrorTerms(measurements)
        self._CalculateUnknownThruErrorTerms(measurements)
        self._CalculateThruErrorTerms(measurements)
        self._CalculateTransferThruErrorTerms()
        self._CheckErrorTerms()
        return self
...
    def DutCalculation(self,sRaw,portList=None,reciprocal=False):
        self.CalculateErrorTerms()
        return SParameters(self.f,[self[n].DutCalculation(sRaw[n],portList,reciprocal)
                                   for n in range(len(self))])
...
