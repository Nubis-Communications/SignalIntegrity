'''
Created on Oct 15, 2015

@author: peterp
'''
import os

def ConvertFileNameToRelativePath(filename):
    if filename!='':
        filenameList=filename.split('/')
        if len(filenameList)>1:
            currentWorkingDirectoryList=os.getcwd().split('/')
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
