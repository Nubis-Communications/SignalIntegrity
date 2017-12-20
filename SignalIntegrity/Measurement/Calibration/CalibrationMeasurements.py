'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
class CalibrationMeasurement(object):
    def __init__(self,type,name=None):
        self.type=type
        self.name=name

class ReflectCalibrationMeasurement(CalibrationMeasurement):
    # gamma is the raw measurement, Gamma is the known value of the standard
    def __init__(self,b1a1,GammaStandard,port,name=None):
        CalibrationMeasurement.__init__(self,'reflect',name)
        self.gamma=b1a1
        self.Gamma=GammaStandard
        self.port = port

class ThruCalibrationMeasurement(CalibrationMeasurement):
    def __init__(self,b1a1,b2a1,SStandard,portDriven,otherPort,name=None):
        CalibrationMeasurement.__init__(self,'thru',name)
        self.b1a1=b1a1
        self.b2a1=b2a1
        self.S=SStandard
        self.portDriven=portDriven
        self.otherPort=otherPort

class XtalkCalibrationMeasurement(CalibrationMeasurement):
    def __init__(self,b2a1,portDriven,otherPort,name=None):
        CalibrationMeasurement.__init__(self,'xtalk',name)
        self.b2a1=b2a1
        self.portDriven=portDriven
        self.otherPort=otherPort