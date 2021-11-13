"""
EyeDiagramConfiguration.py
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
from SignalIntegrity.App.PreferencesFile import EyeConfiguration
from SignalIntegrity.App.DeviceExtendedConfiguration import DeviceExtendedConfiguration
from SignalIntegrity.App.EyeDiagramPropertiesDialog import EyeDiagramPropertiesDialog
import SignalIntegrity.App.Preferences
import copy

class EyeDiagramConfiguration(EyeConfiguration,DeviceExtendedConfiguration):
    def __init__(self):
        EyeConfiguration.__init__(self)
        DeviceExtendedConfiguration.__init__(self,
            label='Eye Diagram Configuration',
            dialog=EyeDiagramPropertiesDialog
            )
    def HandleBackwardsCompatibility(self):
        # for backwards compatibility with old projects with eye probes with global eye diagram configurations,
        # assign the global configuration to the probe.  When the file is written, these individual configurations
        # will be retained and the global configuration will be removed.
        import SignalIntegrity.App.Project
        if not SignalIntegrity.App.Project['EyeDiagram'] is None:
            self.dict = copy.deepcopy(SignalIntegrity.App.Project['EyeDiagram'].dict)