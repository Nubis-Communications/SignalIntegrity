"""
 Calibration Measurements
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

class CalibrationMeasurement(object):
    """Base class for calibration measurements"""
    def __init__(self,type,name=None):
        """Constructor
        @param type string representing the type of the measurement.
        @param name (optional) string representing the name of the measurement
        @remark
        The name of the measurement is not used for anything, but can be used to identify
        the name of a calibration measurement externally.

        valid types of calibration measurements are:

        - 'reflect' - a reflect measurement taken on a port with a reflect standard
        (like short, open, or load).
        - 'thru' - a thru calibration measurement taken between two ports.
        - 'xtalk' - a crosstalk calibration measurement typically taken between two ports that
        are completely unconnected.
        @see ReflectCalibrationMeasurement
        @see ThruCalibrationMeasurement
        @see XtalkCalibrationMeasurement
        """
        self.type=type
        self.name=name

class ReflectCalibrationMeasurement(CalibrationMeasurement):
    """A reflect measurement taken on a port with a reflect standard
    (like short, open, or load)."""
    def __init__(self,b1a1,GammaStandard,port,name=None):
        """Constructor
        @param b1a1 list of complex raw measured ratios of the reflect to incident wave at the driven port.
        @param GammaStandard instance of SParameters for the one-port reflect calibration standard being measured.
        @param port integer port number where the calibration is being performed.
        @param name (optional) string representing the name of the measurement.
        @note the name is not actually used for anything.
        """
        CalibrationMeasurement.__init__(self,'reflect',name)
        self.gamma=b1a1
        self.Gamma=GammaStandard
        self.port = port

class ThruCalibrationMeasurement(CalibrationMeasurement):
    """A thru calibration measurement taken between two ports."""
    def __init__(self,b1a1,b2a1,SStandard,portDriven,otherPort,name=None):
        """Constructor
        @param b1a1 list of complex raw measured ratios of the reflect to incident wave at the driven port.
        @param b2a1 list or complex raw measured ratios of the reflect wave at the undriven port to the incident
        wave at the driven port.
        @param SStandard instance of SParameters for the two-port thru calibration standard being measured.
        @param portDriven integer port number of the driven port.
        @param otherPort integer port number of the other undriven port
        @param name (optional) string representing the name of the measurement.
        @note the name is not actually used for anything.
        @note It is assumed that the standard is being driven from port 1 of the standard
        """
        CalibrationMeasurement.__init__(self,'thru',name)
        self.b1a1=b1a1
        self.b2a1=b2a1
        self.S=SStandard
        self.portDriven=portDriven
        self.otherPort=otherPort

class UnknownThruCalibrationMeasurement(CalibrationMeasurement):
    """An unknown thru calibration measurement taken between two ports."""
    def __init__(self,Smeasured,SStandard,port1,port2,limit=None,name=None):
        """Constructor
        @param Smeasured instance of SParameters measured. 
        @param SStandard instance of SParameters for the two-port thru calibration standard being measured.  This is an estimate of the
        thru standard, otherwise None can be supplied and the algorithm will try to figure it out itself.
        @param port1 integer zero based port number of the first port assumed to be connected to port 1 of the standard.
        @param port2 integer zero based port number of the second port assumed to be connected to port 2 of the standard.
        @param limit (optional) tuple of floats containing negative and positive time limit for the impulse response of the recovered thru
        @param name (optional) string representing the name of the measurement.
        @note the name is not actually used for anything.
        """
        CalibrationMeasurement.__init__(self,'reciprocal',name)
        self.Smeasured=Smeasured
        self.S=SStandard
        self.portDriven=port1
        self.otherPort=port2
        self.limit=limit

class XtalkCalibrationMeasurement(CalibrationMeasurement):
    """ A crosstalk calibration measurement typically taken between two ports that
    are completely unconnected."""
    def __init__(self,b2a1,portDriven,otherPort,name=None):
        """Constructor
        @param b2a1 list or complex raw measured ratios of the reflect wave at the undriven port to the incident
        wave at the driven port.
        @param portDriven integer port number of the driven port.
        @param otherPort integer port number of the other undriven port
        @param name (optional) string representing the name of the measurement.
        @note the name is not actually used for anything.
        """
        CalibrationMeasurement.__init__(self,'xtalk',name)
        self.b2a1=b2a1
        self.portDriven=portDriven
        self.otherPort=otherPort