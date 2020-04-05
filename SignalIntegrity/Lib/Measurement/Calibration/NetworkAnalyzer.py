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
    def __init__(self,f,filename,etfilename,portListstring=None,calculate=True):
        if portListstring!=None:
            portlist=[int(p)-1 for p in portListstring.split(',')]
        else: portlist=None
        spraw=SParameterFile(filename).resample(f)
        calibration=Calibration().ReadFromFile(etfilename)
        fixtures=calibration.Fixtures()
        fixtures=[fixture.resample(f) for fixture in fixtures]
        calibration.InitializeFromFixtures(fixtures)
        if calculate:
            dut=calibration.DutCalculation(spraw,portlist)
        else:
            dut=calibration.DutUnCalculations(spraw,portlist)
        SParameters.__init__(self,f,dut)
