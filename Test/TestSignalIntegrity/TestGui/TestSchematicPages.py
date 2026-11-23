"""Tests for schematic page import and export."""

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

import copy
import os
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


class TestSchematicPages(unittest.TestCase):
    def setUp(self):
        try:
            root=tk.Tk()
        except tk.TclError:
            if os.environ.get('SIGNALINTEGRITY_REQUIRE_GUI_TESTS') == '1':
                raise
            self.skipTest('No Tk display available')
        root.update_idletasks()
        root.destroy()
        import SignalIntegrity.App
        from SignalIntegrity.App.SignalIntegrityApp import SignalIntegrityApp
        self.previousProject=SignalIntegrity.App.Project
        self.previousPreferences=SignalIntegrity.App.Preferences
        self.cwd=os.getcwd()
        self.directory=tempfile.TemporaryDirectory()
        self.addCleanup(self.cleanup)
        self.app=SignalIntegrityApp('',runMainLoop=False)
        options=patch.object(self.app,'SelectPageImportOptions',return_value=(False,False))
        self.options=options.start()
        self.addCleanup(options.stop)
        self.sourceDir=Path(self.directory.name)/'source'
        self.targetDir=Path(self.directory.name)/'target'
        self.sourceDir.mkdir()
        self.targetDir.mkdir()
        self.makeProjects()

    def cleanup(self):
        import SignalIntegrity.App
        if hasattr(self,'app'):
            self.app.root.destroy()
        os.chdir(self.cwd)
        self.directory.cleanup()
        SignalIntegrity.App.Project=self.previousProject
        SignalIntegrity.App.Preferences=self.previousPreferences

    def makeProjects(self):
        from SignalIntegrity.App.Device import DeviceList,DeviceResistor,DeviceFile,Port
        from SignalIntegrity.App.ProjectFile import ProjectFile,SchematicPageConfiguration,VariableConfiguration
        from SignalIntegrity.App.ProjectFileBase import ProjectFileBase
        from SignalIntegrity.App.Wire import Vertex,Wire

        resistor=copy.deepcopy(next(device for device in DeviceList
                                     if isinstance(device,DeviceResistor) and device['ports'].GetValue()==1))
        resistor['ref']['Value']='R1'
        resistor.partPicture.current.SetOrigin((6,7))
        fileDevice=copy.deepcopy(next(device for device in DeviceList if isinstance(device,DeviceFile)))
        fileDevice['ref']['Value']='D1'
        fileDevice['file']['Value']='channel.s2p'
        fileDevice.partPicture.current.SetOrigin((12,7))
        source=ProjectFile()
        source.WritePageDevices(source.PageDrawings()[0],[resistor,Port(1),fileDevice])
        source['Drawing.Schematic.Wires']=[Wire([Vertex((6,7)),Vertex((9,7))])]
        variable=VariableConfiguration()
        variable['Name']='newvar'
        variable['Value']='3'
        fileVariable=VariableConfiguration()
        fileVariable['Name']='sourcefile'
        fileVariable['Type']='file'
        fileVariable['Value']='other.s2p'
        source['Variables.Items']=[variable,fileVariable]
        source['Equations'].PutTextString('newvar=3')
        page=SchematicPageConfiguration()
        page['Name']='Not imported'
        source['Pages']=[page]
        self.source=str(self.sourceDir/'source.si')
        ProjectFileBase.Write(source,self.source)

        target=ProjectFile()
        target.WritePageDevices(target.PageDrawings()[0],[resistor,Port(1)])
        variable=VariableConfiguration()
        variable['Name']='x'
        variable['Value']='2'
        fileVariable=VariableConfiguration()
        fileVariable['Name']='channel'
        fileVariable['Type']='file'
        fileVariable['Value']='shared.s2p'
        target['Variables.Items']=[variable,fileVariable]
        target['Equations'].PutTextString('x=2')
        self.target=str(self.targetDir/'target.si')
        ProjectFileBase.Write(target,self.target)
        self.app.OpenProjectFile(self.target,showError=False,readOnly=False)
        self.app.root.update()
        self.assertEqual(self.app.fileparts.filename,'target')

    def addPage(self):
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskOpenFileName',return_value=self.source), \
             patch('tkinter.simpledialog.askstring',return_value='Imported'):
            self.app.onAddSchematicPageFromProject()

    def test_add_and_save_page_project(self):
        import SignalIntegrity.App
        from SignalIntegrity.App.ProjectFile import ProjectFile

        self.addPage()
        project=SignalIntegrity.App.Project
        self.assertEqual(project.PageNames(),['Main','Imported'])
        devices=self.app.Drawing.schematic.deviceList
        self.assertEqual([device['ref'].GetValue() for device in devices if device['ref'] is not None],
                         ['R2','D1'])
        self.assertEqual(devices[1]['pn'].GetValue(),2)
        self.assertEqual(os.path.normcase(os.path.abspath(os.path.join(self.targetDir,devices[2]['file']['Value']))),
                         os.path.normcase(str(self.sourceDir/'channel.s2p')))
        vertices=[vertex['Coord'] for wire in project['Drawing.Schematic.Wires'] for vertex in wire['Vertices']]
        self.assertIn((6,7),vertices)
        self.assertIn((9,7),vertices)

        # The inactive page can contain unsaved live edits.
        original=self.app.Drawing.schematic.CircuitPages()[0][0].deviceList[0]
        original['r']['Value']='75'
        output=str(self.sourceDir/'export.si')
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskSaveAsFilename',return_value=output):
            self.app.onSaveSchematicPage(0)
        exported=ProjectFile().Read(output)
        self.assertEqual(exported.PageNames(),['Main'])
        self.assertEqual(exported['Variables.Items'][0]['Name'],'x')
        self.assertEqual(exported['Equations'].GetTextString(),'x=2')
        value=exported['Variables.Items'][1]['Value']
        self.assertEqual(os.path.normcase(os.path.abspath(os.path.join(self.sourceDir,value))),
                         os.path.normcase(str(self.targetDir/'shared.s2p')))
        props=exported['Drawing.Schematic.Devices'][0]['PartProperties']
        self.assertEqual(next(prop['Value'] for prop in props if prop['Keyword']=='r'),'75')
        self.assertEqual(project.PageNames(),['Main','Imported'])
        output=str(self.targetDir/'export-imported.si')
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskSaveAsFilename',return_value=output):
            self.app.onSaveSchematicPage(1)
        exported=ProjectFile().Read(output)
        props=exported['Drawing.Schematic.Devices'][2]['PartProperties']
        filename=next(prop['Value'] for prop in props if prop['Keyword']=='file')
        self.assertEqual(os.path.normcase(os.path.abspath(os.path.join(self.targetDir,filename))),
                         os.path.normcase(str(self.sourceDir/'channel.s2p')))
        self.app.history.Undo()
        self.assertEqual(project.PageNames(),['Main'])
        self.app.history.Redo()
        self.assertEqual(project.PageNames(),['Main','Imported'])

    def test_import_uses_clipboard_and_can_undo_placement(self):
        import SignalIntegrity.App
        self.addPage()
        project=SignalIntegrity.App.Project
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskOpenFileName',return_value=self.source):
            self.app.onImportSchematicPage(0)
        drawing=self.app.Drawing
        self.assertEqual(project.activePage,0)
        self.assertEqual(drawing.stateMachine.state,'MultipleItemsOnClipboard')
        self.assertEqual(len(drawing.schematic.deviceList),2)
        self.assertEqual(len(drawing.wiresToDuplicate),1)
        drawing.stateMachine.onMouseButton1_MultipleItemsOnClipboard(SimpleNamespace(x=400,y=300))
        self.assertEqual(len(drawing.schematic.deviceList),5)
        self.assertEqual(drawing.schematic.deviceList[2]['ref'].GetValue(),'R3')
        self.assertEqual(drawing.schematic.deviceList[3]['pn'].GetValue(),3)
        self.assertEqual(len(project['Drawing.Schematic.Wires']),1)
        self.app.history.Undo()
        self.assertEqual(len(drawing.schematic.deviceList),2)
        self.assertEqual(len(project['Drawing.Schematic.Wires']),0)

    def test_cancel_and_invalid_project_do_not_change_pages(self):
        import SignalIntegrity.App
        project=SignalIntegrity.App.Project
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskOpenFileName',return_value=None):
            self.app.onAddSchematicPageFromProject()
        bad=str(self.sourceDir/'invalid.si')
        Path(bad).write_text('<NotProject/>',encoding='utf-8')
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskOpenFileName',return_value=bad), \
             patch('SignalIntegrity.App.SignalIntegrityApp.messagebox.showerror') as error:
            self.app.onImportSchematicPage(0)
        error.assert_called_once()
        self.assertEqual(project.PageNames(),['Main'])

    def test_import_into_empty_page_undoes_all_items(self):
        import SignalIntegrity.App
        self.app.Drawing.schematic.deviceList=[]
        self.app.history.Event('clear page')
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskOpenFileName',return_value=self.source):
            self.app.onImportSchematicPage(0)
        drawing=self.app.Drawing
        drawing.stateMachine.onMouseButton1_MultipleItemsOnClipboard(SimpleNamespace(x=400,y=300))
        self.assertEqual(len(drawing.schematic.deviceList),3)
        self.app.history.Undo()
        self.assertEqual(len(drawing.schematic.deviceList),0)
        self.assertEqual(len(SignalIntegrity.App.Project['Drawing.Schematic.Wires']),0)

    def test_import_renames_noise_probe_reference(self):
        from SignalIntegrity.App.Device import DeviceList,DeviceOutput,DeviceVoltageStatisticalNoiseSource
        probe=DeviceOutput()
        probe['ref']['Value']='VO1'
        self.app.Drawing.schematic.deviceList.append(copy.deepcopy(probe))
        noise=copy.deepcopy(next(device for device in DeviceList
                                 if isinstance(device,DeviceVoltageStatisticalNoiseSource)))
        noise.configuration['Crosstalk.ProbeName']='VO1'
        self.app.AssignImportedPageIdentifiers([probe,noise])
        self.assertNotEqual(probe['ref'].GetValue(),'VO1')
        self.assertEqual(noise.configuration['Crosstalk.ProbeName'],probe['ref'].GetValue())

    def test_tab_context_menu_requires_writable_project(self):
        self.app.root.update()
        self.app.UpdatePagesMenu()
        self.assertEqual([self.app.pagesMenu.entrycget(i,'label')
                          for i in range(self.app.pagesMenu.index('end')+1)],
                         ['Add Page','Add Page from Project...','Rename Page','Delete Page','Duplicate Page'])
        event=SimpleNamespace(widget=self.app.pageTabs,x=20,y=5,x_root=10,y_root=10)
        with patch.object(self.app.pageMenu,'tk_popup') as popup:
            self.app.onSchematicTabMenu(event)
            labels=[self.app.pageMenu.entrycget(i,'label')
                    for i in range(self.app.pageMenu.index('end')+1)]
            self.assertEqual(labels,['Rename Page','Delete Page','Duplicate Page',
                                     'Import Page from Project...','Save Page to Project...'])
            self.assertEqual([self.app.pageMenu.entrycget(i,'state') for i in range(len(labels))],
                             ['normal','disabled','normal','normal','normal'])
            self.app.SetReadOnly(True)
            popup.reset_mock()
            self.app.onSchematicTabMenu(event)
            empty=SimpleNamespace(widget=self.app.pageTabSpace,x=5,y=5,x_root=10,y_root=10)
            self.app.onSchematicTabMenu(empty)
            popup.assert_not_called()
            self.app.UpdatePagesMenu()
            self.assertTrue(all(self.app.pagesMenu.entrycget(i,'state')=='disabled'
                                for i in range(self.app.pagesMenu.index('end')+1)))
        output=str(self.sourceDir/'readonly.si')
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskSaveAsFilename',return_value=output) as picker:
            self.app.onSaveSchematicPage(0)
            picker.assert_not_called()
        self.assertFalse(Path(output).exists())

    def test_save_cannot_overwrite_current_project(self):
        before=Path(self.target).read_bytes()
        withoutExtension=str(Path(self.target).with_suffix(''))
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskSaveAsFilename',return_value=withoutExtension), \
             patch('SignalIntegrity.App.SignalIntegrityApp.messagebox.showerror') as error:
            self.app.onSaveSchematicPage(0)
        error.assert_called_once()
        self.assertEqual(Path(self.target).read_bytes(),before)

    def test_add_page_with_variables_and_equations_undoes_together(self):
        import SignalIntegrity.App
        self.options.return_value=(True,True)
        self.addPage()
        project=SignalIntegrity.App.Project
        self.assertEqual(project['Variables'].Names(),['x','channel','newvar','sourcefile'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2\nnewvar=3')
        value=project['Variables.Items'][-1]['Value']
        self.assertEqual(os.path.normcase(os.path.abspath(os.path.join(self.targetDir,value))),
                         os.path.normcase(str(self.sourceDir/'other.s2p')))
        self.app.history.Undo()
        self.assertEqual(project.PageNames(),['Main'])
        self.assertEqual(project['Variables'].Names(),['x','channel'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2')
        self.app.history.Redo()
        self.assertEqual(project.PageNames(),['Main','Imported'])
        self.assertEqual(project['Variables'].Names(),['x','channel','newvar','sourcefile'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2\nnewvar=3')

    def test_clipboard_import_applies_options_only_on_placement(self):
        import SignalIntegrity.App
        self.options.return_value=(True,True)
        project=SignalIntegrity.App.Project
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskOpenFileName',return_value=self.source):
            self.app.onImportSchematicPage(0)
        self.assertEqual(project['Variables'].Names(),['x','channel'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2')
        self.app.Drawing.stateMachine.onMouseButton1_MultipleItemsOnClipboard(SimpleNamespace(x=400,y=300))
        self.assertEqual(project['Variables'].Names(),['x','channel','newvar','sourcefile'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2\nnewvar=3')
        self.app.history.Undo()
        self.assertEqual(project['Variables'].Names(),['x','channel'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2')
        self.assertEqual(len(self.app.Drawing.schematic.deviceList),2)
        self.app.history.Redo()
        self.assertEqual(project['Variables'].Names(),['x','channel','newvar','sourcefile'])
        self.assertEqual(len(self.app.Drawing.schematic.deviceList),5)

    def test_clipboard_cancellation_discards_selected_project_data(self):
        import SignalIntegrity.App
        self.options.return_value=(True,True)
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskOpenFileName',return_value=self.source):
            self.app.onImportSchematicPage(0)
        self.app.Drawing.stateMachine.onEscapeKey_MultipleItemsOnClipboard(None)
        project=SignalIntegrity.App.Project
        self.assertIsNone(self.app.Drawing.pendingPageImport)
        self.assertEqual(project['Variables'].Names(),['x','channel'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2')
        self.assertEqual(len(self.app.Drawing.schematic.deviceList),2)
        drawing=self.app.Drawing
        drawing.schematic.deviceList[0].selected=True
        drawing.Button1Coord=(0,0)
        drawing.stateMachine.MultipleSelections()
        drawing.DuplicateMultipleSelections()
        drawing.stateMachine.onMouseButton1_MultipleItemsOnClipboard(SimpleNamespace(x=400,y=300))
        self.assertEqual(len(drawing.schematic.deviceList),3)
        self.assertEqual(project['Variables'].Names(),['x','channel'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2')

    def test_duplicate_variable_aborts_before_page_or_script_changes(self):
        import SignalIntegrity.App
        from SignalIntegrity.App.ProjectFile import ProjectFile
        from SignalIntegrity.App.ProjectFileBase import ProjectFileBase
        source=ProjectFile().Read(self.source)
        source['Variables.Items'][0]['Name']='x'
        ProjectFileBase.Write(source,self.source)
        self.options.return_value=(True,True)
        project=SignalIntegrity.App.Project
        with patch('SignalIntegrity.App.SignalIntegrityApp.messagebox.showerror') as error:
            self.addPage()
        error.assert_called_once()
        self.assertIn('x',error.call_args.args[1])
        self.assertEqual(project.PageNames(),['Main'])
        self.assertEqual(project['Variables'].Names(),['x','channel'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2')
        with patch('SignalIntegrity.App.SignalIntegrityApp.messagebox.showerror') as error, \
             patch('SignalIntegrity.App.SignalIntegrityApp.AskOpenFileName',return_value=self.source):
            self.app.onImportSchematicPage(0)
        error.assert_called_once()
        self.assertNotEqual(self.app.Drawing.stateMachine.state,'MultipleItemsOnClipboard')

    def test_project_options_cancel_and_independent_choices(self):
        import SignalIntegrity.App
        project=SignalIntegrity.App.Project
        self.options.return_value=None
        self.addPage()
        self.assertEqual(project.PageNames(),['Main'])
        self.options.return_value=(False,True)
        self.addPage()
        self.assertEqual(project['Variables'].Names(),['x','channel'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2\nnewvar=3')

    def test_import_only_variables_does_not_append_equations(self):
        import SignalIntegrity.App
        self.options.return_value=(True,False)
        self.addPage()
        project=SignalIntegrity.App.Project
        self.assertEqual(project['Variables'].Names(),['x','channel','newvar','sourcefile'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2')

    def test_duplicate_added_before_placement_aborts_without_partial_import(self):
        import SignalIntegrity.App
        from SignalIntegrity.App.ProjectFile import VariableConfiguration
        self.options.return_value=(True,True)
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskOpenFileName',return_value=self.source):
            self.app.onImportSchematicPage(0)
        project=SignalIntegrity.App.Project
        variable=VariableConfiguration()
        variable['Name']='newvar'
        variable['Value']='1'
        project['Variables.Items']=project['Variables.Items']+[variable]
        with patch('SignalIntegrity.App.SignalIntegrityApp.messagebox.showerror') as error:
            self.app.Drawing.stateMachine.onMouseButton1_MultipleItemsOnClipboard(SimpleNamespace(x=400,y=300))
        error.assert_called_once()
        self.assertEqual(project['Variables'].Names(),['x','channel','newvar'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2')
        self.assertEqual(len(self.app.Drawing.schematic.deviceList),2)
        self.assertIsNone(self.app.Drawing.pendingPageImport)
        self.assertNotEqual(self.app.Drawing.stateMachine.state,'MultipleItemsOnClipboard')

    def test_import_options_follow_clipboard_when_switching_pages(self):
        import SignalIntegrity.App
        self.addPage()
        self.options.return_value=(True,True)
        with patch('SignalIntegrity.App.SignalIntegrityApp.AskOpenFileName',return_value=self.source):
            self.app.onImportSchematicPage(0)
        self.app.ShowSchematicPage(1)
        project=SignalIntegrity.App.Project
        self.assertEqual(self.app.Drawing.stateMachine.state,'MultipleItemsOnClipboard')
        self.assertEqual(project['Variables'].Names(),['x','channel'])
        self.app.Drawing.stateMachine.onMouseButton1_MultipleItemsOnClipboard(SimpleNamespace(x=400,y=300))
        self.assertEqual(project['Variables'].Names(),['x','channel','newvar','sourcefile'])
        self.assertEqual(project['Equations'].GetTextString(),'x=2\nnewvar=3')
        self.assertEqual(len(self.app.Drawing.schematic.deviceList),6)

    def test_undo_restores_empty_variables_and_equations(self):
        import SignalIntegrity.App
        project=SignalIntegrity.App.Project
        project['Variables.Items']=[]
        project['Equations'].PutTextString('')
        self.app.history.Event('clear settings')
        self.options.return_value=(True,True)
        self.addPage()
        self.app.history.Undo()
        self.assertEqual(project['Variables'].Names(),[])
        self.assertEqual(project['Equations'].GetTextString(),'')
        self.app.history.Redo()
        self.assertEqual(project['Variables'].Names(),['newvar','sourcefile'])
        self.assertEqual(project['Equations'].GetTextString(),'newvar=3')

    def test_import_options_dialog_checkboxes_and_cancel(self):
        from tkinter import ttk
        from SignalIntegrity.App.SignalIntegrityApp import PageImportOptionsDialog

        def findDialog():
            return next(child for child in self.app.root.winfo_children()
                        if isinstance(child,PageImportOptionsDialog))

        def selectBoth():
            dialog=findDialog()
            self.assertFalse(dialog.importVariables.get())
            self.assertFalse(dialog.importEquations.get())
            checkboxes=[child for frame in dialog.winfo_children() for child in frame.winfo_children()
                        if isinstance(child,ttk.Checkbutton)]
            self.assertEqual(len(checkboxes),2)
            for checkbox in checkboxes:
                checkbox.invoke()
            dialog.ok()

        self.app.root.after(50,selectBoth)
        result=PageImportOptionsDialog(self.app.root,title='Import Page').result
        self.assertEqual(result,(True,True))
        self.app.root.after(50,lambda:findDialog().cancel())
        self.assertIsNone(PageImportOptionsDialog(self.app.root,title='Import Page').result)

