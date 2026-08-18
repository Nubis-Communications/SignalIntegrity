"""
RegressionFiles.py

The comparison primitives behind regression testing, in a form that is independent
of unittest.  Each artifact is written when a reference is absent (write mode) or
compared against the reference (check mode), and the outcome is returned rather
than asserted, so the same code serves both the unittest helpers and the headless
regression sprayer.
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

import ast
import json
import os
import re
import shutil
import tempfile

#: artifacts in the order a difference in one explains a difference in the next
ArtifactOrder=['netlist','project','sparameters','waveform','noise','measurements','eye','picture']

#: full artifact order used to sort tree differences; upstream inputs before outputs
DiffArtifactOrder=['arguments','netlist','project','sparameters','waveform','noise','measurements','eye','picture','file']

#: stands in for the reference file's own directory inside a stored netlist
PathPlaceholder='{DIR}'

class RegressionCallSite(object):
    """Tracks the active device reference during regression-aware parsing."""
    enabled=False
    stack=[]
    observer=None
    @classmethod
    def Push(cls,reference):
        if not cls.enabled:
            return
        cls.stack.append(str(reference))
        if cls.observer is not None:
            cls.observer(cls.Current())
    @classmethod
    def Pop(cls):
        if cls.enabled and cls.stack:
            cls.stack.pop()
    @classmethod
    def Current(cls):
        return '/'.join(cls.stack)
    @classmethod
    def Reset(cls):
        cls.stack=[]
        cls.observer=None

class RegressionContext(object):
    """Context shared by headless regression calculation hooks."""
    active=False
    write=False
    archiveRoot=None
    regressionRoot=None
    artifacts=list(ArtifactOrder)
    results=[]
    @classmethod
    def Start(cls,archiveRoot,regressionRoot,write=True,artifacts=None):
        """Starts a regression run.
        @param archiveRoot string root of the extracted project archive.
        @param regressionRoot string root of the sprayed regression tree.
        @param write bool (optional, defaults to True) whether artifacts are sprayed.
        @param artifacts list (optional) enabled artifact names.
        """
        cls.active=True
        cls.write=write
        cls.archiveRoot=os.path.abspath(archiveRoot)
        cls.regressionRoot=os.path.abspath(regressionRoot)
        cls.artifacts=list(ArtifactOrder) if artifacts is None else list(artifacts)
        cls.results=[]
        RegressionCallSite.enabled=True
    @classmethod
    def Stop(cls):
        """Stops the run and clears all shared state."""
        cls.active=False
        cls.write=False
        cls.archiveRoot=None
        cls.regressionRoot=None
        cls.results=[]
        cls.artifacts=list(ArtifactOrder)
        RegressionCallSite.enabled=False
        RegressionCallSite.Reset()
    @classmethod
    def CallSiteKey(cls,filename,args=None):
        """Returns the stable key for one sub-project invocation."""
        project=os.path.relpath(os.path.abspath(filename),cls.archiveRoot).replace('\\','/')
        callsite=RegressionCallSite.Current()
        return project+('|'+callsite if callsite else '')
    @classmethod
    def RecordCall(cls,filename,args=None):
        """Records one invocation, spraying its arguments, and returns its key."""
        if not cls.active:
            return None
        key=cls.CallSiteKey(filename,args)
        if cls.write:
            # spray the arguments so a tree diff can report argument changes
            arguments=RegressionFiles.CanonicalArguments(args)
            argumentsPath=cls.ReferencePath(filename,'arguments','')
            os.makedirs(os.path.dirname(argumentsPath),exist_ok=True)
            with open(argumentsPath,'w') as argumentsFile:
                json.dump(arguments,argumentsFile,indent=2,sort_keys=True)
        return key
    @classmethod
    def ReferencePath(cls,filename,artifact,extension,label=None):
        """Returns the mirrored regression path for the active call site.
        @param label object (optional) distinguishes multiple results of one artifact
        (e.g. a waveform or noise name) within the same call site.
        """
        project=os.path.relpath(os.path.abspath(filename),cls.archiveRoot)
        directory=os.path.join(cls.regressionRoot,os.path.dirname(project))
        stem=os.path.splitext(os.path.basename(project))[0]
        callsite=RegressionCallSite.Current()
        if callsite:
            stem=stem+'__'+callsite.replace('/','__')
        if label is not None:
            stem=stem+'__'+str(label)
        # suffixes are self-describing so a tree diff can dispatch by name alone
        suffix={'sparameters':'.s','waveform':'.wf','noise':'.noise.json',
            'picture':'.TpX','netlist':'.net','project':'.project.json',
            'measurements':'.measurements.json','eye':'.eye.png','arguments':'.args.json'}[artifact]
        if artifact=='sparameters':
            suffix=suffix+str(extension)+'p'
        return os.path.join(directory,stem+suffix)
    @classmethod
    def RecordSParameters(cls,filename,sp,args=None):
        """Writes or checks one s-parameter result when a run is active."""
        if not cls.active or 'sparameters' not in cls.artifacts:
            return None
        cls.RecordCall(filename,args)
        reference=cls.ReferencePath(filename,'sparameters',sp.m_P)
        result=RegressionFiles(write=cls.write).SParameters(sp,reference)
        cls.results.append(result)
        return result
    @classmethod
    def RecordProjectArtifacts(cls,filename,app,args=None):
        """Writes or checks the non-result artifacts of an opened project."""
        if not cls.active:
            return []
        cls.RecordCall(filename,args)
        results=[]
        if 'netlist' in cls.artifacts:
            reference=cls.ReferencePath(filename,'netlist','')
            result=RegressionFiles(write=cls.write).NetList(
                app.Drawing.schematic.NetList().Text(),reference)
            results.append(result)
        if 'project' in cls.artifacts:
            import SignalIntegrity.App.Project
            reference=cls.ReferencePath(filename,'project','')
            result=RegressionFiles(write=cls.write).Project(
                SignalIntegrity.App.Project.ToDictionary(),reference)
            results.append(result)
        if 'picture' in cls.artifacts:
            from SignalIntegrity.App.TikZ import TikZ
            from SignalIntegrity.App.TpX import TpX
            tpx=app.Drawing.DrawSchematic(TpX()).Finish()
            tikz=app.Drawing.DrawSchematic(TikZ()).Finish()
            lineList=tpx.lineList+tikz.lineList
            reference=cls.ReferencePath(filename,'picture','')
            result=RegressionFiles(write=cls.write).Picture(lineList,reference)
            results.append(result)
        cls.results.extend(results)
        return results
    @classmethod
    def RecordWaveform(cls,filename,waveform,wfname,args=None):
        """Writes or checks one waveform result when a run is active."""
        if not cls.active or 'waveform' not in cls.artifacts or waveform is None:
            return None
        cls.RecordCall(filename,args)
        reference=cls.ReferencePath(filename,'waveform','',label=wfname)
        result=RegressionFiles(write=cls.write).Native(waveform,reference)
        cls.results.append(result)
        return result
    @classmethod
    def RecordNoise(cls,filename,noise,noiseName,args=None):
        """Writes or checks one spectral-density result when a run is active."""
        if not cls.active or 'noise' not in cls.artifacts or noise is None:
            return None
        cls.RecordCall(filename,args)
        reference=cls.ReferencePath(filename,'noise','',label=noiseName)
        result=RegressionFiles(write=cls.write).Native(noise,reference)
        cls.results.append(result)
        return result
    @classmethod
    def RecordMeasurements(cls,filename,measurements,args=None):
        """Writes the scalar measurement results of a project when a run is active."""
        if not cls.active or 'measurements' not in cls.artifacts or not measurements:
            return None
        cls.RecordCall(filename,args)
        reference=cls.ReferencePath(filename,'measurements','')
        result=RegressionFiles(write=cls.write).Measurements(measurements,reference)
        cls.results.append(result)
        return result
    @classmethod
    def RecordProjectDictionary(cls,filename,projectDictionary,args=None):
        """Writes a project's serializable dictionary when a run is active.
        @remark For applications whose project is not the SignalIntegrity schematic
        (e.g. NubisSystemSim); RecordProjectArtifacts covers the schematic case.
        """
        if not cls.active or 'project' not in cls.artifacts:
            return None
        cls.RecordCall(filename,args)
        reference=cls.ReferencePath(filename,'project','')
        result=RegressionFiles(write=cls.write).Project(projectDictionary,reference)
        cls.results.append(result)
        return result
    @classmethod
    def RecordEyeDiagram(cls,filename,image,eyeName,args=None):
        """Writes one eye diagram bitmap when a run is active.
        @remark The bitmap is archived for reference but never compared, since eye
        rendering is not reproducible across environments; generating it exercises the
        eye/BER computation path so a failure there fails the run.
        """
        if not cls.active or 'eye' not in cls.artifacts or image is None:
            return None
        cls.RecordCall(filename,args)
        reference=cls.ReferencePath(filename,'eye','',label=eyeName)
        result=RegressionFiles(write=cls.write).EyeDiagram(image,reference)
        cls.results.append(result)
        return result

class RegressionResult(object):
    """The outcome of checking or writing one regression artifact."""
    def __init__(self,artifact,filename,ok=True,message=None,written=False):
        self.artifact=artifact
        self.filename=filename
        self.ok=ok
        self.message=message
        self.written=written
        #: set by the sprayer when a project this one depends on already differed
        self.secondary=False
    def __bool__(self):
        return self.ok
    __nonzero__=__bool__
    def __str__(self):
        if self.written:
            return self.filename+': written'
        if self.ok:
            return self.filename+': ok'
        return self.filename+': '+(self.message if self.message else 'incorrect')

class RegressionFiles(object):
    """Writes or checks the regression artifacts of one calculation.
    @remark In write mode a missing reference is created.  In check mode a missing
    reference is a failure, because a regression archive that was generated
    incompletely must not quietly pass.  The 'relearn' behaviour of the unittest
    helpers - write the reference when it is absent, even while checking - is kept
    as a separate flag so those helpers keep behaving as they always have.
    """
    def __init__(self,write=False,relearn=False,artifacts=None,
                 spCompareResolution=1e-3,allowReferenceImpedanceTranslation=True,
                 measurementRelativeTolerance=1e-6,measurementAbsoluteTolerance=1e-12,
                 waveformTolerance=1e-4,eyeMeasurementRelativeTolerance=1e-3):
        """Constructor
        @param write bool (optional, defaults to False) whether to write references
        rather than check them.
        @param relearn bool (optional, defaults to False) whether a missing reference
        is written and accepted while checking.
        @param artifacts list of strings (optional, defaults to all of them) the
        artifacts to process; see ArtifactOrder.
        @param spCompareResolution float (optional, defaults to 1e-3) s-parameter
        comparison epsilon.
        @param allowReferenceImpedanceTranslation bool (optional, defaults to True)
        whether s-parameters may be translated to the reference's impedance before
        being compared.
        """
        self.write=write
        self.relearn=relearn
        self.artifacts=list(ArtifactOrder) if artifacts is None else list(artifacts)
        self.spCompareResolution=spCompareResolution
        self.allowReferenceImpedanceTranslation=allowReferenceImpedanceTranslation
        self.measurementRelativeTolerance=measurementRelativeTolerance
        self.measurementAbsoluteTolerance=measurementAbsoluteTolerance
        self.eyeMeasurementRelativeTolerance=eyeMeasurementRelativeTolerance
        #: waveform samples must agree within this fraction of the waveform's peak
        self.waveformTolerance=waveformTolerance
    def Enabled(self,artifact):
        """Whether an artifact is processed.
        @param artifact string one of ArtifactOrder.
        @return bool True if the artifact is enabled.
        """
        return artifact in self.artifacts
    def _Missing(self,artifact,filename):
        """The result for a reference that does not exist.
        @return RegressionResult, or None if the caller should write the reference.
        """
        if self.write or self.relearn:
            return None
        return RegressionResult(artifact,filename,False,'reference file not found')
    @staticmethod
    def _WriteLines(filename,lines):
        directory=os.path.dirname(filename)
        if directory != '':
            os.makedirs(directory,exist_ok=True)
        with open(filename,'w') as f:
            f.writelines(lines)
    @staticmethod
    def CanonicalArguments(args):
        """The arguments of a calculation in a form that compares and stores stably.
        @param args dict the arguments.
        @return dict with sorted keys and string values.
        """
        if not args:
            return {}
        return {str(key):str(args[key]) for key in sorted(args.keys(),key=str)}
    @staticmethod
    def ArgumentDifferences(old,new):
        """The differences between two argument dictionaries.
        @param old dict the arguments recorded previously.
        @param new dict the arguments of this calculation.
        @return list of strings, one per difference, empty if they agree.
        """
        old=RegressionFiles.CanonicalArguments(old)
        new=RegressionFiles.CanonicalArguments(new)
        differences=[]
        for name in sorted(set(list(old.keys())+list(new.keys()))):
            if name not in old:
                differences.append(name+' added as '+new[name])
            elif name not in new:
                differences.append(name+' removed (was '+old[name]+')')
            elif old[name] != new[name]:
                differences.append(name+' was '+old[name]+', is now '+new[name])
        return differences

    def NetList(self,netlist,filename):
        """Writes or checks a netlist.
        @param netlist list of strings the netlist lines, without line endings.
        @param filename string the reference file.
        @return RegressionResult
        """
        directory=os.path.dirname(os.path.abspath(filename))
        lines=self.CanonicalizePaths([line+'\n' for line in netlist],directory)
        if not os.path.exists(filename):
            missing=self._Missing('netlist',filename)
            if missing is not None:
                return missing
            self._WriteLines(filename,lines)
            return RegressionResult('netlist',filename,written=True)
        if self.write:
            self._WriteLines(filename,lines)
            return RegressionResult('netlist',filename,written=True)
        with open(filename) as f:
            regression=self.CanonicalizePaths(f.readlines(),directory)
        if lines == regression:
            return RegressionResult('netlist',filename)
        if len(lines) != len(regression):
            return RegressionResult('netlist',filename,False,
                                    'netlist has '+str(len(lines))+' lines, reference has '+str(len(regression)))
        difference=self._NetListDifference(lines,regression)
        if difference is None:
            return RegressionResult('netlist',filename,True,'netlist in a different order')
        return RegressionResult('netlist',filename,False,difference)
    @staticmethod
    def CanonicalizePaths(lines,directory):
        """Replaces a directory appearing inside netlist lines with a placeholder.
        @param lines list of strings the netlist lines.
        @param directory string the directory to stand in for.
        @return list of strings the lines, with the directory replaced.
        @remark A file referenced by a variable is written into the netlist as an
        absolute path, so a stored netlist would otherwise record the machine it was
        generated on and could never match anywhere else.  Only the part of the path
        that varies is replaced, so a reference to a different file still differs.
        """
        if not directory:
            return lines
        directory=directory.replace('\\','/').rstrip('/')
        if directory=='':
            return lines
        alternatives=[re.escape(directory),re.escape(directory.replace('/','\\'))]
        # drive letters and file names do not distinguish case on Windows
        expression=re.compile('|'.join(alternatives),re.IGNORECASE if os.name=='nt' else 0)
        return [expression.sub(PathPlaceholder.replace('\\','\\\\'),line) for line in lines]
    @staticmethod
    def _ConnectionPairs(line):
        """The device/pin pairs of a connect line, or None if it is not one.
        @param line string a netlist line.
        @return list of (device,pin) tuples, or None.
        @remark A connection joins a set of device pins, so the order the pins are
        listed in carries no meaning and two orderings describe the same circuit.
        """
        tokens=line.split()
        if len(tokens)<2 or tokens[0]!='connect':
            return None
        tokens=tokens[1:]
        if len(tokens)%2 != 0:
            return None
        return [(tokens[i],tokens[i+1]) for i in range(0,len(tokens),2)]
    @staticmethod
    def _CanonicalNetListLine(line):
        """A netlist line in a form independent of connection pin order.
        @remark Non-connect lines are returned stripped of their line ending; a
        connect line has its device/pin pairs sorted so any pin order matches.
        """
        stripped=line.rstrip('\n')
        pairs=RegressionFiles._ConnectionPairs(stripped)
        if pairs is None:
            return stripped
        return 'connect '+' '.join(device+' '+pin for device,pin in sorted(pairs))
    @staticmethod
    def _NetListDifference(lines,regression):
        """Describes a difference between two netlists, ignoring line order.
        @return string the difference, or None if the netlists hold the same lines
        (a netlist is an unordered set of device, port and connection statements, and
        the pin order within a connection carries no meaning).
        """
        candidate=sorted(RegressionFiles._CanonicalNetListLine(line) for line in lines)
        reference=sorted(RegressionFiles._CanonicalNetListLine(line) for line in regression)
        if candidate == reference:
            return None
        remaining=list(reference)
        for line in candidate:
            if line in remaining:
                remaining.remove(line)
            else:
                return 'line '+repr(line)+' is not in the reference'
        if remaining:
            return 'reference line '+repr(remaining[0])+' is missing'
        return 'netlists differ'

    def Project(self,projectDictionary,filename):
        """Writes or checks a project, as a diffable dictionary dump.
        @param projectDictionary dict the project.
        @param filename string the reference file.
        @return RegressionResult
        """
        if not os.path.exists(filename):
            missing=self._Missing('project',filename)
            if missing is not None:
                return missing
            self._WriteProject(projectDictionary,filename)
            return RegressionResult('project',filename,written=True)
        if self.write:
            self._WriteProject(projectDictionary,filename)
            return RegressionResult('project',filename,written=True)
        with open(filename) as f:
            regression=json.load(f)
        lines=self.DiffableDictionary(projectDictionary)
        regressionLines=self.DiffableDictionary(regression)
        if lines == regressionLines:
            return RegressionResult('project',filename)
        import difflib
        diff=list(difflib.unified_diff(regressionLines,lines,
                                       fromfile='regression',tofile='current',lineterm='',n=5))
        return RegressionResult('project',filename,False,'project changed\n'+'\n'.join(diff))
    def Native(self,value,filename):
        """Writes or compares an object through its native WriteToFile method."""
        if not os.path.exists(filename):
            missing=self._Missing('native',filename)
            if missing is not None:
                return missing
            value.WriteToFile(filename)
            return RegressionResult('native',filename,written=True)
        if self.write:
            value.WriteToFile(filename)
            return RegressionResult('native',filename,written=True)
        temporary=None
        try:
            descriptor,temporary=tempfile.mkstemp(suffix=os.path.splitext(filename)[1])
            os.close(descriptor)
            value.WriteToFile(temporary)
            with open(temporary,'rb') as currentFile:
                current=currentFile.read()
            with open(filename,'rb') as referenceFile:
                reference=referenceFile.read()
        finally:
            if temporary is not None and os.path.exists(temporary):
                os.remove(temporary)
        if current == reference:
            return RegressionResult('native',filename)
        return RegressionResult('native',filename,False,'native result differs')
    @staticmethod
    def _WriteProject(projectDictionary,filename):
        directory=os.path.dirname(filename)
        if directory != '':
            os.makedirs(directory,exist_ok=True)
        with open(filename,'w') as f:
            json.dump(projectDictionary,f)

    def Picture(self,lineList,filename):
        """Writes or checks a schematic picture, as TpX/TikZ lines.
        @param lineList list of strings the picture lines.
        @param filename string the reference file.
        @return RegressionResult
        """
        if not os.path.exists(filename):
            missing=self._Missing('picture',filename)
            if missing is not None:
                return missing
            self._WriteLines(filename,lineList)
            return RegressionResult('picture',filename,written=True)
        if self.write:
            self._WriteLines(filename,lineList)
            return RegressionResult('picture',filename,written=True)
        with open(filename) as f:
            regression=f.readlines()
        if lineList == regression:
            return RegressionResult('picture',filename)
        if len(lineList) != len(regression):
            return RegressionResult('picture',filename,False,
                                    'picture has '+str(len(lineList))+' lines, reference has '+str(len(regression)))
        # the drawing emits the same geometry in a varying order
        if self._SameIgnoringOrder(lineList,regression):
            return RegressionResult('picture',filename,True,'picture in a different order')
        return RegressionResult('picture',filename,False,self._FirstLineDifference(lineList,regression))

    def SParameters(self,sp,filename):
        """Writes or checks s-parameters.
        @param sp instance of class SParameters.
        @param filename string the reference file.
        @return RegressionResult
        """
        from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile
        if not os.path.exists(filename):
            missing=self._Missing('sparameters',filename)
            if missing is not None:
                return missing
            self._WriteSParameters(sp,filename)
            return RegressionResult('sparameters',filename,written=True)
        if self.write:
            self._WriteSParameters(sp,filename)
            return RegressionResult('sparameters',filename,written=True)
        regression=SParameterFile(filename)
        if (sp.m_Z0 != regression.m_Z0) and self.allowReferenceImpedanceTranslation:
            sp.SetReferenceImpedance(regression.m_Z0)
        if self.SParametersAreEqual(sp,regression,self.spCompareResolution):
            return RegressionResult('sparameters',filename)
        return RegressionResult('sparameters',filename,False,
                                self._SParameterDifference(sp,regression))
    @staticmethod
    def _WriteSParameters(sp,filename):
        directory=os.path.dirname(filename)
        if directory != '':
            os.makedirs(directory,exist_ok=True)
        sp.WriteToFile(filename,'R '+str(sp.m_Z0))

    @staticmethod
    def SParametersAreEqual(lhs,rhs,epsilon=0.00001):
        """Whether two sets of s-parameters agree to within epsilon.
        @return bool True if they agree.
        """
        if lhs.m_P != rhs.m_P: return False
        if lhs.m_Z0 != rhs.m_Z0: return False
        if len(lhs) != len(rhs): return False
        for n in range(len(lhs)):
            if abs(lhs.m_f[n] - rhs.m_f[n]) > .1:
                return False
            lhsn=lhs[n]
            rhsn=rhs[n]
            for r in range(lhs.m_P):
                for c in range(lhs.m_P):
                    if abs(lhsn[r][c] - rhsn[r][c]) > epsilon:
                        return False
        return True
    @staticmethod
    def _SParameterDifference(sp,regression):
        """Describes how far apart two sets of s-parameters are."""
        if sp.m_P != regression.m_P:
            return 'has '+str(sp.m_P)+' ports, reference has '+str(regression.m_P)
        if sp.m_Z0 != regression.m_Z0:
            return 'reference impedance is '+str(sp.m_Z0)+', reference has '+str(regression.m_Z0)
        if len(sp) != len(regression):
            return 'has '+str(len(sp))+' frequencies, reference has '+str(len(regression))
        worst=0.; where=None
        for n in range(len(sp)):
            if abs(sp.m_f[n]-regression.m_f[n]) > .1:
                return 'frequency '+str(n)+' is '+str(sp.m_f[n])+', reference has '+str(regression.m_f[n])
            for r in range(sp.m_P):
                for c in range(sp.m_P):
                    error=abs(sp[n][r][c]-regression[n][r][c])
                    if error > worst:
                        worst=error; where=(n,r,c)
        if where is None:
            return 'incorrect'
        n,r,c=where
        return ('worst difference '+str(worst)+' in S'+str(r+1)+str(c+1)+
                ' at '+str(sp.m_f[n])+' Hz')

    @staticmethod
    def DiffableDictionary(value,indent=0):
        """Renders a dictionary as indented lines that diff readably.
        @return list of strings.
        """
        lines=[]
        indentString=' '*indent
        if isinstance(value,dict):
            for key in value.keys():
                lines.append(indentString+str(key))
                lines=lines+RegressionFiles.DiffableDictionary(value[key],indent+4)
        else:
            lines.append(indentString+str(value))
        return lines
    @staticmethod
    def _SameIgnoringOrder(lines,regression,prefix=None):
        """Whether two equal-length line lists hold the same lines in any order.
        @param prefix string (optional) when given, only lines starting with it may
        be reordered; every other line must match in place.
        """
        if prefix is not None:
            fixed=[(a,b) for a,b in zip(lines,regression)
                   if not (a.startswith(prefix) and b.startswith(prefix))]
            if any(a != b for a,b in fixed):
                return False
            lines=[line for line in lines if line.startswith(prefix)]
            regression=[line for line in regression if line.startswith(prefix)]
            if len(lines) != len(regression):
                return False
        remaining=list(regression)
        for line in lines:
            if line not in remaining:
                return False
            remaining.remove(line)
        return True
    @staticmethod
    def _FirstLineDifference(lines,regression):
        for index,(line,regressionLine) in enumerate(zip(lines,regression)):
            if line != regressionLine:
                return ('line '+str(index+1)+' is '+repr(line)+
                        ', reference has '+repr(regressionLine))
        return 'incorrect'

    # -- file-vs-file comparators, for diffing two sprayed trees ------------------
    def CompareNetListFiles(self,referenceFile,candidateFile):
        """Compares two stored netlists, tolerant of connection ordering."""
        with open(referenceFile) as f:
            reference=self.CanonicalizePaths(f.readlines(),os.path.dirname(os.path.abspath(referenceFile)))
        with open(candidateFile) as f:
            candidate=self.CanonicalizePaths(f.readlines(),os.path.dirname(os.path.abspath(candidateFile)))
        if candidate == reference:
            return RegressionResult('netlist',candidateFile)
        if len(candidate) != len(reference):
            return RegressionResult('netlist',candidateFile,False,
                'netlist has '+str(len(candidate))+' lines, reference has '+str(len(reference)))
        difference=self._NetListDifference(candidate,reference)
        if difference is None:
            return RegressionResult('netlist',candidateFile,True,'netlist in a different order')
        return RegressionResult('netlist',candidateFile,False,difference)
    def CompareProjectFiles(self,referenceFile,candidateFile):
        """Compares two stored project dumps, insensitive to key order."""
        with open(referenceFile) as f:
            reference=json.load(f)
        with open(candidateFile) as f:
            candidate=json.load(f)
        referenceLines=self.DiffableDictionary(reference)
        candidateLines=self.DiffableDictionary(candidate)
        if candidateLines == referenceLines:
            return RegressionResult('project',candidateFile)
        import difflib
        diff=list(difflib.unified_diff(referenceLines,candidateLines,
                                       fromfile='reference',tofile='candidate',lineterm='',n=5))
        return RegressionResult('project',candidateFile,False,'project changed\n'+'\n'.join(diff))
    def CompareNativeFiles(self,referenceFile,candidateFile):
        """Compares two natively serialized results byte-for-byte."""
        with open(referenceFile,'rb') as f:
            reference=f.read()
        with open(candidateFile,'rb') as f:
            candidate=f.read()
        artifact='noise' if referenceFile.endswith('.noise.json') else 'waveform'
        if candidate == reference:
            return RegressionResult(artifact,candidateFile)
        return RegressionResult(artifact,candidateFile,False,artifact+' result differs')
    @staticmethod
    def _ReadWaveform(filename):
        """The (H,K,Fs) timebase and sample values of a stored waveform."""
        with open(filename) as f:
            lines=f.read().split('\n')
        points=int(lines[1])
        header=(float(lines[0]),points,float(lines[2]))
        dataLines=[line.strip() for line in lines[3:] if line.strip()]
        if len(dataLines) < points:
            raise ValueError('waveform has '+str(len(dataLines))+
                             ' samples, header specifies '+str(points))
        values=[]
        for line in dataLines[:points]:
            try:
                values.append(float(line))
            except ValueError:
                value=ast.literal_eval(line)
                if not isinstance(value,(int,float,complex)):
                    raise ValueError('waveform sample is not numeric: '+line)
                values.append(value)
        return header,values
    def CompareWaveformFiles(self,referenceFile,candidateFile):
        """Compares two stored waveforms to within a fraction of their peak amplitude."""
        referenceHeader,reference=self._ReadWaveform(referenceFile)
        candidateHeader,candidate=self._ReadWaveform(candidateFile)
        referenceStart,referencePoints,referenceSampleRate=referenceHeader
        candidateStart,candidatePoints,candidateSampleRate=candidateHeader
        startTimeTolerance=0.001/referenceSampleRate
        if (candidatePoints != referencePoints or candidateSampleRate != referenceSampleRate or
                abs(candidateStart-referenceStart) > startTimeTolerance):
            return RegressionResult('waveform',candidateFile,False,
                'timebase is '+str(candidateHeader)+', reference has '+str(referenceHeader))
        if len(candidate) != len(reference):
            return RegressionResult('waveform',candidateFile,False,
                'has '+str(len(candidate))+' points, reference has '+str(len(reference)))
        peak=max([abs(value) for value in reference],default=0.)
        tolerance=self.waveformTolerance*peak if peak != 0. else self.waveformTolerance
        worst=0.; where=None
        for n in range(len(reference)):
            error=abs(candidate[n]-reference[n])
            if error>worst:
                worst=error; where=n
        if where is None or worst<=tolerance:
            return RegressionResult('waveform',candidateFile)
        return RegressionResult('waveform',candidateFile,False,
            'worst difference '+str(worst)+' at point '+str(where)+
            ' exceeds tolerance '+str(tolerance))
    def ComparePictureFiles(self,referenceFile,candidateFile):
        """Compares two stored pictures, tolerant of geometry ordering."""
        with open(referenceFile) as f:
            reference=f.readlines()
        with open(candidateFile) as f:
            candidate=f.readlines()
        if candidate == reference:
            return RegressionResult('picture',candidateFile)
        if len(candidate) != len(reference):
            return RegressionResult('picture',candidateFile,False,
                'picture has '+str(len(candidate))+' lines, reference has '+str(len(reference)))
        if self._SameIgnoringOrder(candidate,reference):
            return RegressionResult('picture',candidateFile,True,'picture in a different order')
        return RegressionResult('picture',candidateFile,False,self._FirstLineDifference(candidate,reference))
    def CompareSParameterFiles(self,referenceFile,candidateFile):
        """Compares two stored s-parameter files to within tolerance."""
        from SignalIntegrity.Lib.SParameters.SParameterFile import SParameterFile
        reference=SParameterFile(referenceFile)
        candidate=SParameterFile(candidateFile)
        if (candidate.m_Z0 != reference.m_Z0) and self.allowReferenceImpedanceTranslation:
            candidate.SetReferenceImpedance(reference.m_Z0)
        if self.SParametersAreEqual(candidate,reference,self.spCompareResolution):
            return RegressionResult('sparameters',candidateFile)
        return RegressionResult('sparameters',candidateFile,False,
                                self._SParameterDifference(candidate,reference))
    def CompareArgumentFiles(self,referenceFile,candidateFile):
        """Compares two stored argument dumps."""
        with open(referenceFile) as f:
            reference=json.load(f)
        with open(candidateFile) as f:
            candidate=json.load(f)
        differences=self.ArgumentDifferences(reference,candidate)
        if not differences:
            return RegressionResult('arguments',candidateFile)
        return RegressionResult('arguments',candidateFile,False,'; '.join(differences))
    @staticmethod
    def CanonicalMeasurements(measurements):
        """Measurement results as a plain dict with string keys, stored stably."""
        return {str(key):measurements[key] for key in measurements}
    def Measurements(self,measurements,filename):
        """Writes the scalar measurement results as a canonical JSON dump.
        @param measurements dict the measurement results.
        @param filename string the reference file.
        @return RegressionResult
        """
        directory=os.path.dirname(filename)
        if directory != '':
            os.makedirs(directory,exist_ok=True)
        with open(filename,'w') as f:
            json.dump(self.CanonicalMeasurements(measurements),f,indent=2,sort_keys=True)
        return RegressionResult('measurements',filename,written=True)
    def EyeDiagram(self,image,filename):
        """Writes an eye diagram bitmap; archived for reference but never compared."""
        directory=os.path.dirname(filename)
        if directory != '':
            os.makedirs(directory,exist_ok=True)
        image.save(filename)
        return RegressionResult('eye',filename,written=True)
    def CompareMeasurementsFiles(self,referenceFile,candidateFile):
        """Compares two stored measurement dumps, tolerant of tiny numeric drift."""
        with open(referenceFile) as f:
            reference=json.load(f)
        with open(candidateFile) as f:
            candidate=json.load(f)
        differences=self.MeasurementDifferences(reference,candidate)
        if not differences:
            return RegressionResult('measurements',candidateFile)
        return RegressionResult('measurements',candidateFile,False,'; '.join(differences))
    def MeasurementDifferences(self,old,new):
        """The differences between two measurement dictionaries.
        @return list of strings, one per difference, empty if they agree.
        """
        differences=[]
        for name in sorted(set(list(old.keys())+list(new.keys())),key=str):
            if name not in old:
                differences.append(str(name)+' added as '+str(new[name]))
            elif name not in new:
                differences.append(str(name)+' removed (was '+str(old[name])+')')
            elif not self._MeasurementsClose(old[name],new[name],
                                              self.eyeMeasurementRelativeTolerance
                                              if self._IsEyeMeasurement(name) else None):
                differences.append(str(name)+' was '+str(old[name])+', is now '+str(new[name]))
        return differences
    @staticmethod
    def _IsEyeMeasurement(name):
        """Whether a measurement name describes a PAM eye level or opening."""
        return any(str(name).endswith(suffix) for suffix in
                   ['.AverageLowerLevel','.AverageUpperLevel','.DecisionLevel',
                    '.Height','.Max','.Min','.MinEyeHeight','.PAM4Height'])
    def _MeasurementsClose(self,old,new,relativeTolerance=None):
        """Whether two measurement values agree within the numeric tolerance."""
        oldNumber=self._AsFloat(old); newNumber=self._AsFloat(new)
        if oldNumber is None or newNumber is None:
            return str(old)==str(new)
        if relativeTolerance is None:
            relativeTolerance=self.measurementRelativeTolerance
        return abs(oldNumber-newNumber) <= (self.measurementAbsoluteTolerance+
                                            relativeTolerance*abs(oldNumber))
    @staticmethod
    def _AsFloat(value):
        """The value as a float, or None if it is not numeric."""
        try:
            return float(value)
        except (TypeError,ValueError):
            return None

    # -- tree-vs-tree diff --------------------------------------------------------
    @staticmethod
    def _RelativeFiles(root):
        """The set of files under a root, as forward-slashed relative paths."""
        found=set()
        for directory,_,files in os.walk(root):
            for filename in files:
                found.add(os.path.relpath(os.path.join(directory,filename),root).replace('\\','/'))
        return found
    @staticmethod
    def _ArtifactOf(relative):
        """The artifact kind implied by a stored file's name."""
        lower=relative.lower()
        if re.search(r'\.s\d+p$',lower): return 'sparameters'
        if lower.endswith('.net'): return 'netlist'
        if lower.endswith('.project.json'): return 'project'
        if lower.endswith('.args.json'): return 'arguments'
        if lower.endswith('.measurements.json'): return 'measurements'
        if lower.endswith('.noise.json'): return 'noise'
        if lower.endswith('.wf'): return 'waveform'
        if lower.endswith('.eye.png'): return 'eye'
        if relative.endswith('.TpX'): return 'picture'
        return 'file'
    def _CompareFiles(self,relative,referenceFile,candidateFile):
        """Dispatches one file pair to the comparator its name implies."""
        artifact=self._ArtifactOf(relative)
        if artifact=='sparameters': return self.CompareSParameterFiles(referenceFile,candidateFile)
        if artifact=='netlist': return self.CompareNetListFiles(referenceFile,candidateFile)
        if artifact=='project': return self.CompareProjectFiles(referenceFile,candidateFile)
        if artifact=='arguments': return self.CompareArgumentFiles(referenceFile,candidateFile)
        if artifact=='measurements': return self.CompareMeasurementsFiles(referenceFile,candidateFile)
        if artifact=='waveform': return self.CompareWaveformFiles(referenceFile,candidateFile)
        if artifact=='noise': return self.CompareNativeFiles(referenceFile,candidateFile)
        if artifact=='picture': return self.ComparePictureFiles(referenceFile,candidateFile)
        return self._CompareByteFiles(referenceFile,candidateFile)
    @staticmethod
    def _CompareByteFiles(referenceFile,candidateFile):
        """The fallback comparator: any unknown file must match byte-for-byte."""
        with open(referenceFile,'rb') as f:
            reference=f.read()
        with open(candidateFile,'rb') as f:
            candidate=f.read()
        if candidate == reference:
            return RegressionResult('file',candidateFile)
        return RegressionResult('file',candidateFile,False,'file differs')
    @staticmethod
    def _DiffSortKey(result):
        """Orders differences so upstream sub-blocks precede downstream results.
        @remark Deeper files are sub-projects that feed shallower results, so a
        deeper difference is the likely cause and is shown first.
        """
        relative=str(result.filename).replace('\\','/')
        depth=relative.count('/')
        try:
            artifactIndex=DiffArtifactOrder.index(result.artifact)
        except ValueError:
            artifactIndex=len(DiffArtifactOrder)
        return (-depth,artifactIndex,relative)
    def DiffTrees(self,referenceRoot,candidateRoot,ignore=None,artifacts=None):
        """Compares two sprayed regression trees file by file.
        @param referenceRoot string the golden tree.
        @param candidateRoot string the freshly generated tree.
        @param ignore set of strings (optional) base names to skip (e.g. manifest.json).
        @param artifacts collection of strings (optional) when given, only files of these
        artifact types are compared; the reference's other artifacts are ignored (used by
        the quick, measurements-only screen against a full golden archive).
        @return list of RegressionResult, one per differing or missing file, ordered
        so an upstream cause precedes its downstream effects.
        """
        ignore=set() if ignore is None else set(ignore)
        artifacts=None if artifacts is None else set(artifacts)
        referenceFiles=self._RelativeFiles(referenceRoot)
        candidateFiles=self._RelativeFiles(candidateRoot)
        results=[]
        for relative in sorted(referenceFiles | candidateFiles):
            if os.path.basename(relative) in ignore:
                continue
            if self._ArtifactOf(relative) == 'eye':
                # eye bitmaps are archived for reference only, never compared
                continue
            if artifacts is not None and self._ArtifactOf(relative) not in artifacts:
                # quick screen: only the requested artifact types participate
                continue
            if relative not in candidateFiles:
                results.append(RegressionResult(self._ArtifactOf(relative),relative,False,
                                                'missing from candidate'))
                continue
            if relative not in referenceFiles:
                results.append(RegressionResult(self._ArtifactOf(relative),relative,False,
                                                'unexpected in candidate'))
                continue
            result=self._CompareFiles(relative,
                                      os.path.join(referenceRoot,relative),
                                      os.path.join(candidateRoot,relative))
            result.filename=relative
            results.append(result)
        results.sort(key=self._DiffSortKey)
        return results
