"""
 Calibration Measurements
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever

## CalibrationMeasurement
#
# Base class for calibration measurement
#
class CalibrationMeasurement(object):
    ## Constructor
    #
    # @param type string representing the type of the measurement.
    # @param name (optional) string representing the name of the measurement
    #
    # The name of the measurement is not used for anything, but can be used to identify
    # the name of a calibration measurement externally.
    #
    # valid types of calibration measurements are:
    #
    # - 'reflect' - a reflect measurement taken on a port with a reflect standard
    # (like short, open, or load).
    # - 'thru' - a thru calibration measurement taken between two ports.
    # - 'xtalk' - a crosstalk calibration measurement typically taken between two ports that
    # are completely unconnected.
    #
    def __init__(self,type,name=None):
        self.type=type
        self.name=name

## ReflectCalibrationMeasurement
#
# a reflect measurement taken on a port with a reflect standard
# (like short, open, or load).
#
class ReflectCalibrationMeasurement(CalibrationMeasurement):
    ## Constructor
    #
    # @param b1a1 list of complex raw measured ratios of the reflect to incident wave at the driven port.
    # @param GammaStandard instance of SParameters for the one-port reflect calibration standard being measured.
    # @param port integer port number where the calibration is being performed.
    # @param name (optional) string representing the name of the measurement.
    #
    # the name is not actually used for anything.
    # 
    def __init__(self,b1a1,GammaStandard,port,name=None):
        CalibrationMeasurement.__init__(self,'reflect',name)
        self.gamma=b1a1
        self.Gamma=GammaStandard
        self.port = port

## ThruCalibrationMeasurement
#
# a thru calibration measurement taken between two ports.
#
class ThruCalibrationMeasurement(CalibrationMeasurement):
    ## Constructor
    #
    # @param b1a1 list of complex raw measured ratios of the reflect to incident wave at the driven port.
    # @param b2a1 list or complex raw measured ratios of the reflect wave at the undriven port to the incident
    # wave at the driven port.
    # @param SStandard instance of SParameters for the two-port thru calibration standard being measured.
    # @param portDriven integer port number of the driven port.
    # @param otherPort integer port number of the other undriven port
    # @param name (optional) string representing the name of the measurement.
    #
    # the name is not actually used for anything.
    #
    def __init__(self,b1a1,b2a1,SStandard,portDriven,otherPort,name=None):
        CalibrationMeasurement.__init__(self,'thru',name)
        self.b1a1=b1a1
        self.b2a1=b2a1
        self.S=SStandard
        self.portDriven=portDriven
        self.otherPort=otherPort

## XtalkCalibrationMeasurement
#
# a crosstalk calibration measurement typically taken between two ports that
# are completely unconnected.
class XtalkCalibrationMeasurement(CalibrationMeasurement):
    ## Constructor
    #
    # @param b2a1 list or complex raw measured ratios of the reflect wave at the undriven port to the incident
    # wave at the driven port.
    # @param portDriven integer port number of the driven port.
    # @param otherPort integer port number of the other undriven port
    # @param name (optional) string representing the name of the measurement.
    #
    # the name is not actually used for anything.
    #
    def __init__(self,b2a1,portDriven,otherPort,name=None):
        CalibrationMeasurement.__init__(self,'xtalk',name)
        self.b2a1=b2a1
        self.portDriven=portDriven
        self.otherPort=otherPort