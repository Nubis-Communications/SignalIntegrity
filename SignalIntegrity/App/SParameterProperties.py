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
from SignalIntegrity.App.ProjectFileBase import ProjectFileBase,XMLPropertyDefaultFloat,XMLProperty,XMLConfiguration,XMLPropertyDefaultBool

class PlotConfiguration(XMLConfiguration):
    def __init__(self,name):
        XMLConfiguration.__init__(self,name)
        self.Add(XMLPropertyDefaultBool('XInitialized',False))
        self.Add(XMLPropertyDefaultFloat('MinX'))
        self.Add(XMLPropertyDefaultFloat('MaxX'))
        self.Add(XMLPropertyDefaultBool('YInitialized',False))
        self.Add(XMLPropertyDefaultFloat('MinY'))
        self.Add(XMLPropertyDefaultFloat('MaxY'))

class SParameterPlotsConfiguration(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'SParameterPlotConfiguration')
        self.SubDir(PlotConfiguration('Magnitude'))
        self.SubDir(PlotConfiguration('Phase'))
        self.SubDir(PlotConfiguration('Impulse'))
        self.SubDir(PlotConfiguration('Step'))
        self.SubDir(PlotConfiguration('Impedance'))
        self.Add(XMLPropertyDefaultFloat('Delay',0.0))

class PlotProperties(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Plot')
        self.Add(XMLProperty('S',[[SParameterPlotsConfiguration() for _ in range(0)] for _ in range(0)],'array',arrayType=SParameterPlotsConfiguration()))
        self.Add(XMLPropertyDefaultBool('VariableLineWidth',False))
        self.Add(XMLPropertyDefaultBool('ShowPassivityViolations',False))
        self.Add(XMLPropertyDefaultBool('ShowCausalityViolations',False))
        self.Add(XMLPropertyDefaultBool('ShowImpedance',False))
        self.Add(XMLPropertyDefaultBool('LogScale',False))

class ZoomJoinProperties(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Join')
        self.Add(XMLPropertyDefaultBool('All',False))
        self.Add(XMLPropertyDefaultBool('OffDiagonal',False))
        self.Add(XMLPropertyDefaultBool('Reciprocals',False))
        self.Add(XMLPropertyDefaultBool('Reflects',False))

class ZoomFrequenciesProperties(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Frequencies')
        self.Add(XMLPropertyDefaultBool('JoinWithin',True))
        self.Add(XMLPropertyDefaultBool('JoinWithOthers',True))
        self.SubDir(ZoomJoinProperties())
        self['Join.All']=True
        self['Join.OffDiagonal']=True
        self['Join.Reciprocals']=True
        self['Join.Reflects']=True

class ZoomTimesProperties(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Times')
        self.Add(XMLPropertyDefaultBool('JoinWithin',True))
        self.Add(XMLPropertyDefaultBool('JoinWithOthers',True))
        self.SubDir(ZoomJoinProperties())
        self['Join.OffDiagonal']=True
        self['Join.Reciprocals']=True
        self['Join.Reflects']=True

class ZoomVerticalProperties(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Vertical')
        self.Add(XMLPropertyDefaultBool('JoinMagnitudeWithOthers',True))
        self.Add(XMLPropertyDefaultBool('JoinPhaseWithOthers',True))
        self.Add(XMLPropertyDefaultBool('JoinImpulseWithOthers',True))
        self.Add(XMLPropertyDefaultBool('JoinStepImpedanceWithOthers',True))
        self.SubDir(ZoomJoinProperties())
        self['Join.Reciprocals']=True
        self['Join.Reflects']=True

class SParameterZoomProperties(XMLConfiguration):
    def __init__(self):
        XMLConfiguration.__init__(self,'Zoom')
        self.SubDir(ZoomFrequenciesProperties())
        self.SubDir(ZoomTimesProperties())
        self.SubDir(ZoomVerticalProperties())

class SParameterProperties(CalculationPropertiesBase):
    def __init__(self):
        CalculationPropertiesBase.__init__(self,'SParameterProperties')
        self.Add(XMLPropertyDefaultFloat('ReferenceImpedance',50.0))
        self.Add(XMLPropertyDefaultFloat('TimeLimitNegative',-100e-12))
        self.Add(XMLPropertyDefaultFloat('TimeLimitPositive',10e-9))
        self.SubDir(PlotProperties())
        self.SubDir(SParameterZoomProperties())

class SParameterPropertiesProject(ProjectFileBase):
    def __init__(self):
        ProjectFileBase.__init__(self,'sp')
        self.SubDir(SParameterProperties())