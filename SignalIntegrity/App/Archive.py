"""
Archive.py
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
import shutil
import stat
import time
import zipfile
import glob

from SignalIntegrity.App.Files import FileParts

from SignalIntegrity.Lib.Exception import SignalIntegrityException

def _RmTreeHandlerKeyword():
    """Returns the keyword to use for shutil.rmtree's error handler.
    @return string 'onexc' or 'onerror'.
    @remark rmtree's 'onerror' callback is deprecated as of Python 3.12 in favor
    of 'onexc' and is slated for removal.  Both are called as
    (function,path,error), so a single handler serves either one and only the
    keyword differs.  The keyword is discovered from rmtree's actual signature
    rather than hard-coded against a version number, so it keeps working both on
    old interpreters that have only 'onerror' and on future ones that have only
    'onexc'.
    """
    try:
        import inspect
        if 'onexc' in inspect.signature(shutil.rmtree).parameters:
            return 'onexc'
    except Exception:
        pass
    return 'onerror'

#: see _RmTreeHandlerKeyword; resolved once, at import
RmTreeHandlerKeyword=_RmTreeHandlerKeyword()

class SignalIntegrityExceptionArchive(SignalIntegrityException):
    def __init__(self,message=''):
        SignalIntegrityException.__init__(self,'Archive',message)

class Archive(list):
    logging=True
    def __init__(self):
        list.__init__(self,[])
    def Archivable(self):
        return self != []
    def AddFileToArchive(self,filename):
        if not os.path.exists(filename):
            return
        for file in self:
            if file['file'] == filename:
                return
        element = {'file':filename,
                     'descended':True,
                     'devices':[],
                     'args':{}}
        self.append(element)
    def AddFilesToArchive(self,files_list):
        for filename in files_list:
            self.AddFileToArchive(filename)
    def BuildArchiveDictionary(self,parent,args={},external=False):
        import SignalIntegrity.App.Project
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        currentPath=os.getcwd()
        try:
            if not isinstance(parent,str):
                thisFile=os.path.abspath(parent.fileparts.FileNameWithExtension())
                app=parent
                fileargs=args
            else:
                thisFile=parent
                app=SignalIntegrityAppHeadless()
                app.projectStack.Push()
                if external:
                    external=False
                    fileargs=args
                else:
                    fileargs=SignalIntegrity.App.Project['Variables'].Dictionary()
                if not app.OpenProjectFile(thisFile,args=fileargs):
                    app.projectStack.Pull()
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
                    #Force equations to evaluate so that variabels are propagated correctly
                    SignalIntegrity.App.Project.EvaluateEquations()
                    for device in app.Drawing.schematic.deviceList:
                        args={}
                        for variable in device.variablesList:
                            name=variable['Name']
                            value=variable.Value()
                            if variable['Type'] == 'file':
                                value=os.path.abspath(value)
                            args[name]=value
                        if device['element_state'] != None and device.PartPropertyByKeyword('element_state').GetValue() != '':
                            continue
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
                                    try:
                                        element
                                    except NameError:
                                        element=self[[fileelement['file'] for fileelement in self].index(thisFile)]
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
            self.common=currentPath
            try:
                shutil.rmtree(archiveDir)
            except FileNotFoundError:
                pass
            self.destList = []
            for filename in self.srcList:
                try:
                    destfile=(archiveDir+'/'+os.path.relpath(filename, self.common)).replace('\\','/')
                    if '../' in destfile:
                        raise ValueError('file is above archive')
                    self.destList.append(destfile)
                except ValueError: # a relative path could not be established - don't copy it to the archive
                    self.destList.append(filename)
                    if self.logging: print(filename+': no relative path')
            for element,srcfile,destfile in zip(self,self.srcList,self.destList):
                element['file']=destfile
                element['orig']=srcfile
                for device in element['devices']:
                    device['File']=device['File'].replace(self.common,archiveDir)
                os.makedirs(os.path.dirname(destfile),exist_ok=True)
                try:
                    if not os.path.exists(destfile):
                        shutil.copy2(src=srcfile,dst=destfile)
                        shutil.copystat(src=srcfile,dst=destfile)
                        if SignalIntegrity.App.Preferences['ProjectFiles.ArchiveCachedResults']:
                            srcpath,srcfile_for_cache=os.path.split(srcfile)
                            srcfile_for_cache,srcext=os.path.splitext(srcfile_for_cache)
                            cache_types=['_cachedTransferMatrices.p','_cachedSParameters.p','*_cachedEyeDiagramBitMap.p']
                            dstpath,_=os.path.split(destfile)
                            for cachefile_suffix in cache_types:
                                cachefile_srcfile_list = glob.glob(os.path.join(srcpath,srcfile_for_cache+cachefile_suffix))
                                for cache_srcfile in cachefile_srcfile_list:
                                    if os.path.exists(cache_srcfile):
                                        cache_dstfile=os.path.join(dstpath,os.path.split(cache_srcfile)[1])
                                        if not os.path.exists(cache_dstfile):
                                            shutil.copy2(src=cache_srcfile,dst=cache_dstfile)
                                            shutil.copystat(src=cache_srcfile,dst=cache_dstfile)
                except Exception as e:
                    print(e)
            # go through all of the files, straightening out the relative path references
            straighten_paths = False
            if straighten_paths:
                for element in self:
                    file=element['file']
                    print('file is: '+file.replace('\\','/'))
                    if file == 'C:/Users/pete_/Documents/NubisSystemSim/Projects/PicMZMSimplified_Archive/ElectricalChannels/Packages/TxElectricalPackage.si':
                        pass
                    deviceList=element['devices']
                    if len(deviceList)>0:
                        app=SignalIntegrityAppHeadless()
                        app.projectStack.Push()
                        if not app.OpenProjectFile(file,element['args'] if 'args' in element else {}):
                            app.projectStack.Pull()
                            raise SignalIntegrityExceptionArchive('During archiving:',file+' could not be opened')
                            return self
                        def NewRelativePath(path):
                            if 'None' in path:
                                pass
                            original_path=path
                            # calculate relative path with respect to common (replacing remaining ../ with up/
                            path=os.path.relpath(os.path.abspath(path),self.common).replace('\\','/').replace('../','up/')
                            path=os.path.abspath(os.path.join(self.common,path)).replace('\\','/')
                            # calculate relative path to archive
                            path=os.path.relpath(os.path.abspath(path),os.path.dirname(element['orig'])).replace('\\','/')
                            # calculate resulting absolute path
                            #path=os.path.join(archiveDir,path)
                            # calculate new relative path from where device was pointing
                            #path=os.path.relpath(path).replace('\\','/')
                            print(original_path + ' >>>> '+path)
                            return path
                        for variable in SignalIntegrity.App.Project['Variables.Items']:
                            if variable['Type'] == 'file':
                                try:
                                    filename=NewRelativePath(variable['Value'])
                                    variable['Value']=filename
                                except (AttributeError,TypeError,ValueError) as e:
                                    if self.logging: print(variable['Value']+': no relative path')
                        for device in deviceList:
                            schematic_device = app.Device(device['Ref'])
                            if schematic_device['element_state'] != None and schematic_device.PartPropertyByKeyword('element_state').GetValue() != '':
                                continue
                            filename=app.Device(device['Ref'])[device['Keyword']]['Value']
                            if (filename != None) and (len(filename)>0) and (filename[0]=='='):
                                import SignalIntegrity.App.Project
                                if filename[1:] in SignalIntegrity.App.Project['Variables'].Names():
                                    variable = SignalIntegrity.App.Project['Variables'].VariableByName(filename[1:])
                                    if variable.Value() != None:
                                        try:
                                            variable['Value']=NewRelativePath(variable['Value'])
                                        except ValueError:
                                            if self.logging: print(variable['Value']+': no relative path')
                            else:
                                try:
                                    app.Device(device['Ref'])[device['Keyword']]['Value'] = NewRelativePath(os.path.join(os.path.dirname(element['orig']),app.Device(device['Ref'])[device['Keyword']]['Value']))
                                except ValueError:
                                    if self.logging: print(variable['Value']+': no relative path')
                        app.SaveProject()
                        app.projectStack.Pull()
            for element,srcfile,destfile in zip(self,self.srcList,self.destList):
                element['file']=destfile
                for device in element['devices']:
                    device['File']=device['File'].replace(self.common,archiveDir)
                try:
                    if os.path.exists(destfile):
                        shutil.copystat(src=srcfile,dst=destfile)
                except Exception as e:
                    print(e)
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

        os.makedirs(archiveDir, exist_ok=True)

        import time

        z = zipfile.ZipFile(filename)

        for f in z.infolist():
            name, date_time = f.filename, f.date_time
            name = os.path.join(fp.AbsoluteFilePath(), name)
            os.makedirs(os.path.dirname(name), exist_ok=True)
            with open(name, 'wb') as outFile:
                outFile.write(z.open(f).read())
            date_time = time.mktime(date_time + (0, 0, -1))
            os.utime(name, (date_time, date_time))

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
        Archive._RemoveTree(archiveDir)

    @staticmethod
    def _MakeRemovable(path):
        """Grants the permissions needed to remove path.
        @param path string the file or directory that could not be removed.
        @remark On Windows it is the read-only attribute on the item itself that
        blocks the removal, so write permission is added to it.  On POSIX it is
        the *containing* directory that must be writable and searchable for an
        entry to be unlinked, so write and execute permission are added there as
        well.  In both cases the permissions are added to the existing mode rather
        than replacing it, so that (for example) a directory does not lose the
        read/execute bits it needs in order to be traversed.
        """
        for p in (path,os.path.dirname(os.path.abspath(path))):
            try:
                mode=os.stat(p).st_mode
                addition=stat.S_IRUSR|stat.S_IWUSR
                if stat.S_ISDIR(mode):
                    addition=addition|stat.S_IXUSR
                os.chmod(p,mode|addition)
            except Exception:
                pass

    @staticmethod
    def _RmTreeException(error):
        """Returns the exception reported to an rmtree removal handler.
        @param error the third argument handed to the handler.
        @return the exception that caused the removal to fail, or None if it
        cannot be determined.
        @remark 'onerror' is called with the sys.exc_info() triple while 'onexc'
        is called with the exception itself, so both forms are accepted here.
        """
        if isinstance(error,BaseException):
            return error
        if isinstance(error,tuple) and (len(error) == 3) and isinstance(error[1],BaseException):
            return error[1]
        return None

    @staticmethod
    def _RemoveTree(directory,attempts=5,delay=0.2):
        """Removes a directory tree, retrying briefly on transient failures.
        @param directory string the directory tree to remove.
        @param attempts int (optional, defaults to 5) number of removal attempts.
        @param delay float (optional, defaults to 0.2) seconds to wait between attempts.
        @remark A removal can fail for reasons that have nothing to do with the
        caller: a read-only file copied out of an archive, or -- on Windows -- a
        file or directory momentarily held open by a virus scanner, the search
        indexer or an editor.  The error handler fixes up the permissions and the
        loop retries a few times, which covers those transient cases.  A genuine,
        persistent problem still raises after the last attempt, so real errors are
        not hidden.
        """
        # shutil.rmtree's 'onerror' callback is deprecated as of Python 3.12 in
        # favor of 'onexc'.  Both are called as (function,path,error), so the same
        # handler serves either one; only the keyword differs.
        handlerKeyword=RmTreeHandlerKeyword
        def handler(function,path,error):
            Archive._MakeRemovable(path)
            try:
                result=function(path)
            except Exception:
                # The retry itself failed.  On POSIX, rmtree removes by file
                # descriptor and so can report os.open, which needs flags as
                # well as a path; calling it with a path alone raises a
                # TypeError that would mask the real reason for the failure.
                # Raising the original error instead lets the loop below retry
                # and, if the trouble persists, report something meaningful.
                original=Archive._RmTreeException(error)
                if original is not None:
                    raise original
                raise
            # os.scandir is reported on POSIX and returns an open iterator whose
            # descriptor would otherwise stay open until it is collected.
            close=getattr(result,'close',None)
            if close is not None:
                close()
        for attempt in range(attempts):
            try:
                shutil.rmtree(directory,**{handlerKeyword:handler})
                return
            except Exception:
                if attempt == attempts-1:
                    raise
                time.sleep(delay)
