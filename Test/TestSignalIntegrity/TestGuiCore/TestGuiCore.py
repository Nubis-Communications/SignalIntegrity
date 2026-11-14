"""
TestGuiCore.py
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
import json
import shutil
import tempfile

from SignalIntegrity.GuiCore.RecordingCanvas import RecordingCanvas
from SignalIntegrity.GuiCore.Session import ProjectSession, SessionError

EXAMPLES=os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
    '..','..','..','SignalIntegrity','App','Examples'))
TESTS=os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),'..'))

class TestRecordingCanvasTest(unittest.TestCase):
    def testPrimitives(self):
        canvas=RecordingCanvas()
        canvas.create_line(0,0,10,0,20,5,fill='blue',width=2,arrow='last',arrowshape=(8,10,3))
        canvas.create_polygon(0,0,5,5,0,5,fill='black')
        canvas.create_rectangle(1,2,3,4,outline='red')
        canvas.create_oval(-5,-5,5,5,fill='black',outline='black')
        canvas.create_arc(0,0,10,10,start=90,extent=180,style='arc',outline='black')
        canvas.create_text(7,8,text='R1',anchor='sw',fill='black')
        types=[item['type'] for item in canvas.items]
        self.assertEqual(types,['line','polygon','rectangle','oval','arc','text'])
        self.assertEqual(canvas.items[0]['points'],[0.,0.,10.,0.,20.,5.])
        self.assertEqual(canvas.items[0]['arrow'],'last')
        self.assertEqual(canvas.items[5]['anchor'],'sw')
        self.assertEqual(canvas.BoundingBox(),[-5.,-5.,20.,10.])
        json.dumps(canvas.items)
    def testEmpty(self):
        self.assertIsNone(RecordingCanvas().BoundingBox())

class TestProjectSessionTest(unittest.TestCase):
    def setUp(self):
        self.cwd=os.getcwd()
        self.session=ProjectSession()
    def tearDown(self):
        os.chdir(self.cwd)
    def testNotOpen(self):
        self.assertFalse(self.session.IsOpen())
        with self.assertRaises(SessionError):
            self.session.Render()
        with self.assertRaises(SessionError):
            self.session.Open(os.path.join(EXAMPLES,'DoesNotExist.si'))
    def testRenderAllExamples(self):
        for name in ['RLC.si','RLCTest2SP.si','DeembedCableFilter.si','telegrapherFourPort.si']:
            drawing=self.session.Open(os.path.join(EXAMPLES,name))
            self.assertGreater(len(drawing['items']),0,name)
            self.assertGreater(len(drawing['devices']),0,name)
            self.assertIsNotNone(drawing['bbox'],name)
            json.dumps(drawing)
    def testCapabilities(self):
        self.assertTrue(self.session.Open(os.path.join(EXAMPLES,'RLC.si'))['capabilities']['simulate'])
        self.assertTrue(self.session.Open(os.path.join(EXAMPLES,'RLCTest2SP.si'))['capabilities']['sparameters'])
        self.assertTrue(self.session.Open(os.path.join(EXAMPLES,'DeembedCableFilter.si'))['capabilities']['deembed'])
    def testSelectAndProperties(self):
        drawing=self.session.Open(os.path.join(EXAMPLES,'RLC.si'))
        device=[d for d in drawing['devices'] if d['partname']=='Resistor'][0]
        x0,y0,x1,y1=device['bbox']
        index=self.session.DeviceAt((x0+x1)/2.,(y0+y1)/2.)
        self.assertEqual(index,device['index'])
        self.session.Select(index)
        self.assertTrue(self.session.Render()['devices'][index]['selected'])
        properties={p['keyword']:p for p in self.session.DeviceProperties(index)}
        self.assertIn('r',properties)
        self.session.SetDeviceProperty(index,'r','33')
        properties={p['keyword']:p for p in self.session.DeviceProperties(index)}
        self.assertTrue(properties['r']['value'].startswith('33.0'))
        self.assertIn('33',self.session.NetList())
        with self.assertRaises(SessionError):
            self.session.SetDeviceProperty(index,'r','not a number')
        with self.assertRaises(SessionError):
            self.session.SetDeviceProperty(index,'nonexistent','1')
        with self.assertRaises(SessionError):
            self.session.DeviceProperties(999)
    def testVariablesAndCalculationProperties(self):
        import SignalIntegrity.App.Project
        from SignalIntegrity.App.ProjectFile import VariableConfiguration
        self.session.Open(os.path.join(EXAMPLES,'RLC.si'))
        variable=VariableConfiguration()
        variable['Name']='Rx'; variable['Value']='50'; variable['Units']='Ohm'
        SignalIntegrity.App.Project['Variables.Items'].append(variable)
        self.assertEqual(self.session.SetVariable('Rx','75')[0]['value'],'75')
        with self.assertRaises(SessionError):
            self.session.SetVariable('NoSuchVariable','1')
        values=self.session.SetCalculationProperties({'EndFrequency':10e9,'FrequencyPoints':500})
        self.assertEqual(values['EndFrequency'],10e9)
        self.assertEqual(values['FrequencyPoints'],500)
        with self.assertRaises(SessionError):
            self.session.SetCalculationProperties({'Bogus':1})
    def testSimulateMatchesHeadless(self):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        filename=os.path.join(EXAMPLES,'RLC.si')
        self.session.Open(filename)
        result=self.session.Calculate('simulate')
        json.dumps(result.Summary())
        app=SignalIntegrityAppHeadless()
        app.OpenProjectFile(filename)
        reference=app.Simulate()
        labels=reference['output waveform labels']
        self.assertEqual([name for name,_ in result.waveforms],labels)
        series=result.Series('time')['series']
        for wf,ref in zip(series,reference['output waveforms']):
            self.assertEqual(len(wf['y']),len(ref))
            for a,b in zip(wf['y'],ref.Values()):
                self.assertAlmostEqual(a,b,12)
    def testSimulationWaveformsMatchTkDialog(self):
        # the tk simulator dialog shows the output waveforms, other waveforms and shown sources once each
        self.session.Open(os.path.join(EXAMPLES,'PID','PIDSimulation.si'))
        result=self.session.Calculate('simulate')
        self.assertEqual([name for name,_ in result.waveforms],['VO','VPID','VU','P','I','D','Vin'])
        info=result.WaveformInfo()
        self.assertEqual(info[-1]['points'],115000)
        self.assertEqual(info[0]['points'],65001)
    def testSeriesDecimationAndRange(self):
        self.session.Open(os.path.join(EXAMPLES,'PID','PIDSimulation.si'))
        result=self.session.Calculate('simulate')
        x,y=result.Arrays(1)
        full=result.Series('time',[1],maxPoints=1000)['series'][0]
        self.assertLessEqual(len(full['x']),1000)
        # decimation keeps the extremes of the waveform
        self.assertAlmostEqual(max(full['y']),float(y.max()),12)
        self.assertAlmostEqual(min(full['y']),float(y.min()),12)
        zoom=result.Series('time',[1],xmin=0.,xmax=20e-6,maxPoints=100000)['series'][0]
        self.assertEqual(len(zoom['x']),zoom['total'])
        self.assertLess(zoom['total'],len(x))
        self.assertLessEqual(zoom['x'][0],0.)
        self.assertGreaterEqual(zoom['x'][-1],20e-6)
        limits=result.AutoscaleLimits('time')
        self.assertEqual(limits[0],float(min(result.Arrays(i)[0][0] for i in range(len(result.waveforms)))))
        content=result.Series('content',[0],maxPoints=500)
        self.assertLessEqual(len(content['series'][0]['x']),500)
        json.dumps(content)
    def testEyeDiagramsDoNotAlterWaveforms(self):
        # clock recovery modifies the waveform it is given, so the eye must be computed on a copy
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        filename=os.path.join(TESTS,'TestClockRecovery','ClockRecoveryCompare.si')
        self.session.Open(filename)
        result=self.session.Calculate('simulate')
        self.assertEqual([n for n,_ in result.eyes],['WithClockRecovery','WithoutClockRecovery'])
        for _,image in result.eyes:
            self.assertGreater(image.size[0]*image.size[1],0)
        self.assertTrue(result.Summary()['eyes'][0]['image'].startswith('data:image/png;base64,'))
        app=SignalIntegrityAppHeadless()
        app.OpenProjectFile(filename)
        reference=app.Simulate()
        for (name,wf),ref in zip(result.waveforms,reference['output waveforms']):
            self.assertEqual(len(wf),len(ref),name)
    def testFailureReasonIsReported(self):
        self.session.Open(os.path.join(TESTS,'TestWaveformProcessor','amplifier_test.si'))
        with self.assertRaises(SessionError) as e:
            self.session.Calculate('simulate')
        self.assertIn('unconnected device ports',str(e.exception))
    def testDCWaveform(self):
        from SignalIntegrity.GuiCore.Results import ResultData
        data=ResultData('waveform','dc')
        data.waveforms=[('V',1.5)]
        series=data.Series('time')['series'][0]
        self.assertEqual(series['dc'],1.5)
        self.assertEqual(data.AutoscaleLimits('time')[2:],[1.5,1.5])
    def testPropertyAndVariableVisibility(self):
        drawing=self.session.Open(os.path.join(EXAMPLES,'PID','PIDSimulation.si'))
        pid=[d for d in drawing['devices'] if d['ref']=='PID'][0]['index']
        texts=lambda: [i['text'] for i in self.session.Render()['items'] if i['type']=='text']
        self.assertNotIn('ref PID',texts())
        properties=self.session.SetDevicePropertyVisibility(pid,'ref',keywordVisible=True)
        self.assertTrue([p for p in properties if p['keyword']=='ref'][0]['keywordVisible'])
        self.assertIn('ref PID',texts())
        self.session.SetDevicePropertyVisibility(pid,'ref',visible=False)
        self.assertNotIn('ref PID',texts())
        self.assertIn('PID_P 60.0 ',texts())
        self.assertFalse(self.session.SetVariableVisible('PID_P',False)[0]['visible'])
        self.assertNotIn('PID_P 60.0 ',texts())
        calcprop=[p for p in self.session.DeviceProperties(pid) if p['keyword']=='calcprop'][0]
        self.assertEqual(calcprop['validEntries'],['true','false'])
        with self.assertRaises(SessionError):
            self.session.SetDeviceProperty(pid,'calcprop','maybe')
    def testTraversal(self):
        drawing=self.session.Open(os.path.join(EXAMPLES,'PID','PIDSimulation.si'))
        pid=[d for d in drawing['devices'] if d['ref']=='PID'][0]['index']
        source=[d for d in drawing['devices'] if d['ref']=='Vin'][0]['index']
        self.assertEqual(self.session.ViewActions(pid),[{'label':'Open Project','action':'file'}])
        self.assertEqual(self.session.ViewActions(source),[{'label':'View Waveform','action':'waveform'}])
        # an unsaved edit in the parent must survive descending and ascending
        self.session.MoveDevice(source,1,0)
        kind,child=self.session.View(pid,'file')
        self.assertEqual(kind,'project')
        self.assertEqual(child['path'],['PIDSimulation.si','PID.si'])
        self.assertTrue(child['readOnly'])
        # the device variables are passed into the sub-project
        self.assertEqual({v['name']:v['value'] for v in self.session.Variables()},{'P':'60.0','I':'500.0','D':'15.0'})
        with self.assertRaises(SessionError):
            self.session.MoveDevice(0,1,0)
        with self.assertRaises(SessionError):
            self.session.Save()
        self.assertTrue(self.session.Capabilities()['sparameters'])
        parent=self.session.Ascend()
        self.assertFalse(parent['readOnly'])
        self.assertEqual(parent['path'],['PIDSimulation.si'])
        self.assertTrue(parent['devices'][pid]['selected'])
        moved=[d for d in parent['devices'] if d['ref']=='Vin'][0]['bbox']
        self.assertEqual(moved,[b+(self.session.Grid() if k%2==0 else 0) for k,b in enumerate(drawing['devices'][source]['bbox'])])
        with self.assertRaises(SessionError):
            self.session.Ascend()
        kind,waveform=self.session.View(source,'waveform')
        self.assertEqual(kind,'result')
        self.assertEqual(waveform.WaveformInfo()[0]['name'],'Vin')
    def testWaveformProjectTraversal(self):
        drawing=self.session.Open(os.path.join(EXAMPLES,'PRBSExample','PRBSTest.si'))
        source=[d for d in drawing['devices'] if d['ref']=='VS1'][0]['index']
        self.assertIn({'label':'Open Project','action':'openproject'},self.session.ViewActions(source))
        kind,child=self.session.View(source,'openproject')
        self.assertEqual(child['path'],['PRBSTest.si','PRBSGenerator.si'])
        self.session.Ascend()
    def testSParameterFileView(self):
        drawing=self.session.Open(os.path.join(EXAMPLES,'telegrapherTestTwoPort.si'))
        for device in drawing['devices']:
            for action in self.session.ViewActions(device['index']):
                if action['action']=='file' and action['label']=='View':
                    kind,result=self.session.View(device['index'],'file')
                    self.assertEqual(kind,'result')
                    self.assertEqual(len(result.sparameters),1)
                    return
    def testSParameters(self):
        self.session.Open(os.path.join(EXAMPLES,'RLCTest2SP.si'))
        result=self.session.Calculate('sparameters').Summary()
        sp=result['sparameters'][0]
        self.assertEqual(len(sp['traces']),sp['ports']**2)
        self.assertEqual(len(sp['traces'][0]['dB']),len(sp['frequencies']))
        json.dumps(result)
    def testDeembed(self):
        self.session.Open(os.path.join(EXAMPLES,'DeembedCableFilter.si'))
        result=self.session.Calculate('deembed')
        self.assertGreater(len(result.sparameters),0)
    def testCalculateNotSupported(self):
        self.session.Open(os.path.join(EXAMPLES,'RLC.si'))
        with self.assertRaises(SessionError):
            self.session.Calculate('sparameters')
        with self.assertRaises(SessionError):
            self.session.Calculate('bogus')
    def testCancel(self):
        self.session.Open(os.path.join(EXAMPLES,'RLCTest2SP.si'))
        with self.assertRaises(SessionError):
            self.session.Calculate('sparameters',lambda progress: False)
        self.assertGreater(len(self.session.Calculate('sparameters',lambda progress: True).sparameters),0)
    def testSaveRoundTrip(self):
        directory=tempfile.mkdtemp()
        try:
            source=os.path.join(EXAMPLES,'RLC.si')
            copy=os.path.join(directory,'RLC.si')
            shutil.copy(source,copy)
            self.session.Open(copy)
            device=[d for d in self.session.Render()['devices'] if d['partname']=='Resistor'][0]['index']
            self.session.SetDeviceProperty(device,'r','12')
            self.session.MoveDevice(device,1,0)
            saved=self.session.Save(os.path.join(directory,'RLC2'))
            self.assertTrue(saved.endswith('RLC2.si'))
            other=ProjectSession()
            other.Open(saved)
            properties={p['keyword']:p['value'] for p in other.DeviceProperties(device)}
            self.assertTrue(properties['r'].startswith('12.0'))
        finally:
            os.chdir(self.cwd)
            shutil.rmtree(directory,ignore_errors=True)

class TestPartStencilTest(unittest.TestCase):
    def setUp(self):
        self.cwd=os.getcwd()
        self.directory=tempfile.mkdtemp()
        self.session=ProjectSession()
        self.catalog=self.session.PartCatalog()
    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.directory,ignore_errors=True)
    def _Part(self,description):
        return [p['index'] for p in self.catalog if p['description']==description][0]
    def testCatalog(self):
        self.assertGreater(len(self.catalog),100)
        self.assertEqual([p['index'] for p in self.catalog],list(range(len(self.catalog))))
        descriptions=[p['description'] for p in self.catalog]
        self.assertEqual(len(descriptions),len(set(descriptions)))
        categories={c for p in self.catalog for c in p['categories']}
        for category in ['Resistors','Sources','Generators','Amplifiers','Transmission Lines']:
            self.assertIn(category,categories)
        previews=self.session.PartCatalog(previews=True)
        json.dumps(previews)
        self.assertTrue(all(p['preview']['items'] for p in previews))
        with self.assertRaises(SessionError):
            self.session.PartPreview(len(self.catalog))
    def testNewAddDelete(self):
        with self.assertRaises(SessionError):
            self.session.AddPart(0,0,0)
        drawing=self.session.New(os.path.join(self.directory,'blank'))
        self.assertTrue(drawing['filename'].endswith('blank.si'))
        self.assertTrue(os.path.isfile(drawing['filename']))
        self.assertEqual(drawing['devices'],[])
        grid=self.session.Grid()
        resistor=self._Part('Two Port Resistor')
        first=self.session.AddPart(resistor,10*grid+3,5*grid-2)
        second=self.session.AddPart(resistor,20*grid,5*grid)
        devices=self.session.Render()['devices']
        self.assertEqual([d['ref'] for d in devices],['R1','R2'])
        self.assertTrue(devices[second]['selected'] and not devices[first]['selected'])
        ox,oy=self.session.Origin()
        origin=self.session.app.Drawing.schematic.deviceList[first].partPicture.current.origin
        self.assertEqual(tuple(origin),(10-ox,5-oy))
        port=self._Part('Port')
        self.session.AddPart(port,0,0); self.session.AddPart(port,0,10*grid)
        numbers=[p['value'] for i in (2,3) for p in self.session.DeviceProperties(i) if p['keyword']=='pn']
        self.assertEqual(numbers,['1','2'])
        # the catalog itself must not change when a part is placed and edited
        self.session.SetDeviceProperty(first,'r','33')
        self.assertNotIn('33',json.dumps(self.session.PartPreview(resistor)))
        self.session.DeleteDevice(first)
        devices=self.session.Render()['devices']
        self.assertEqual([(d['partname'],d['ref']) for d in devices],[('Resistor','R2'),('Port',''),('Port','')])
        self.assertFalse(any(d['selected'] for d in devices))
        with self.assertRaises(SessionError):
            self.session.DeleteDevice(10)
        self.session.Save()
        self.assertEqual(len(ProjectSession().Open(drawing['filename'])['devices']),3)
    def testReadOnlyLevelRejectsEdits(self):
        drawing=self.session.Open(os.path.join(EXAMPLES,'PID','PIDSimulation.si'))
        pid=[d for d in drawing['devices'] if d['ref']=='PID'][0]['index']
        self.session.View(pid,'file')
        with self.assertRaises(SessionError):
            self.session.AddPart(0,0,0)
        with self.assertRaises(SessionError):
            self.session.DeleteDevice(0)

def BuildDivider(session,directory):
    """a step generator driving a 50 ohm divider, wired through the session API; @return grid"""
    catalog={p['description']:p['index'] for p in session.PartCatalog()}
    session.New(os.path.join(directory,'divider'))
    g=session.Grid()
    session.AddPart(catalog['One Port Voltage Step Generator'],5*g,10*g)    # pin at pixel (96,160)
    session.AddPart(catalog['Two Port Resistor'],15*g,5*g)                  # pins at (240,96) and (304,96)
    session.AddPart(catalog['Output'],25*g,5*g)                             # pin at (400,96)
    session.AddPart(catalog['One Port Resistor to Ground'],30*g,5*g)        # pin at (496,80)
    return g

class TestWiresTest(unittest.TestCase):
    def setUp(self):
        self.cwd=os.getcwd()
        self.directory=tempfile.mkdtemp()
        self.session=ProjectSession()
    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.directory,ignore_errors=True)
    def testDrawAndSimulate(self):
        BuildDivider(self.session,self.directory)
        self.assertEqual(self.session.Render()['wires'],[])
        # points snap to the nearest grid point, and repeated points are dropped
        self.session.AddWire([[96,160],[97,161],[96,96],[241,95]])
        self.session.AddWire([[304,96],[400,96],[496,96],[496,80]])
        wires=self.session.Render()['wires']
        self.assertEqual(wires[0]['points'],[96.,160.,96.,96.,240.,96.])
        # consolidation splits the second wire at the output probe's pin, as the tk app does
        self.assertEqual([w['points'] for w in wires[1:]],[[304.,96.,400.,96.],[400.,96.,496.,96.,496.,80.]])
        netlist=self.session.NetList()
        for line in ('connect R1 1 VG1 1','voltageoutput VO1 R1 2','connect R1 2 R2 1'):
            self.assertIn(line,netlist)
        result=self.session.Calculate('simulate')
        self.assertAlmostEqual(max(result.waveforms[0][1].Values()),0.5,9)
    def testSelectAndDelete(self):
        BuildDivider(self.session,self.directory)
        self.session.AddWire([[96,160],[96,96],[240,96]])
        self.session.AddWire([[304,96],[400,96]])
        self.assertEqual(self.session.WireAt(97,130),0)
        self.assertEqual(self.session.WireAt(350,99),1)
        self.assertIsNone(self.session.WireAt(350,110))
        self.assertEqual(self.session.WireAt(350,110,15),1)
        self.session.Select(1)
        self.session.SelectWire(1)
        drawing=self.session.Render()
        self.assertEqual([w['selected'] for w in drawing['wires']],[False,True])
        self.assertFalse(any(d['selected'] for d in drawing['devices']))
        self.session.Select(0)
        self.assertFalse(any(w['selected'] for w in self.session.Wires()))
        self.session.DeleteWire(0)
        self.assertEqual([w['points'] for w in self.session.Wires()],[[304.,96.,400.,96.]])
        self.session.Save()
        self.assertEqual(len(ProjectSession().Open(self.session.filename)['wires']),1)
    def testErrors(self):
        with self.assertRaises(SessionError):
            self.session.AddWire([[0,0],[16,0]])     # nothing open
        BuildDivider(self.session,self.directory)
        for bad in ([[0,0]],[[0,0],[3,2]],[[0,0],[1]],'0,0,16,0',[[0,0],['a',0]]):
            with self.assertRaises(SessionError):
                self.session.AddWire(bad)
        for index in (0,-1,'0'):
            with self.assertRaises(SessionError):
                self.session.DeleteWire(index)
            with self.assertRaises(SessionError):
                self.session.SelectWire(index)
    def testReadOnlyLevel(self):
        drawing=self.session.Open(os.path.join(EXAMPLES,'PID','PIDSimulation.si'))
        self.assertGreater(len(drawing['wires']),0)
        pid=[d for d in drawing['devices'] if d['ref']=='PID'][0]['index']
        child=self.session.View(pid,'file')[1]
        with self.assertRaises(SessionError):
            self.session.AddWire([[0,0],[32,0]])
        with self.assertRaises(SessionError):
            self.session.DeleteWire(0)
        self.session.SelectWire(0)    # selecting is allowed, editing is not
        self.assertTrue(child['wires'])

class TestEditingTest(unittest.TestCase):
    """undo/redo, clipboard, flip and wire-corner editing"""
    def setUp(self):
        self.cwd=os.getcwd()
        self.directory=tempfile.mkdtemp()
        shutil.copy(os.path.join(EXAMPLES,'RLC.si'),self.directory)
        self.session=ProjectSession()
        self.session.Open(os.path.join(self.directory,'RLC.si'))
        self.resistor=[d for d in self.session.Render()['devices'] if d['partname']=='Resistor'][0]['index']
    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.directory,ignore_errors=True)
    def _Origin(self,index):
        return tuple(self.session.app.Drawing.schematic.deviceList[index].partPicture.current.origin)
    def testUndoRedo(self):
        s=self.session
        self.assertFalse(s.CanUndo() or s.CanRedo())
        before=self._Origin(self.resistor)
        s.MoveDevice(self.resistor,2,0)
        s.SetDeviceProperty(self.resistor,'r','75')
        drawing=s.Render()
        self.assertEqual((drawing['canUndo'],drawing['undoName']),(True,'edit property'))
        self.assertEqual(s.Undo(),'edit property')
        self.assertTrue([p for p in s.DeviceProperties(self.resistor) if p['keyword']=='r'][0]['value'].startswith('50'))
        self.assertEqual(s.Undo(),'move part')
        self.assertEqual(self._Origin(self.resistor),before)
        self.assertFalse(s.CanUndo())
        with self.assertRaises(SessionError):
            s.Undo()
        self.assertEqual(s.Redo(),'move part')
        self.assertNotEqual(self._Origin(self.resistor),before)
        # a new edit after an undo drops the redo branch, as in tk
        s.RotateDevice(self.resistor)
        self.assertFalse(s.CanRedo())
        s.SetEquations('x=1')
        s.Undo()
        self.assertEqual(s.Equations(),'')
        wires=len(s.Wires())
        s.DeleteWire(0)
        s.Undo()
        self.assertEqual(len(s.Wires()),wires)
    def testHistoryIsPerLevel(self):
        s=ProjectSession()
        drawing=s.Open(os.path.join(EXAMPLES,'PID','PIDSimulation.si'))
        pid=[d for d in drawing['devices'] if d['ref']=='PID'][0]['index']
        s.MoveDevice(pid,1,0)
        s.View(pid,'file')
        self.assertFalse(s.Render()['canUndo'])
        with self.assertRaises(SessionError):
            s.Undo()
        s.Ascend()
        self.assertEqual(s.Undo(),'move part')
    def testClipboardAndFlip(self):
        s=self.session
        self.assertFalse(s.Render()['canPaste'])
        with self.assertRaises(SessionError):
            s.Paste()
        s.Copy(self.resistor)
        pasted=s.Paste()
        devices=s.Render()['devices']
        self.assertEqual(devices[pasted]['ref'],'R2')
        self.assertTrue(devices[pasted]['selected'])
        x,y=self._Origin(self.resistor)
        self.assertEqual(self._Origin(pasted),(x+2,y+2))
        duplicate=s.Duplicate(pasted,20*s.Grid(),3*s.Grid())
        self.assertEqual(s.Render()['devices'][duplicate]['ref'],'R3')
        ox,oy=s.Origin()
        self.assertEqual(self._Origin(duplicate),(20-ox,3-oy))
        count=len(s.Render()['devices'])
        s.Cut(duplicate)
        self.assertEqual(len(s.Render()['devices']),count-1)
        pasted=s.Paste()
        self.assertEqual(s.Render()['devices'][pasted]['ref'],'R3')
        picture=s.app.Drawing.schematic.deviceList[self.resistor].partPicture.current
        s.FlipDevice(self.resistor,'horizontal')
        self.assertTrue(picture.mirroredHorizontally)
        s.FlipDevice(self.resistor,'vertical')
        self.assertTrue(picture.mirroredVertically)
        with self.assertRaises(SessionError):
            s.FlipDevice(self.resistor,'diagonal')
    def testVertices(self):
        s=self.session
        wire=s.Wires()[0]
        x,y=wire['points'][0],wire['points'][1]
        self.assertEqual(s.VertexAt(x+1,y-1),[0,0])
        self.assertIsNone(s.VertexAt(x+40,y+40))
        s.SelectVertex(0,0)
        self.assertEqual(s.Render()['selectedVertex'],[0,0])
        self.assertEqual(s.DuplicateVertex(0,0),[0,1])
        self.assertEqual(s.Render()['selectedVertex'],[0,1])
        g=s.Grid()
        s.MoveVertex(0,1,x,y+2*g+3)
        self.assertIsNone(s.Render()['selectedVertex'])
        corners=[[w['points'][k],w['points'][k+1]] for w in s.Wires() for k in range(0,len(w['points']),2)]
        self.assertIn([x,y+2*g],corners)
        before=len(s.Wires())
        w=[i for i,ww in enumerate(s.Wires()) if len(ww['points'])==4][0]
        s.DeleteVertex(w,0)
        self.assertEqual(len(s.Wires()),before-1)
        for bad in ((0,99),(99,0),('0',0)):
            with self.assertRaises(SessionError):
                s.SelectVertex(*bad)

class TestProjectToolsTest(unittest.TestCase):
    """equations, post-processing, archives and exports"""
    def setUp(self):
        self.cwd=os.getcwd()
        self.directory=tempfile.mkdtemp()
        shutil.copy(os.path.join(EXAMPLES,'RLC.si'),self.directory)
        self.session=ProjectSession()
        self.session.Open(os.path.join(self.directory,'RLC.si'))
    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.directory,ignore_errors=True)
    def testEquationsAndPostProcessing(self):
        s=self.session
        self.assertEqual(s.Equations(),'')
        self.assertIsNotNone(s.CheckEquations('x = 1 +'))
        self.assertIsNone(s.CheckEquations('x = 1 + 2'))
        self.assertIsNone(s.SetEquations('a = 2\nb = a * 3\n\n'))
        self.assertEqual(s.Equations(),'a = 2\nb = a * 3')
        s.SetPostProcessing('print(1)\n')
        self.assertEqual(s.PostProcessing(),'print(1)')
        s.Save()
        other=ProjectSession(); other.Open(s.filename)
        self.assertEqual((other.Equations(),other.PostProcessing()),('a = 2\nb = a * 3','print(1)'))
    def testExports(self):
        from PIL import Image
        s=self.session
        netlist=s.ExportNetList(os.path.join(self.directory,'out'))
        self.assertTrue(netlist.endswith('out.txt'))
        with open(netlist) as f:
            self.assertIn('device R1',f.read())
        with open(s.ExportTikZ(os.path.join(self.directory,'drawing'))) as f:
            text=f.read()
        self.assertIn('<TpX',text)
        self.assertIn('\\begin{tikzpicture}',text)
        with open(s.ExportTikZ(os.path.join(self.directory,'drawing.tex'))) as f:
            self.assertIn('\\begin{tikzpicture}',f.read())
        image=Image.open(s.ExportImage(os.path.join(self.directory,'drawing')))
        self.assertEqual(image.format,'PNG')
        self.assertGreater(image.size[0],200)
        self.assertGreater(len(image.convert('L').getcolors(256*256) or []),2)
        dark=Image.open(s.ExportImage(os.path.join(self.directory,'dark.png'),colorMap={'black':'#ffffff','white':'#000000'}))
        self.assertEqual(dark.getpixel((1,1)),(0,0,0))
        with self.assertRaises(SessionError):
            s.ExportNetList(os.path.join(self.directory,'missing','x.txt'))
    def testArchive(self):
        s=self.session
        archive=s.Archive()
        self.assertTrue(archive.endswith('RLC.siz') and os.path.isfile(archive))
        other=ProjectSession()
        drawing=other.ExtractArchive(archive)
        self.assertTrue(drawing['filename'].endswith(os.path.join('RLC_Archive','RLC.si')))
        self.assertEqual(len(drawing['devices']),len(s.Render()['devices']))
        self.assertFalse(drawing['readOnly'])
        with self.assertRaises(SessionError):
            other.ExtractArchive(os.path.join(self.directory,'RLC.si'))

class TestResultViewsTest(unittest.TestCase):
    """the S-parameter viewer's time-domain views and the statistical noise results"""
    def setUp(self):
        self.cwd=os.getcwd()
    def tearDown(self):
        os.chdir(self.cwd)
    def testSParameterTimeViews(self):
        s=ProjectSession()
        s.Open(os.path.join(EXAMPLES,'RLCTest2SP.si'))
        result=s.Calculate('sparameters')
        P=result.sparameters[0][1].m_P
        impulse=result.SParameterTime(0,'impulse',300)
        self.assertEqual(len(impulse['traces']),P*P)
        self.assertTrue(all(len(t['x'])<=300 for t in impulse['traces']))
        step=result.SParameterTime(0,'step')
        impedance=result.SParameterTime(0,'impedance')
        self.assertEqual([t['name'] for t in impedance['traces']],['S'+str(p)+str(p) for p in range(1,P+1)])
        for trace in impedance['traces']:
            self.assertTrue(all(v<=3000. for v in trace['y'] if v is not None))
        # port 1 sees L in series with C, an open at DC (capped at 3000 ohms); ports 2 and 3 are
        # ideal amplifier outputs (zo=0); every port starts at the 50 ohm reference
        self.assertEqual([round(t['y'][-1]) for t in impedance['traces']],[3000,0,0])
        self.assertTrue(all(abs(t['y'][0]-50.)<0.1 for t in impedance['traces']))
        # impedance is plotted against half the round-trip time
        self.assertAlmostEqual(impedance['traces'][0]['x'][-1]*2,step['traces'][0]['x'][-1],12)
        json.dumps(step)
        with self.assertRaises(ValueError):
            result.SParameterTime(0,'bogus')
    def testStatisticalNoise(self):
        s=ProjectSession()
        s.Open(os.path.join(TESTS,'TestStatisticalNoise','StatisticalNoise.si'))
        result=s.Calculate('simulate')
        info=result.NoiseInfo()
        self.assertEqual([i['name'] for i in info],['Comp','Uncomp'])
        comp=info[0]
        self.assertEqual(comp['type'],'voltage')
        self.assertAlmostEqual(comp['rms'],result.noise['output_noise_spectral_density']['Comp']['rms'],15)
        self.assertEqual([c['name'] for c in comp['contributions']],['VN1','VN2'])
        # independent contributions add in power
        self.assertAlmostEqual(sum(c['rms']**2 for c in comp['contributions']),comp['rms']**2,9)
        # VN1 does not reach Uncomp: no -3000 dBm floor values
        unreached=info[1]['contributions'][0]
        self.assertEqual((unreached['name'],unreached['rms'],unreached['dBm'],unreached['SNR']),('VN1',0.,None,None))
        series=result.NoiseSeries(maxPoints=100)
        self.assertEqual(len(series['series']),2)
        self.assertTrue(all(len(t['x'])<=100 for t in series['series']))
        self.assertLess(series['autoscale'][2],series['autoscale'][3])
        self.assertEqual(json.loads(json.dumps(result.Summary()))['noise'][0]['name'],'Comp')
        s.Open(os.path.join(EXAMPLES,'RLC.si'))
        self.assertEqual(s.Calculate('simulate').NoiseInfo(),[])

class TestPreferencesAndHelpTest(unittest.TestCase):
    def setUp(self):
        from unittest import mock
        self.directory=tempfile.mkdtemp()
        self.patch=mock.patch.dict(os.environ,{'SIGNALINTEGRITY_PREFERENCES':os.path.join(self.directory,'preferences.xml')})
        self.patch.start()
        self.session=ProjectSession()
    def tearDown(self):
        self.patch.stop()
        shutil.rmtree(self.directory,ignore_errors=True)
        ProjectSession()
    def testPreferences(self):
        from SignalIntegrity.GuiCore import Preferences
        self.assertEqual(Preferences.FileName(),os.path.join(self.directory,'preferences.xml'))
        sections=Preferences.Items()
        self.assertEqual(sections[0]['section'],'Appearance')
        paths={i['path']:i for s in sections for i in s['items']}
        self.assertIn('Appearance.FontSize',paths)
        self.assertFalse(any(p.startswith(('Encryption','ProjectFiles.LastFile','Version')) for p in paths))
        self.assertEqual(Preferences.Set('Appearance.FontSize','13'),13)
        self.assertIs(Preferences.Set('Appearance.GridsOnPlots','false'),False)
        self.assertEqual(Preferences.Set('Calculation.Processing.ConvergenceThreshold',2e-3),2e-3)
        with open(Preferences.FileName()) as f:
            self.assertIn('<FontSize>13</FontSize>',f.read())
        for path,value in (('Appearance.FontSize','big'),('Appearance.FontSize',1.5),('Appearance.GridsOnPlots','maybe'),
                           ('Encryption.Password','x'),('Nope.Nothing',1)):
            with self.assertRaises(Preferences.PreferencesError):
                Preferences.Set(path,value)
        json.dumps(sections)
    def testHelpUrls(self):
        from SignalIntegrity.GuiCore import Help, Preferences
        Preferences.Set('OnlineHelp.UseOnlineHelp',False)
        url=Help.Url('equations')
        self.assertTrue(url.startswith('file:'))
        self.assertIn('Help/site/',url)
        self.assertTrue(Help.Url('documentation').endswith('Doc/xhtml/index.xhtml'))
        with self.assertRaises(ValueError):
            Help.Url('nothing')

class TestSettingsTest(unittest.TestCase):
    def setUp(self):
        from unittest import mock
        from SignalIntegrity.GuiCore import Settings
        self.Settings=Settings
        self.directory=tempfile.mkdtemp()
        self.patch=mock.patch.dict(os.environ,{Settings.ENVIRONMENT_VARIABLE:os.path.join(self.directory,'settings')})
        self.patch.start()
    def tearDown(self):
        self.patch.stop()
        shutil.rmtree(self.directory,ignore_errors=True)
    def _File(self,name):
        path=os.path.join(self.directory,name)
        open(path,'w').close()
        return path
    def testRecentProjects(self):
        from SignalIntegrity.GuiCore import Themes
        self.assertEqual(self.Settings.SettingsDirectory(),os.path.join(self.directory,'settings'))
        self.assertTrue(Themes.SettingsFile().startswith(self.Settings.SettingsDirectory()))
        self.assertEqual(self.Settings.RecentProjects(),[])
        a,b=self._File('a.si'),self._File('b.si')
        self.Settings.AddRecentProject(a)
        self.Settings.AddRecentProject(b)
        self.assertEqual(self.Settings.RecentProjects(),[b,a])
        self.Settings.AddRecentProject(a)
        self.assertEqual(self.Settings.RecentProjects(),[a,b])
        os.remove(b)
        self.assertEqual(self.Settings.RecentProjects(),[a])
        for k in range(15):
            self.Settings.AddRecentProject(self._File('p%d.si'%k))
        recent=self.Settings.RecentProjects()
        self.assertEqual(len(recent),self.Settings.MAX_RECENT_PROJECTS)
        self.assertTrue(recent[0].endswith('p14.si'))
        self.Settings.ClearRecentProjects()
        self.assertEqual(self.Settings.RecentProjects(),[])
    def testCorruptFile(self):
        os.makedirs(self.Settings.SettingsDirectory())
        with open(os.path.join(self.Settings.SettingsDirectory(),'gui-recent-projects.json'),'w') as f:
            f.write('not json')
        self.assertEqual(self.Settings.RecentProjects(),[])
        a=self._File('a.si')
        self.assertEqual(self.Settings.AddRecentProject(a),[a])

class TestMenusTest(unittest.TestCase):
    def testDefinition(self):
        from SignalIntegrity.GuiCore import Menus
        self.assertEqual([title for title,_ in Menus.MENUS],['File','Edit','Parts','Wires','View','Calculate','Variables','Help'])
        for gui in ('qt','web'):
            ids=Menus.CommandIds(gui)+Menus.SubmenuIds(gui)
            self.assertEqual(len(ids),len(set(ids)),gui)
            self.assertTrue(all(c is None or c in ids for c in Menus.TOOLBAR),gui)
        self.assertIn('exit',Menus.CommandIds('qt'))
        self.assertNotIn('exit',Menus.CommandIds('web'))
        self.assertIn('recent',Menus.SubmenuIds('web'))
        self.assertEqual(set(ProjectSession.CALCULATIONS)-set(Menus.CommandIds('web')),set())
        json.dumps(Menus.MenusFor('web'))
    def testToolbarIcons(self):
        import xml.etree.ElementTree as ET
        from SignalIntegrity.GuiCore import Menus, Icons
        for commandId in [c for c in Menus.TOOLBAR if c is not None]:
            self.assertTrue(Icons.HasIcon(commandId),commandId)
            self.assertIn(commandId,Menus.TOOLBAR_LABELS)
        svgs=Icons.AllSvgs(Menus.CommandIds('qt'))
        ids=[]
        for commandId,svg in svgs.items():
            root=ET.fromstring(svg)
            self.assertEqual(root.get('viewBox'),'0 0 32 32')
            ids+=[e.get('id') for e in root.iter() if e.get('id')]
        # gradient ids must stay unique when every icon is inlined into one web page
        self.assertEqual(len(ids),len(set(ids)))

class TestThemesTest(unittest.TestCase):
    DARK_THEME='''{
        // a comment, a trailing comma and a URL that is not a comment
        "name": "Child Dark",
        "type": "dark",
        "include": "./base.json",
        "colors": {
            "editor.foreground": "#e0e0e0",
            "textLink.foreground": "#4daafc",
            "terminal.ansiBlue": "#6699ff", "terminal.ansiYellow": "#ffcc00",
            "terminal.ansiGreen": "#66cc66", "terminal.ansiRed": "#ff6666",
        },
        "$schema": "vscode://schemas/color-theme", /* block comment */
    }'''
    BASE_THEME='{"colors":{"editor.background":"#1a1b26","sideBar.background":"#16161e","editor.foreground":"#000000"}}'
    PACKAGE={'name':'test-themes','displayName':'%displayName%',
             'contributes':{'themes':[{'label':'Child Dark','uiTheme':'vs-dark','path':'./themes/child.json'},
                                      {'label':'Plain Light','uiTheme':'vs','path':'./themes/light.json'},
                                      {'label':'TextMate','uiTheme':'vs','path':'./themes/old.tmTheme'}]}}
    def setUp(self):
        from SignalIntegrity.GuiCore import Themes
        self.Themes=Themes
        self.directory=tempfile.mkdtemp()
        self.extension=os.path.join(self.directory,'extensions','publisher.test-themes-1.0.0')
        os.makedirs(os.path.join(self.extension,'themes'))
        self._Write('package.json',json.dumps(self.PACKAGE))
        self._Write('package.nls.json','{"displayName":"Test Themes"}')
        self._Write('themes/child.json',self.DARK_THEME)
        self._Write('themes/base.json',self.BASE_THEME)
        self._Write('themes/light.json','{"type":"light","colors":{"editor.background":"#fdf6e3"}}')
    def tearDown(self):
        shutil.rmtree(self.directory,ignore_errors=True)
    def _Write(self,name,text):
        with open(os.path.join(self.extension,*name.split('/')),'w') as f:
            f.write(text)
    def testJsonc(self):
        value=self.Themes.ParseJsonc('{"a":"http://x", // c\n"b":[1,2,],/* d */}')
        self.assertEqual(value,{'a':'http://x','b':[1,2]})
    def testDiscoverAndInclude(self):
        themes=self.Themes.DiscoverThemes([os.path.join(self.directory,'extensions')])
        self.assertEqual([t['id'] for t in themes[:2]],['builtin:light','builtin:dark'])
        labels={t['label']:t for t in themes[2:]}
        self.assertEqual(sorted(labels),['Child Dark','Plain Light'])
        self.assertEqual(labels['Child Dark']['extension'],'Test Themes')
        name,palette=self.Themes.LoadTheme(labels['Child Dark']['id'])
        self.assertEqual(name,'Child Dark')
        self.assertTrue(palette['dark'])
        self.assertEqual(palette['background'],'#1a1b26')   # from the included file
        self.assertEqual(palette['panel'],'#16161e')
        self.assertEqual(palette['foreground'],'#e0e0e0')   # the including file wins
        self.assertEqual(palette['traces'][:4],['#6699ff','#ffcc00','#66cc66','#ff6666'])
        name,palette=self.Themes.LoadTheme(labels['Plain Light']['id'])
        self.assertFalse(palette['dark'])
        self.assertEqual(palette['schematicBackground'],'#fdf6e3')
        self.assertEqual(name,'light')
    def testVsix(self):
        import zipfile
        vsix=os.path.join(self.directory,'test.vsix')
        with zipfile.ZipFile(vsix,'w') as z:
            for root,_,files in os.walk(self.extension):
                for f in files:
                    full=os.path.join(root,f)
                    z.write(full,'extension/'+os.path.relpath(full,self.extension).replace(os.sep,'/'))
        themes=self.Themes.ThemesInPackage(vsix)
        self.assertEqual([t['label'] for t in themes],['Child Dark','Plain Light'])
        self.assertEqual(self.Themes.LoadTheme(themes[0]['id'])[1]['background'],'#1a1b26')
        self.assertEqual(self.Themes.LoadTheme(vsix)[0],'Child Dark')
    def testErrors(self):
        with self.assertRaises(self.Themes.ThemeError):
            self.Themes.LoadTheme(os.path.join(self.directory,'missing.json'))
        self._Write('themes/loop.json','{"include":"./loop.json"}')
        with self.assertRaises(self.Themes.ThemeError):
            self.Themes.LoadTheme(os.path.join(self.extension,'themes','loop.json'))
    def testReadableSchematic(self):
        for themeId in self.Themes.BUILTIN:
            palette=self.Themes.LoadTheme(themeId)[1]
            colorMap=self.Themes.SchematicColorMap(palette)
            self.assertEqual(set(colorMap),{'black','blue','salmon','white'})
            ink=self.Themes._Rgb(colorMap['black'])[0]; paper=self.Themes._Rgb(colorMap['white'])[0]
            self.assertGreater(self.Themes._Contrast(ink,paper),7.)
        # a selection color that would vanish on the background is replaced
        palette=self.Themes.Palette({'type':'dark','colors':{'editor.background':'#000000','textLink.foreground':'#010101'}})
        self.assertGreaterEqual(self.Themes._Contrast(self.Themes._Rgb(palette['schematicSelected'])[0],(0,0,0)),3.)
    def testSavedTheme(self):
        from unittest import mock
        settings=os.path.join(self.directory,'settings','gui-theme.json')
        with mock.patch.object(self.Themes,'SettingsFile',return_value=settings):
            self.assertEqual(self.Themes.CurrentTheme()[0],'builtin:light')
            self.Themes.SaveThemeId('builtin:dark')
            self.assertEqual(self.Themes.CurrentTheme()[:2],('builtin:dark','SignalIntegrity Dark'))
            self.Themes.SaveThemeId(os.path.join(self.directory,'gone.json'))
            self.assertEqual(self.Themes.CurrentTheme()[0],'builtin:light')

if __name__ == '__main__':
    unittest.main()
