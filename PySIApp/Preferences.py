'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2017 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''

from PreferencesFile import PreferencesFile

import os,errno
import platform

class Preferences(PreferencesFile):
    def __init__(self):
        PreferencesFile.__init__(self)
        thisOS=platform.system()
        if thisOS == 'Linux':
            pathToPreferencesFile = os.path.expanduser('~')+'/.pysi'
        else:
            pathToPreferencesFile = '/LeCroy/PySI'
        self.preferencesFileName=pathToPreferencesFile+'/preferences'
        try:
            os.makedirs(pathToPreferencesFile)
        except OSError, e:
            if e.errno != errno.EEXIST:
                return
        try:
            self.Read(self.preferencesFileName)
        except:
            try:
                self.Write(self.preferencesFileName)
            except:
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
        return [lf.GetValue('Name') for lf in lastFiles]

if __name__ == '__main__':
    pf=Preferences()
    pf.PrintFullInformation()
