"""
TestGuiCore.py
"""
# Copyright (c) 2026 Nubis Communications, Inc.
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
        json.dumps(result)
        app=SignalIntegrityAppHeadless()
        app.OpenProjectFile(filename)
        reference=app.Simulate()
        labels=reference['output waveform labels']
        self.assertEqual([wf['name'] for wf in result['waveforms']][:len(labels)],labels)
        for wf,ref in zip(result['waveforms'],reference['output waveforms']):
            self.assertEqual(len(wf['y']),len(ref))
            for a,b in zip(wf['y'],ref.Values()):
                self.assertAlmostEqual(a,b,12)
    def testSParameters(self):
        self.session.Open(os.path.join(EXAMPLES,'RLCTest2SP.si'))
        result=self.session.Calculate('sparameters')
        sp=result['sparameters'][0]
        self.assertEqual(len(sp['traces']),sp['ports']**2)
        self.assertEqual(len(sp['traces'][0]['dB']),len(sp['frequencies']))
        json.dumps(result)
    def testDeembed(self):
        self.session.Open(os.path.join(EXAMPLES,'DeembedCableFilter.si'))
        result=self.session.Calculate('deembed')
        self.assertGreater(len(result['sparameters']),0)
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
        self.assertGreater(len(self.session.Calculate('sparameters',lambda progress: True)['sparameters']),0)
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

if __name__ == '__main__':
    unittest.main()
