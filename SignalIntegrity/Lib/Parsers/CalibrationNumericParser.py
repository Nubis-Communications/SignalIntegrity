"""
 calibrations from netlists
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

from SignalIntegrity.Lib.SystemDescriptions.SystemSParametersNumeric import SystemSParametersNumeric
from SignalIntegrity.Lib.Parsers.SystemDescriptionParser import SystemDescriptionParser
from SignalIntegrity.Lib.Parsers.CalibrationParser import CalibrationParser
from SignalIntegrity.Lib.SParameters import SParameters
from SignalIntegrity.Lib.CallBacker import CallBacker
from SignalIntegrity.Lib.ResultsCache import LinesCache

class CalibrationNumericParser(CalibrationParser,CallBacker,LinesCache):
    """generates a calibration from a netlist"""
    def __init__(self, f=None, args=None, callback=None, cacheFileName=None):
        """constructor  
        frequencies may be provided at construction time (or not for symbolic solutions).
        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback.
        @param cacheFileName (optional) string name of file used to cache results
        @remark Arguments are provided on a line as pairs of names and values separated by a space.  
        The optional callback is used as described in the class CallBacker.  
        The use of the cacheFileName is described in the class LineCache.  
        """
        CalibrationParser.__init__(self, f, args)
        self.calibration = None
        # pragma: silent exclude
        CallBacker.__init__(self,callback)
        LinesCache.__init__(self,'Calibration',cacheFileName)
        # pragma: include
    def CalculateCalibration(self):
        """calculates a calibration like for a VNA or TDR
        @return instance of class Calibration
        @see Calibration
        """
        # pragma: silent exclude
        if self.CheckCache():
            self.CallBack(100.0)
            return self.calibration
        # pragma: include
        self.SystemDescription()
        self.calibration.CalculateErrorTerms()
        # pragma: silent exclude
        self.CacheResult()
        # pragma: include
        return self.calibration