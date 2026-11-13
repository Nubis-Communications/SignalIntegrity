"""
TestEquationsDialog.py
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

import sys
import os
import tkinter as tk
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import SignalIntegrity.App
from SignalIntegrity.App.EquationsDialog import EquationsDialog
from SignalIntegrity.App.ScriptEditorDialog import ScriptEditorDialog
from SignalIntegrity.App.ProjectFile import EquationsConfiguration
from SignalIntegrity.App.MenuSystemHelpers import StatusBar


class TestEquationsDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.root=tk.Tk()
        except tk.TclError as error:
            if os.environ.get('SIGNALINTEGRITY_REQUIRE_GUI_TESTS') == '1':
                raise
            raise unittest.SkipTest('Tk display unavailable: '+str(error))
        cls.root.withdraw()
        cls.addClassCleanup(cls.root.destroy)
        cls.addClassCleanup(cls.root.update_idletasks)

    def testLinuxStatusHeightSurvivesResizeAndScriptEditorHeight(self):
        equations=EquationsConfiguration()
        equations.PutTextString('x=1')
        project={'Equations.AutoDebug':False,'Equations':equations}
        with patch.object(SignalIntegrity.App,'Project',project),patch.object(sys,'platform','linux'),patch.dict(
                sys.modules,{'chlorophyll':SimpleNamespace(CodeView=tk.Text)}):
            for scale in (1.0,2.0):
                with self.subTest(scale=scale):
                    self.root.displayScale=scale
                    self.root.tk.call('tk','scaling',(96.0/72.0)*scale)
                    editor=EquationsDialog(self.root)
                    try:
                        statusHeight=editor.statusbar.winfo_reqheight()
                        self.assertGreaterEqual(statusHeight,round(24*scale))
                        for textHeight in (1,25):
                            editor.TextArea.configure(height=textHeight)
                            for height in (400,120):
                                editor.geometry('600x'+str(height))
                                editor.update()
                                self.assertTrue(editor.statusbar.winfo_ismapped())
                                self.assertEqual(editor.statusbar.winfo_height(),statusHeight)
                                self.assertGreaterEqual(
                                    editor.statusbar.label.winfo_height(),
                                    editor.statusbar.label.winfo_reqheight())
                                for message in ('','No Errors','Error: '+'long message '*40):
                                    editor.statusbar.set(message)
                                    self.assertEqual(editor.statusbar.winfo_height(),statusHeight)
                    finally:
                        editor.destroy()

    def testEditorStartsAtReadableSizeAndShowsMultilineErrors(self):
        equations=EquationsConfiguration()
        equations.PutTextString('x=1')
        project={'Equations.AutoDebug':False,'Equations':equations}
        with patch.object(SignalIntegrity.App,'Project',project),patch.dict(
                sys.modules,{'chlorophyll':SimpleNamespace(CodeView=tk.Text)}):
            self.root.displayScale=2.0
            self.root.tk.call('tk','scaling',(96.0/72.0)*2.0)
            for platform in ('linux','win32'):
                with self.subTest(platform=platform),patch.object(sys,'platform',platform):
                    editor=EquationsDialog(self.root)
                    try:
                        editor.update()
                        self.assertEqual(int(editor.TextArea.cget('width')),80)
                        self.assertEqual(int(editor.TextArea.cget('height')),25)
                        self.assertEqual(editor.winfo_width(),
                            min(editor.winfo_reqwidth(),round(editor.winfo_screenwidth()*0.9)))
                        self.assertEqual(editor.winfo_height(),
                            min(editor.winfo_reqheight(),round(editor.winfo_screenheight()*0.9)))
                        minimumHeight=editor.statusbar.winfo_height()
                        editor.statusbar.set('Traceback:\n  script line 1\n  invalid expression\nValueError: invalid value')
                        self.assertGreater(editor.statusbar.winfo_height(),minimumHeight)
                        self.assertGreaterEqual(
                            editor.statusbar.label.winfo_height(),
                            editor.statusbar.label.winfo_reqheight())
                        editor.statusbar.clear()
                        self.assertEqual(editor.statusbar.winfo_height(),minimumHeight)
                    finally:
                        editor.destroy()

    def testScriptEditorUsesReadableInitialSizeAndMultilineStatus(self):
        equations=EquationsConfiguration()
        project={'Equations.AutoDebug':False,'Equations':equations}
        device={'script':{'Value':'output_waveform = None'},'ref':SimpleNamespace(GetValue=lambda: 'X1')}

        def inspectDialog(dialog):
            dialog.update()
            self.assertEqual(dialog.TextString(),device['script']['Value'])
            self.assertEqual(int(dialog.TextArea.cget('height')),25)
            self.assertGreater(dialog.TextArea.winfo_height(),100)
            minimumHeight=dialog.statusbar.winfo_height()
            dialog.statusbar.set('Script failed:\nValueError: invalid value')
            self.assertGreater(dialog.statusbar.winfo_height(),minimumHeight)
            self.assertGreaterEqual(
                dialog.statusbar.label.winfo_height(),dialog.statusbar.label.winfo_reqheight())
            dialog.destroy()

        self.root.displayScale=2.0
        self.root.tk.call('tk','scaling',(96.0/72.0)*2.0)
        with patch.object(SignalIntegrity.App,'Project',project),patch.object(sys,'platform','linux'),patch.dict(
                sys.modules,{'chlorophyll':SimpleNamespace(CodeView=tk.Text)}),patch.object(
                self.root,'wait_window',side_effect=inspectDialog):
            ScriptEditorDialog(self.root,device,self.root)

    def testOrdinaryLinuxStatusBarsRemainFixedHeight(self):
        with patch.object(sys,'platform','linux'):
            status=StatusBar(self.root,displayScale=2.0)
            try:
                minimumHeight=status.winfo_reqheight()
                status.set('Line one\nLine two\nLine three')
                self.assertEqual(status.winfo_reqheight(),minimumHeight)
            finally:
                status.destroy()
