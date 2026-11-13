"""
SParameterViewerPreferencesDialog.py
"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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

def AddPlotPreferences(dialog,parentFrame,preferences):
    dialog.plotWidthFrame=CalculationProperty(parentFrame,'plot width',None,dialog.onUpdatePreferences,preferences,'Appearance.PlotWidth')
    dialog.plotHeightFrame=CalculationProperty(parentFrame,'plot height',None,dialog.onUpdatePreferences,preferences,'Appearance.PlotHeight')
    dialog.plotDPIFrame=CalculationProperty(parentFrame,'plot DPI',None,dialog.onUpdatePreferences,preferences,'Appearance.PlotDPI')
    dialog.matPlotLibColorFrame=CalculationPropertyColor(parentFrame,'plot color',None,dialog.onUpdateColors,preferences,'Appearance.Color.Plot')
    dialog.plotCursors=CalculationPropertyTrueFalseButton(parentFrame,'show cursor values on plots',None,dialog.onUpdatePreferences,preferences,'Appearance.PlotCursorValues')
    dialog.significantDigits=CalculationProperty(parentFrame,'significant digits',None,dialog.onUpdatePreferences,preferences,'SParameterProperties.SignificantDigits')
    dialog.maxSParameterButtons=CalculationProperty(parentFrame,'max s-parameter buttons',None,dialog.onUpdatePreferences,preferences,'SParameterProperties.MaxSParameterButtons')

class SParameterViewerPreferencesDialog(PropertiesDialog):
    def __init__(self, parent,preferences):
        PropertiesDialog.__init__(self,parent,preferences,parent,'Preferences')
        AddPlotPreferences(self,self.propertyListFrame,preferences)
        self.Finish()
    def onUpdatePreferences(self):
        self.project.SaveToFile()
        if hasattr(self.parent,'UpdateSParameterButtonsView'):
            self.parent.UpdateSParameterButtonsView()
    def onUpdateColors(self):
        self.onUpdatePreferences()
    def Finish(self):
        PropertiesDialog.Finish(self)