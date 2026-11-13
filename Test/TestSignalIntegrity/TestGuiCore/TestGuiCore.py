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
