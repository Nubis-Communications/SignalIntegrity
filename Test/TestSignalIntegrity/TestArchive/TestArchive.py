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
        source=os.path.join(self.path,'..','TestSParameterFile','IdealFourPort.si')
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
    def WriteMiniProjectWithEquationFile(self,directory,csvName='dep.csv'):
        """Writes a minimal project whose equations pull csvName in via ArchiveFile()."""
        with open(os.path.join(directory,csvName),'w') as f:
            f.write('a,b\n1,2\n')
        project=os.path.join(directory,'MiniEqn.si')
        with open(project,'w') as f:
            f.write('<Project>\n'
                    '<Drawing><Schematic><Devices></Devices><Wires></Wires></Schematic></Drawing>\n'
                    '<Equations>\n<AutoDebug>True</AutoDebug>\n<Lines>\n'
                    '<EquationLine><Line>import csv</Line></EquationLine>\n'
                    "<EquationLine><Line>depfile = open(ArchiveFile('"+csvName+"'))</Line></EquationLine>\n"
                    '<EquationLine><Line>rows = list(csv.DictReader(depfile))</Line></EquationLine>\n'
                    '<EquationLine><Line>depfile.close()</Line></EquationLine>\n'
                    '</Lines>\n</Equations>\n'
                    '<CalculationProperties></CalculationProperties>\n'
                    '<Variables><Items></Items></Variables>\n'
                    '</Project>\n')
        return project
    def testArchiveFileEquationHelperRecordsDependency(self):
        import SignalIntegrity.App.ProjectFile as PF
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App as App
        currentDir=os.getcwd()
        try:
            os.chdir(self.tempDir)
            project=self.WriteMiniProjectWithEquationFile(self.tempDir)
            app=SignalIntegrityAppHeadless()
            self.assertTrue(app.OpenProjectFile(project),self.id()+' project could not be opened')
            ad=Archive()
            ad.BuildArchiveDictionary(app,App.Project['Variables'].Dictionary())
            names=[os.path.basename(element['file']) for element in ad]
            self.assertIn('dep.csv',names,self.id()+' equation-declared file not archived')
            self.assertFalse(PF.RecordingArchiveFiles,self.id()+' recording flag not reset')
        finally:
            os.chdir(currentDir)
    def testEquationEvaluatorSharesNamespace(self):
        import SignalIntegrity.App.ProjectFile as PF
        result=PF.ProjectFile.EvaluateSafely(
            'T_b=1/f_b',{'f_b':106.25e9},{'T_b':None})
        self.assertAlmostEqual(result['T_b'],1/106.25e9)
    def testArchiveFileHelperIsNoOpDuringNormalEvaluation(self):
        import SignalIntegrity.App.ProjectFile as PF
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App as App
        currentDir=os.getcwd()
        try:
            os.chdir(self.tempDir)
            project=self.WriteMiniProjectWithEquationFile(self.tempDir)
            app=SignalIntegrityAppHeadless()
            self.assertTrue(app.OpenProjectFile(project),self.id()+' project could not be opened')
            PF.RecordingArchiveFiles=False
            PF.EquationArchiveFiles.clear()
            error=App.Project.EvaluateEquations(force=True)
            self.assertIsNone(error,self.id()+' equations raised during normal evaluation: '+str(error))
            self.assertEqual(PF.EquationArchiveFiles,[],self.id()+' recorded a file while not archiving')
        finally:
            os.chdir(currentDir)
    def testArchiveFileEquationRoundTrip(self):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        currentDir=os.getcwd()
        try:
            os.chdir(self.tempDir)
            self.WriteMiniProjectWithEquationFile(self.tempDir)
            app=SignalIntegrityAppHeadless()
            self.assertTrue(app.OpenProjectFile(os.path.join(self.tempDir,'MiniEqn.si')),
                            self.id()+' project could not be opened')
            self.assertTrue(app.Archive(),self.id()+' project could not be archived')
            siz=os.path.join(self.tempDir,'MiniEqn.siz')
            self.assertTrue(os.path.exists(siz),self.id()+' no archive produced')
            Archive.ExtractArchive(siz)
            archiveDir=os.path.join(self.tempDir,'MiniEqn_Archive')
            self.assertTrue(os.path.exists(os.path.join(archiveDir,'dep.csv')),
                            self.id()+' equation-declared file missing from archive')
        finally:
            os.chdir(currentDir)
    def testMangledFileName(self):
        from SignalIntegrity.Lib.FileNameMangling import MangledFileName,IsMangledFileName
        # only s-parameter file names are mangled, for now
        for name in ['foo.si','foo.csv','foo.txt','foo.s4','foo.sp','foo.sxp','foo']:
            self.assertEqual(MangledFileName(os.path.join(self.tempDir,name)),'',
                             self.id()+' mangled '+name)
        for name in ['foo.s1p','foo.S4P','foo.s16p']:
            mangled=MangledFileName(os.path.join(self.tempDir,name))
            self.assertTrue(IsMangledFileName(mangled),self.id()+' did not mangle '+name)
            self.assertEqual(os.path.splitext(mangled)[1],os.path.splitext(name)[1],
                             self.id()+' extension not preserved for '+name)
            self.assertFalse('/' in mangled or '\\' in mangled or ':' in mangled,
                             self.id()+' mangled name is not a bare file name')
        # the drive letter case must not change the mangled name
        if os.path.splitdrive(self.tempDir)[0] != '':
            drive,rest=os.path.splitdrive(os.path.join(self.tempDir,'foo.s2p'))
            self.assertEqual(MangledFileName(drive.lower()+rest),MangledFileName(drive.upper()+rest),
                             self.id()+' mangled name depends on drive letter case')
        self.assertFalse(IsMangledFileName('foo.s2p'),self.id()+' plain name reported as mangled')
    def testResolveFileNamePrefersMangledCopy(self):
        from SignalIntegrity.Lib.FileNameMangling import MangledFileName,ResolveFileName
        outside=os.path.join(self.tempDir,'outside'); os.makedirs(outside)
        project=os.path.join(self.tempDir,'project'); os.makedirs(project)
        referenced=os.path.join(outside,'TestDut.s2p')
        with open(referenced,'w') as f: f.write('original\n')
        # with no mangled copy present, the name is returned untouched
        self.assertEqual(ResolveFileName(referenced,project),referenced,
                         self.id()+' resolved without a mangled copy')
        mangled=os.path.join(project,MangledFileName(referenced))
        with open(mangled,'w') as f: f.write('mangled\n')
        # the mangled copy wins even though the original is still reachable
        self.assertEqual(os.path.normcase(ResolveFileName(referenced,project)),
                         os.path.normcase(mangled),self.id()+' mangled copy not preferred')
        # a relative name is never resolved
        self.assertEqual(ResolveFileName('TestDut.s2p',project),'TestDut.s2p',
                         self.id()+' resolved a relative name')
    def NonRelativeProject(self,directory,outsideDir):
        """Writes a project referencing an s-parameter file that has no relative path.
        @param directory string where the project is written.
        @param outsideDir string the directory holding the referenced file.
        @return tuple (project file name, referenced file name).
        """
        source=os.path.join(self.path,'..','TestSParameterFile','Reordered.si')
        sparameters=os.path.join(self.path,'..','TestSParameterFile','TestDut.s4p')
        if not os.path.exists(source) or not os.path.exists(sparameters):
            self.skipTest('Reordered.si and TestDut.s4p not available')
        os.makedirs(outsideDir,exist_ok=True)
        referenced=os.path.join(outsideDir,'TestDut.s4p').replace('\\','/')
        shutil.copy2(sparameters,referenced)
        project=os.path.join(directory,'Reordered.si')
        with open(source,'r') as f: text=f.read()
        with open(project,'w') as f: f.write(text.replace('<Value>TestDut.s4p</Value>','<Value>'+referenced+'</Value>'))
        return (project,referenced)
    def BuiltArchive(self,project,archiveNonRelativeFiles):
        """Builds and copies an archive of a project, returning the archive directory."""
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        import SignalIntegrity.App as App
        app=SignalIntegrityAppHeadless()
        self.assertTrue(app.OpenProjectFile(project),self.id()+' project could not be opened')
        archiveDir=os.path.join(os.path.dirname(project),'Reordered_Archive').replace('\\','/')
        archiveDict=Archive(archiveNonRelativeFiles)
        archiveDict.BuildArchiveDictionary(app,App.Project['Variables'].Dictionary())
        archiveDict.CopyArchiveFilesToDestination(archiveDir)
        return archiveDir
    def testArchiveNonRelativeFileExcludedByDefault(self):
        currentDir=os.getcwd()
        try:
            projectDir=os.path.join(self.tempDir,'project'); os.makedirs(projectDir)
            project,referenced=self.NonRelativeProject(projectDir,os.path.join(self.tempDir,'outside'))
            os.chdir(projectDir)
            archiveDir=self.BuiltArchive(project,False)
            self.assertEqual([name for name in os.listdir(archiveDir) if name.endswith('.s4p')],[],
                             self.id()+' non-relative file archived while the option is off')
        finally:
            os.chdir(currentDir)
    def testArchiveNonRelativeFileUnderMangledName(self):
        from SignalIntegrity.Lib.FileNameMangling import MangledFileName
        currentDir=os.getcwd()
        try:
            projectDir=os.path.join(self.tempDir,'project'); os.makedirs(projectDir)
            project,referenced=self.NonRelativeProject(projectDir,os.path.join(self.tempDir,'outside'))
            os.chdir(projectDir)
            archiveDir=self.BuiltArchive(project,True)
            mangled=os.path.join(archiveDir,MangledFileName(referenced))
            self.assertTrue(os.path.exists(mangled),self.id()+' non-relative file not archived')
            with open(mangled,'r') as f: mangledText=f.read()
            with open(referenced,'r') as f: referencedText=f.read()
            self.assertEqual(mangledText,referencedText,self.id()+' archived copy differs from the original')
        finally:
            os.chdir(currentDir)
    def testArchiveUsesExistingMangledFileUnconditionally(self):
        from SignalIntegrity.Lib.FileNameMangling import MangledFileName
        currentDir=os.getcwd()
        try:
            projectDir=os.path.join(self.tempDir,'project'); os.makedirs(projectDir)
            project,referenced=self.NonRelativeProject(projectDir,os.path.join(self.tempDir,'outside'))
            mangledName=MangledFileName(referenced)
            shutil.copy2(referenced,os.path.join(projectDir,mangledName))
            os.remove(referenced) # the original location is no longer reachable
            os.chdir(projectDir)
            # the option is off: the mangled file is picked up because it is already local
            archiveDir=self.BuiltArchive(project,False)
            self.assertTrue(os.path.exists(os.path.join(archiveDir,mangledName)),
                            self.id()+' existing mangled file not archived')
        finally:
            os.chdir(currentDir)

class TestArchiveProjects(unittest.TestCase):
    def setUp(self):
        import uuid
        import SignalIntegrity.App as App
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        self.cwd=os.getcwd()
        self.directory=os.path.abspath('archive-project-test-'+uuid.uuid4().hex)
        os.mkdir(self.directory)
        self.project=App.Project
        self.preferences=App.Preferences
        self.stack=SignalIntegrityAppHeadless.projectStack
        self.stackContents=self.stack.stack[:]
        self.addCleanup(self.cleanup)

    def cleanup(self):
        import SignalIntegrity.App as App
        os.chdir(self.cwd)
        App.Project=self.project
        App.Preferences=self.preferences
        self.stack.stack[:]=self.stackContents
        shutil.rmtree(self.directory)

    def makeProject(self):
        import copy
        from SignalIntegrity.App.ProjectFile import ProjectFile,SchematicPageConfiguration,VariableConfiguration
        from SignalIntegrity.App.ProjectFileBase import ProjectFileBase
        fixture=os.path.join(os.path.dirname(__file__),'..','TestSParameterFile','Reordered.si')
        template=ProjectFile().Read(fixture)['Drawing.Schematic.Devices'][0]
        def device(filename):
            result=copy.deepcopy(template)
            for prop in result['PartProperties']:
                if prop['Keyword']=='file':
                    prop['Value']=filename
            return result
        for name in ('inactive.s4p','second.s4p','live.s4p','equation.csv','equation_data','nested.csv'):
            with open(os.path.join(self.directory,name),'w') as stream:
                stream.write('data')
        nested=ProjectFile().New()
        nestedVariable=VariableConfiguration()
        nestedVariable['Name']='data'
        nestedVariable['Type']='file'
        nestedVariable['Value']='missing.s4p'
        nested['Variables.Items']=[nestedVariable]
        nested.AddProject('NestedInactive')
        nested.SelectProject(1)
        nested['Equations'].PutTextString("ArchiveFile('nested.csv')")
        nested.SelectProject(0)
        ProjectFileBase.Write(nested,os.path.join(self.directory,'nested.si'))
        project=ProjectFile().New()
        project.AddProject('Inactive')
        project.SelectProject(1)
        project['Drawing.Schematic.Devices']=[device('=path')]
        variable=VariableConfiguration()
        variable['Name']='path'
        variable['Type']='file'
        variable['Value']='unused.s4p'
        variable['ReadOnly']=True
        subprojectVariable=VariableConfiguration()
        subprojectVariable['Name']='subproject'
        subprojectVariable['Type']='file'
        subprojectVariable['Value']='nested.si'
        project['Variables.Items']=[variable,subprojectVariable]
        project['Equations'].PutTextString(
            "path = 'inactive.s4p'\nArchiveFile('equation.csv')\nArchiveFile('equation_data')")
        page=SchematicPageConfiguration()
        page['Name']='Other page'
        childDevice=device('=subproject')
        childArg=VariableConfiguration()
        childArg['Name']='data'
        childArg['Type']='file'
        childArg['Value']='second.s4p'
        childDevice['Variables.Items']=[childArg]
        page['Drawing.Schematic.Devices']=[device('second.s4p'),childDevice]
        project['Pages']=[page]
        project.SelectProject(0)
        filename=os.path.join(self.directory,'parent.si')
        ProjectFileBase.Write(project,filename)
        return filename,device('live.s4p')

    def test_inactive_projects_pages_and_nested_dependencies(self):
        import SignalIntegrity.App as App
        import SignalIntegrity.App.ProjectFile as PF
        from SignalIntegrity.App.Device import DeviceFromProject
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        filename,liveConfig=self.makeProject()
        app=SignalIntegrityAppHeadless()
        self.assertTrue(app.OpenProjectFile(filename))
        original=App.Project
        liveDevice=DeviceFromProject(liveConfig).result
        app.Drawing.schematic.deviceList.append(liveDevice)
        before=original.LinesToWrite()
        stackMarker=('outer nesting',self.cwd)
        self.stack.stack.append(stackMarker)
        stackBefore=self.stack.stack[:]
        current=os.getcwd()
        result=Archive().BuildArchiveDictionary(app,original['Variables'].Dictionary())
        self.assertEqual(os.getcwd(),current)
        self.assertIs(App.Project,original)
        self.assertEqual(original['Selected'],0)
        self.assertEqual(original.LinesToWrite(),before)
        self.assertEqual(original['Projects'][1]['Variables.Items'][0]['Value'],'unused.s4p')
        self.assertIs(app.Drawing.schematic.deviceList[0],liveDevice)
        self.assertEqual(self.stack.stack,stackBefore)
        self.assertFalse(PF.RecordingArchiveFiles)
        names={os.path.basename(entry['file']) for entry in result}
        self.assertTrue({'parent.si','inactive.s4p','second.s4p','live.s4p',
                         'equation.csv','equation_data','nested.si','nested.csv'}.issubset(names),names)
        destination=os.path.join(self.directory,'output')
        result.CopyArchiveFilesToDestination(destination)
        for name in ('inactive.s4p','second.s4p','live.s4p','equation.csv','equation_data','nested.si','nested.csv'):
            self.assertTrue(os.path.isfile(os.path.join(destination,name)),name)

    def test_missing_inactive_dependency_restores_state(self):
        import SignalIntegrity.App as App
        import SignalIntegrity.App.ProjectFile as PF
        from SignalIntegrity.App.Archive import SignalIntegrityExceptionArchive
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        filename,_=self.makeProject()
        os.remove(os.path.join(self.directory,'inactive.s4p'))
        app=SignalIntegrityAppHeadless()
        self.assertTrue(app.OpenProjectFile(filename))
        original=App.Project
        stackBefore=self.stack.stack[:]
        current=os.getcwd()
        with self.assertRaises(SignalIntegrityExceptionArchive):
            Archive().BuildArchiveDictionary(app,{})
        self.assertIs(App.Project,original)
        self.assertEqual(original['Selected'],0)
        self.assertEqual(self.stack.stack,stackBefore)
        self.assertEqual(os.getcwd(),current)
        self.assertFalse(PF.RecordingArchiveFiles)

    def test_external_scan_preserves_outer_recording(self):
        import SignalIntegrity.App as App
        import SignalIntegrity.App.ProjectFile as PF
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        filename,_=self.makeProject()
        app=SignalIntegrityAppHeadless()
        self.assertTrue(app.OpenProjectFile(filename))
        original=App.Project
        recording=PF.RecordingArchiveFiles
        files=PF.EquationArchiveFiles[:]
        marker=(self.directory,'outer.csv')
        try:
            PF.RecordingArchiveFiles=True
            PF.EquationArchiveFiles[:]=[marker]
            result=Archive().BuildArchiveDictionary(filename,{},external=True)
            self.assertTrue(PF.RecordingArchiveFiles)
            self.assertEqual(PF.EquationArchiveFiles,[marker])
            self.assertIs(App.Project,original)
            self.assertIn('nested.csv',[os.path.basename(entry['file']) for entry in result])
        finally:
            PF.RecordingArchiveFiles=recording
            PF.EquationArchiveFiles[:]=files

    def test_copy_failure_is_reported(self):
        from unittest.mock import patch
        from SignalIntegrity.App.Archive import SignalIntegrityExceptionArchive
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        filename,_=self.makeProject()
        app=SignalIntegrityAppHeadless()
        self.assertTrue(app.OpenProjectFile(filename))
        archive=Archive().BuildArchiveDictionary(app,{})
        with patch.object(shutil,'copy2',side_effect=OSError('copy failed')):
            with self.assertRaises(SignalIntegrityExceptionArchive):
                archive.CopyArchiveFilesToDestination(os.path.join(self.directory,'output'))

if __name__ == '__main__':
    unittest.main()
