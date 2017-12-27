class Calibration(object):
    def __init__(self,ports,f,calibrationList=[]):
        self.ports=ports
        self.f=f
        self.ET=[ErrorTerms().Initialize(ports) for _ in range(len(self.f))]
        self.calibrationMatrix=[[[] for _ in range(self.ports)]
                                for _ in range(self.ports)]
        self.AddMeasurements(calibrationList)
    def AddMeasurements(self,calibrationList=[]):
        self.ET=None
        for calibrationMeasurement in calibrationList:
            if calibrationMeasurement.type=='reflect':
                portDriven=calibrationMeasurement.port
                otherPort=portDriven
                self.calibrationMatrix[otherPort][portDriven].\
                    append(calibrationMeasurement)
            elif (calibrationMeasurement.type=='thru') or\
                (calibrationMeasurement.type=='xtalk'):
                portDriven=calibrationMeasurement.portDriven
                otherPort=calibrationMeasurement.otherPort
                self.calibrationMatrix[otherPort][portDriven].\
                    append(calibrationMeasurement)
        return self
    def CalculateErrorTerms(self):
        self.ET=[ErrorTerms().Initialize(self.ports) for _ in range(len(self.f))]
        for port in range(self.ports):
            measurementList=self.calibrationMatrix[port][port]
            for n in range(len(self.f)):
                hatGamma=[measurement.gamma[n] for measurement in measurementList]
                Gamma=[measurement.Gamma[n][0][0] for measurement in measurementList]
                self.ET[n].ReflectCalibration(hatGamma,Gamma,port)
        for otherPort in range(self.ports):
            for drivenPort in range(self.ports):
                if (otherPort != drivenPort):
                    measurementList=self.calibrationMatrix[otherPort][drivenPort]
                    xtalkMeasurementList=[]
                    thruMeasurementList=[]
                    for meas in measurementList:
                        if meas.type=='xtalk':
                            xtalkMeasurementList.append(meas)
                        elif meas.type=='thru':
                            thruMeasurementList.append(meas)
                    if len(xtalkMeasurementList)!=0:
                        for n in range(len(self.f)):
                            self.ET[n].ExCalibration(xtalkMeasurementList[0].b2a1[n],
                                    otherPort,drivenPort)
                    if len(thruMeasurementList)!=0:
                        for n in range(len(self.f)):
                            b1a1=[measurement.b1a1[n]
                                  for measurement in thruMeasurementList]
                            b2a1=[measurement.b2a1[n]
                                  for measurement in thruMeasurementList]
                            S=[measurement.S[n] for measurement in thruMeasurementList]
                            self.ET[n].ThruCalibration(b1a1,b2a1,S,otherPort,drivenPort)
        if Calibration.FillInTransferThru:
            for n in range(len(self.f)):
                self.ET[n].TransferThruCalibration()
        return self
    def ErrorTerms(self):
        if self.ET is None:
            self.CalculateErrorTerms()
        return self.ET
    def DutCalculation(self,sRaw):
        self.ErrorTerms()
        return SParameters(self.f,[self.ET[n].DutCalculation(sRaw[n])
                                   for n in range(len(self.f))])
