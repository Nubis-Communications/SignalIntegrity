"""
TestSignalIntegrityAppHeadless.py
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
import math
from unittest.mock import patch

class TestSchematicPageLookups(unittest.TestCase):
    def setUp(self):
        import SignalIntegrity.App
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        from SignalIntegrity.App.ProjectFile import ProjectFile,SchematicPageConfiguration
        self.addCleanup(setattr,SignalIntegrity.App,'Project',SignalIntegrity.App.Project)
        self.addCleanup(setattr,SignalIntegrity.App,'Preferences',SignalIntegrity.App.Preferences)
        self.app=SignalIntegrityAppHeadless()
        self.project=ProjectFile()
        SignalIntegrity.App.Project=self.project
        self.project['Pages']=[SchematicPageConfiguration()]

    def resistor(self,name):
        import copy
        from SignalIntegrity.App.Device import DeviceList,DeviceResistor
        device=copy.deepcopy(next(device for device in DeviceList
                                 if isinstance(device,DeviceResistor) and device['ports'].GetValue()==1))
        device['ref']['Value']=name
        device.partPicture.current.SetOrigin((5,5))
        return device

    def test_equations_find_devices_on_other_pages_without_changing_active_page(self):
        from SignalIntegrity.App.ProjectFile import SchematicConfiguration
        drawings=self.project.PageDrawings()
        self.project.WritePageDevices(drawings[0],[self.resistor('R1')])
        self.project.WritePageDevices(drawings[1],[self.resistor('R2')])
        self.project['Equations'].PutTextString(
            "import SignalIntegrity.App.Project\n"
            "schematic=SignalIntegrity.App.Project['Drawing.Schematic']\n"
            "schematic.Device('R1').Property('r')['Value']='75'\n"
            "schematic.Device('R2').Property('r')['Value']='100'")
        for page in (0,1):
            with self.subTest(page=page):
                self.project.activePage=page
                self.assertIsNone(self.project.EvaluateEquations(force=True))
                self.assertTrue(self.project['Equations.Valid'])
                self.assertEqual(self.project.activePage,page)
                self.assertEqual(drawings[0]['Schematic'].Device('R1').Property('r')['Value'],'75')
                self.assertEqual(drawings[1]['Schematic'].Device('R2').Property('r')['Value'],'100')
                self.assertIsNone(self.project['Drawing.Schematic'].Device('missing'))
        self.assertIsNone(SchematicConfiguration().Device('R1'))

    def test_stimulus_attachment_is_page_local_on_shared_named_net(self):
        import copy
        from SignalIntegrity.App.Device import DeviceStim,DeviceNetName
        from SignalIntegrity.App.Schematic import Schematic
        resistor=self.resistor('R1')
        pin=resistor.PinCoordinates()[0]
        stim=DeviceStim()
        stim['ref']['Value']='M1'
        stimPin=next(coord for coord,partPin in zip(stim.PinCoordinates(),stim.partPicture.current.pinList)
                     if partPin['Number']==1)
        stim.partPicture.current.SetOrigin((pin[0]-stimPin[0],pin[1]-stimPin[1]))
        net=DeviceNetName()
        net['netname']['Value']='shared'
        netPin=net.PinCoordinates()[0]
        net.partPicture.current.SetOrigin((pin[0]-netPin[0],pin[1]-netPin[1]))
        drawings=self.project.PageDrawings()
        self.project.WritePageDevices(drawings[0],[resistor,stim,net])
        self.project.WritePageDevices(drawings[1],[self.resistor('R2'),copy.deepcopy(net)])
        schematic=Schematic()
        schematic.InitFromProject()
        for offset in (0,20):
            if offset:
                for device in schematic.CircuitPages()[1][0].deviceList:
                    x,y=device.partPicture.current.origin
                    device.partPicture.current.SetOrigin((x+offset,y))
            for page in (0,1):
                with self.subTest(offset=offset,page=page):
                    schematic.SelectPage(page)
                    lines=schematic.NetList().Text()
                    self.assertEqual([line for line in lines if line.startswith('stim ')],['stim m1 R1 1'])
                    self.assertTrue(any(line.startswith('connect ') and 'R1 1' in line and 'R2 1' in line
                                        for line in lines))
class TestSignalIntegrityAppHeadlessTest(unittest.TestCase):
    """tests of the headless (scripted) application calculations

    These use the example and test projects that ship with SignalIntegrity, with the frequency list
    made logarithmic, where needed, through the project arguments.
    """
    logarithmicFrequencies={'UnderlyingType':'Logarithmic',
                            'LogarithmicStartFrequency':1e6,
                            'LogarithmicEndFrequency':20e9,
                            'LogarithmicPointsPerDecade':20}
    virtualProbeProject='SignalIntegrity/App/Examples/VirtualProbingExample/VirtualProbeExample.si'
    networkAnalyzerModelProject='Test/TestSignalIntegrity/TestVNACalibrationObject/Load1.si'
    deembedProject='SignalIntegrity/App/Examples/DeembedCableFilter.si'

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.cwd=os.getcwd()
        self.path=os.path.dirname(os.path.realpath(__file__))
        self.root=os.path.abspath(os.path.join(self.path,'..','..','..'))
    def tearDown(self):
        os.chdir(self.cwd)
        unittest.TestCase.tearDown(self)

    def OpenProject(self,project,args={}):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        app=SignalIntegrityAppHeadless()
        filename=os.path.join(self.root,project)
        self.assertTrue(app.OpenProjectFile(filename,args),filename+' could not be opened')
        return app
    def Calculate(self,app,method,**kwargs):
        """performs a calculation, failing the test (rather than erroring) if the calculation raises"""
        try:
            return getattr(app,method)(**kwargs)
        except Exception as e:
            self.fail(method+str(kwargs)+' raised '+type(e).__name__+': '+str(e))
    def assertWaveformsFinite(self,result,message):
        for label,wf in zip(result['output waveform labels'],result['output waveforms']):
            self.assertTrue(len(wf) > 0 and all(math.isfinite(v) for v in wf.Values()),message+': '+label+' is not finite')

    def testHeadlessPictureIgnoresGuiTextSpacing(self):
        from SignalIntegrity.App.PartPicture import PartPicture
        from SignalIntegrity.App.TpX import TpX
        from SignalIntegrity.App.TikZ import TikZ
        for directory,name in (('TestSignalIntegrityApp','TestWaveformGood'),
                               ('TestSystemVariables','RelayTest1')):
            with self.subTest(project=name),patch.object(PartPicture,'textSpacing',14):
                path=os.path.join('Test','TestSignalIntegrity',directory,name)
                app=self.OpenProject(path+'.si')
                picture=app.Drawing.DrawSchematic(TpX()).Finish().lineList
                picture+=app.Drawing.DrawSchematic(TikZ()).Finish().lineList
                with open(os.path.join(self.root,path+'.TpX')) as reference:
                    self.assertEqual(picture,reference.readlines())

    def testVirtualProbeEyeDiagrams(self):
        """VirtualProbe with EyeDiagrams=True calculates the eye diagrams of the eye probes that are on"""
        result=self.Calculate(self.OpenProject(self.virtualProbeProject),'VirtualProbe',EyeDiagrams=True)
        self.assertNotEqual(result,{},'virtual probe with eye diagrams produced nothing')
        self.assertEqual(result['type'],'virtual probe')
        self.assertEqual(result['eye diagram labels'],['Vout2'])
        eye=result.EyeDiagram('Vout2')
        self.assertIsNotNone(eye.Image(),'eye diagram has no image')
        # measurements are calculated only when they are enabled for the eye probe
        app=self.OpenProject(self.virtualProbeProject)
        if app.Device('Vout2').configuration['Measure.Measure']:
            self.assertTrue(isinstance(eye.Measurements(),dict) and len(eye.Measurements()) > 0,'eye diagram has no measurements')
        else:
            self.assertIsNone(eye.Measurements(),'eye diagram has measurements that are not enabled')
        # calculating the eye diagrams does not change the waveforms
        withoutEyes=self.OpenProject(self.virtualProbeProject).VirtualProbe()
        self.assertEqual(result['output waveform labels'],withoutEyes['output waveform labels'])
        for wf,reference in zip(result['output waveforms'],withoutEyes['output waveforms']):
            self.assertEqual(wf,reference,'calculating eye diagrams changed the waveforms')

    def testVirtualProbeLogarithmicFrequencies(self):
        """VirtualProbe resamples the transfer matrices when the frequency list is not evenly spaced"""
        result=self.Calculate(self.OpenProject(self.virtualProbeProject,self.logarithmicFrequencies),'VirtualProbe')
        self.assertNotEqual(result,{},'virtual probe with logarithmic frequencies produced nothing')
        linear=self.OpenProject(self.virtualProbeProject).VirtualProbe()
        self.assertEqual(result['output waveform labels'],linear['output waveform labels'])
        self.assertWaveformsFinite(result,'virtual probe with logarithmic frequencies')

    def testSimulateLogarithmicFrequencies(self):
        """Simulate already handles a frequency list that is not evenly spaced - the behavior that
        VirtualProbe and SimulateNetworkAnalyzerModel must match"""
        result=self.Calculate(self.OpenProject('SignalIntegrity/App/Examples/RC.si',self.logarithmicFrequencies),'Simulate')
        self.assertNotEqual(result,{},'simulation with logarithmic frequencies produced nothing')
        self.assertWaveformsFinite(result,'simulation with logarithmic frequencies')

    def testNetworkAnalyzerModelWithoutDrawing(self):
        """SimulateNetworkAnalyzerModel draws the schematic (running the equations) if it has not been drawn,
        like every other calculation

        The network analyzer model's waveforms differ from run to run, so the results are compared with
        those calculated after drawing the schematic in their structure, not their values."""
        for sParameters in [False,True]:
            result=self.Calculate(self.OpenProject(self.networkAnalyzerModelProject),'SimulateNetworkAnalyzerModel',SParameters=sParameters)
            self.assertNotEqual(result,{},'network analyzer model (SParameters='+str(sParameters)+') produced nothing without drawing first')
            drawn=self.OpenProject(self.networkAnalyzerModelProject)
            drawn.Drawing.DrawSchematic()
            reference=drawn.SimulateNetworkAnalyzerModel(SParameters=sParameters)
            if sParameters:
                sp=result['s-parameters']; spReference=reference['s-parameters']
                self.assertEqual(sp.m_P,spReference.m_P,'number of ports differs from that calculated after drawing')
                self.assertEqual(list(sp.f()),list(spReference.f()),'frequencies differ from those calculated after drawing')
            else:
                self.assertEqual(result['output waveform labels'],reference['output waveform labels'])
                for wf,ref in zip(result['output waveforms'],reference['output waveforms']):
                    self.assertEqual(wf.td,ref.td,'waveform time descriptors differ from those calculated after drawing')

    def testNetworkAnalyzerModelLogarithmicFrequencies(self):
        """SimulateNetworkAnalyzerModel resamples the transfer matrices when the frequency list is not evenly spaced"""
        for sParameters in [False,True]:
            app=self.OpenProject(self.networkAnalyzerModelProject,self.logarithmicFrequencies)
            app.Drawing.DrawSchematic()
            result=self.Calculate(app,'SimulateNetworkAnalyzerModel',SParameters=sParameters)
            self.assertNotEqual(result,{},'network analyzer model (SParameters='+str(sParameters)+') with logarithmic frequencies produced nothing')
            if sParameters:
                sp=result['s-parameters']
                self.assertTrue(all(math.isfinite(abs(sp[n][r][c])) for n in range(len(sp)) for r in range(sp.m_P) for c in range(sp.m_P)),
                                'network analyzer model s-parameters with logarithmic frequencies are not finite')
            else:
                self.assertWaveformsFinite(result,'network analyzer model with logarithmic frequencies')

    def testDeembedFileNames(self):
        """Deembed returns the file names that SignalIntegrityApp saves the de-embedded s-parameters to"""
        result=self.Calculate(self.OpenProject(self.deembedProject),'Deembed')
        self.assertNotEqual(result,{},'de-embedding produced nothing')
        self.assertEqual(result['unknown names'],['Filter'])
        self.assertIn('file names',result,'de-embedding result has no file names')
        self.assertEqual(result['file names'],['DeembedCableFilter_Filter.s'+str(result['s-parameters'][0].m_P)+'p'])

if __name__ == '__main__':
    unittest.main()
