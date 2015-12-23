'''
Created on Oct 15, 2015

@author: peterp
'''
import os

def ConvertFileNameToRelativePath(filename):
    if filename!='':
        filenameList=('/'.join(filename.split('\\'))).split('/')
        if len(filenameList)>1:
            currentWorkingDirectoryList=('/'.join(os.getcwd().split('\\'))).split('/')
            atOrBelow=True
            for tokenIndex in range(min(len(filenameList),len(currentWorkingDirectoryList))):
                if filenameList[tokenIndex]!=currentWorkingDirectoryList[tokenIndex]:
                    atOrBelow=False
                    break
                if atOrBelow: tokenIndex=tokenIndex+1
            if tokenIndex > 0:
                filenameprefix=''
                for i in range(tokenIndex,len(currentWorkingDirectoryList)):
                    filenameprefix=filenameprefix+'../'
                filenamesuffix='/'.join(filenameList[tokenIndex:])
                filename=filenameprefix+filenamesuffix
    return filename

class FileParts(object):
    def __init__(self,filename=None):
        if not filename is None:
            filename=str(filename)
        else:
            filename=''
        if filename=='':
            self.filename=''
            self.filepath=os.getcwd()
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
    
        

        
    
        
        
