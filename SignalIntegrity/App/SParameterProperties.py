"""
SParameterProperties.py
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
from SignalIntegrity.App.ProjectFile import CalculationPropertiesBase
from SignalIntegrity.App.ProjectFileBase import ProjectFileBase,XMLPropertyDefaultFloat

class SParameterProperties(CalculationPropertiesBase):
    def __init__(self):
        CalculationPropertiesBase.__init__(self,'SParameterProperties')
        self.Add(XMLPropertyDefaultFloat('ReferenceImpedance',50.0))
        self.Add(XMLPropertyDefaultFloat('TimeLimitNegative',-100e-12))
        self.Add(XMLPropertyDefaultFloat('TimeLimitPositive',10e-9))

class SParameterPropertiesProject(ProjectFileBase):
    def __init__(self):
        ProjectFileBase.__init__(self,'sp')
        self.SubDir(SParameterProperties())