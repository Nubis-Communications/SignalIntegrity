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
import sys
import time
import zipfile
import glob

from SignalIntegrity.App.Files import FileParts

from SignalIntegrity.Lib.Exception import SignalIntegrityException
from SignalIntegrity.Lib.Log import Logger

import logging as _logging

#: the logger for everything in this file.
_log=Logger('Archive')


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
    """the exception raised for archiving and archive extraction problems.
    @remark The second, optional argument is accepted because the exception is
    raised in places as (context,detail); without it those raises would fail with
    a TypeError and hide the problem they were meant to report.  Both parts end
    up in the message, which is what the callers display.
    """
    def __init__(self,message='',detail=None):
        if detail is not None:
            message=(str(message)+' '+str(detail)).strip()
        SignalIntegrityException.__init__(self,'Archive',message)

class EquationFileRecorder(object):
    """Records the data files that the project equations read.

    @remark The archive is built by inspecting the file properties of the
    devices in the schematic, which cannot see a file that the equations open
    for themselves -- a csv of channel definitions is the usual example.  Such a
    project archives and extracts without complaint but cannot be calculated
    afterwards, because evaluating its equations fails with a FileNotFoundError.
    The files are therefore observed while the equations run, using an audit
    hook, and added to the archive.  The hook is only installed when an archive
    is actually being built, does nothing at all unless recording is switched
    on, and is simply absent on an interpreter that has no auditing, in which
    case the archive is no worse than it was before.
    """
    _files=set()
    _recording=False
    _installed=False
    #: files that are code rather than project data
    _excludedExtensions=('.py','.pyc','.pyo','.pyd','.so','.dll','.egg','.zip')

    @classmethod
    def _Hook(cls,event,args):
        if not cls._recording or (event != 'open'):
            return
        try:
            path,mode=args[0],args[1]
        except (IndexError,TypeError):
            return
        # only files being read are of interest; a file the equations write is
        # an output, not an input the archive needs to carry
        if not isinstance(path,str) or ((mode is not None) and ('r' not in str(mode))):
            return
        cls._files.add(path)

    @classmethod
    def _Interesting(cls,path):
        """Whether a recorded file is project data worth archiving."""
        try:
            if not os.path.isfile(path):
                return False
        except (OSError,ValueError):
            return False
        absolute=os.path.abspath(path)
        if os.path.splitext(absolute)[1].lower() in cls._excludedExtensions:
            return False
        lowered=absolute.lower()
        for prefix in set([sys.prefix,getattr(sys,'base_prefix',sys.prefix)]):
            if prefix and lowered.startswith(os.path.abspath(prefix).lower()+os.sep):
                return False # part of the python installation, not the project
        return True

    @classmethod
    def Start(cls):
        """Begins recording.
        @return bool whether recording could be started.
        """
        if not cls._installed:
            try:
                sys.addaudithook(cls._Hook)
            except (AttributeError,RuntimeError,TypeError) as e:
                _log.debug('equation data files cannot be recorded: %s',e)
                return False
            cls._installed=True
        cls._files=set()
        cls._recording=True
        return True

    @classmethod
    def Stop(cls):
        """Ends recording.
        @return list of the data files the equations read.
        """
        cls._recording=False
        files=sorted(f for f in cls._files if cls._Interesting(f))
        cls._files=set()
        return files

class Archive(list):

    @property
    def logging(self):
        """whether archive logging is turned on.
        @return bool whether the 'Archive' logging category is enabled at DEBUG.
        """
        return _log.isEnabledFor(_logging.DEBUG)
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
                    # the data files the equations read cannot be discovered from
                    # the schematic, so they are observed while the equations run
                    self.AddFilesToArchive(Archive._EvaluateEquationsRecordingFiles())
                    for device in app.Drawing.schematic.deviceList:
                        args={}
                        for variable in device.variablesList:
                            name=variable['Name']
                            value=variable.Value()
                            if (variable['Type'] == 'file') and value:
                                # an unset file variable has an empty value;
                                # os.path.abspath('') is the current directory,
                                # which is not a file to archive
                                value=os.path.abspath(value)
                            args[name]=value
                        # skip only devices that are removed or bypassed in the netlist
                        # (see NetList.py); any other element state (including None or '')
                        # keeps the device, so its referenced files must still be archived
                        if device['element_state'] != None and device.PartPropertyByKeyword('element_state').GetValue() in ['disabled','thru','thru_wires']:
                            continue
                        for property in device.propertiesList:
                            if property['Type']=='file':
                                propertyValue=property.GetValue()
                                if not propertyValue:
                                    continue # unset file property, nothing to archive
                                filename=os.path.abspath(propertyValue)
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
            _log.exception('building the archive dictionary failed')
            raise(e)
        finally:
            os.chdir(currentPath)
        return self
    @staticmethod
    def _CommonRoot(projectDir,fileList):
        """Returns the directory the archive is built relative to.
        @param projectDir string the directory holding the project being archived.
        @param fileList list of strings the files to be archived.
        @return string the common ancestor directory of the project and its files.
        @remark The archive used to be built relative to the project directory
        alone, so a file the project refers to through '..' landed above the
        archive and was quietly left out of it: the archive extracted without
        complaint but the project inside it could not be calculated because its
        sub-projects and touchstone files were missing.  Building the archive
        relative to the common ancestor instead copies the whole referenced tree
        verbatim, which keeps every relative reference between the archived files
        valid without having to rewrite any of them.  When all of the files are
        at or below the project directory the common ancestor *is* the project
        directory, so the usual archive layout is unchanged.  Files on another
        drive have no common ancestor and are left out, as before.
        """
        common=os.path.abspath(projectDir)
        drive=os.path.splitdrive(common)[0].lower()
        for filename in fileList:
            path=os.path.dirname(os.path.abspath(filename))
            if os.path.splitdrive(path)[0].lower() != drive:
                _log.warning('%s: on another drive, cannot be archived',filename)
                continue
            try:
                common=os.path.commonpath([common,path])
            except ValueError:
                _log.warning('%s: no common path with the project, cannot be archived',filename)
        return common.replace('\\','/')

    def ProjectDestination(self,archiveDir,projectFile):
        """Returns where a project file must be written inside the archive.
        @param archiveDir string the archive directory.
        @param projectFile string the project file being archived.
        @return string the file to write the project to.
        @remark The project keeps its position relative to the common root, which
        is what makes the relative references it holds resolve inside the archive.
        """
        common=getattr(self,'common',None)
        if common is None:
            common=os.path.dirname(os.path.abspath(projectFile))
        relative=os.path.relpath(os.path.abspath(projectFile),common)
        return os.path.join(archiveDir,relative).replace('\\','/')

    @staticmethod
    def _EvaluateEquationsRecordingFiles():
        """Evaluates the project equations, noting the data files they read.
        @return list of the absolute names of the data files the equations read.
        """
        import SignalIntegrity.App.Project
        project=SignalIntegrity.App.Project
        recording=EquationFileRecorder.Start()
        try:
            # the equations are only re-evaluated when their definition has
            # changed, and they were already evaluated when the project was
            # opened, so a re-evaluation is forced here or nothing would be seen
            if recording:
                project.variablesDefinition=None
                project.equationsDefinition=None
            error=project.EvaluateEquations()
            if error is not None:
                _log.warning('evaluating the equations while archiving: %s',error)
        finally:
            files=EquationFileRecorder.Stop() if recording else []
        for filename in files:
            _log.debug('%s: read by the equations, archiving it',filename)
        return [os.path.abspath(filename).replace('\\','/') for filename in files]

    def CopyArchiveFilesToDestination(self,archiveDir,projectFile=None):
        """Copies every file in the archive dictionary into the archive directory.
        @param archiveDir string the archive directory to build.
        @param projectFile string (optional) the project being archived, used to
        locate the common root; the current directory is used when it is omitted.
        @return self
        """
        import SignalIntegrity.App.Project
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        if not self.Archivable():
            return self
        currentPath=os.getcwd()
        try:
            # archive dictionary exists.  copy all of the files in the archive to a directory underneath the project with the name postpended with '_Archive'
            self.srcList=[element['file'].replace('\\','/') for element in self]
            projectDir=os.path.dirname(os.path.abspath(projectFile)) if projectFile else currentPath
            self.common=Archive._CommonRoot(projectDir,self.srcList)
            _log.debug('archive root is %s',self.common)
            try:
                Archive._RemoveTree(archiveDir)
            except FileNotFoundError:
                pass
            self.destList = []
            for filename in self.srcList:
                try:
                    relative=os.path.relpath(filename, self.common)
                    destfile=(archiveDir+'/'+relative).replace('\\','/')
                    if '../' in destfile.replace('\\','/'):
                        raise ValueError('file is above archive')
                    self.destList.append(destfile)
                except ValueError: # a relative path could not be established - don't copy it to the archive
                    self.destList.append(filename)
                    _log.warning('%s: no relative path to the archive root, not archived',filename)
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
                    _log.warning('while copying %s to the archive: %s',srcfile,e)
            # go through all of the files, straightening out the relative path references
            straighten_paths = False
            if straighten_paths:
                for element in self:
                    file=element['file']
                    _log.debug('file is: %s',file.replace('\\','/'))
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
                                    _log.debug('%s: no relative path',variable['Value'])
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
                                            _log.debug('%s: no relative path',variable['Value'])
                            else:
                                try:
                                    app.Device(device['Ref'])[device['Keyword']]['Value'] = NewRelativePath(os.path.join(os.path.dirname(element['orig']),app.Device(device['Ref'])[device['Keyword']]['Value']))
                                except ValueError:
                                    _log.debug('%s: no relative path',variable['Value'])
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
                    _log.warning('while copying file status of %s: %s',srcfile,e)
        finally:
            os.chdir(currentPath)
        return self

    @staticmethod
    def ZipArchive(archiveName,archiveDir,removeDir=True):
        """Zips an archive directory into a .siz file.
        @param archiveName string the name of the archive file to write.
        @param archiveDir string the archive directory, relative or absolute.
        @param removeDir bool (optional, defaults to True) whether to remove the
        archive directory afterwards.
        @remark The names stored in the zip file are always relative to the
        *parent* of the archive directory, so that the archive always contains a
        single 'ProjectName_Archive' folder.  Storing the names as walked would
        make the content of the zip file depend on the current directory at the
        time of the archiving (and, for an absolute archive directory, would
        store the whole path with the drive stripped off), which produces
        archives that either extract into the wrong place or are empty.
        """
        archiveRoot=os.path.abspath(archiveDir)
        parentDir=os.path.dirname(archiveRoot)
        def zipdir(path, ziph):
            # ziph is zipfile handle
            written=0
            for root, dirs, files in os.walk(path):
                for file in files:
                    fullPath=os.path.join(root, file)
                    ziph.write(fullPath,arcname=os.path.relpath(fullPath,parentDir))
                    written+=1
            return written
        zipFileName=os.path.abspath(FileParts(archiveName).FullFilePathExtension('siz'))
        zipf = zipfile.ZipFile(zipFileName, 'w', zipfile.ZIP_DEFLATED)
        try:
            written=zipdir(archiveRoot, zipf)
        finally:
            zipf.close()
        if written == 0:
            _log.warning('%s: nothing was archived from %s',zipFileName,archiveRoot)
        if removeDir:
            Archive._RemoveTree(archiveRoot)

    @staticmethod
    def _ExtractedFileName(destinationDir,entryName):
        """Returns the file to write for one zip entry, or None to skip it.
        @param destinationDir string the directory the archive extracts into.
        @param entryName string the name of the entry in the zip file.
        @return string the absolute file name, or None if the entry cannot be
        extracted safely.
        @remark Entry names are stored with forward slashes.  A name that is
        absolute, that contains a drive letter, or that climbs above the
        destination with '..' would write outside of the destination directory,
        so such entries are skipped rather than extracted.  Archives written by
        older versions of ZipArchive, which stored the walked path rather than a
        path relative to the archive directory, can contain such names.
        """
        name=entryName.replace('\\','/')
        parts=[part for part in name.split('/') if part not in ('','.')]
        if not parts:
            return None
        fileName=os.path.abspath(os.path.join(destinationDir,*parts))
        root=os.path.abspath(destinationDir)
        if os.path.splitdrive(name)[0] or name.startswith('/') or \
                (os.path.commonpath([root,fileName]) != root):
            _log.warning('%s: entry is outside of the archive, skipped',entryName)
            return None
        return fileName

    @staticmethod
    def _MakeWritable(filename):
        """Grants write permission to an existing file so it can be overwritten.
        @param filename string the file to make writable.
        @remark A file copied into an archive keeps the mode of the file it was
        copied from (CopyArchiveFilesToDestination calls copystat), so a
        read-only source file yields a read-only file in the archive.  Extracting
        the archive a second time then fails with a PermissionError on Windows
        unless the read-only attribute is cleared first.
        """
        try:
            if os.path.exists(filename):
                os.chmod(filename,os.stat(filename).st_mode|stat.S_IWUSR)
        except Exception:
            pass

    @staticmethod
    def ExtractArchive(filename):
        """Extracts a .siz archive next to the archive file.
        @param filename string the archive (.siz) file to extract.
        @remark The archive is extracted into the directory containing the
        archive file, which is where the 'ProjectName_Archive' folder held in the
        archive lands.  Existing files are overwritten, including read-only ones,
        so that an archive can be extracted over a previous extraction.
        """
        if filename is None:
            raise SignalIntegrityExceptionArchive('During archive extraction:','no archive file was provided')
        fp=FileParts(filename)
        destinationDir=fp.AbsoluteFilePath()

        try:
            with zipfile.ZipFile(filename) as z:
                extracted=0
                for f in z.infolist():
                    name=Archive._ExtractedFileName(destinationDir,f.filename)
                    if name is None:
                        continue
                    if f.is_dir():
                        os.makedirs(name, exist_ok=True)
                        continue
                    os.makedirs(os.path.dirname(name), exist_ok=True)
                    Archive._MakeWritable(name)
                    try:
                        with open(name, 'wb') as outFile:
                            outFile.write(z.open(f).read())
                    except PermissionError as e:
                        raise SignalIntegrityExceptionArchive(
                            'During archive extraction:',
                            name+' could not be written.  It is either read-only or '
                            'open in another program.\n('+str(e)+')')
                    extracted+=1
                    try:
                        date_time = time.mktime(f.date_time + (0, 0, -1))
                        os.utime(name, (date_time, date_time))
                    except (OverflowError,ValueError,OSError) as e:
                        # a bad or out of range time stamp in the archive must not
                        # cost us the extracted file
                        _log.debug('%s: time stamp could not be set: %s',name,e)
            if extracted == 0:
                raise SignalIntegrityExceptionArchive('During archive extraction:',
                                                      filename+' contains no extractable files')
        except SignalIntegrityExceptionArchive:
            _log.exception('extracting the archive failed')
            raise
        except Exception as e:
            _log.exception('extracting the archive failed')
            raise SignalIntegrityExceptionArchive('During archive extraction:',
                                                  filename+' could not be extracted.\n('+str(e)+')')

    @staticmethod
    def FindProjectInArchive(archiveDir,projectName):
        """Finds a project file inside an extracted archive.
        @param archiveDir string the extracted archive directory.
        @param projectName string the project file name, with or without its
        extension.
        @return string the project file, or None if it is not in the archive.
        @remark The project is at the root of the archive whenever everything it
        refers to is at or below it, but it sits deeper when it refers to files
        through '..', because the archive is then built relative to the common
        ancestor so that those references stay valid.  The root is therefore
        checked first and the rest of the archive only afterwards, which finds
        the project in either layout and keeps older archives working.
        """
        name=FileParts(projectName).FileNameTitle()+'.si'
        candidate=os.path.join(archiveDir,name)
        if os.path.exists(candidate):
            return candidate.replace('\\','/')
        matches=[]
        for root,dirs,files in os.walk(archiveDir):
            if name in files:
                matches.append(os.path.join(root,name).replace('\\','/'))
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            # the shallowest one is the project; a deeper one of the same name is
            # a sub-project that happens to share the name
            matches.sort(key=lambda m: len(m.split('/')))
            _log.warning('%s: found more than once in the archive, using %s',name,matches[0])
            return matches[0]
        return None

    @staticmethod
    def ArchiveRoot(ProjectName):
        """Returns the archive directory a project has been extracted into.
        @param ProjectName string the project file.
        @return string the '<Name>_Archive' directory the project is in, or None
        if the project is not inside one.
        @remark The project is not necessarily at the root of the archive, so
        every directory above it is examined rather than just its own parent.
        """
        filename=os.path.abspath(ProjectName).replace('\\','/')
        directory=os.path.dirname(filename)
        while True:
            name=os.path.basename(directory)
            if name.endswith('_Archive'):
                title=name[:-len('_Archive')]
                if os.path.exists(os.path.join(os.path.dirname(directory),title+'.siz')):
                    return directory
            parent=os.path.dirname(directory)
            if parent == directory:
                return None
            directory=parent

    @staticmethod
    def InAnArchive(ProjectName):
        """Whether a project is one that has been extracted from an archive.
        @param ProjectName string the project file.
        @return bool True when the project lives inside an extracted archive.
        """
        return Archive.ArchiveRoot(ProjectName) is not None

    @staticmethod
    def Freshen(ProjectName):
        """Rewrites the .siz of the archive a project was extracted from.
        @param ProjectName string a project inside an extracted archive.
        """
        archiveRoot=Archive.ArchiveRoot(ProjectName)
        if archiveRoot is None:
            raise SignalIntegrityExceptionArchive('During archiving:',
                                                  ProjectName+' is not inside an extracted archive')
        dirAbove=os.path.dirname(archiveRoot)
        archiveDirName=os.path.basename(archiveRoot)
        archiveFileName=archiveDirName[:-len('_Archive')]+'.siz'
        currentDir=os.getcwd()
        try:
            os.chdir(dirAbove)
            Archive.ZipArchive(os.path.join(dirAbove,archiveFileName),archiveDirName,removeDir=False)
        finally:
            os.chdir(currentDir)

    @staticmethod
    def UnExtractArchive(archiveDir):
        """Removes an extracted archive directory.
        @param archiveDir string the extracted archive directory, or a directory
        inside one.
        """
        archiveRoot=archiveDir
        if not os.path.basename(os.path.abspath(archiveDir)).endswith('_Archive'):
            found=Archive.ArchiveRoot(os.path.join(archiveDir,'x.si'))
            if found is not None:
                archiveRoot=found
        splitDir=os.path.abspath(archiveRoot).replace('\\', '/').split('/')
        dirAbove='/'.join(splitDir[:-1])
        os.chdir(dirAbove)
        Archive._RemoveTree(archiveRoot)

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
