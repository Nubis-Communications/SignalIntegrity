"""
 NetworkAnalyzer
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
from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile
from SignalIntegrity.Lib.Measurement.Calibration.Calibration import Calibration

class NetworkAnalyzer(SParameters):
    """produces calibrated or uncalibrated s-parameters from a network analyzer.  
    The usual use of this class is to provide calibrated s-parameters, given raw s-parameters
    and error terms, but it can also be used to go the reverse direction."""
    def __init__(self,f,filename,etfilename,portListstring=None,calculate=True):
        """Constructor  
        Calculates calibrated or raw s-parameters from a network analyzer.
        @param f list of frequencies to calculate s-parameters
        @param filename string filename containing (usually raw) s-parameters.
        @param etfilename string filename containing error-terms (see Calibration).
        @param portListstring (optional, defaults to None) string containing comma delimited list
        of one-based port numbers to use.  This is so that the error-terms from a large port count calibration
        can be used to make a smaller measurement on less ports, and for port reordering.  Essentially, this
        is the list of network analyzer ports used for the measurement.
        @param calculate (optional, defaults to True) bool that defines the calculation direction.  If calculate
        is True, then the assumption is that the s-parameters provided are raw and the goal is to convert the
        raw s-parameters to calibrated s-parameters.  In the unusual situation where calculate is False, the direction
        is reversed and the assumption is that the s-parameters provided are calibrated and the goal is to convert the
        calibrated s-parameters to raw s-parameters.
        """
        if portListstring!=None:
            portlist=[int(p)-1 for p in portListstring.split(',')]
        else: portlist=None
        spraw=SParameterFile(filename).Resample(f)
        calibration=Calibration(0,0).ReadFromFile(etfilename)
        fixtures=calibration.Fixtures()
        fixtures=[fixture.Resample(f) for fixture in fixtures]
        calibration.InitializeFromFixtures(fixtures)
        if calculate:
            dut=calibration.DutCalculation(spraw,portlist)
        else:
            dut=calibration.DutUnCalculation(spraw,portlist)
        SParameters.__init__(self,f,dut)
