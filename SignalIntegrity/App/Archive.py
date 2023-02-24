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

class Archive(list):
    def __init__(self):
        list.__init__(self,[])
    def Archivable(self):
        return self != []
    def BuildArchiveDictionary(self,parent):
        import SignalIntegrity.App.Project
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        currentPath=os.getcwd()
        try:
            if not isinstance(parent,str):
                thisFile=os.path.abspath(parent.fileparts.FileNameWithExtension())
                app=parent
                fileargs={}
            else:
                thisFile=parent
                app=SignalIntegrityAppHeadless()
                app.projectStack.Push()
                fileargs=SignalIntegrity.App.Project['Variables'].Dictionary()
                if not app.OpenProjectFile(thisFile,args=fileargs):
                    app.projectStack.Pull()
                    list.__init__(self,[])
                    return self
 
            initial=True

            done=False
            while not done:
                if not initial:
                    done=True
                    for element in self:
                        thisFile=element['file']
                        if not element['descended']:
                            done=False
                            break
                    if not done:
                        app=SignalIntegrityAppHeadless()
                        app.projectStack.Push()
                        fileargs=element['args']
                        if not app.OpenProjectFile(thisFile,args=fileargs):
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
                        args={}
                        for variable in device.variablesList:
                            name=variable['Name']
                            value=variable.Value()
                            if variable['Type'] == 'file':
                                value=os.path.abspath(value)
                            args[name]=value
                        for property in device.propertiesList:
                            if property['Type']=='file':
                                filename=os.path.abspath(property.GetValue())
                                if len(filename.split(os.path.sep)[-1].split('.')) != 2:
                                    continue # file name does not have an extension
                                if not thisFile in [fileelement['file'] for fileelement in self]:
                                    element={'file':thisFile,
                                             'descended':True,
                                             'devices':[{'Ref':device['ref']['Value'],
                                                         'Keyword':property['Keyword'],
                                                         'File':filename,
                                                         'args':args}],
                                             'args':fileargs}
                                    self.append(element)
                                else:
                                    element['devices'].append({'Ref':device['ref']['Value'],
                                                               'Keyword':property['Keyword'],
                                                               'File':filename,
                                                               'args':args})
                                if not filename in [fileelement['file'] for fileelement in self]:
                                    self.append({'file':filename,
                                                 'descended':(not filename.endswith('.si')),
                                                 'devices':[],
                                                 'args':args})
                                else:
                                    # this file is in the list, but now a check is made to ensure that the file, if a project file
                                    # was opened with the same arguments.  If not, we must add a duplicate file to the list with the
                                    # new, different set of arguments.
                                    for newElement in self:
                                        if newElement['file'] == filename:
                                            if newElement['args'] != args:
                                                self.append({'file':filename,
                                                             'descended':(not filename.endswith('.si')),
                                                             'devices':[],
                                                             'args':args})
                                                break
                    if not thisFile in [fileelement['file'] for fileelement in self]: # does not reference any files
                        element = {'file':thisFile,
                                     'descended':True,
                                     'devices':[],
                                     'args':{}}
                        self.append(element)
                    element['descended']=True # done searching for file devices in this project
                    if hasattr(app, 'projectStack') and (app.projectStack.stack != []):
                        app.projectStack.Pull()
        except Exception as e:
            print(e)
            raise(e)
        finally:
            os.chdir(currentPath)
        return self
    def CopyArchiveFilesToDestination(self,archiveDir):
        import SignalIntegrity.App.Project
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        if not self.Archivable():
            return self
        currentPath=os.getcwd()
        try:
            # archive dictionary exists.  copy all of the files in the archive to a directory underneath the project with the name postpended with '_Archive'
            self.srcList=[element['file'].replace('\\','/') for element in self]
            self.common=os.path.dirname(self.srcList[0]).replace('\\','/')
            try:
                shutil.rmtree(archiveDir)
            except FileNotFoundError:
                pass
            self.destList=[(archiveDir+'/'+os.path.relpath(filename, self.common)).replace('\\','/').replace('../','up/') for filename in self.srcList]
            for element,srcfile,destfile in zip(self,self.srcList,self.destList):
                element['file']=destfile
                for device in element['devices']:
                    device['File']=device['File'].replace(self.common,archiveDir)
                os.makedirs(os.path.dirname(destfile),exist_ok=True)
                try:
                    if not os.path.exists(destfile):
                        shutil.copy(src=srcfile,dst=destfile)
                except Exception as e:
                    print(e)
            # go through all of the files, straightening out the relative path references
            for element in self:
                file=element['file']
                deviceList=element['devices']
                if len(deviceList)>0:
                    app=SignalIntegrityAppHeadless()
                    app.projectStack.Push()
                    if not app.OpenProjectFile(file,element['args'] if 'args' in element else {}):
                        app.projectStack.Pull()
                        raise SignalIntegrityExceptionArchive('During archiving:',file+' could not be opened')
                        return self
                    for variable in SignalIntegrity.App.Project['Variables.Items']:
                        if variable['Type'] == 'file':
                            try:
                                filename=os.path.abspath(variable['Value'].replace('\\','/').replace('../','up/'))
                                if os.path.exists(filename):
                                    variable['Value']=os.path.relpath(filename)
                            except (AttributeError,TypeError):
                                pass
                    for device in deviceList:
                        filename=app.Device(device['Ref'])[device['Keyword']]['Value']
                        if (filename != None) and (len(filename)>0) and (filename[0]=='='):
                            import SignalIntegrity.App.Project
                            if filename[1:] in SignalIntegrity.App.Project['Variables'].Names():
                                variable = SignalIntegrity.App.Project['Variables'].VariableByName(filename[1:])
                                if variable.Value() != None:
                                    variable['Value']=os.path.relpath(os.path.abspath(variable.Value())).replace('\\','/').replace('../','up/')
                        else:
                            app.Device(device['Ref'])[device['Keyword']]['Value']=os.path.relpath(os.path.abspath(app.Device(device['Ref'])[device['Keyword']]['Value'])).replace('\\','/').replace('../','up/')
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
