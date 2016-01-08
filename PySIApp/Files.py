'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
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







