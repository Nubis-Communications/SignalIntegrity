"""
Files.py
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
import os

def ConvertFileNameToRelativePath(filename):
    if filename!='':
        filename=os.path.relpath(filename,os.getcwd())
    return filename

class FileParts(object):
    def __init__(self,filename=None):
        if not filename is None:
            filename=str(filename)
        else:
            filename=''
        if filename=='':
            self.filename=''
            self.filepath=''
            self.fileext=''
        else:
            filename=ConvertFileNameToRelativePath(filename)
            self.filename=('/'.join(filename.split('\\'))).split('/')[-1]
            self.filepath='/'.join(('/'.join(filename.split('\\'))).split('/')[:-1])
            if self.filepath != '':
                self.filepath=self.filepath+'/'
            self.fileext=''
            if len(self.filename.split('.')) > 1:
                splitl=self.filename.split('.')
                self.filename='.'.join(splitl[:-1])
                self.fileext='.'+splitl[-1]
            if self.filename is None:
                self.filename=''
            if self.filepath is None:
                self.filepath=''
            if self.fileext is None:
                self.fileext=''
    def FullFilePathExtension(self,ext=None):
        if not ext is None:
            ext=str(ext)
            if len(ext)>0:
                if not ext[0]=='.':
                    ext='.'+ext
            self.fileext=ext
        if self.filename=='':
            return ''
        return self.filepath+self.filename+self.fileext
    def FileNameTitle(self):
        return self.filename
    def FileNameWithExtension(self,ext=None):
        if self.filename=='':
            return ''
        if not ext is None:
            ext=str(ext)
            if len(ext)>0:
                if not ext[0]=='.':
                    ext='.'+ext
            self.fileext=ext
        return self.filename+self.fileext
    def FilePath(self):
        return self.filepath
    def AbsoluteFilePath(self):
        return os.path.abspath(self.filepath)







