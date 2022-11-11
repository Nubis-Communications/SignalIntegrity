"""
Archive.py
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
import shutil
import zipfile

from SignalIntegrity.App.Files import FileParts

from SignalIntegrity.Lib.Exception import SignalIntegrityException

class SignalIntegrityExceptionArchive(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'Archive',message)

class Archive(dict):
    def __init__(self):
        dict.__init__(self,{})
    def Archivable(self):
        return self != {}
    def BuildArchiveDictionary(self,parent):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        currentPath=os.getcwd()
        try:
            if not isinstance(parent,str):
                thisFile=os.path.abspath(parent.fileparts.FileNameWithExtension())
                app=parent
            else:
                thisFile=parent
                app=SignalIntegrityAppHeadless()
                app.projectStack.Push()
                if not app.OpenProjectFile(thisFile):
                    app.projectStack.Pull()
                    dict.__init__(self,{})
                    return self
 
            initial=True

            done=False
            while not done:
                if not initial:
                    done=True
                    for thisFile in self.keys():
                        if not self[thisFile]['descended']:
                            done=False
                            break
                    if not done:
                        app=SignalIntegrityAppHeadless()
                        app.projectStack.Push()
                        if not app.OpenProjectFile(thisFile):
                            app.projectStack.Pull()
                            dict.__init__(self,{})
                            raise SignalIntegrityExceptionArchive('During archiving:',thisFile+' could not be opened')
                            return self
                    else: # done building the archive dictionary
                        done=True
                else:
                    initial=False
                if not done:
                    for device in app.Drawing.schematic.deviceList:
                        for property in device.propertiesList:
                            if property['Type']=='file':
                                filename=os.path.abspath(property['Value'])
                                if len(filename.split(os.path.sep)[-1].split('.')) != 2:
                                    continue # file name does not have an extension
                                if not thisFile in self.keys():
                                    self[thisFile]={'descended':True,'devices':[{'Ref':device['ref']['Value'],'Keyword':property['Keyword'],'File':filename}]}
                                else:
                                    self[thisFile]['devices'].append({'Ref':device['ref']['Value'],'Keyword':property['Keyword'],'File':filename})
                                if not filename in self.keys():
                                    self[filename]={'descended':(not filename.endswith('.si')),'devices':[]}
                    if not thisFile in self.keys(): # does not reference any files
                        self[thisFile]={'descended':True,'devices':[]}

                    self[thisFile]['descended']=True # done searching for file devices in this project

                    if hasattr(app, 'projectStack'):
                        app.projectStack.Pull()
        finally:
            os.chdir(currentPath)
        return self
    def CopyArchiveFilesToDestination(self,archiveDir):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        if not self.Archivable():
            return self
        currentPath=os.getcwd()
        try:
            # archive dictionary exists.  copy all of the files in the archive to a directory underneath the project with the name postpended with '_Archive'
            self.srcList=[filename for filename in self.keys()]
            self.common=os.path.dirname(self.srcList[0])
            try:
                shutil.rmtree(archiveDir)
            except FileNotFoundError:
                pass
            self.destList=[archiveDir+'\\'+os.path.relpath(filename, self.common).replace('/','\\').replace('..\\','up\\') for filename in self.srcList]
            for srcfile,destfile in zip(self.srcList,self.destList):
                self[destfile]=self[srcfile]
                del self[srcfile]
                for device in self[destfile]['devices']:
                    device['File']=device['File'].replace(self.common,archiveDir)
                os.makedirs(os.path.dirname(destfile),exist_ok=True)
                shutil.copy(src=srcfile,dst=destfile)
            # go through all of the files, straightening out the relative path references
            for file in self.keys():
                deviceList=self[file]['devices']
                if len(deviceList)>0:
                    app=SignalIntegrityAppHeadless()
                    app.projectStack.Push()
                    if not app.OpenProjectFile(file):
                        app.projectStack.Pull()
                        raise SignalIntegrityExceptionArchive('During archiving:',file+' could not be opened')
                        return self
                    self.update()
                    for device in deviceList:
                        app.Device(device['Ref'])[device['Keyword']]['Value']=app.Device(device['Ref'])[device['Keyword']]['Value'].replace('/','\\').replace('..\\','up\\')
                    app.SaveProject()
                    app.projectStack.Pull()
        finally:
            os.chdir(currentPath)
        return self

    @staticmethod
    def ZipArchive(archiveName,archiveDir,removeDir=True):
        # zip the files
        def zipdir(path, ziph):
            # ziph is zipfile handle
            for root, dirs, files in os.walk(path):
                for file in files:
                    ziph.write(os.path.join(root, file))
        zipf = zipfile.ZipFile(os.path.abspath(os.path.abspath(FileParts(archiveName).FullFilePathExtension('siz'))), 'w', zipfile.ZIP_DEFLATED)
        zipdir(archiveDir, zipf)
        zipf.close()
        if removeDir:
            shutil.rmtree(archiveDir)

    @staticmethod
    def ExtractArchive(filename):
        fp=FileParts(filename)
        projectName=fp.FileNameTitle()
        archiveDir=projectName+'_Archive'

        zipdata = zipfile.ZipFile(filename)
        zipinfos = zipdata.infolist()
        oldArchiveDir=zipinfos[0].filename.split('/')[0]
        oldProjectName=oldArchiveDir[:-len('_Archive')]

        if (projectName == oldProjectName) and (archiveDir == oldArchiveDir):
            zipdata.close()
            shutil.unpack_archive(filename,fp.AbsoluteFilePath(),format='zip')
        else:
            # iterate through each file
            for zipinfo in zipinfos:
                # This will do the renaming
                zipfilename=zipinfo.filename.split('/')
                zipfilename[0]=archiveDir
                if len(zipfilename)==2 and zipfilename[1] == oldProjectName+'.si':
                    zipfilename[1]=projectName+'.si'
                zipinfo.filename='/'.join(zipfilename)
                zipdata.extract(zipinfo,path=fp.AbsoluteFilePath())
            zipdata.close()

    @staticmethod
    def InAnArchive(ProjectName):
        fp=FileParts(ProjectName)
        filename=os.path.abspath(ProjectName)
        splitDir=filename.replace('\\', '/').split('/')
        currentDirName=splitDir[-2]
        dirAbove='/'.join(splitDir[:-2])
        archiveDirName=fp.FileNameTitle()+'_Archive'
        archiveFileName=fp.FileNameWithExtension('.siz')
        return (currentDirName == archiveDirName) and (os.path.exists(dirAbove+'/'+archiveFileName))

    @staticmethod
    def Freshen(ProjectName):
        fp=FileParts(ProjectName)
        filename=os.path.abspath(ProjectName)
        splitDir=filename.replace('\\', '/').split('/')
        currentDirName=splitDir[-2]
        dirAbove='/'.join(splitDir[:-2])
        archiveDirName=fp.FileNameTitle()+'_Archive'
        archiveFileName=fp.FileNameWithExtension('.siz')
        currentDir=os.getcwd()
        os.chdir('..')
        try:
            Archive.ZipArchive(dirAbove+'/'+archiveFileName,archiveDirName,removeDir=False)
        finally:
            os.chdir(currentDir)

    @staticmethod
    def UnExtractArchive(archiveDir):
        splitDir=archiveDir.replace('\\', '/').split('/')
        dirAbove='/'.join(splitDir[:-1])
        os.chdir(dirAbove)
        shutil.rmtree(archiveDir)
