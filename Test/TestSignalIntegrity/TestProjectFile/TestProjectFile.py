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