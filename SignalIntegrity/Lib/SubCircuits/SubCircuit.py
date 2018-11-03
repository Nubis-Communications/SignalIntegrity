"""
SubCircuit.py
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
from SignalIntegrity.Lib.SParameters import SParameters

class SubCircuit(SParameters):
    def __init__(self,f,fileName,args):
        # pragma: silent exclude
        from SignalIntegrity.Lib.Parsers import SystemSParametersNumericParser
        # pragma: include
        sspnp=SystemSParametersNumericParser(f,args).File(fileName)
        SParameters.__init__(self,f,sspnp.SParameters())
