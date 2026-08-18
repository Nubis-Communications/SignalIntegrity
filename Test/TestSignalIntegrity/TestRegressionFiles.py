"""
TestRegressionFiles.py
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
import os
import shutil
import tempfile

import SignalIntegrity.Lib as si
from SignalIntegrity.Lib.Test.RegressionFiles import RegressionFiles,RegressionCallSite,RegressionContext

class TestRegressionFiles(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        self.path=os.path.dirname(os.path.realpath(__file__))
        unittest.TestCase.__init__(self,methodName)
    def setUp(self):
        os.chdir(self.path)
        self.tempDir=tempfile.mkdtemp()
    def tearDown(self):
        shutil.rmtree(self.tempDir,ignore_errors=True)
        os.chdir(self.path)
    def File(self,name):
        return os.path.join(self.tempDir,name)
    def Write(self,root,relative,content):
        path=os.path.join(root,relative)
        directory=os.path.dirname(path)
        if directory != '':
            os.makedirs(directory,exist_ok=True)
        with open(path,'w') as f:
            f.write(content)
        return path
    def SParameters(self,value=0.5,ports=2,points=4):
        f=si.fd.EvenlySpacedFrequencyList(1e9,points)
        data=[[[value for _ in range(ports)] for _ in range(ports)] for _ in range(len(f))]
        return si.sp.SParameters(f,data)

    def testNetListWritesWhenAbsent(self):
        filename=self.File('a.net')
        r=RegressionFiles(write=True).NetList(['device D1 2','port 1 D1 1'],filename)
        self.assertTrue(r.ok,self.id()+' write failed')
        self.assertTrue(r.written,self.id()+' not reported as written')
        with open(filename) as f:
            self.assertEqual(f.readlines(),['device D1 2\n','port 1 D1 1\n'],self.id()+' wrong content')
    def testNetListMissingReferenceFails(self):
        r=RegressionFiles().NetList(['device D1 2'],self.File('missing.net'))
        self.assertFalse(r.ok,self.id()+' a missing reference passed')
        self.assertIn('not found',r.message,self.id()+' unexpected message')
    def testNetListMissingReferenceRelearns(self):
        filename=self.File('relearn.net')
        r=RegressionFiles(relearn=True).NetList(['device D1 2'],filename)
        self.assertTrue(r.written,self.id()+' relearn did not write')
        self.assertTrue(os.path.exists(filename),self.id()+' reference not created')
    def testNetListSame(self):
        filename=self.File('same.net')
        netlist=['device D1 2','device D2 2','connect D1 2 D2 1']
        RegressionFiles(write=True).NetList(netlist,filename)
        self.assertTrue(RegressionFiles().NetList(netlist,filename).ok,self.id()+' identical netlist failed')
    def testNetListDifferentLineFails(self):
        # this is the case the old checker silently passed
        filename=self.File('diff.net')
        RegressionFiles(write=True).NetList(['device D1 2','device D2 2'],filename)
        r=RegressionFiles().NetList(['device D1 2','device D2 4'],filename)
        self.assertFalse(r.ok,self.id()+' a changed device line passed')
        self.assertIn('device D2 4',r.message,self.id()+' did not identify the line')
    def testNetListLengthDifferenceFails(self):
        filename=self.File('len.net')
        RegressionFiles(write=True).NetList(['device D1 2'],filename)
        r=RegressionFiles().NetList(['device D1 2','device D2 2'],filename)
        self.assertFalse(r.ok,self.id()+' a length difference passed')
    def testNetListConnectionsInDifferentOrder(self):
        filename=self.File('order.net')
        RegressionFiles(write=True).NetList(
            ['device D1 2','connect D1 1 D2 1','connect D1 2 D2 2'],filename)
        r=RegressionFiles().NetList(
            ['device D1 2','connect D1 2 D2 2','connect D1 1 D2 1'],filename)
        self.assertTrue(r.ok,self.id()+' reordered connections failed')
        self.assertIn('different order',r.message,self.id()+' reordering not reported')
    def testNetListConnectionPinsInDifferentOrder(self):
        # a connection joins a set of pins, so the order they are listed in is meaningless
        filename=self.File('pinorder.net')
        RegressionFiles(write=True).NetList(['connect VG1 1 VG4 1'],filename)
        r=RegressionFiles().NetList(['connect VG4 1 VG1 1'],filename)
        self.assertTrue(r.ok,self.id()+' reordered connection pins failed')
    def testNetListDifferentConnectionFails(self):
        filename=self.File('diffconn.net')
        RegressionFiles(write=True).NetList(['connect VG1 1 VG4 1'],filename)
        r=RegressionFiles().NetList(['connect VG1 1 VG4 2'],filename)
        self.assertFalse(r.ok,self.id()+' a changed connection passed')
    def testNetListNonConnectReorderingPasses(self):
        # a netlist is an unordered set of statements, so device order is meaningless
        filename=self.File('devorder.net')
        RegressionFiles(write=True).NetList(['device D1 2','device D2 4'],filename)
        r=RegressionFiles().NetList(['device D2 4','device D1 2'],filename)
        self.assertTrue(r.ok,self.id()+' reordered devices failed')
    def testNetListPathIsCanonicalized(self):
        # a file variable is written into the netlist as an absolute path, which
        # would otherwise record the machine the reference was generated on
        filename=self.File('paths.net')
        netlist=['var $file_name$ '+self.tempDir.replace('\\','/')+'/sparam_res.s4p']
        RegressionFiles(write=True).NetList(netlist,filename)
        with open(filename) as f:
            stored=f.read()
        self.assertNotIn(self.tempDir.replace('\\','/'),stored,self.id()+' directory stored')
        self.assertIn('{DIR}/sparam_res.s4p',stored,self.id()+' placeholder not stored')
        self.assertTrue(RegressionFiles().NetList(netlist,filename).ok,
                        self.id()+' canonicalized netlist did not match')
    def testNetListPathFromAnotherMachineMatches(self):
        # the same reference, written on another machine, must still match here
        filename=self.File('othermachine.net')
        with open(filename,'w') as f:
            f.write('var $file_name$ C:/Users/someone/elsewhere/sparam_res.s4p\n')
        netlist=['var $file_name$ C:/Users/someone/elsewhere/sparam_res.s4p']
        self.assertTrue(RegressionFiles().NetList(netlist,filename).ok,
                        self.id()+' identical stored path did not match')
    def testNetListDifferentFileNameStillFails(self):
        # only the directory is neutralized, so a different file is still a difference
        filename=self.File('otherfile.net')
        directory=self.tempDir.replace('\\','/')
        RegressionFiles(write=True).NetList(['var $f$ '+directory+'/a.s4p'],filename)
        r=RegressionFiles().NetList(['var $f$ '+directory+'/b.s4p'],filename)
        self.assertFalse(r.ok,self.id()+' a different file name passed')

    def testProjectSameAndDifferent(self):
        filename=self.File('p.json')
        project={'a':1,'b':{'c':2}}
        RegressionFiles(write=True).Project(project,filename)
        self.assertTrue(RegressionFiles().Project(project,filename).ok,self.id()+' identical project failed')
        r=RegressionFiles().Project({'a':1,'b':{'c':3}},filename)
        self.assertFalse(r.ok,self.id()+' changed project passed')
        self.assertIn('project changed',r.message,self.id()+' no diff reported')

    def testPictureSameReorderedAndDifferent(self):
        filename=self.File('pic.TpX')
        picture=['\\line(1,0)\n','\\line(0,1)\n']
        RegressionFiles(write=True).Picture(picture,filename)
        self.assertTrue(RegressionFiles().Picture(picture,filename).ok,self.id()+' identical picture failed')
        r=RegressionFiles().Picture(list(reversed(picture)),filename)
        self.assertTrue(r.ok,self.id()+' reordered picture failed')
        self.assertIn('different order',r.message,self.id()+' reordering not reported')
        self.assertFalse(RegressionFiles().Picture(['\\line(1,1)\n','\\line(0,1)\n'],filename).ok,
                         self.id()+' changed picture passed')

    def testSParametersSame(self):
        filename=self.File('sp.s2p')
        sp=self.SParameters()
        RegressionFiles(write=True).SParameters(sp,filename)
        self.assertTrue(RegressionFiles().SParameters(self.SParameters(),filename).ok,
                        self.id()+' identical s-parameters failed')
    def testSParametersDifferentReportsWorstDifference(self):
        filename=self.File('spdiff.s2p')
        RegressionFiles(write=True).SParameters(self.SParameters(0.5),filename)
        r=RegressionFiles().SParameters(self.SParameters(0.6),filename)
        self.assertFalse(r.ok,self.id()+' differing s-parameters passed')
        self.assertIn('worst difference',r.message,self.id()+' worst difference not reported')
    def testSParametersWithinResolution(self):
        filename=self.File('spres.s2p')
        RegressionFiles(write=True).SParameters(self.SParameters(0.5),filename)
        self.assertTrue(RegressionFiles(spCompareResolution=1e-2).SParameters(
            self.SParameters(0.5001),filename).ok,self.id()+' a difference within resolution failed')
    def testSParametersMissingReferenceFails(self):
        r=RegressionFiles().SParameters(self.SParameters(),self.File('nosuch.s2p'))
        self.assertFalse(r.ok,self.id()+' a missing reference passed')

    def testArtifactsAreSwitchable(self):
        rf=RegressionFiles(artifacts=['netlist','sparameters'])
        self.assertTrue(rf.Enabled('netlist'),self.id()+' netlist not enabled')
        self.assertFalse(rf.Enabled('picture'),self.id()+' picture not disabled')
        self.assertTrue(RegressionFiles().Enabled('picture'),self.id()+' picture off by default')
    def testCanonicalArguments(self):
        self.assertEqual(RegressionFiles.CanonicalArguments({'b':2,'a':1}),{'a':'1','b':'2'},
                         self.id()+' arguments not canonical')
        self.assertEqual(RegressionFiles.CanonicalArguments(None),{},self.id()+' None not handled')
    def testArgumentDifferences(self):
        differences=RegressionFiles.ArgumentDifferences(
            {'risetime':'20e-12','trim':'1'},{'risetime':'25e-12','mode':'a'})
        self.assertEqual(differences,
                         ['mode added as a',
                          'risetime was 20e-12, is now 25e-12',
                          'trim removed (was 1)'],
                         self.id()+' wrong differences: '+str(differences))
        self.assertEqual(RegressionFiles.ArgumentDifferences({'a':1},{'a':1}),[],
                         self.id()+' identical arguments differed')
    def testCallSiteStackTracksDeviceConstruction(self):
        observed=[]
        RegressionCallSite.enabled=True
        RegressionCallSite.observer=observed.append
        try:
            parser=si.p.SystemDescriptionParser()
            parser.AddLines(['device D1 1 open','device D2 1 open'])
            parser.SystemDescription()
        finally:
            RegressionCallSite.Reset()
            RegressionCallSite.enabled=False
        self.assertEqual(observed,['D1','D2'],self.id()+' wrong call sites')
        self.assertEqual(RegressionCallSite.Current(),'',self.id()+' stack not reset')
    def testRegressionContextRecordsStableCallSiteAndSpraysArguments(self):
        import json
        archiveRoot=self.tempDir
        regressionRoot=self.File('Regression')
        project=os.path.join(archiveRoot,'Top.si')
        RegressionContext.Start(archiveRoot,regressionRoot)
        try:
            RegressionCallSite.Push('D1')
            key=RegressionContext.RecordCall(project,{'risetime':'20e-12'})
            RegressionCallSite.Pop()
            self.assertEqual(key,'Top.si|D1',self.id()+' wrong call-site key')
            argumentsPath=os.path.join(regressionRoot,'Top__D1.args.json')
            self.assertTrue(os.path.exists(argumentsPath),self.id()+' arguments not sprayed')
            with open(argumentsPath) as argumentsFile:
                self.assertEqual(json.load(argumentsFile),{'risetime':'20e-12'},
                                 self.id()+' wrong sprayed arguments')
        finally:
            RegressionContext.Stop()
        self.assertFalse(RegressionContext.active,self.id()+' context remained active')
        self.assertFalse(RegressionCallSite.enabled,self.id()+' call-site tracking remained enabled')
    def testRegressionReferencePathUsesMirroredProjectLayout(self):
        RegressionContext.Start(self.tempDir,self.File('Regression'),write=True)
        try:
            path=RegressionContext.ReferencePath(os.path.join(self.tempDir,'sub','Leaf.si'),
                                                 'project','')
            self.assertTrue(path.endswith(os.path.join('sub','Leaf.project.json')),
                            self.id()+' wrong mirrored project path')
        finally:
            RegressionContext.Stop()
    def testRegressionPreferenceNames(self):
        from SignalIntegrity.App.PreferencesFile import PreferencesFile
        preferences=PreferencesFile()
        self.assertFalse(preferences['Features.Regression'],self.id()+' regression enabled by default')
        self.assertTrue(preferences['Regression.OpenDiffToolOnFailure'],
                        self.id()+' open diff tool not enabled by default')
    def testRegressionContextRecordsSParametersInMirroredTree(self):
        archiveRoot=self.tempDir
        regressionRoot=self.File('Regression')
        project=os.path.join(archiveRoot,'sub','Leaf.si')
        os.makedirs(os.path.dirname(project))
        sp=self.SParameters()
        RegressionContext.Start(archiveRoot,regressionRoot,write=True)
        try:
            RegressionCallSite.Push('D3')
            result=RegressionContext.RecordSParameters(project,sp,{'mode':'a'})
            RegressionCallSite.Pop()
            self.assertTrue(result.written,self.id()+' s-parameters not written')
            reference=os.path.join(regressionRoot,'sub','Leaf__D3.s2p')
            self.assertTrue(os.path.exists(reference),self.id()+' mirrored reference missing')
            arguments=os.path.join(regressionRoot,'sub','Leaf__D3.args.json')
            self.assertTrue(os.path.exists(arguments),self.id()+' mirrored arguments missing')
        finally:
            RegressionContext.Stop()
    def testRegressionContextNativeArtifactsAreSwitchable(self):
        self.assertIn('waveform',RegressionContext.artifacts,self.id()+' waveform not enabled')
        self.assertIn('noise',RegressionContext.artifacts,self.id()+' noise not enabled')
        RegressionContext.Start(self.tempDir,self.File('Regression'),artifacts=['netlist'])
        try:
            self.assertIsNone(RegressionContext.RecordWaveform('Top.si',object(),'V1'),
                              self.id()+' disabled waveform was recorded')
            self.assertIsNone(RegressionContext.RecordNoise('Top.si',object(),'N1'),
                              self.id()+' disabled noise was recorded')
        finally:
            RegressionContext.Stop()
    def testRegressionContextProjectArtifactsAreSwitchable(self):
        class App(object):
            pass
        app=App()
        app.Drawing=object()
        RegressionContext.Start(self.tempDir,self.File('Regression'),artifacts=['sparameters'])
        try:
            self.assertEqual(RegressionContext.RecordProjectArtifacts('Top.si',app),[],
                             self.id()+' disabled project artifacts were recorded')
        finally:
            RegressionContext.Stop()
    def testDiffTreesReportsMissingUnexpectedAndChanged(self):
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'a.net','device D1 2\n')
        self.Write(candidate,'a.net','device D1 4\n')
        self.Write(reference,'only_ref.net','device D2 2\n')
        self.Write(candidate,'only_cand.net','device D3 2\n')
        self.Write(reference,'same.net','device D4 2\n')
        self.Write(candidate,'same.net','device D4 2\n')
        results=RegressionFiles().DiffTrees(reference,candidate)
        byName={os.path.basename(str(r.filename)):r for r in results}
        self.assertTrue(byName['same.net'].ok,self.id()+' identical file flagged')
        self.assertFalse(byName['a.net'].ok,self.id()+' changed file passed')
        self.assertIn('missing',byName['only_ref.net'].message,self.id()+' missing not reported')
        self.assertIn('unexpected',byName['only_cand.net'].message,self.id()+' unexpected not reported')
    def testDiffTreesToleratesNetlistConnectionReorder(self):
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'c.net','connect VG1 1 VG4 1\n')
        self.Write(candidate,'c.net','connect VG4 1 VG1 1\n')
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertTrue(all(r.ok for r in results),self.id()+' harmless reorder flagged as failure')
    def testDiffTreesToleratesNetlistLineReorder(self):
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'n.net','device D1 2\ndevice D2 4\nport 1 D1 1\n')
        self.Write(candidate,'n.net','port 1 D1 1\ndevice D2 4\ndevice D1 2\n')
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertTrue(all(r.ok for r in results),self.id()+' reordered netlist lines flagged as failure')
    def Waveform(self,values,H=0.0,Fs=1e9):
        return '\n'.join([str(H),str(len(values)),str(Fs)]+[str(v) for v in values])+'\n'
    def testDiffTreesToleratesWaveformWithinTolerance(self):
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'w.wf',self.Waveform([0.0,0.5,1.0,-0.5]))
        self.Write(candidate,'w.wf',self.Waveform([0.0,0.5+1e-5,1.0-1e-5,-0.5]))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertTrue(all(r.ok for r in results),self.id()+' within-tolerance waveform flagged')
    def testDiffTreesToleratesComplexWaveform(self):
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'w.wf',self.Waveform([0.0265-0.0305j,1.0j]))
        self.Write(candidate,'w.wf',self.Waveform([0.0265-0.0305j,1.0j]))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertTrue(all(r.ok for r in results),self.id()+' complex waveform failed')
    def testDiffTreesReportsWaveformBeyondTolerance(self):
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'w.wf',self.Waveform([0.0,0.5,1.0]))
        self.Write(candidate,'w.wf',self.Waveform([0.0,0.5,1.0+1e-2]))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertEqual(len(results),1,self.id()+' wrong number of waveform results')
        self.assertFalse(results[0].ok,self.id()+' beyond-tolerance waveform passed')
        self.assertIn('exceeds tolerance',results[0].message,self.id()+' wrong waveform message')
    def testDiffTreesToleratesWaveformStartTimeWithinSamplePeriodFraction(self):
        reference=self.File('ref'); candidate=self.File('cand')
        sampleRate=1e9
        self.Write(reference,'w.wf',self.Waveform([0.0,1.0],H=0.0,Fs=sampleRate))
        self.Write(candidate,'w.wf',self.Waveform([0.0,1.0],H=0.001/sampleRate,Fs=sampleRate))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertTrue(results[0].ok,self.id()+' small waveform start-time difference flagged')
    def testDiffTreesReportsWaveformStartTimeBeyondSamplePeriodFraction(self):
        reference=self.File('ref'); candidate=self.File('cand')
        sampleRate=1e9
        self.Write(reference,'w.wf',self.Waveform([0.0,1.0],H=0.0,Fs=sampleRate))
        self.Write(candidate,'w.wf',self.Waveform([0.0,1.0],H=0.0011/sampleRate,Fs=sampleRate))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertFalse(results[0].ok,self.id()+' large waveform start-time difference passed')
        self.assertIn('timebase',results[0].message,self.id()+' start-time difference not reported')
    def testDiffTreesReportsWaveformTimebaseChange(self):
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'w.wf',self.Waveform([0.0,1.0],Fs=1e9))
        self.Write(candidate,'w.wf',self.Waveform([0.0,1.0],Fs=2e9))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertFalse(results[0].ok,self.id()+' timebase change passed')
        self.assertIn('timebase',results[0].message,self.id()+' timebase change not reported')
    def testDiffTreesReportsArgumentChange(self):
        import json
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'Top.args.json',json.dumps({'risetime':'20e-12'}))
        self.Write(candidate,'Top.args.json',json.dumps({'risetime':'25e-12'}))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertEqual(len(results),1,self.id()+' wrong number of argument results')
        self.assertFalse(results[0].ok,self.id()+' argument change passed')
        self.assertIn('risetime was 20e-12, is now 25e-12',results[0].message,
                      self.id()+' wrong argument difference')
    def testDiffTreesOrdersDeeperDifferencesFirst(self):
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'top.net','device A 2\n')
        self.Write(candidate,'top.net','device A 4\n')
        self.Write(reference,os.path.join('sub','leaf.net'),'device B 2\n')
        self.Write(candidate,os.path.join('sub','leaf.net'),'device B 4\n')
        failing=[r for r in RegressionFiles().DiffTrees(reference,candidate) if not r.ok]
        self.assertEqual(os.path.basename(str(failing[0].filename)),'leaf.net',
                         self.id()+' deeper difference not reported first')
    def testDiffTreesIgnoresNamedFiles(self):
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'manifest.json','{"a": 1}')
        self.Write(candidate,'manifest.json','{"a": 2}')
        results=RegressionFiles().DiffTrees(reference,candidate,ignore={'manifest.json'})
        self.assertEqual(results,[],self.id()+' ignored file was compared')
    def testDiffTreesIgnoresEyeDiagrams(self):
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'probe.eye.png','AAAA')
        self.Write(candidate,'probe.eye.png','BBBB')
        self.Write(candidate,'only_candidate.eye.png','CCCC')
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertEqual(results,[],self.id()+' eye bitmap was compared')
    def testDiffTreesReportsMeasurementChange(self):
        import json
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'m.measurements.json',json.dumps({'BER':1e-12,'OMA':0.5}))
        self.Write(candidate,'m.measurements.json',json.dumps({'BER':1e-9,'OMA':0.5}))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertEqual(len(results),1,self.id()+' wrong number of measurement results')
        self.assertFalse(results[0].ok,self.id()+' measurement change passed')
        self.assertIn('BER',results[0].message,self.id()+' wrong measurement difference')
    def testDiffTreesToleratesMeasurementWithinTolerance(self):
        import json
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'m.measurements.json',json.dumps({'OMA':0.5}))
        self.Write(candidate,'m.measurements.json',json.dumps({'OMA':0.5+1e-9}))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertTrue(all(r.ok for r in results),self.id()+' within-tolerance drift flagged')
    def testDiffTreesToleratesSmallEyeMeasurementDrift(self):
        import json
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'m.measurements.json',json.dumps({'Measurements.0.Height':0.5}))
        self.Write(candidate,'m.measurements.json',json.dumps({'Measurements.0.Height':0.5*1.0005}))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertTrue(all(r.ok for r in results),self.id()+' small eye drift flagged')
    def testDiffTreesReportsLargeEyeMeasurementDrift(self):
        import json
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'m.measurements.json',json.dumps({'Measurements.0.Height':0.5}))
        self.Write(candidate,'m.measurements.json',json.dumps({'Measurements.0.Height':0.5*1.002}))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertFalse(results[0].ok,self.id()+' large eye drift passed')
    def testDiffTreesReportsMeasurementAddedAndRemoved(self):
        import json
        reference=self.File('ref'); candidate=self.File('cand')
        self.Write(reference,'m.measurements.json',json.dumps({'OMA':0.5,'BER':1e-12}))
        self.Write(candidate,'m.measurements.json',json.dumps({'OMA':0.5,'SNR':20.0}))
        results=RegressionFiles().DiffTrees(reference,candidate)
        self.assertEqual(len(results),1,self.id()+' wrong number of measurement results')
        self.assertFalse(results[0].ok,self.id()+' measurement add/remove passed')
        self.assertIn('BER removed',results[0].message,self.id()+' removal not reported')
        self.assertIn('SNR added',results[0].message,self.id()+' addition not reported')
    def testRegressionContextSpraysMeasurements(self):
        import json
        archiveRoot=self.tempDir
        regressionRoot=self.File('Regression')
        project=os.path.join(archiveRoot,'Top.si')
        RegressionContext.Start(archiveRoot,regressionRoot)
        try:
            result=RegressionContext.RecordMeasurements(project,{'BER':1e-12},{'mode':'a'})
            self.assertTrue(result.written,self.id()+' measurements not written')
            reference=os.path.join(regressionRoot,'Top.measurements.json')
            self.assertTrue(os.path.exists(reference),self.id()+' measurements file missing')
            with open(reference) as measurementsFile:
                self.assertEqual(json.load(measurementsFile),{'BER':1e-12},
                                 self.id()+' wrong sprayed measurements')
        finally:
            RegressionContext.Stop()
    def testRegressionArchiveGenerateCheckByDiffDetectsProjectChange(self):
        import shutil
        from SignalIntegrity.App.Regression import GenerateRegression,CheckRegressionByDiff
        sourceDirectory=os.path.join(self.path,'TestDwellTime')
        projectDirectory=os.path.join(self.tempDir,'Project')
        shutil.copytree(sourceDirectory,projectDirectory)
        project=os.path.join(projectDirectory,'DwellTime.si')
        regressionArchive=os.path.join(self.tempDir,'DwellTime.regression.siz')
        currentDirectory=os.getcwd()
        GenerateRegression(project,regressionArchive,artifacts=['netlist','project'])
        self.assertTrue(os.path.exists(regressionArchive),self.id()+' regression archive missing')
        results=CheckRegressionByDiff(project,regressionArchive,
                                      artifacts=['netlist','project'],openDiffTool=False)
        self.assertEqual(os.getcwd(),currentDirectory,self.id()+' check changed directory')
        self.assertFalse(os.path.exists(os.path.splitext(project)[0]+'_Archive'),
                 self.id()+' check left extracted project tree')
        self.assertFalse(os.path.exists(os.path.splitext(project)[0]+'_RegressionCandidate'),
                 self.id()+' check left candidate tree')
        self.assertFalse(os.path.exists(os.path.splitext(project)[0]+'_RegressionReference'),
                 self.id()+' check left reference tree')
        self.assertFalse(os.path.exists(os.path.splitext(project)[0]+'.siz'),
                 self.id()+' check left project archive byproduct')
        self.assertTrue(results,self.id()+' unchanged project produced no checks')
        self.assertTrue(all(result.ok for result in results),
                self.id()+' unchanged project did not pass: '+
                '; '.join(str(r) for r in results if not r.ok))
        with open(project) as projectFile:
            projectText=projectFile.read()
        self.assertIn('<FrequencyPoints>',projectText,self.id()+' fixture not suitable')
        projectText=projectText.replace('<FrequencyPoints>4000</FrequencyPoints>',
                                        '<FrequencyPoints>4001</FrequencyPoints>')
        with open(project,'w') as projectFile:
            projectFile.write(projectText)
        results=CheckRegressionByDiff(project,regressionArchive,
                                      artifacts=['netlist','project'],openDiffTool=False)
        self.assertTrue(any(not result.ok for result in results),
                        self.id()+' changed project passed regression check')
    def testRegressionThroughHeadlessHonorsArguments(self):
        """Generation and check via SignalIntegrityAppHeadless accept and apply project args."""
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        project=os.path.join(self.tempDir,'IdealTwoPort.si')
        shutil.copyfile(os.path.join(self.path,'IdealTwoPort.si'),project)
        archive=os.path.join(self.tempDir,'IdealTwoPort_regression.siz')
        app=SignalIntegrityAppHeadless()
        self.assertTrue(app.OpenProjectFile(project),self.id()+' project did not open')
        # generate the golden archive with a specific argument, through the headless app
        self.assertTrue(app.GenerateRegression(archive,args={'IdealZc':'50.0'}),
                self.id()+' generation did not return an archive')
        self.assertTrue(os.path.exists(archive),self.id()+' regression archive missing')
        # check with matching args passes; with a different arg value fails (args are applied)
        matched=app.RunRegression(archive,args={'IdealZc':'50.0'},openDiffTool=False)
        mismatched=app.RunRegression(archive,args={'IdealZc':'75.0'},openDiffTool=False)
        os.chdir(self.path)  # leave the temp dir so tearDown can remove it
        self.assertTrue(matched,self.id()+' matched-args check produced no results')
        self.assertTrue(all(result.ok for result in matched),
                self.id()+' matched-args check failed: '+
                '; '.join(str(r) for r in matched if not r.ok))
        self.assertTrue(any(not result.ok for result in mismatched),
                self.id()+' mismatched-args check did not detect the argument change')

if __name__ == "__main__": # pragma: no cover
    unittest.main()
