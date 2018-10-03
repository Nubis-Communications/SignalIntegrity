"""
results caching
"""
# Copyright (c) 2018 Teledyne LeCroy, all rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import pickle

class ResultsCache(object):
    '''
    classdocs
    '''
    def __init__(self,name,filename=None):
        '''
        Constructor
        '''
        self.filename=filename
        self.extra='_cached'+name+'.p'
    def CheckCache(self):
        self.hash=self.HashValue()
        import os
        if self.filename is None:
            return False
        if not os.path.exists(self.filename+self.extra):
            return False
        if not self.CheckTimes(self.filename+self.extra):
            return False
        try:
            f = open(self.filename+self.extra, 'rb')
            tmp_dict = pickle.load(f)
            f.close()
        except:
            return False
        try:
            if tmp_dict['hash'] == self.hash:
                self.__dict__.update(tmp_dict)
                return True
            return False
        except:
            return False
    def CacheResult(self):
        if self.filename is None:
            return
        f = open(self.filename+self.extra, 'wb')
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        pickleDict = {x:self.__dict__[x] for x in members}
        pickle.dump(pickleDict, f, 2)
        f.close()
    def CheckTimes(self,cacheFilename):
        return True

class LinesCache(ResultsCache):
    '''
    classdocs
    '''
    def __init__(self,name,filename=None):
        '''
        Constructor
        '''
        ResultsCache.__init__(self,name,filename)
    def HashValue(self):
        return hash(repr(self.m_lines)+repr(self.m_f)+repr(self.m_args))
    def FileTime(self,fileName):
        import os
        modificationTime = os.path.getmtime(fileName)
        return modificationTime
    def CheckTimes(self,cacheFilename):
        import os
        fileList=[]
        from SignalIntegrity.Helpers.LineSplitter import LineSplitter
        for line in self.m_lines:
            lineList=LineSplitter(line)
            if len(lineList) == 0: # pragma: no cover
                pass
            elif lineList[0] == 'device':
                if len(lineList)>=5:
                    if lineList[3]=='file':
                        fileList.append(lineList[4])
            elif lineList[0] == 'system':
                fileList.append(lineList[2])
        try:
            cacheFileTime = os.path.getmtime(cacheFilename)
        except:
            return False
        for fileName in fileList:
            try:
                modificationTime = os.path.getmtime(fileName)
                if modificationTime > cacheFileTime:
                    return False
            except:
                return False
        return True
