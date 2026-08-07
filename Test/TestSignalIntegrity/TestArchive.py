"""
TestArchive.py
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
import unittest
import inspect
import os
import shutil
import stat
import sys
import tempfile
import warnings

from SignalIntegrity.App.Archive import Archive,RmTreeHandlerKeyword,_RmTreeHandlerKeyword

class TestArchive(unittest.TestCase):
    """Tests the removal of archive directories.
    @remark The removal is the part of archiving that behaves differently on
    Windows and on POSIX, so the tests are split into those that can run
    anywhere and those that must simulate POSIX, since on Windows chmod only
    moves the read-only attribute on files and does nothing at all to
    directories.
    """
    def __init__(self, methodName='runTest'):
        self.path=os.path.dirname(os.path.realpath(__file__))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        os.chdir(self.path)
        self.tempDir=tempfile.mkdtemp()
    def tearDown(self):
        for root,dirs,files in os.walk(self.tempDir):
            for name in dirs+files:
                try: os.chmod(os.path.join(root,name),stat.S_IRWXU)
                except Exception: pass
        shutil.rmtree(self.tempDir,ignore_errors=True)
        os.chdir(self.path)
    def Tree(self,mode=None,contents='x'):
        """Builds a directory tree to remove.
        @param mode int (optional) mode to apply to the subdirectory.
        @param contents string (optional) contents of the file in the tree.
        @return string the root of the tree.
        """
        tree=os.path.join(self.tempDir,'tree')
        sub=os.path.join(tree,'sub')
        os.makedirs(sub)
        with open(os.path.join(sub,'file.txt'),'w') as f:
            f.write(contents)
        if mode is not None:
            os.chmod(sub,mode)
        return tree
    def testRmTreeHandlerKeywordIsAccepted(self):
        self.assertTrue(RmTreeHandlerKeyword in inspect.signature(shutil.rmtree).parameters,
                        self.id()+' keyword not accepted by rmtree')
    def testRmTreeHandlerKeywordResolution(self):
        def signature311(path,ignore_errors=False,onerror=None,*,dir_fd=None): pass
        def signature312(path,ignore_errors=False,onerror=None,*,onexc=None,dir_fd=None): pass
        def signature314(path,ignore_errors=False,*,onexc=None,dir_fd=None): pass
        real=shutil.rmtree
        try:
            for signature,expected in ((signature311,'onerror'),
                                       (signature312,'onexc'),
                                       (signature314,'onexc')):
                shutil.rmtree=signature
                self.assertEqual(_RmTreeHandlerKeyword(),expected,self.id()+' wrong keyword')
            # a signature that cannot be introspected must fall back, not raise
            shutil.rmtree=dir
            self.assertEqual(_RmTreeHandlerKeyword(),'onerror',self.id()+' no fallback')
        finally:
            shutil.rmtree=real
    def testRemoveTreeReadOnlyFile(self):
        tree=self.Tree()
        os.chmod(os.path.join(tree,'sub','file.txt'),stat.S_IRUSR)
        Archive._RemoveTree(tree)
        self.assertFalse(os.path.exists(tree),self.id()+' tree not removed')
    def testRemoveTreeReadOnlyDirectory(self):
        # on POSIX it is this, not the read-only file, that blocks the removal
        tree=self.Tree(mode=stat.S_IRUSR|stat.S_IXUSR)
        Archive._RemoveTree(tree)
        self.assertFalse(os.path.exists(tree),self.id()+' tree not removed')
    def testRemoveTreeUnsearchableDirectory(self):
        tree=self.Tree(mode=0)
        Archive._RemoveTree(tree)
        self.assertFalse(os.path.exists(tree),self.id()+' tree not removed')
    def testRemoveTreeDoesNotFollowSymlinks(self):
        tree=os.path.join(self.tempDir,'tree')
        outside=os.path.join(self.tempDir,'outside')
        os.makedirs(tree); os.makedirs(outside)
        keep=os.path.join(outside,'keep.txt')
        with open(keep,'w') as f: f.write('x')
        try:
            os.symlink(outside,os.path.join(tree,'link'))
        except (OSError,NotImplementedError,AttributeError):
            self.skipTest('symlinks not available')
        Archive._RemoveTree(tree)
        self.assertFalse(os.path.exists(tree),self.id()+' tree not removed')
        self.assertTrue(os.path.exists(keep),self.id()+' followed a symlink out of the tree')
    def testRemoveTreeBrokenSymlink(self):
        tree=os.path.join(self.tempDir,'tree')
        os.makedirs(tree)
        broken=os.path.join(tree,'broken')
        try:
            os.symlink(os.path.join(self.tempDir,'nothing_here'),broken)
        except (OSError,NotImplementedError,AttributeError):
            self.skipTest('symlinks not available')
        Archive._MakeRemovable(broken) # chmod follows symlinks and so will fail
        Archive._RemoveTree(tree)
        self.assertFalse(os.path.exists(tree),self.id()+' tree not removed')
    def testRemoveTreeRaisesWhenImpossible(self):
        self.assertRaises(OSError,Archive._RemoveTree,
                          os.path.join(self.tempDir,'does_not_exist'),2,0.01)
    def MakeRemovableModes(self,modes,path):
        """Runs _MakeRemovable against simulated POSIX modes.
        @param modes dict of normalized path to st_mode.
        @param path string the path handed to _MakeRemovable.
        @return dict of normalized path to the mode it was chmod'ed to.
        """
        chmods={}
        class Result(object): pass
        def fakestat(p,*args,**kwargs):
            result=Result(); result.st_mode=modes[os.path.normpath(p)]; return result
        def fakechmod(p,mode,*args,**kwargs):
            chmods[os.path.normpath(p)]=mode
        realstat,realchmod=os.stat,os.chmod
        try:
            os.stat,os.chmod=fakestat,fakechmod
            Archive._MakeRemovable(path)
        finally:
            os.stat,os.chmod=realstat,realchmod
        return chmods
    def testMakeRemovablePosixFileModes(self):
        parent=os.path.normpath(os.path.abspath('/proj/archive'))
        child=os.path.normpath(os.path.abspath('/proj/archive/ro.txt'))
        chmods=self.MakeRemovableModes({child:stat.S_IFREG|0o444,
                                        parent:stat.S_IFDIR|0o555},child)
        fileMode=chmods.get(child); parentMode=chmods.get(parent)
        self.assertTrue(fileMode is not None,self.id()+' file not chmoded')
        self.assertTrue(fileMode&stat.S_IWUSR,self.id()+' file did not gain u+w')
        self.assertEqual(fileMode&0o444,0o444,self.id()+' file lost its read bits')
        # on POSIX the containing directory must be writable and searchable
        # before an entry within it can be unlinked
        self.assertTrue(parentMode is not None,self.id()+' parent not chmoded')
        self.assertEqual(parentMode&(stat.S_IWUSR|stat.S_IXUSR),stat.S_IWUSR|stat.S_IXUSR,
                         self.id()+' parent did not gain u+wx')
        self.assertEqual(parentMode&0o055,0o055,self.id()+' parent lost group/other bits')
    def testMakeRemovablePosixDirectoryModes(self):
        parent=os.path.normpath(os.path.abspath('/proj/archive'))
        subdir=os.path.normpath(os.path.abspath('/proj/archive/sub'))
        chmods=self.MakeRemovableModes({subdir:stat.S_IFDIR|0o000,
                                        parent:stat.S_IFDIR|0o555},subdir)
        dirMode=chmods.get(subdir)
        self.assertTrue(dirMode is not None,self.id()+' directory not chmoded')
        self.assertEqual(dirMode&stat.S_IRWXU,stat.S_IRWXU,self.id()+' directory did not gain u+rwx')
    def testMakeRemovableToleratesChmodFailure(self):
        # not owning the item makes chmod raise EPERM, which must be swallowed
        realchmod=os.chmod
        def raising(p,mode,*args,**kwargs):
            raise PermissionError(1,'Operation not permitted')
        tree=self.Tree()
        try:
            os.chmod=raising
            Archive._MakeRemovable(os.path.join(tree,'sub','file.txt'))
        finally:
            os.chmod=realchmod
    def RunHandler(self,function,useExcInfo=True,error=None):
        """Calls the removal handler the way rmtree would.
        @param function the callable rmtree reports as having failed.
        @param useExcInfo bool (optional) True to pass an exc_info triple as
        'onerror' does, False to pass the exception as 'onexc' does.
        @param error the exception to report.
        @remark On POSIX, rmtree removes by file descriptor and so reports
        os.open, os.lstat and os.scandir, which is why they are worth testing.
        """
        tree=os.path.join(self.tempDir,'tree')
        if not os.path.exists(tree): os.makedirs(tree)
        keyword=RmTreeHandlerKeyword
        def fake_rmtree(path,**kwargs):
            kwargs[keyword](function,tree,
                            (type(error),error,None) if useExcInfo else error)
        real=shutil.rmtree
        try:
            shutil.rmtree=fake_rmtree
            Archive._RemoveTree(tree,attempts=1,delay=0)
        finally:
            shutil.rmtree=real
    def testRemoveTreeHandlerReRaisesOriginalError(self):
        error=PermissionError(13,'Permission denied')
        # os.open needs flags, so retrying it with a path alone raises TypeError,
        # which would otherwise mask the real reason for the failure
        gone=lambda p: os.unlink(os.path.join(p,'gone'))
        for function in (os.open,gone):
            for useExcInfo in (True,False):
                try:
                    self.RunHandler(function,useExcInfo,error)
                    self.fail(self.id()+' no exception raised')
                except Exception as e:
                    self.assertTrue(e is error,self.id()+' original error not re-raised')
    def testRemoveTreeHandlerRetriesSucceed(self):
        error=PermissionError(13,'Permission denied')
        # os.lstat takes a path alone, so the retry simply succeeds
        self.RunHandler(os.lstat,True,error)
        # os.scandir returns an open iterator that must be closed, not leaked
        with warnings.catch_warnings():
            warnings.simplefilter('error',ResourceWarning)
            self.RunHandler(os.scandir,True,error)
    def testRmTreeExceptionUnwrapping(self):
        error=PermissionError(13,'Permission denied')
        self.assertTrue(Archive._RmTreeException((type(error),error,None)) is error,
                        self.id()+' exc_info triple not unwrapped')
        self.assertTrue(Archive._RmTreeException(error) is error,
                        self.id()+' exception not passed through')
        self.assertTrue(Archive._RmTreeException(None) is None,
                        self.id()+' None not handled')
        self.assertTrue(Archive._RmTreeException(('a','b','c')) is None,
                        self.id()+' non-exception triple not handled')
    def testArchiveRoundTrip(self):
        source=os.path.join(self.path,'IdealFourPort.si')
        if not os.path.exists(source):
            self.skipTest('IdealFourPort.si not available')
        project=os.path.join(self.tempDir,'IdealFourPort.si')
        shutil.copy2(source,project)
        currentDir=os.getcwd()
        try:
            os.chdir(self.tempDir)
            from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
            app=SignalIntegrityAppHeadless()
            self.assertTrue(app.OpenProjectFile(project),self.id()+' project could not be opened')
            self.assertTrue(app.Archive(),self.id()+' project could not be archived')
            siz=os.path.join(self.tempDir,'IdealFourPort.siz')
            self.assertTrue(os.path.exists(siz),self.id()+' no archive produced')
            Archive.ExtractArchive(siz)
            archiveDir=os.path.join(self.tempDir,'IdealFourPort_Archive')
            self.assertTrue(os.path.isdir(archiveDir),self.id()+' archive not extracted')
            self.assertTrue(Archive.InAnArchive(os.path.join(archiveDir,'IdealFourPort.si')),
                            self.id()+' extracted project not recognized as archived')
            # extracted files are commonly read-only, which used to defeat removal
            for root,dirs,files in os.walk(archiveDir):
                for name in files:
                    os.chmod(os.path.join(root,name),stat.S_IRUSR|stat.S_IRGRP|stat.S_IROTH)
            Archive.Freshen(os.path.join(archiveDir,'IdealFourPort.si'))
            self.assertTrue(os.path.exists(siz),self.id()+' archive not freshened')
            Archive.UnExtractArchive(archiveDir)
            self.assertFalse(os.path.exists(archiveDir),self.id()+' archive directory not removed')
        finally:
            os.chdir(currentDir)
    def Variable(self,type,value):
        """Builds a project variable of a given type and raw value.
        @param type string the variable type.
        @param value the raw value to store, or None for an unset variable.
        @return VariableConfiguration the variable.
        @remark An unset variable cannot be made through the item assignment,
        which stringifies None into the literal 'None'.  It arises from the
        project file, where an empty <Value/> element reads back as an actual
        None, so the underlying property value is set here the same way.
        """
        from SignalIntegrity.App.ProjectFile import VariableConfiguration
        variable=VariableConfiguration()
        variable['Name']='v'
        variable['Type']=type
        if value is None:
            property=variable.dict['Value']
            property.dict['value']=None
            property.UpdateValue()
            self.assertTrue(variable.GetValue('Value') is None,
                            self.id()+' the unset variable was not built')
        else:
            variable['Value']=value
        return variable
    def testUnsetVariableValue(self):
        """An unset variable of any type must evaluate rather than raise.
        @remark A device bypassed through its element_state leaves its 'file'
        variable with a value of None.  Only the 'string' type used to be
        guarded, so every other type raised a TypeError out of len(None), which
        is what made archiving such a project fail with the unhelpful message
        'object of type NoneType has no len()'.
        """
        for type in ('string','file','float','int','enum'):
            variable=self.Variable(type,None)
            self.assertEqual(variable.Value(),'',
                             self.id()+' unset '+type+' variable did not evaluate empty')
            # the display string must not raise either
            variable.DisplayString()
    def testUnsetVariableDictionary(self):
        """An unset 'file' variable must not become the current directory.
        @remark os.path.abspath('') returns the current directory, which would
        turn an unset file name into a directory name that later looks to the
        archiver like a real file to archive.
        """
        from SignalIntegrity.App.ProjectFile import VariablesConfiguration
        variables=VariablesConfiguration()
        variables['Items']=[self.Variable('file',None)]
        self.assertEqual(variables.Dictionary()['v'],'',
                         self.id()+' unset file variable did not stay empty')
        variables['Items']=[self.Variable('file','some.s4p')]
        self.assertEqual(variables.Dictionary()['v'],
                         os.path.abspath('some.s4p').replace('\\','/'),
                         self.id()+' set file variable not made absolute')
    def testExtractedFileNameRejectsEscapes(self):
        """Entries that would write outside of the destination must be skipped."""
        destination=os.path.abspath(self.tempDir)
        for name in ('../escape.txt','/absolute.txt','a/../../escape.txt','','.'):
            self.assertTrue(Archive._ExtractedFileName(destination,name) is None,
                            self.id()+' '+repr(name)+' was not rejected')
        good=Archive._ExtractedFileName(destination,'Project_Archive/file.txt')
        self.assertEqual(good,os.path.join(destination,'Project_Archive','file.txt'),
                         self.id()+' a good entry was not accepted')
    def testExtractOverReadOnlyFiles(self):
        """Re-extracting over read-only files must succeed.
        @remark CopyArchiveFilesToDestination calls copystat, so a read-only
        source file yields a read-only file inside the archive.  Extracting the
        archive a second time then failed with a PermissionError.
        """
        import zipfile
        siz=os.path.join(self.tempDir,'Project.siz')
        with zipfile.ZipFile(siz,'w') as z:
            z.writestr('Project_Archive/file.txt','contents')
        Archive.ExtractArchive(siz)
        extracted=os.path.join(self.tempDir,'Project_Archive','file.txt')
        self.assertTrue(os.path.exists(extracted),self.id()+' not extracted')
        os.chmod(extracted,stat.S_IRUSR)
        Archive.ExtractArchive(siz) # must not raise
        with open(extracted) as f:
            self.assertEqual(f.read(),'contents',self.id()+' wrong contents')
    def testExtractEmptyArchiveReports(self):
        """An archive with nothing extractable must say so rather than pass."""
        import zipfile
        from SignalIntegrity.App.Archive import SignalIntegrityExceptionArchive
        siz=os.path.join(self.tempDir,'Empty.siz')
        with zipfile.ZipFile(siz,'w') as z:
            pass
        self.assertRaises(SignalIntegrityExceptionArchive,Archive.ExtractArchive,siz)
        self.assertRaises(SignalIntegrityExceptionArchive,Archive.ExtractArchive,None)

if __name__ == '__main__':
    unittest.main()
