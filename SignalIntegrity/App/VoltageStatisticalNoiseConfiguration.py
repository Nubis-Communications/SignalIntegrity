"""
VoltageStatisticalNoiseConfiguration.py
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
from SignalIntegrity.App.StatisticalNoisePreferencesFile import VoltageNoiseConfiguration
from SignalIntegrity.App.DeviceExtendedConfiguration import DeviceExtendedConfiguration
import SignalIntegrity.App.Preferences
import copy

class VoltageStatisticalNoiseConfiguration(VoltageNoiseConfiguration,DeviceExtendedConfiguration):
    # legacy XML tag name used before the voltage/current split (files saved as <Noise>)
    legacyName='Noise'
    def __init__(self):
        if DeviceExtendedConfiguration.headless:
            dialog=None
        else:
            from SignalIntegrity.App.VoltageStatisticalNoisePropertiesDialog import VoltageStatisticalNoisePropertiesDialog
            dialog=VoltageStatisticalNoisePropertiesDialog
        VoltageNoiseConfiguration.__init__(self)
        DeviceExtendedConfiguration.__init__(self,
            label='Voltage Statistical Noise Configuration',
            dialog=dialog
            )
    def HandleBackwardsCompatibility(self):
        return
