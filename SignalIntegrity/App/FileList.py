"""
FileList.py
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
import os

class FileList(object):
    spaces=''
    def __init__(self,filename=None):
        self.filename = os.path.abspath(filename).replace('\\','/')
        self.filelist=[]
        self.cache_file_name = None
    def AddFile(self,filenamelist):
        if isinstance(filenamelist,str):
            self.AddFile(FileList(filenamelist))
        elif isinstance(filenamelist,FileList):
            # print(f'adding: {filenamelist.filename}+{str([item.filename for item in filenamelist.filelist])} to {self.filename}+{str([item.filename for item in self.filelist])}')
            self.filelist.append(filenamelist)
        else:
            raise ValueError('not proper type for adding to file list')
    def AddCacheFile(self,filename):
        self.cache_file_name = os.path.abspath(filename).replace('\\','/')
    def Print(self,spaces=''):
        FileList.spaces=FileList.spaces+'    '
        print(spaces+self.filename+((' cache='+self.cache_file_name) if self.cache_file_name != None else ''))
        for item in self.filelist:
            item.Print(spaces+'+')
        return self
    def _eq_(self,other):
        if self.filename != other.filename:
            return False
        if len(self.filelist) != len(other.filelist):
            return False
        if all([this_item == other_item for this_item,other_item in zip(self.filelist,other.filelist)]):
            return True
        return False
    def Deduplicate(self):
        new_file_list=[]
        for i in range(len(self.filelist)):
            self.filelist[i].Deduplicate()
        for i in range(len(self.filelist)):
            duplicate=False
            for j in range(i,len(self.filelist)):
                if self.filelist[i] == self.filelist[j]:
                    duplicate=True
                    break
            if not duplicate:
                new_file_list.append(self.filelist[i])
        self.filelist = new_file_list
        return self
    def Initialize(self):
        self.filelist=[]
        self.cache_file_name = None
        return self
    def DeleteCacheFile(self):
        if self.cache_file_name == None:
            return
        if not os.path.exists(self.cache_file_name):
            return
        os.remove(self.cache_file_name)
    def ResolveCacheFiles(self):
        good = True
        for item in self.filelist:
            good = good and item.ResolveCacheFiles()
        if not good:
            self.DeleteCacheFile()
            return False
        if self.cache_file_name == None:
            return True
        if not os.path.exists(self.cache_file_name):
            return False
        if not os.path.exists(self.filename):
            self.DeleteCacheFile()
            return False
        cache_file_time = os.path.getmtime(self.cache_file_name)
        file_time = os.path.getmtime(self.filename)
        if file_time > cache_file_time:
            self.DeleteCacheFile()
            return False
        good = True
        for item in self.filelist:
            if not os.path.exists(item.filename):
                good = False
                continue
            file_time = os.path.getmtime(item.filename)
            if file_time > cache_file_time:
                good = False
                continue
            if item.cache_file_name == None:
                continue
            if not os.path.exists(item.cache_file_name):
                good = False
                continue
            file_time = os.path.getmtime(item.cache_file_name)
            if file_time > cache_file_time:
                good = False
                continue
        if not good:
            self.DeleteCacheFile()
            return False
        return True
