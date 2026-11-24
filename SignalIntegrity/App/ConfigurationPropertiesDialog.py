"""Visibility and variable bindings alongside the existing configuration controls."""

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

from SignalIntegrity.App import MessageBox as messagebox
from SignalIntegrity.App import CalculationPropertiesProject as controls
from SignalIntegrity.App.ConfigurationProperty import ConfigurationError, BrowseConfigurationFile, OfferConfigurationVariable
from SignalIntegrity.App.MenuSystemHelpers import ToolTip


def ConfigurationPropertiesDialog(configuration,parent):
    if configuration.name=='EyeDiagram':
        from SignalIntegrity.App.EyeDiagramPropertiesDialog import EyeDiagramPropertiesDialog
        dialog=EyeDiagramPropertiesDialog
    elif configuration.name=='CurrentNoise':
        from SignalIntegrity.App.CurrentStatisticalNoisePropertiesDialog import CurrentStatisticalNoisePropertiesDialog
        dialog=CurrentStatisticalNoisePropertiesDialog
    else:
        from SignalIntegrity.App.VoltageStatisticalNoisePropertiesDialog import VoltageStatisticalNoisePropertiesDialog
        dialog=VoltageStatisticalNoisePropertiesDialog
    return dialog(configuration,parent)


class ConfigurationDialog(controls.PropertiesDialog):
    def __init__(self,parent,project,top,title):
        controls.PropertiesDialog.__init__(self,parent,project,top,title)
        self.app=parent
        while self.app is not None and not hasattr(self.app,'Drawing'):
            self.app=getattr(self.app,'master',None)
        self.readOnly=self.app is not None and self.app.ReadOnly()
        self.preview=hasattr(parent,'UpdatePicture')
        self.rows={}
        self.browsing=False
        self.help=tk.Label(self,anchor='w',justify=tk.LEFT,wraplength=950)
        self.help.pack(side=tk.TOP,fill=tk.X,padx=6)
        self.error=tk.Label(self,anchor='w',justify=tk.LEFT,wraplength=950,fg='red')
        self.error.pack(side=tk.TOP,fill=tk.X,padx=6)
        self.protocol('WM_DELETE_WINDOW',self.Close)

    def FinishConfiguration(self):
        self.SaveToPreferencesButton.configure(command=self.SavePreferences,
                                               state='disabled' if self.readOnly else 'normal')
        tk.Label(self,text='=: bind to a system variable',
                 anchor='w').pack(side=tk.TOP,fill=tk.X,padx=6)
        tk.Button(self,text='Close',command=self.Close).pack(side=tk.BOTTOM,pady=3)
        self.RefreshConfiguration()
        controls.PropertiesDialog.Finish(self)

    def RefreshConfiguration(self):
        for row in self.rows.values():
            row.Refresh()

        def arrange(frame):
            containsRows=False
            activeRows=False
            for child in frame.winfo_children():
                if isinstance(child,ConfigurationProperty):
                    containsRows=True
                    activeRows=child.shown or activeRows
                elif isinstance(child,(tk.Frame,tk.LabelFrame)):
                    contains,active=arrange(child)
                    if not hasattr(child,'configurationPack'):
                        child.configurationPack=(child.pack_info() if child.winfo_manager()=='pack'
                                                 else {'side':tk.TOP,'fill':tk.X,'expand':False})
                    if contains:
                        containsRows=True
                        activeRows=active or activeRows
                    child.pack_forget()
                    if active or not contains:
                        child.pack(**child.configurationPack)
            return containsRows,activeRows

        arrange(self.propertyListFrame)

    def Notify(self):
        if self.preview:
            self.parent.UpdatePicture()
        elif self.app is not None:
            self.app.Drawing.DrawSchematic()
            self.app.history.Event('edit device configuration')

    def SavePreferences(self):
        if self.readOnly:
            return
        try:
            self.project.SaveToPreferences()
        except ConfigurationError as error:
            messagebox.showerror('Configuration',str(error),parent=self)

    def Close(self):
        self.destroy()


class ConfigurationProperty(tk.Frame):
    labelWidth=controls.CalculationProperty.labelWidth
    controlClass=controls.CalculationProperty

    def __init__(self,parent,text,enteredCallback,updateCallback,project=None,projectPath=None,**options):
        tk.Frame.__init__(self,parent)
        self.dialog=self.winfo_toplevel()
        self.field=project.configurationFields[projectPath]
        self.project,self.projectPath=project,projectPath
        self.dialog.rows[projectPath]=self
        self.bindingEditing=False
        self.explicitReadOnly=False
        self.readOnly=self.dialog.readOnly
        self.invalid=False
        self.focusCallback=None
        self.shown=True
        self.pack(side=tk.TOP,fill=tk.X)
        self.showVariable=tk.BooleanVar(value=self.field.visible)
        self.show=tk.Checkbutton(self,variable=self.showVariable,command=self.ToggleVisibility)
        self.show.pack(side=tk.LEFT)
        self.bindingButton=tk.Button(self,text='=',width=2,command=self.BeginBinding)
        self.bindingButton.pack(side=tk.RIGHT,padx=2)
        self.browseButton=None
        if self.field.type=='file':
            self.browseButton=tk.Button(self,text='...',width=2,command=self.Browse)
            self.browseButton.pack(side=tk.RIGHT)
        options.pop('tooltip',None)
        self.control=self.controlClass(self,text,self.NativeChanged,None,
                                       project=None,projectPath=None,**options)
        self.control.pack_configure(side=tk.LEFT,fill=tk.X,expand=True)
        self.nativeEntry=self.control.entry
        self.bindingString=tk.StringVar()
        self.bindingEntry=tk.Entry(self.control,textvariable=self.bindingString,
                                   width=controls.CalculationProperty.entryWidth)
        for entry in (self.nativeEntry,self.bindingEntry):
            if isinstance(entry,tk.Entry):
                entry.bindtags((str(entry),entry.winfo_class(),'all'))
                entry.bind('<Return>',lambda event:self.Commit())
                entry.bind('<Tab>',lambda event:self.Commit())
                entry.bind('<Escape>',lambda event:self.Cancel())
                entry.bind('<FocusOut>',lambda event:self.LoseFocus())
                entry.bind('<Button-1>',lambda event:None)
                entry.bind('<Double-Button-1>',lambda event:None)
        if self.field.type=='file':
            self.nativeEntry.bind('<Button-1>',lambda event:self.Browse())
        help=self.field.Help()
        for widget in (self.control.label,self.nativeEntry,self.bindingEntry):
            ToolTip.createToolTip(widget,help)
            widget.bind('<Enter>',lambda event:self.dialog.help.configure(
                text=self.field.Help()+'\n'+self.field.DisplayString()),add='+')
        ToolTip.createToolTip(self.show,'Show this property next to the device on the schematic.')
        ToolTip.createToolTip(self.bindingButton,'Enter =system_variable_name. Enter a literal to restore the normal control.')
        self.Refresh()

    @property
    def entry(self):
        return self.bindingEntry if self.bindingEntry.winfo_manager() else self.nativeEntry

    def SetReadOnly(self,readOnly=False):
        self.explicitReadOnly=readOnly
        self.Refresh()

    def Show(self,whetherTo=True):
        self.shown=whetherTo
        if not whetherTo:
            self.pack_forget()
        elif self.winfo_manager()!='pack':
            siblings=self.master.winfo_children()
            options={'side':tk.TOP,'fill':tk.X}
            for sibling in siblings[siblings.index(self)+1:]:
                if sibling.winfo_manager()=='pack':
                    options['before']=sibling
                    break
            self.pack(**options)

    def UpdateStrings(self):
        self.Refresh()

    def Refresh(self):
        field=self.field
        try:
            active=field.Active()
            if not active:
                self.Show(False)
                return
            computed=field.Computed() if active else False
            value=field.Value() if not field.reference or computed else None
            text=field.EntryString()
        except ConfigurationError as error:
            active,computed=True,True
            text='='+field.reference if field.reference else ''
            value=None
            self.dialog.error.configure(text=str(error))
        else:
            if field.reference:
                try:
                    field.Value()
                except ConfigurationError as error:
                    self.dialog.error.configure(text=str(error))
        self.readOnly=self.dialog.readOnly or self.explicitReadOnly or computed
        self.showVariable.set(field.visible)
        self.show.configure(state='disabled' if self.dialog.readOnly else 'normal')
        self.bindingButton.configure(state='disabled' if self.readOnly else 'normal')
        if self.browseButton is not None:
            self.browseButton.configure(state='disabled' if self.readOnly else 'normal')
        self.nativeEntry.pack_forget()
        self.bindingEntry.pack_forget()
        if (field.reference and not computed) or self.bindingEditing:
            self.bindingString.set(text)
            self.bindingEntry.pack(side=tk.LEFT,expand=True,fill=tk.X)
            self.bindingEntry.configure(state='readonly' if self.readOnly else 'normal')
        else:
            if isinstance(self.control,controls.CalculationProperty):
                self.control.string.set(text)
            elif value is not None:
                self.control.SetString(str(value))
            self.nativeEntry.pack(side=tk.LEFT,expand=True,fill=tk.X)
            self.Disable(self.nativeEntry,self.readOnly)
            if hasattr(self.control,'readonly'):
                self.control.readonly=self.readOnly
        self.initial=text
        self.Show(active)

    @staticmethod
    def Disable(widget,disabled):
        if 'state' in widget.keys():
            widget.configure(state='disabled' if disabled else 'normal')
        for child in widget.winfo_children():
            ConfigurationProperty.Disable(child,disabled)

    def ToggleVisibility(self):
        if not self.dialog.readOnly:
            self.field.visible=self.showVariable.get()
            self.dialog.Notify()

    def BeginBinding(self):
        if self.readOnly:
            return
        self.bindingEditing=True
        self.Refresh()
        self.bindingString.set('='+self.field.reference)
        self.bindingEntry.focus_set()
        self.bindingEntry.icursor(tk.END)

    def NativeChanged(self,event=None):
        return self.Commit()

    def Commit(self):
        if self.readOnly:
            return 'break'
        text=self.bindingString.get() if self.entry is self.bindingEntry else self.control.string.get()
        self.dialog.browsing=True
        try:
            OfferConfigurationVariable(self.field,text.strip(),self.dialog)
            self.field.SetEntry(text)
        except ConfigurationError as error:
            self.invalid=True
            self.dialog.error.configure(text=str(error))
            self.entry.focus_set()
            return 'break'
        finally:
            self.dialog.browsing=False
        self.invalid=False
        self.bindingEditing=False
        self.dialog.error.configure(text='')
        self.dialog.Notify()
        self.dialog.RefreshConfiguration()
        return 'break'

    def Cancel(self):
        self.invalid=False
        self.bindingEditing=False
        self.dialog.error.configure(text='')
        self.Refresh()
        return 'break'

    def LoseFocus(self):
        if self.focusCallback is not None:
            self.after_cancel(self.focusCallback)
        self.focusCallback=self.after_idle(self.RefreshIfUnfocused)

    def RefreshIfUnfocused(self):
        self.focusCallback=None
        focus=self.focus_get()
        if focus is not None and str(focus).startswith(str(self)+'.'):
            return
        if not self.dialog.browsing and not self.invalid:
            self.bindingEditing=False
            self.Refresh()

    def destroy(self):
        if self.focusCallback is not None:
            self.after_cancel(self.focusCallback)
        super().destroy()

    def Browse(self):
        if self.readOnly:
            return 'break'
        self.dialog.browsing=True
        try:
            entry=self.bindingString.get() if self.entry is self.bindingEntry else self.control.string.get()
            fileparts=self.dialog.app.fileparts if self.dialog.app is not None else self.control.fileparts
            filename=BrowseConfigurationFile(self.field,entry,
                                             fileparts,self.dialog)
        except ConfigurationError as error:
            self.dialog.error.configure(text=str(error))
            return 'break'
        finally:
            self.dialog.browsing=False
        if filename:
            (self.bindingString if self.entry is self.bindingEntry else self.control.string).set(filename)
            self.Commit()
        return 'break'


class ConfigurationPropertySI(ConfigurationProperty):
    controlClass=controls.CalculationPropertySI

    def __init__(self,parent,text,enteredCallback,updateCallback,project=None,projectPath=None,unit=None,**options):
        super().__init__(parent,text,enteredCallback,updateCallback,project,projectPath,unit=unit,**options)


class ConfigurationPropertyTrueFalseButton(ConfigurationProperty):
    controlClass=controls.CalculationPropertyTrueFalseButton


class ConfigurationPropertyChoices(ConfigurationProperty):
    controlClass=controls.CalculationPropertyChoices

    def __init__(self,parent,text,enteredCallback,updateCallback,choiceStrings,project=None,projectPath=None,**options):
        super().__init__(parent,text,enteredCallback,updateCallback,project,projectPath,choiceStrings=choiceStrings,**options)


class ConfigurationPropertyColor(ConfigurationProperty):
    controlClass=controls.CalculationPropertyColor


class ConfigurationPropertyFileName(ConfigurationProperty):
    controlClass=controls.CalculationPropertyFileName

    def __init__(self,parent,text,enteredCallback,updateCallback,fileparts,project=None,projectPath=None,**options):
        super().__init__(parent,text,enteredCallback,updateCallback,project,projectPath,fileparts=fileparts,**options)


class ConfigurationPropertySpectralDensityFileName(ConfigurationPropertyFileName):
    controlClass=controls.CalculationPropertySpectralDensityFileName
