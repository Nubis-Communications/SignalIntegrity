"""
ScriptEditorDialog.py
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

import tkinter as tk
from tkinter import messagebox
import os

import SignalIntegrity.App.Project

class ScriptEditorDialog(object):
    """Modal editor for the script of a scripted source, reusing the EquationsDialog.

    Debug > Execute runs the edited script with the device's properties and project variables
    and plots the resulting output_waveform.  Auto debug runs the script as it is edited and
    reports errors in the status bar.  On close, the script is written back to the device and
    modified is set if it changed.
    """
    def __init__(self,parent,device,app):
        from SignalIntegrity.App.EquationsDialog import EquationsDialog
        self.device=device
        self.app=app
        self.modified=False
        self.originalScript=device['script']['Value'] or ''
        self.dialog=dialog=EquationsDialog(parent)
        dialog.withdraw()
        dialog.titleText='Script - '+str(device['ref'].GetValue())
        dialog.title(dialog.titleText)
        fileMenu=tk.Menu(dialog.TheMenu,tearoff=False)
        dialog.TheMenu.insert_cascade(0,label='File',menu=fileMenu,underline=0)
        fileMenu.add_command(label='Import...',command=self.onImport)
        fileMenu.add_command(label='Save As...',command=self.onSaveAs)
        dialog.TextArea.delete(1.0,tk.END)
        dialog.TextArea.insert(1.0,self.originalScript)
        dialog.TextArea.config(height=25)
        # the EquationsDialog handlers evaluate the text as project equations and assume the parent
        # is the main application, so they are replaced with ones that run the script for the device
        dialog.ExcuteDoer.command=self.onExecute
        dialog.ExitDoer.command=self.onExit
        dialog.onTouched=self.onTouched
        dialog.TextArea.bind('<Button-1>',self.onTouched)
        dialog.TextArea.bind('<Return>',self.onTouched)
        dialog.protocol('WM_DELETE_WINDOW',self.onExit)
        self.onTouched()
        dialog.transient(parent)
        dialog.deiconify()
        dialog.wait_visibility()
        dialog.grab_set()
        dialog.TextArea.focus_set()
        parent.wait_window(dialog)
        if parent is not app:
            try:
                parent.grab_set()
            except tk.TclError:
                pass

    def _InitialDirectory(self):
        fileparts=getattr(self.app,'fileparts',None)
        return fileparts.AbsoluteFilePath() if fileparts is not None else os.getcwd()

    def onImport(self):
        from SignalIntegrity.App.FilePicker import AskOpenFileName
        filename=AskOpenFileName(parent=self.dialog,
                                 filetypes=[('Python scripts','*.py'),('All files','*')],
                                 initialdir=self._InitialDirectory())
        if filename is None:
            return
        try:
            with open(filename,'r',encoding='utf-8-sig') as scriptFile:
                script=scriptFile.read()
        except OSError as error:
            messagebox.showerror('Import Script',str(error),parent=self.dialog)
            return
        self.dialog.TextArea.delete(1.0,tk.END)
        self.dialog.TextArea.insert(1.0,script)
        self.onTouched()
        self.dialog.TextArea.focus_set()

    def onSaveAs(self):
        from SignalIntegrity.App.FilePicker import AskSaveAsFilename
        reference=self.device['ref'].GetValue() or 'waveform_processor'
        filename=AskSaveAsFilename(parent=self.dialog,
                                   initialdir=self._InitialDirectory(),
                                   initialfile=str(reference)+'.py',
                                   defaultextension='.py',
                                   filetypes=[('Python scripts','*.py'),('All files','*')])
        if filename is None:
            return
        try:
            with open(filename,'w',encoding='utf-8',newline='') as scriptFile:
                scriptFile.write(self.dialog.TextString())
        except OSError as error:
            messagebox.showerror('Save Script As',str(error),parent=self.dialog)
            return
        self.dialog.statusbar.set('Script saved: '+filename)

    def Run(self):
        """runs the edited script, returning the waveform, or None after reporting the error"""
        import SignalIntegrity.Lib as si
        try:
            wf=self.device.ScriptedWaveform(self.dialog.TextString())
        except si.SignalIntegrityException as e:
            self.dialog.statusbar.set(e.message)
            return None
        self.dialog.statusbar.set('No Errors')
        return wf

    def onTouched(self,event=None,force=False):
        if force or SignalIntegrity.App.Project['Equations.AutoDebug']:
            self.Run()
        else:
            self.dialog.statusbar.set('')

    def onExecute(self):
        wf=self.Run()
        if wf is None:
            return
        from SignalIntegrity.App.DeviceProperties import ViewWaveform
        ViewWaveform(self.app,wf,str(self.device['ref'].GetValue()))
        if self.dialog.winfo_exists():
            self.dialog.grab_set()
            self.dialog.TextArea.focus_set()

    def onExit(self):
        script=self.dialog.TextString()
        if script != self.originalScript:
            self.device['script']['Value']=script
            self.modified=True
        self.dialog.grab_release()
        self.dialog.destroy()
