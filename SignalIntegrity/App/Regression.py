"""
Regression.py
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
import subprocess
import time
import zipfile
import contextlib

from SignalIntegrity.App.Archive import Archive
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
from SignalIntegrity.Lib.Test.RegressionFiles import RegressionContext, RegressionFiles


def _retryFileAction(action,attempts=8,delay=1.0):
    """Runs a filesystem action, retrying transient Windows access errors.
    @remark Antivirus / the search indexer briefly hold handles on a just-extracted tree,
    so an immediate rename or rmtree can fail with WinError 5; a short retry clears it.
    """
    for attempt in range(attempts):
        try:
            return action()
        except OSError:
            if attempt == attempts-1:
                raise
            time.sleep(delay)
from SignalIntegrity.Lib.ResultsCache import ResultsCache


@contextlib.contextmanager
def _CachingDisabled():
    """Disables SignalIntegrity result caching for the duration of a regression run.
    A cache hit would (a) skip re-parsing a sub-project, so its nested devices are never
    expanded or recorded and the sprayed artifact set varies run to run, and (b) return a
    stored result even after the computation code changed - the cache hash covers the
    netlist definition, not the code - masking a genuine regression.  Verified: caching on
    non-deterministically omitted sub-project artifacts; off records the complete set.
    """
    previous=ResultsCache.enabled
    ResultsCache.enabled=False
    try:
        yield
    finally:
        ResultsCache.enabled=previous


def _RegressionRoot(projectFile):
    projectFile=os.path.abspath(projectFile)
    return os.path.join(os.path.dirname(projectFile),
                        os.path.splitext(os.path.basename(projectFile))[0]+'_RegressionCandidate')


def _RegressionReferenceRoot(projectFile):
    projectFile=os.path.abspath(projectFile)
    return os.path.join(os.path.dirname(projectFile),
                        os.path.splitext(os.path.basename(projectFile))[0]+'_RegressionReference')


def _MeldReferenceRoot(projectFile):
    projectFile=os.path.abspath(projectFile)
    return os.path.join(os.path.dirname(projectFile),
                        os.path.splitext(os.path.basename(projectFile))[0]+'_RegressionMeldReference')


def _MeldCandidateRoot(projectFile):
    projectFile=os.path.abspath(projectFile)
    return os.path.join(os.path.dirname(projectFile),
                        os.path.splitext(os.path.basename(projectFile))[0]+'_RegressionMeldCandidate')



def _ZipRegression(root,archiveFile):
    with zipfile.ZipFile(archiveFile,'w',zipfile.ZIP_DEFLATED) as archive:
        parent=os.path.dirname(root)
        for directory,_,files in os.walk(root):
            for filename in files:
                path=os.path.join(directory,filename)
                archive.write(path,os.path.relpath(path,parent).replace('\\','/'))


def _ExtractRegression(archiveFile,destination):
    with zipfile.ZipFile(archiveFile) as archive:
        archive.extractall(destination)


def _RemoveIfExists(path):
    """Removes a file if it exists (used to clear the project archive byproduct)."""
    if path and os.path.exists(path):
        os.remove(path)


def _CleanupRegressionTrees(archiveRoot,regressionRoot,currentDirectory):
    """Removes temporary extracted trees and restores the caller's directory."""
    try:
        os.chdir(currentDirectory)
        if os.path.exists(archiveRoot):
            Archive._RemoveTree(archiveRoot)
        if os.path.exists(regressionRoot):
            Archive._RemoveTree(regressionRoot)
    finally:
        os.chdir(currentDirectory)


def _RecordEyeDiagrams(projectFile,result,args):
    """Records the eye diagram bitmaps of a simulation result, if any."""
    if not result or result == {}:
        return
    try:
        labels=result['eye diagram labels']
        diagrams=result['eye diagrams']
    except Exception:
        return
    for label,eyeDiagram in zip(labels,diagrams):
        RegressionContext.RecordEyeDiagram(projectFile,eyeDiagram.Image(),label,args)


def _Calculate(app,projectFile,args=None,callback=None):
    args={} if args is None else args
    if callback is not None and callback(0,'+'+os.path.basename(projectFile)) is False:
        return False
    try:
        if not app.OpenProjectFile(os.path.abspath(projectFile),args):
            raise ValueError('project could not be opened: '+projectFile)
        app.Drawing.DrawSchematic()
        RegressionContext.RecordProjectArtifacts(projectFile,app,args)
        if app.Drawing.canCalculateSParameters:
            result=app.CalculateSParameters(callback)
            if result != {}:
                RegressionContext.RecordSParameters(projectFile,result['s-parameters'],args)
        elif app.Drawing.canSimulate:
            # eye diagrams are computed (needed for BER) and archived, but not compared
            _RecordEyeDiagrams(projectFile,app.Simulate(callback,EyeDiagrams=True),args)
        elif app.Drawing.canVirtualProbe:
            _RecordEyeDiagrams(projectFile,app.VirtualProbe(callback,EyeDiagrams=True),args)
    finally:
        if callback is not None:
            callback(0,'-')
    return True


class RegressionAdapter(object):
    """Bridges the generic regression orchestration to one application's project
    archiving and calculation.  Subclasses supply the application-specific steps."""
    def Archive(self,projectFile,archiveNonRelativeFiles=None,args=None):
        """Archives the project headlessly and returns the produced .siz path."""
        raise NotImplementedError
    def CalculateAndRecord(self,extractedProject,args=None,callback=None):
        """Opens the extracted project, calculates it, and sprays its artifacts via
        RegressionContext.  Returns False if the callback aborted before calculation."""
        raise NotImplementedError


class SignalIntegrityRegressionAdapter(RegressionAdapter):
    """Drives regression for SignalIntegrity schematic projects."""
    def Archive(self,projectFile,archiveNonRelativeFiles=None,args=None):
        app=SignalIntegrityAppHeadless()
        if not app.OpenProjectFile(projectFile,args={} if args is None else args):
            raise ValueError('project could not be opened: '+projectFile)
        if not app.Archive(archiveNonRelativeFiles=archiveNonRelativeFiles):
            raise ValueError('project could not be archived: '+projectFile)
        return os.path.splitext(projectFile)[0]+'.siz'
    def CalculateAndRecord(self,extractedProject,args=None,callback=None):
        return _Calculate(SignalIntegrityAppHeadless(),extractedProject,args,callback)


def RunGeneration(adapter,projectFile,regressionArchiveFile,archiveNonRelativeFiles=None,
                  args=None,artifacts=None,callback=None):
    """Generate a regression archive using an application adapter.
    @param adapter RegressionAdapter supplying archiving and calculation.
    @param projectFile string project file to archive and calculate.
    @param regressionArchiveFile string explicit output regression archive path.
    @param archiveNonRelativeFiles bool (optional) forwarded to project archiving.
    @param args dict (optional) project arguments.
    @param artifacts list (optional) enabled regression artifacts.
    @return string the generated regression archive path.
    """
    projectFile=os.path.abspath(projectFile)
    regressionArchiveFile=os.path.abspath(regressionArchiveFile)
    currentDirectory=os.getcwd()
    if callback is not None and callback(0,'+Archiving '+os.path.basename(projectFile)) is False:
        return None
    archiveRoot=os.path.splitext(projectFile)[0]+'_Archive'
    regressionRoot=_RegressionRoot(projectFile)
    projectArchive=os.path.splitext(projectFile)[0]+'.siz'
    aborted=False
    contextStarted=False
    # every artifact below is torn down in the finally, so a failed generation - at any
    # stage, archiving included - leaves nothing behind (the finished regression archive
    # is written elsewhere)
    try:
        projectArchive=adapter.Archive(projectFile,archiveNonRelativeFiles,args) or projectArchive
        if callback is not None:
            callback(0,'-')
        Archive.ExtractArchive(projectArchive)
        if os.path.exists(regressionRoot):
            shutil.rmtree(regressionRoot)
        os.makedirs(regressionRoot)
        extractedProject=os.path.join(archiveRoot,os.path.basename(projectFile))
        RegressionContext.Start(archiveRoot,regressionRoot,write=True,artifacts=artifacts)
        contextStarted=True
        with _CachingDisabled():
            try:
                # CalculateAndRecord returns False when the callback aborts before calculation
                if adapter.CalculateAndRecord(extractedProject,args,callback) is False:
                    aborted=True
            finally:
                RegressionContext.Stop()
                contextStarted=False
        if not aborted:
            _ZipRegression(regressionRoot,regressionArchiveFile)
    finally:
        # cleanup runs whether the traversal completed, aborted, or raised at any stage
        if contextStarted:
            RegressionContext.Stop()
        _CleanupRegressionTrees(archiveRoot,regressionRoot,currentDirectory)
        _RemoveIfExists(projectArchive)
    if callback is not None and not aborted:
        callback(100,'Regression generation complete')
    return regressionArchiveFile


def GenerateRegression(projectFile,regressionArchiveFile,archiveNonRelativeFiles=None,args=None,artifacts=None,callback=None):
    """Generate a regression archive for a SignalIntegrity project.
    @return string the generated regression archive path.
    """
    return RunGeneration(SignalIntegrityRegressionAdapter(),projectFile,regressionArchiveFile,
                         archiveNonRelativeFiles=archiveNonRelativeFiles,args=args,
                         artifacts=artifacts,callback=callback)



def _CopyIfExists(source,destination):
    """Copies a file, creating parent directories, when it exists."""
    if not os.path.exists(source):
        return
    directory=os.path.dirname(destination)
    if directory != '':
        os.makedirs(directory,exist_ok=True)
    shutil.copy2(source,destination)


def _OpenDiffTool(referenceRoot,candidateRoot,results,projectFile):
    """Opens meld on only the failing files so harmless differences stay hidden.
    @return bool True if meld was launched (its trees must then be left on disk).
    """
    meld=shutil.which('meld')
    if meld is None:
        return False
    failing=[result for result in results if not result.ok]
    if not failing:
        return False
    meldReference=_MeldReferenceRoot(projectFile)
    meldCandidate=_MeldCandidateRoot(projectFile)
    for root in (meldReference,meldCandidate):
        if os.path.exists(root):
            shutil.rmtree(root)
    os.makedirs(meldReference,exist_ok=True)
    os.makedirs(meldCandidate,exist_ok=True)
    for result in failing:
        relative=str(result.filename)
        _CopyIfExists(os.path.join(referenceRoot,relative),os.path.join(meldReference,relative))
        _CopyIfExists(os.path.join(candidateRoot,relative),os.path.join(meldCandidate,relative))
    # reference is the golden tree on the left, candidate on the right
    subprocess.Popen([meld,meldReference,meldCandidate])
    return True


def _OpenDiffToolPreference():
    """The preference that gates auto-opening meld, defaulting to True."""
    try:
        import SignalIntegrity.App
        return bool(SignalIntegrity.App.Preferences['Regression.OpenDiffToolOnFailure'])
    except Exception:
        return True


def RunCheckByDiff(adapter,projectFile,regressionArchiveFile,archiveNonRelativeFiles=None,
                   args=None,artifacts=None,callback=None,openDiffTool=None,disableCaching=True):
    """Check a project by regenerating its artifacts and diffing the two trees.
    @param adapter RegressionAdapter supplying archiving and calculation.
    @param projectFile string project file to archive and calculate.
    @param regressionArchiveFile string explicit golden regression archive path.
    @param archiveNonRelativeFiles bool (optional) forwarded to project archiving.
    @param args dict (optional) project arguments.
    @param artifacts list (optional) enabled regression artifacts.
    @param callback callable (optional) progress callback.
    @param openDiffTool bool (optional) whether to open meld on failure; defaults to
    the Regression.OpenDiffToolOnFailure preference.
    @param disableCaching bool (optional, defaults True) disable result caching for the
    calc.  Leave True for authoritative checks (a stale cache could mask a code change);
    set False only for a fast measurements-only screen, where within-run cache reuse of a
    repeated sub-block (e.g. a crosstalk solve embedded in several channels) saves time
    without changing the values.
    @return list of RegressionResult objects, ordered upstream-before-downstream.
    """
    projectFile=os.path.abspath(projectFile)
    regressionArchiveFile=os.path.abspath(regressionArchiveFile)
    currentDirectory=os.getcwd()
    if openDiffTool is None:
        openDiffTool=_OpenDiffToolPreference()
    if callback is not None and callback(0,'+Checking '+os.path.basename(projectFile)) is False:
        return []
    try:
        projectArchive=adapter.Archive(projectFile,archiveNonRelativeFiles,args)
    finally:
        if callback is not None:
            callback(0,'-')
    archiveRoot=os.path.splitext(projectFile)[0]+'_Archive'
    candidateRoot=_RegressionRoot(projectFile)
    referenceRoot=_RegressionReferenceRoot(projectFile)
    extractedProject=os.path.join(archiveRoot,os.path.basename(projectFile))
    results=None
    meldOpened=False
    # every tree created below is torn down in the finally, so a crash cannot leave a
    # stale '_RegressionReference' that masquerades as a golden result
    try:
        # wipe any stale trees from a previous run, including meld trees left for inspection
        for root in (archiveRoot,candidateRoot,referenceRoot,
                     _MeldReferenceRoot(projectFile),_MeldCandidateRoot(projectFile)):
            if os.path.exists(root):
                _retryFileAction(lambda r=root: shutil.rmtree(r))
        Archive.ExtractArchive(projectArchive)
        # the golden archive extracts to '<proj>_RegressionCandidate'; move it aside as the reference
        _ExtractRegression(regressionArchiveFile,os.path.dirname(projectFile))
        _retryFileAction(lambda: os.rename(candidateRoot,referenceRoot))
        RegressionContext.Start(archiveRoot,candidateRoot,write=True,artifacts=artifacts)
        with (_CachingDisabled() if disableCaching else contextlib.nullcontext()):
            try:
                adapter.CalculateAndRecord(extractedProject,args,callback)
            finally:
                RegressionContext.Stop()
        results=RegressionFiles(artifacts=artifacts).DiffTrees(
            referenceRoot,candidateRoot,ignore={'manifest.json'},artifacts=artifacts)
        if openDiffTool and any(not result.ok for result in results):
            meldOpened=_OpenDiffTool(referenceRoot,candidateRoot,results,projectFile)
    finally:
        os.chdir(currentDirectory)
        # keep the comparison trees whenever anything differed (or a crash left results
        # undetermined), so a failure can always be inspected; a clean pass is tidied up
        keepTrees=meldOpened or results is None or any(not result.ok for result in results)
        if not keepTrees:
            for root in (archiveRoot,referenceRoot,candidateRoot):
                if os.path.exists(root):
                    Archive._RemoveTree(root)
            os.chdir(currentDirectory)
        _RemoveIfExists(projectArchive)
    if callback is not None:
        callback(0,'-')
        callback(100,'Regression check complete')
    return results


def CheckRegressionByDiff(projectFile,regressionArchiveFile,archiveNonRelativeFiles=None,
                          args=None,artifacts=None,callback=None,openDiffTool=None):
    """Check a SignalIntegrity project against a golden regression archive.
    @return list of RegressionResult objects, ordered upstream-before-downstream.
    """
    return RunCheckByDiff(SignalIntegrityRegressionAdapter(),projectFile,regressionArchiveFile,
                          archiveNonRelativeFiles=archiveNonRelativeFiles,args=args,
                          artifacts=artifacts,callback=callback,openDiffTool=openDiffTool)

