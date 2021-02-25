"""
TestSignalIntegrityApp.py
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

from SignalIntegrity.App.PreferencesFile import PreferencesFile
from SignalIntegrity.App.Preferences import Preferences
from SignalIntegrity.App.ProjectFile import (
    ProjectFile, SchematicPageConfiguration, VariableConfiguration,
)
from SignalIntegrity.App.ProjectFileBase import ProjectFileBase

class TestProjectFileTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)

    def setUp(self):
        self.cwd=os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))


    def tearDown(self):
        if os.path.exists('preferencesOldStyle.xml'):
            os.remove('preferencesOldStyle.xml')
        os.chdir(self.cwd)


    def testProjectFileOldSurvival(self):
        pf=Preferences('preferencesOldStyle.si')
        pf.SaveToFile()

class TestProjectModel(unittest.TestCase):
    def make_directory(self):
        import shutil
        import uuid
        directory=os.path.abspath('project-model-'+uuid.uuid4().hex)
        os.mkdir(directory)
        self.addCleanup(shutil.rmtree,directory)
        return directory

    def file_device(self,filename,kind='SParameterFile',subproject=None):
        from SignalIntegrity.App.Device import DeviceFile
        from SignalIntegrity.App.PartProperty import PartPropertyPorts
        from SignalIntegrity.App.PartPicture import PartPictureVariableSpecifiedPorts
        device=DeviceFile([PartPropertyPorts(2)],PartPictureVariableSpecifiedPorts(2))
        device['file']['Value']=filename
        device['filetype']['Value']=kind
        device['subproject']['Value']=subproject
        return device

    def app_with_pages(self,device_lists,source):
        from types import SimpleNamespace
        from SignalIntegrity.App.Files import FileParts
        pages=[(SimpleNamespace(deviceList=devices),None) for devices in device_lists]
        schematic=SimpleNamespace(CircuitPages=lambda: pages)
        return SimpleNamespace(Drawing=SimpleNamespace(schematic=schematic),fileparts=FileParts(source))

    def test_select_filename_and_snapshot(self):
        directory=self.make_directory()
        source=os.path.join(directory,'source.si')
        saved=os.path.join(directory,'saved.si')
        project=ProjectFile().New()
        page=SchematicPageConfiguration()
        page['Name']='More'
        project['Pages']=[page]
        project.AddProject('Other')
        project.Write(None,source)
        project=ProjectFile().Read(source)
        self.assertEqual(project['FileName'],source)
        self.assertIs(project.Select('Other'),project)
        project['CalculationProperties.ReferenceImpedance']=75
        self.assertIsNone(project.Select('Missing'))
        self.assertEqual(project['Selected'],1)
        self.assertIs(project.Select(None),project)
        project.Select('Main')
        device=self.file_device('live.s2p')
        app=self.app_with_pages([[],[device]],source)
        snapshot=project.SnapshotLines(app)
        self.assertNotIn('<FileName>',''.join(snapshot))
        project.Write(None,saved)
        project.Select('Other')
        project.FromText(snapshot)
        self.assertEqual(project['FileName'],saved)
        self.assertEqual(project['Selected'],0)
        self.assertEqual(project['Pages'][0]['Drawing.Schematic.Devices'][0].Property('file')['Value'],'live.s2p')
        project.Select('Other')
        self.assertEqual(project['CalculationProperties.ReferenceImpedance'],75)

    def test_infer_legacy_file_properties_without_changing_serialization(self):
        project=ProjectFile().New()
        device=self.file_device('network.si')
        ProjectFile.WritePageDevices(project.PageDrawings()[0],[device])
        config=project['Drawing.Schematic.Devices'][0]
        config['PartProperties']=[p for p in config['PartProperties'] if p['Keyword'] not in ('filetype','subproject')]
        lines=project.LinesToWrite()
        restored=ProjectFile().FromText(lines)
        config=restored['Drawing.Schematic.Devices'][0]
        self.assertEqual(config.Property('filetype')['Value'],'SelectedProjectFile')
        self.assertIsNotNone(config.Property('subproject'))
        self.assertEqual(restored.LinesToWrite(),lines)
        config.Property('file')['Value']='network.s2p'
        config['PartProperties']=[p for p in config['PartProperties'] if p['Keyword'] != 'filetype']
        restored._inferFileTypes()
        self.assertEqual(config.Property('filetype')['Value'],'SParameterFile')
        self.assertEqual(len([p for p in config['PartProperties'] if p['Keyword']=='subproject']),1)

    def test_export_full_project_rebases_all_pages_and_live_edits(self):
        directory=self.make_directory()
        destination=os.path.join(directory,'exports')
        os.mkdir(destination)
        source=os.path.join(directory,'source.si')
        output=os.path.join(destination,'selected.si')
        project=ProjectFile().New()
        project.AddProject('Other')
        project.SelectProject(1)
        page=SchematicPageConfiguration()
        page['Name']='Second'
        project['Pages']=[page]
        project.activePage=1
        project['CalculationProperties.ReferenceImpedance']=75
        project['Equations'].PutTextString('x = 2')
        variable=VariableConfiguration()
        variable['Name']='f'
        variable['Type']='file'
        variable['Value']='data/input.csv'
        project['Variables.Items']=[variable]
        project.Write(None,source)
        first=self.file_device('data/first.s2p')
        device_variable=VariableConfiguration()
        device_variable['Name']='devicefile'
        device_variable['Type']='file'
        device_variable['Value']='=f'
        first.variablesList=[device_variable]
        second=self.file_device('', 'TabInCurrent','Main')
        app=self.app_with_pages([[first],[second]],source)
        exported=project.WriteTab(app,1,output)
        restored=ProjectFile().Read(output)
        self.assertEqual(restored['Projects'][0]['Name'],'Other')
        self.assertEqual(restored.activePage,1)
        self.assertEqual(restored.PageNames(),['Main','Second'])
        self.assertEqual(restored['CalculationProperties.ReferenceImpedance'],75)
        self.assertEqual(restored['Equations'].GetTextString(),'x = 2')
        expected=os.path.relpath(os.path.join(directory,'data','input.csv'),destination).replace('\\','/')
        self.assertEqual(restored['Variables.Items'][0]['Value'],expected)
        devices=[d['Schematic.Devices'][0] for d in restored.PageDrawings()]
        expected=os.path.relpath(os.path.join(directory,'data','first.s2p'),destination).replace('\\','/')
        self.assertEqual(devices[0].Property('file')['Value'],expected)
        self.assertEqual(devices[0]['Variables.Items'][0]['Value'],'=f')
        self.assertEqual(devices[1].Property('filetype')['Value'],'ProjectFile')
        self.assertEqual(devices[1].Property('subproject')['Value'],'Main')
        self.assertEqual(os.path.normcase(os.path.normpath(devices[1].Property('file')['Value'])),os.path.normcase(source))
        self.assertEqual(project.PageDrawings()[0]['Schematic.Devices'][0].Property('file')['Value'],'data/first.s2p')
        self.assertEqual(exported.PageNames(),['Main','Second'])
        project.SelectProject(0)
        self.assertEqual(project['CalculationProperties.ReferenceImpedance'],50)
        current=self.file_device('unsaved.s2p')
        app=self.app_with_pages([[current]],source)
        project.WriteTab(app,1,os.path.join(destination,'other.si'))
        self.assertEqual(project['Drawing.Schematic.Devices'][0].Property('file')['Value'],'unsaved.s2p')

    def test_export_rejects_unsaved_or_overwritten_tab_reference(self):
        directory=self.make_directory()
        output=os.path.join(directory,'out.si')
        project=ProjectFile().New()
        device=self.file_device('','TabInCurrent','Main')
        ProjectFile.WritePageDevices(project.PageDrawings()[0],[device])
        with self.assertRaises(ValueError):
            project.WriteTab(None,0,output)
        project.Write(None,output)
        with self.assertRaises(ValueError):
            project.WriteTab(None,0,output)
        self.assertEqual(project['Drawing.Schematic.Devices'][0].Property('filetype')['Value'],'TabInCurrent')

    def test_headless_in_file_subproject(self):
        import copy
        import numpy as np
        import SignalIntegrity.App
        from SignalIntegrity.App.Device import DeviceFile,DeviceList,DeviceResistor,Port
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless

        def place(device):
            x,y=device.PinCoordinates()[0]
            ox,oy=device.partPicture.current.origin
            device.partPicture.current.SetOrigin((ox+4-x,oy+4-y))
            return device

        directory=self.make_directory()
        filename=os.path.join(directory,'source.si')
        export_directory=os.path.join(directory,'export')
        os.mkdir(export_directory)
        exported=os.path.join(export_directory,'main.si')
        previous=SignalIntegrity.App.Project
        cwd=os.getcwd()
        try:
            project=ProjectFile().New()
            index=project.AddProject('Termination')
            project.SelectProject(index)
            resistor=copy.deepcopy(next(device for device in DeviceList
                if isinstance(device,DeviceResistor) and device['ports'].GetValue()==1))
            project.WritePageDevices(project.PageDrawings()[0],[place(resistor),place(Port(1))])
            project.SelectProject(0)
            file_device=copy.deepcopy(next(device for device in DeviceList
                if isinstance(device,DeviceFile) and device['ports'].GetValue()==1))
            file_device['filetype']['Value']='TabInCurrent'
            file_device['subproject']['Value']='Termination'
            project.WritePageDevices(project.PageDrawings()[0],[place(file_device),place(Port(1))])
            project['CalculationProperties.FrequencyPoints']=8
            project.Write(None,filename)
            project.WriteTab(None,0,exported)
            app=SignalIntegrityAppHeadless()
            self.assertTrue(app.OpenProjectFile(filename))
            self.assertTrue(any('subproject Termination' in line for line in app.NetListText()))
            nested=app.CalculateSParameters()['s-parameters']
            self.assertTrue(app.OpenProjectFile(filename,subproject='Termination'))
            app.Drawing.DrawSchematic()
            direct=app.CalculateSParameters()['s-parameters'].Resample(nested.m_f)
            np.testing.assert_allclose(nested.m_d,direct.m_d)
            self.assertTrue(app.OpenProjectFile(exported))
            app.Drawing.DrawSchematic()
            exported_result=app.CalculateSParameters()['s-parameters']
            np.testing.assert_allclose(nested.m_d,exported_result.m_d)
        finally:
            os.chdir(cwd)
            SignalIntegrity.App.Project=previous

    def test_switch_and_round_trip_independent_projects(self):
        project=ProjectFile().New()
        project['Drawing.DrawingProperties.Originx']=11
        page=SchematicPageConfiguration()
        page['Name']='Second'
        page['Drawing.DrawingProperties.Originx']=12
        project['Pages']=[page]
        project.activePage=1
        project['Drawing.DrawingProperties.Originx']=13
        project['CalculationProperties.ReferenceImpedance']=75
        project['PostProcessing'].PutTextString('first')
        variable=VariableConfiguration()
        variable['Name']='x'
        variable['Value']='1'
        project['Variables.Items']=[variable]
        project['Equations'].PutTextString('x = 1')
        index=project.AddProject('Other',project)
        project.SelectProject(index)
        self.assertEqual(project.activePage,1)
        project['Drawing.DrawingProperties.Originx']=23
        project['Variables.Items'][0]['Value']='2'
        project['Equations'].PutTextString('x = 2')
        project['PostProcessing'].PutTextString('second')
        project['CalculationProperties.ReferenceImpedance']=25
        project.SelectProject(0)
        self.assertEqual(project.activePage,1)
        self.assertEqual(project['Drawing.DrawingProperties.Originx'],13)
        self.assertEqual(project['Variables.Items'][0]['Value'],'1')
        self.assertEqual(project['Equations'].GetTextString(),'x = 1')
        self.assertEqual(project['PostProcessing'].GetTextString(),'first')
        self.assertEqual(project['CalculationProperties.ReferenceImpedance'],75)
        self.assertEqual([d['DrawingProperties.Originx'] for d in project.PageDrawings()],[11,13])
        project.SelectProject(1)
        restored=ProjectFile().FromText(project.LinesToWrite())
        self.assertEqual(restored['Selected'],1)
        self.assertEqual(restored.activePage,1)
        self.assertEqual(restored['Drawing.DrawingProperties.Originx'],23)
        self.assertEqual(restored['Variables.Items'][0]['Value'],'2')
        self.assertEqual(restored['Equations'].GetTextString(),'x = 2')
        restored.SelectProject(0)
        self.assertEqual(restored.PageNames(),['Main','Second'])
        self.assertEqual(restored['Drawing.DrawingProperties.Originx'],13)

    def test_empty_independent_fields_and_undo(self):
        project=ProjectFile().New()
        variable=VariableConfiguration()
        variable['Name']='shared'
        project['Variables.Items']=[variable]
        project['Equations'].PutTextString('x = 1')
        project.AddProject('Empty')
        text=project.LinesToWrite()
        project.SelectProject(1)
        project.FromText(text)
        project.SelectProject(1)
        self.assertEqual(project['Variables.Items'],[])
        self.assertEqual(project['Equations'].GetTextString(),'')
        project.FromText(ProjectFile().LinesToWrite())
        self.assertEqual(len(project['Projects']),1)
        self.assertEqual(project['Variables.Items'],[])
        self.assertEqual(project.activePage,0)

    def test_legacy_embedded_projects(self):
        text='''<Project>
        <Variables><Items><Variable><Name>global</Name><Value>1</Value></Variable></Items></Variables>
        <Equations><Lines><EquationLine><Line>global = 1</Line></EquationLine></Lines></Equations>
        <Selected>1</Selected><Projects>
          <Project><Name>A</Name><Selected>1</Selected><Pages>
            <Page><Name>A1</Name><Drawing><DrawingProperties><Originx>11</Originx></DrawingProperties></Drawing></Page>
            <Page><Name>A2</Name><Drawing><DrawingProperties><Originx>12</Originx></DrawingProperties></Drawing></Page>
          </Pages></Project>
          <Project><Name>B</Name><Selected>0</Selected><Pages>
            <Page><Name>B1</Name><Drawing><DrawingProperties><Originx>21</Originx></DrawingProperties></Drawing></Page>
          </Pages></Project>
        </Projects></Project>'''
        project=ProjectFile().FromText(text)
        self.assertEqual(project['Selected'],1)
        self.assertEqual(project.PageNames(),['B1'])
        self.assertEqual(project['Drawing.DrawingProperties.Originx'],21)
        project['Variables.Items'][0]['Value']='2'
        project.SelectProject(0)
        self.assertEqual(project.PageNames(),['A1','A2'])
        self.assertEqual(project.activePage,1)
        self.assertEqual(project['Drawing.DrawingProperties.Originx'],12)
        self.assertEqual(project['Variables.Items'][0]['Value'],'1')
        self.assertEqual(project['Equations'].GetTextString(),'global = 1')
        restored=ProjectFile().FromText(project.LinesToWrite())
        self.assertEqual(restored.PageNames(),['A1','A2'])
        restored.SelectProject(1)
        self.assertEqual(restored['Variables.Items'][0]['Value'],'2')

    def test_single_file_compatibility_and_delete(self):
        import uuid
        filename='project-model-'+uuid.uuid4().hex+'.si'
        self.addCleanup(lambda: os.path.exists(filename) and os.remove(filename))
        project=ProjectFile().New()
        page=SchematicPageConfiguration()
        page['Name']='P2'
        project['Pages']=[page]
        project.activePage=1
        lines=project.LinesToWrite()
        self.assertEqual(lines[0],'<Project>\n')
        self.assertNotIn('<Projects>',''.join(lines))
        self.assertNotIn('Projects',project.ToDictionary())
        self.assertNotIn('Selected',project.ToDictionary())
        self.assertEqual(ProjectFileBase().LinesToWrite()[0],'<Project>\n')
        ProjectFileBase.Write(project,filename)
        restored=ProjectFile().Read(filename)
        self.assertEqual(restored.PageNames(),['Main','P2'])
        restored.activePage=1
        restored.FromText(lines)
        self.assertEqual(restored.activePage,1)
        restored.AddProject('B')
        self.assertIn('Projects',restored.ToDictionary())
        restored.SelectProject(1)
        restored.DeleteProject(0)
        self.assertEqual(restored['Selected'],0)
        self.assertEqual(restored['Projects'][0]['Name'],'B')
        with self.assertRaises(ValueError):
            restored.DeleteProject(0)

    def test_import_independence_and_invalid_migration(self):
        source=ProjectFile().New()
        source['Drawing.DrawingProperties.Originx']=42
        page=SchematicPageConfiguration()
        page['Name']='More'
        source['Pages']=[page]
        target=ProjectFile().New()
        index=target.ImportProject(source,name='Imported')
        target.SelectProject(index)
        target['Drawing.DrawingProperties.Originx']=99
        target['Pages'][0]['Name']='Changed'
        self.assertEqual(source['Drawing.DrawingProperties.Originx'],42)
        self.assertEqual(source.PageNames(),['Main','More'])
        before=target.LinesToWrite()
        with self.assertRaises(ValueError):
            target.FromText('<Project><Projects><Project><Name>Broken</Name></Project></Projects></Project>')
        self.assertEqual(target.LinesToWrite(),before)
        with self.assertRaises(IndexError):
            target.SelectProject(-1)
        self.assertEqual(target['Selected'],index)

    def test_extract_project_round_trip(self):
        source=ProjectFile().New()
        source['Drawing.DrawingProperties.Originx']=11
        index=source.AddProject('Other')
        source.SelectProject(index)
        source['Drawing.DrawingProperties.Originx']=21
        page=SchematicPageConfiguration()
        page['Name']='Second'
        page['Drawing.DrawingProperties.Originx']=22
        source['Pages']=[page]
        source.activePage=1
        source['CalculationProperties.ReferenceImpedance']=75
        source['PostProcessing'].PutTextString('post')
        variable=VariableConfiguration()
        variable['Name']='x'
        variable['Value']='2'
        source['Variables.Items']=[variable]
        source['Equations'].PutTextString('x = 2')
        source['ProjectProperties.ReadOnly']=True

        extracted=source.ExtractProject(index)
        self.assertEqual(len(extracted['Projects']),1)
        self.assertEqual(extracted['Selected'],0)
        self.assertEqual(extracted['Projects'][0]['Name'],'Other')
        self.assertEqual(extracted.activePage,1)
        self.assertEqual(extracted.PageNames(),['Main','Second'])
        self.assertEqual([d['DrawingProperties.Originx'] for d in extracted.PageDrawings()],[21,22])
        self.assertEqual(extracted['ProjectProperties.ReadOnly'],True)
        restored=ProjectFile().FromText(extracted.LinesToWrite())
        self.assertEqual(restored.activePage,1)
        self.assertEqual(restored.PageNames(),['Main','Second'])
        self.assertEqual(restored['CalculationProperties.ReferenceImpedance'],75)
        self.assertEqual(restored['PostProcessing'].GetTextString(),'post')
        self.assertEqual(restored['Variables.Items'][0]['Value'],'2')
        self.assertEqual(restored['Equations'].GetTextString(),'x = 2')
        extracted['Drawing.DrawingProperties.Originx']=99
        extracted['Variables.Items'][0]['Value']='3'
        self.assertEqual(source['Drawing.DrawingProperties.Originx'],22)
        self.assertEqual(source['Variables.Items'][0]['Value'],'2')
        source['Equations'].PutTextString('x = 4')
        self.assertEqual(extracted['Equations'].GetTextString(),'x = 2')
        self.assertEqual(source.ExtractProject(0)['Drawing.DrawingProperties.Originx'],11)
        with self.assertRaises(IndexError):
            source.ExtractProject(-1)
        with self.assertRaises(IndexError):
            source.ExtractProject(2)
        self.assertEqual(source['Selected'],index)

    def test_real_legacy_file_headless_round_trip(self):
        import copy
        fixture=os.path.join(os.path.dirname(__file__),'..','TestSystemVariables','RelayTest.si')
        project=ProjectFile().Read(fixture)
        self.assertGreater(len(project['Drawing.Schematic.Devices']),0)
        self.assertGreater(len(project['Drawing.Schematic.Wires']),0)
        self.assertGreater(len(project['Variables.Items']),0)
        lines=project.LinesToWrite()
        self.assertEqual(ProjectFile().FromText(lines).LinesToWrite(),lines)
        page=SchematicPageConfiguration()
        page['Name']='Copied'
        page.dict['Drawing']=copy.deepcopy(project.PageDrawings()[0])
        project['Pages']=[page]
        project.activePage=1
        project.MovePage(1,0)
        self.assertEqual(project.activePage,0)
        saved=project.LinesToWrite()
        restored=ProjectFile().FromText(saved)
        self.assertEqual(restored.PageNames(),['Copied','Main'])
        self.assertEqual(restored.LinesToWrite(),saved)
        self.assertTrue(all(len(drawing['Schematic.Wires']) > 0 for drawing in restored.PageDrawings()))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()