class Calibration(object):
    def _CalculateReflectErrorTerms(self,measurements):
        for port in range(self.ports):
            measurementList=measurements[port][port]
            for n in range(len(self)):
                hatGamma=[meas.gamma[n] for meas in measurementList]
                Gamma=[meas.Gamma[n][0][0] for meas in measurementList]
                self[n].ReflectCalibration(hatGamma,Gamma,port)
...
    def _CalculateXtalkErrorTerms(self,measurements):
        self._InitializeXtalkErrorTerms()
        for other in range(self.ports):
            for driven in range(self.ports):
                if (other != driven):
                    measurementList=measurements[other][driven]
                    xtalkMeasurementList=[]
                    for meas in measurementList:
                        if meas.type=='xtalk': xtalkMeasurementList.append(meas)
                    if len(xtalkMeasurementList)!=0:
                        for n in range(len(self.f)):
                            self[n].ExCalibration(
                                xtalkMeasurementList[0].b2a1[n],other,driven)
    def _CalculateUnknownThruErrorTerms(self,measurements):
        for other in range(self.ports):
            for driven in range(self.ports):
                if (other != driven):
                    for meas in measurements[other][driven]:
                        if meas.type=='reciprocal':
                            Sestsp= [s for s in meas.S] if not (meas.S is None)\
                                else [Thru() for _ in range(len(self.f))]
                            for n in range(len(self.f)):
                                Sestsp[n]=self[n].UnknownThruCalibration(
                                    meas.Smeasured[n],
                                    Sestsp[n] if not meas.S is None
                                    else Sestsp[max(n-1,0)],driven,other)
                            Sest=SParameters(self.f,Sestsp)
                            Sest=Sest.LimitImpulseResponseLength(meas.limit)
                            measurements[other][driven].append(
                                ThruCalibrationMeasurement(
                                meas.Smeasured.FrequencyResponse(1,1),
                                meas.Smeasured.FrequencyResponse(2,1),
                                Sest,other,driven))
                            measurements[driven][other].append(
                                ThruCalibrationMeasurement(
                                meas.Smeasured.FrequencyResponse(2,2),
                                meas.Smeasured.FrequencyResponse(1,2),
                                Sest.PortReorder([1,0]),driven,other))
    def _CalculateThruErrorTerms(self,measurements):
        for other in range(self.ports):
            for driven in range(self.ports):
                if (other != driven):
                    measurementList=measurements[other][driven]
                    thruMeasurementList=[]
                    for meas in measurementList:
                        if meas.type=='thru': thruMeasurementList.append(meas)
                    if len(thruMeasurementList)!=0:
                        for n in range(len(self.f)):
                            b1a1=[meas.b1a1[n] for meas in thruMeasurementList]
                            b2a1=[meas.b2a1[n] for meas in thruMeasurementList]
                            S=[meas.S[n] for meas in thruMeasurementList]
                            self[n].ThruCalibration(b1a1,b2a1,S,other,driven)
    def _CalculateTransferThruErrorTerms(self):
        if Calibration.FillInTransferThru:
            for n in range(len(self.f)): self[n].TransferThruCalibration()
...
