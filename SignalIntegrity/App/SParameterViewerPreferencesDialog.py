"""
SParameterViewerPreferencesDialog.py
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
from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationProperty,CalculationPropertyTrueFalseButton,CalculationPropertyColor

class SParameterViewerPreferencesDialog(PropertiesDialog):
    def __init__(self, parent,preferences):
        PropertiesDialog.__init__(self,parent,preferences,parent,'Preferences')
        self.plotWidthFrame=CalculationProperty(self.propertyListFrame,'plot width',None,self.onUpdatePreferences,preferences,'Appearance.PlotWidth')
        self.plotHeightFrame=CalculationProperty(self.propertyListFrame,'plot height',None,self.onUpdatePreferences,preferences,'Appearance.PlotHeight')
        self.plotDPIFrame=CalculationProperty(self.propertyListFrame,'plot DPI',None,self.onUpdatePreferences,preferences,'Appearance.PlotDPI')
        self.matPlotLibColorFrame=CalculationPropertyColor(self.propertyListFrame,'plot color',None,self.onUpdateColors,preferences,'Appearance.Color.Plot')
        self.plotCursors=CalculationPropertyTrueFalseButton(self.propertyListFrame,'show cursor values on plots',None,self.onUpdatePreferences,preferences,'Appearance.PlotCursorValues')
        self.significantDigits=CalculationProperty(self.propertyListFrame,'significant digits',None,self.onUpdatePreferences,preferences,'SParameterProperties.SignificantDigits')
        self.Finish()
    def onUpdatePreferences(self):
        self.project.SaveToFile()
    def onUpdateColors(self):
        self.onUpdatePreferences()
    def Finish(self):
        PropertiesDialog.Finish(self)