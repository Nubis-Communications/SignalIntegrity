"""
Preferences.py
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

from SignalIntegrity.App.PreferencesFile import PreferencesFile

import os,errno
import platform

from SignalIntegrity.__about__ import __version__

class Preferences(PreferencesFile):
    def __init__(self,preferencesFileName=None):
        PreferencesFile.__init__(self)
        self.fileExists=False
        if preferencesFileName is None:
            thisOS=platform.system()
            if thisOS == 'Linux':
                pathToPreferencesFile = os.path.expanduser('~')+'/.signalintegrity'
            else:
                pathToPreferencesFile = '/LeCroy/SignalIntegrity'
            self.preferencesFileName=pathToPreferencesFile+'/preferences'
            try:
                os.makedirs(pathToPreferencesFile)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    return
        else:
            self.preferencesFileName=preferencesFileName
        try:
            self.Read(self.preferencesFileName)
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
    def SaveToFile(self):
        if self.fileExists:
            try:
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
