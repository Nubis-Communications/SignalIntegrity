"""
StatisticalNoisePreferencesDialog.py
"""
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
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

from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog,CalculationPropertySI

class StatisticalNoisePreferencesDialog(PropertiesDialog):
    def __init__(self, parent,preferences):
        PropertiesDialog.__init__(self,parent,preferences,parent,'Statistical Noise Preferences')
        self.zeroThreshold=CalculationPropertySI(self.propertyListFrame,'zero threshold (blank values below)',None,self.onUpdatePreferences,preferences,'StatisticalNoise.ZeroThreshold',None,round=3,tooltip='Displayed rms/linear values whose magnitude is below this threshold are blanked.')
        self.maximumSNR=CalculationPropertySI(self.propertyListFrame,'maximum SNR (blank values above)',None,self.onUpdatePreferences,preferences,'StatisticalNoise.MaximumSNR','dB',round=3,tooltip='Displayed signal-to-noise ratios above this value (dB) are blanked.')
        self.Finish()
    def onUpdatePreferences(self):
        self.project.SaveToFile()
        if hasattr(self.parent,'UpdateMeasurementsView'):
            self.parent.UpdateMeasurementsView()
    def Finish(self):
        PropertiesDialog.Finish(self)
