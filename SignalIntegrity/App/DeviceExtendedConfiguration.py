"""
DeviceExtendedConfiguration.py
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

class DeviceExtendedConfiguration(object):
    # override __getstate__ so if someone is trying to copy this object, the dialog window
    # does not get in the way.
    headless=True
    def __getstate__(self):
        state=self.__dict__.copy()
        state['window']=None
        return state
    def __init__(self,label,dialog):
        self.label=label
        self.dialog=dialog
        self.window=None
    def onConfiguration(self,parent):
        from SignalIntegrity.App.ConfigurationProperty import BindConfiguration
        from SignalIntegrity.App.ConfigurationPropertiesDialog import ConfigurationPropertiesDialog
        import SignalIntegrity.App.Project
        if hasattr(self,'configurationFields'):
            BindConfiguration(self,SignalIntegrity.App.Project['Variables'],
                              getattr(self,'configurationReference',''))
        if (self.window is None) or not self.window.winfo_exists():
            self.window=(ConfigurationPropertiesDialog(self,parent) if hasattr(self,'configurationFields')
                         else self.dialog(self,parent))
        # the following makes the window go to the top, but not necessarily stay there
        self.window.wait_visibility(self.window)
        self.window.grab_set()
        self.window.attributes('-topmost',True)
        self.window.wait_window(self.window)
        return self.window
    def InitializeFromPreferences(self):
        import SignalIntegrity.App.Preferences
        import copy
        self.dict=copy.deepcopy(SignalIntegrity.App.Preferences['Devices'][self.name]).dict
        if hasattr(self,'configurationFields'):
            from SignalIntegrity.App.ConfigurationProperty import InitializeConfiguration
            InitializeConfiguration(self)
        return self
    def SaveToPreferences(self):
        import SignalIntegrity.App.Preferences
        import copy
        target=SignalIntegrity.App.Preferences['Devices'][self.name]
        if hasattr(self,'configurationFields'):
            from SignalIntegrity.App.ConfigurationProperty import InitializeConfiguration
            snapshot=copy.deepcopy(self)
            for field in snapshot.configurationFields.values():
                if field.reference:
                    value=field.Resolve(field.reference)
                    field.state.entries[field.path]['reference']=''
                    field.leaf.dict['value']=str(value)
                    field.leaf.UpdateValue()
            target.dict=snapshot.dict
            InitializeConfiguration(target)
        else:
            target.dict=copy.deepcopy(self.dict)
        SignalIntegrity.App.Preferences.SaveToFile()
    # override this if there is a backwards compatibility issue
    def HandleBackwardsCompatibility(self):
        pass