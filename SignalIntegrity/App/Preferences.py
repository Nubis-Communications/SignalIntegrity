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
            self.fileExists=not (self.GetValue('Version') is None)
        except:
            self.fileExists=False
        if not self.fileExists:
            try:
                PreferencesFile.__init__(self)
                self.SetValue('Version', __version__)
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
    def AnotherFileOpened(self,filename):
        filepath=os.getcwd()
        lastFiles=self.GetValue('ProjectFiles.LastFile')
        if self.GetValue('ProjectFiles.RetainLastFilesOpened'):
            if (lastFiles[0].GetValue('Name') != filename) or (lastFiles[0].GetValue('Directory') != filepath):
                for lfi in range(len(lastFiles)-1,0,-1):
                    lastFiles[lfi].SetValue('Name',lastFiles[lfi-1].GetValue('Name'))
                    lastFiles[lfi].SetValue('Directory',lastFiles[lfi-1].GetValue('Directory'))
                lastFiles[0].SetValue('Name',filename)
                lastFiles[0].SetValue('Directory',filepath)
                self.SaveToFile()
        else:
            foundOne=False
            for lfi in range(len(lastFiles)):
                if (lastFiles[lfi].GetValue('Name') != None) or (lastFiles[lfi].GetValue('Directory') != None):
                    foundOne=True
                    lastFiles[lfi].SetValue('Name',None)
                    lastFiles[lfi].SetValue('Directory',None)
            if foundOne:
                self.SaveToFile()

    def GetLastFileOpened(self,index=0):
        if self.GetValue('ProjectFiles.OpenLastFile'):
            dirString=self.GetValue('ProjectFiles.LastFile')[index].GetValue('Directory')
            nameString=self.GetValue('ProjectFiles.LastFile')[index].GetValue('Name')
            if (dirString is None) or (nameString is None):
                return None
            else:
                return dirString+'/'+nameString
        else:
            return None

    def GetRecentFileList(self):
        lastFiles=self.GetValue('ProjectFiles.LastFile')
        if lastFiles is None:
            return None
        return [lf.GetValue('Name') for lf in lastFiles]

if __name__ == '__main__':
    pf=Preferences()
    pf.PrintFullInformation()
