"""
Preferences.py
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

from SignalIntegrity.App.PreferencesFile import PreferencesFile
from SignalIntegrity.App.ProjectFileBase import ResolvePreferencesPath

import os
import shutil
import platform

from SignalIntegrity.__about__ import __version__

class Preferences(PreferencesFile):
    baseWindows='c:/Nubis/SignalIntegrity'
    baseLinux='~/.signalintegrity'
    envVar='SIGNALINTEGRITY_PREFERENCES'
    def __init__(self,preferencesFileName=None):
        PreferencesFile.__init__(self)
        self.fileExists=False
        if preferencesFileName is None:
            self.preferencesFileName=ResolvePreferencesPath(self.baseWindows,self.baseLinux,self.envVar)
            self._SeedFromLegacy(self.preferencesFileName)
        else:
            self.preferencesFileName=preferencesFileName
        try:
            self.Read(self.preferencesFileName)
            self.HandleBackwardsCompatibility()
            self.fileExists=not (self['Version'] is None)
        except:
            self.fileExists=False
        if not self.fileExists:
            try:
                PreferencesFile.__init__(self)
                self['Version']=__version__
                self.Write(self.preferencesFileName)
            except:
                self.fileExists=False
                return
        self.fileExists=True
    @classmethod
    def ResolveFileName(cls):
        """Return the preferences file this installation/user/venv resolves to (no side effects on state)."""
        return ResolvePreferencesPath(cls.baseWindows,cls.baseLinux,cls.envVar)
    def _SeedFromLegacy(self,targetFileName):
        # First run at a tagged location: carry forward settings from the old flat/legacy file.
        if os.path.isfile(targetFileName):
            return
        if platform.system() == 'Linux':
            candidates=[os.path.expanduser(self.baseLinux)+'/preferences.xml']
        else:
            candidates=[self.baseWindows+'/preferences.xml','c:/LeCroy/SignalIntegrity/preferences.xml']
        for source in candidates:
            if os.path.abspath(source)==os.path.abspath(targetFileName):
                continue
            if os.path.isfile(source):
                try:
                    os.makedirs(os.path.dirname(targetFileName),exist_ok=True)
                    shutil.copy2(source,targetFileName)
                except:
                    pass
                return
    def SaveToFile(self):
        if self.fileExists:
            try:
                self['Version']=__version__
                self.Write(self.preferencesFileName)
            except:
                pass
    def AnotherFileOpened(self,filename,keepTrackOfFile=True):
        if not keepTrackOfFile:
            return
        filepath=os.getcwd()
        lastFiles=self['ProjectFiles.LastFile']
        if self['ProjectFiles.RetainLastFilesOpened']:
            if (lastFiles[0]['Name'] != filename) or (lastFiles[0]['Directory'] != filepath):
                for lfi in range(len(lastFiles)-1,0,-1):
                    lastFiles[lfi]['Name']=lastFiles[lfi-1]['Name']
                    lastFiles[lfi]['Directory']=lastFiles[lfi-1]['Directory']
                lastFiles[0]['Name']=filename
                lastFiles[0]['Directory']=filepath
                self.SaveToFile()
        else:
            foundOne=False
            for lfi in range(len(lastFiles)):
                if (lastFiles[lfi]['Name'] != None) or (lastFiles[lfi]['Directory'] != None):
                    foundOne=True
                    lastFiles[lfi]['Name']=None
                    lastFiles[lfi]['Directory']=None
            if foundOne:
                self.SaveToFile()

    def GetLastFileOpened(self,index=0):
        if self['ProjectFiles.OpenLastFile']:
            dirString=self['ProjectFiles.LastFile'][index]['Directory']
            nameString=self['ProjectFiles.LastFile'][index]['Name']
            if (dirString is None) or (nameString is None):
                return None
            else:
                return dirString+'/'+nameString
        else:
            return None

    def GetRecentFileList(self):
        lastFiles=self['ProjectFiles.LastFile']
        if lastFiles is None:
            return None
        return [lf['Name'] for lf in lastFiles]

if __name__ == '__main__':
    pf=Preferences()
    pf.PrintFullInformation()
