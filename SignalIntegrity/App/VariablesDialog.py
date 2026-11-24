"""
VariablesDialog.py
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
import os

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from SignalIntegrity.App import MessageBox as messagebox

import copy

from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog, CalculationPropertyTrueFalseButton, CalculationProperty, CalculationPropertyChoices
from SignalIntegrity.App.ProjectFile import VariableConfiguration
import SignalIntegrity.App.Project
from SignalIntegrity.App.InformationMessage import InformationMessage
from SignalIntegrity.App.MenuSystemHelpers import ToolBarElement,ToolTip
from SignalIntegrity.App.Files import FileParts
from SignalIntegrity.App.FilePicker import AskOpenFileName

class VariablePropertyDialog(PropertiesDialog):

    def __init__(self, parent, project, top, add=False):
        self.add = add
        self.projectCopy = copy.deepcopy(project)
        PropertiesDialog.__init__(self, parent, project, top, 'System Variable')
        self.transient(top)
        self.Description = CalculationProperty(self.propertyListFrame, 'Description', None, None, self.project, 'Description')
        self.Name = CalculationProperty(self.propertyListFrame, 'Name', self.onEnteredName, None, self.project, 'Name')
        self.SavedName=self.project['Name']
        self.Type = CalculationPropertyChoices(self.propertyListFrame, 'Type', None, self.onType, [('integer','int'),('float','float'),('string','string'),('enum','enum'),('file','file')], self.project, 'Type')
        self.Value = CalculationProperty(self.propertyListFrame, 'Value', None, None, self.project, 'Value')
        self.Units = CalculationProperty(self.propertyListFrame, 'Units', None, None, self.project, 'Units')
        self.ReadOnly = CalculationPropertyTrueFalseButton(self.propertyListFrame, 'Output Variable', None, None, self.project, 'ReadOnly')
        self.InCache = CalculationPropertyTrueFalseButton(self.propertyListFrame, 'In Cache Calculation', None, None, self.project, 'InCache')
        self.onType()
        PropertiesDialog.bind(self, '<Return>', self.ok)
        PropertiesDialog.bind(self, '<Escape>', self.cancel)
        PropertiesDialog.protocol(self, "WM_DELETE_WINDOW", self.onClosing)
        self.attributes('-topmost', True)
        self.Finish()

    def onType(self):
        self.ReadOnly.Show(False)
        self.Units.Show(self.project['Type']=='float')
        self.ReadOnly.Show(True)

    def onEnteredName(self,event):
        newVariableName=self.project['Name']
        oldVariableName=self.SavedName
        if not self.add and (oldVariableName != newVariableName):
            self.SavedName=newVariableName
            for device in self.top.Drawing.schematic.CircuitDevices():
                from SignalIntegrity.App.ConfigurationProperty import DeviceConfigurations
                for configuration in DeviceConfigurations(device):
                    for field in getattr(configuration,'configurationFields',{}).values():
                        if field.reference==oldVariableName:
                            field.state.entries[field.path]['reference']=newVariableName
                            field.state.SetChanged()
                for prop in device.propertiesList:
                    if prop['Value']==('='+oldVariableName):
                        prop.SetValueFromString('='+newVariableName)
                for variable in device.variablesList:
                    if variable['Value']==('='+oldVariableName):
                        variable['Value']='='+newVariableName

    def onClosing(self):
        self.ok(None)

    def ok(self, event):
        if not self.project.CheckValidity():
            self.cancel(event)
        self.parent.focus_set()
        self.parent.AddVariable(self.project, self.add)
        self.top.statusbar.set('System Variables Modified')
        self.top.history.Event('modify system variables')
        PropertiesDialog.destroy(self)

    def cancel(self, event):
        self.parent.focus_set()
        self.project = copy.deepcopy(self.projectCopy)
        PropertiesDialog.destroy(self)


class VariablesDialog(PropertiesDialog):
    columns=('visible','name','value','units','type','description')
    headings={'visible':'Show','name':'Name','value':'Value','units':'Units','type':'Type','description':'Description'}
    maxColumnChars={'name':30,'value':30,'units':8,'type':16,'description':40}
    maxRows=20
    checked,unchecked='\u2611','\u2610'

    def __init__(self, parent,project=None,top=None,title='System Variables',filename=None, parameterizable = False):
        # the system variables are edited when no project is supplied, otherwise these are device variables
        self.systemVariables=(project == None)
        if project == None: project = SignalIntegrity.App.Project['Variables.Items']
        if top == None: top = parent
        PropertiesDialog.__init__(self, parent, project, top, title)
        self.transient(self.top)
        self.propertyListFrame.pack_configure(fill=tk.BOTH,expand=tk.YES)

        self.filename=filename
        self.device=getattr(parent,'device',None)
        self.isWaveformProcessor=(self.device is not None
                      and self.device['script'] is not None
                      and self.device['inputports'] is not None
                      and self.device['outputports'] is not None)
        self.savedVariables=copy.deepcopy(self.project)
        self.cellEditor=None

        self.controlFrame = tk.Frame(self.propertyListFrame)
        self.controlFrame.pack(side=tk.TOP, fill=tk.X, expand=tk.NO)

        def ToolButton(icon,command,tip):
            button=ToolBarElement(self.controlFrame,iconfile=SignalIntegrity.App.IconsDir+icon,
                                  iconsize=16,padx=1,pady=0,borderwidth=1,highlightthickness=0,
                                  command=command).Pack(side=tk.LEFT).button
            ToolTip.createToolTip(button,tip)
            return button

        self.addButton=ToolButton('edit-add-2.gif',self.onAddVariable,'Add variable (Insert)')
        self.editButton=ToolButton('edit-3.gif',lambda: self.onSelected(self.onEditVariable),'Edit variable properties (Ctrl+E)')
        self.deleteButton=ToolButton('edit-delete-6.gif',lambda: self.onSelected(self.onDeleteVariable),'Delete variable (Delete)')
        self.upButton=ToolButton('up.gif',lambda: self.onSelected(self.onUpVariable),'Move up (Ctrl+Up)')
        self.downButton=ToolButton('down.gif',lambda: self.onSelected(self.onDownVariable),'Move down (Ctrl+Down)')
        self.browseButton=ToolButton('browse-file.gif',lambda: self.onSelected(self.onFileBrowse),'Browse for file')

        if self.isWaveformProcessor:
            tk.Button(self.controlFrame, text='import from script', command=self.onImportFromScript).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        elif self.filename != None:
            tk.Button(self.controlFrame, text='import from project', command=self.onImportFromProject).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
            tk.Button(self.controlFrame, text='parameterize project', command=self.onParameterizeProject).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        elif parameterizable:
            tk.Button(self.controlFrame, text='parameterize project', command=self.onParameterizeProject).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)

        tableFrame=tk.Frame(self.propertyListFrame)
        tableFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        self.treeStyle=ttk.Style(self)
        self.treeFont=tkfont.nametofont('TkDefaultFont')
        self.UpdateStyle()
        self.tree=ttk.Treeview(tableFrame,columns=self.columns,show='headings',selectmode='browse',style='Variables.Treeview')
        scrollbar=ttk.Scrollbar(tableFrame,orient=tk.VERTICAL,command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        self.tree.pack(side=tk.LEFT,fill=tk.BOTH,expand=tk.YES)
        for column in self.columns:
            self.tree.heading(column,text=self.headings[column],anchor=tk.W)
            self.tree.column(column,anchor=tk.CENTER if column=='visible' else tk.W,stretch=(column=='description'))
        self.tree.bind('<<ThemeChanged>>',self.UpdateStyle)
        self.tree.bind('<<TreeviewSelect>>',lambda event: self.UpdateButtons())
        self.tree.bind('<Button-1>',self.onTreeClick)
        self.tree.bind('<Double-Button-1>',self.onTreeDoubleClick)
        for key in ('<Return>','<KP_Enter>','<F2>'):
            self.tree.bind(key,lambda event: self.onSelected(self.BeginCellEdit) or 'break')
        self.tree.bind('<space>',lambda event: self.onSelected(self.onPropertyVisible) or 'break')
        self.tree.bind('<Delete>',lambda event: self.onSelected(self.onDeleteVariable) or 'break')
        self.tree.bind('<Insert>',lambda event: self.onAddVariable() or 'break')
        self.tree.bind('<Control-e>',lambda event: self.onSelected(self.onEditVariable) or 'break')
        self.tree.bind('<Control-Up>',lambda event: self.onSelected(self.onUpVariable) or 'break')
        self.tree.bind('<Control-Down>',lambda event: self.onSelected(self.onDownVariable) or 'break')

        self.DrawVariables()
        if len(self.project) > 0:
            self.Select(0)

        PropertiesDialog.bind(self, '<Return>', self.ok)
        PropertiesDialog.bind(self, '<Escape>', self.cancel)
        PropertiesDialog.protocol(self, "WM_DELETE_WINDOW", self.onClosing)
        self.attributes('-topmost', True)
        self.minsize(200, 1)
        self.Finish()
        self.tree.focus_set()

    def UpdateStyle(self,event=None):
        displayScale=max(1.0,float(self.tk.call('tk','scaling'))/(96.0/72.0))
        self.treeStyle.configure('Variables.Treeview',
            rowheight=self.treeFont.metrics('linespace')+round(4*displayScale))

    def RowValues(self,variable):
        return (self.checked if variable['Visible'] else self.unchecked,
                variable['Name'],
                variable.EntryString(),
                variable['Units'] if variable['Type']=='float' else '',
                variable['Type']+(' (output)' if variable['ReadOnly'] else ''),
                variable['Description'])

    def DrawVariables(self):
        """refreshes the table rows from the variables (no widgets are created per variable)"""
        self.CancelCellEdit()
        selected=self.SelectedIndex()
        self.tree.delete(*self.tree.get_children())
        rows=[self.RowValues(variable) for variable in self.project]
        for v,values in enumerate(rows):
            self.tree.insert('','end',iid=str(v),values=values)
        self.tree.configure(height=max(3,min(len(rows),self.maxRows)))
        pad=self.treeFont.measure('0')*2
        self.tree.column('visible',width=self.treeFont.measure(self.headings['visible'])+pad,minwidth=10)
        for c,column in enumerate(self.columns[1:],1):
            longest=max([self.treeFont.measure(self.headings[column])]+
                        [self.treeFont.measure(str(values[c])) for values in rows])
            width=min(longest,self.treeFont.measure('0')*self.maxColumnChars[column])+pad
            self.tree.column(column,width=width,minwidth=pad)
        if selected is not None and len(rows) > 0:
            self.Select(min(selected,len(rows)-1))
        self.UpdateButtons()

    def RefreshRow(self,v):
        self.tree.item(str(v),values=self.RowValues(self.project[v]))
        self.UpdateButtons()

    def SelectedIndex(self):
        selection=self.tree.selection()
        return int(selection[0]) if selection else None

    def Select(self,v):
        iid=str(v)
        self.tree.selection_set(iid)
        self.tree.focus(iid)
        self.tree.see(iid)
        self.UpdateButtons()

    def onSelected(self,action):
        v=self.SelectedIndex()
        if v is not None:
            action(v)

    def UpdateButtons(self):
        v=self.SelectedIndex()
        selected=v is not None
        for button,active in ((self.editButton,selected),
                              (self.deleteButton,selected),
                              (self.upButton,selected and v > 0),
                              (self.downButton,selected and v < len(self.project)-1),
                              (self.browseButton,selected and self.project[v]['Type']=='file')):
            button.toolbarElement.Activate(active)

    def onTreeClick(self,event):
        if self.tree.identify_region(event.x,event.y) == 'cell' and self.tree.identify_column(event.x) == '#1':
            row=self.tree.identify_row(event.y)
            if row:
                self.onPropertyVisible(int(row))

    def onTreeDoubleClick(self,event):
        if self.tree.identify_region(event.x,event.y) != 'cell':
            return
        row=self.tree.identify_row(event.y)
        if not row:
            return
        v=int(row)
        column=self.columns[int(self.tree.identify_column(event.x)[1:])-1]
        if column == 'visible':
            self.onPropertyVisible(v)
        elif column == 'value':
            self.BeginCellEdit(v)
        else:
            self.onEditVariable(v)
        return 'break'

    def BeginCellEdit(self,v):
        self.CancelCellEdit()
        iid=str(v)
        self.Select(v)
        self.tree.update_idletasks()
        bbox=self.tree.bbox(iid,'value')
        if not bbox:
            return
        x,y,width,height=bbox
        entry=tk.Entry(self.tree,borderwidth=1)
        entry.insert(0,self.project[v].EntryString())
        entry.place(x=x,y=y,width=width,height=height)
        entry.select_range(0,tk.END)
        entry.icursor(tk.END)
        entry.focus_set()
        for key in ('<Return>','<KP_Enter>','<Tab>'):
            entry.bind(key,lambda event: self.CommitCellEdit())
        entry.bind('<Escape>',lambda event: self.CancelCellEdit())
        entry.bind('<FocusOut>',lambda event: self.CommitCellEdit())
        self.cellEditor=(v,entry)

    def CancelCellEdit(self):
        if self.cellEditor is not None:
            v,entry=self.cellEditor
            self.cellEditor=None
            entry.destroy()
            self.tree.focus_set()
        return 'break'

    def CommitCellEdit(self):
        if self.cellEditor is None:
            return 'break'
        v,entry=self.cellEditor
        string=entry.get()
        self.CancelCellEdit()
        self.SetVariableFromString(v,string)
        return 'break'

    def SetVariableFromString(self,v,string):
        """sets the value of variable v from an edited string, returning whether it was accepted"""
        variable=self.project[v]
        previousValue=variable['Value']
        if not variable.SetValueFromEntryString(string):
            self.bell()
            return False
        if variable['Value'] != previousValue:
            self.onVariableEntered(v,previousValue)
            self.RefreshValues()
        else:
            self.RefreshRow(v)
        return True

    def RefreshValues(self):
        self.top.Drawing.DrawSchematic()
        for v in range(len(self.project)):
            self.RefreshRow(v)

    def onFileBrowse(self,v):
        filename=AskVariableFileName(self.project[v]['Value'],self.top.fileparts,self)
        if filename != '' and filename != self.project[v]['Value']:
            self.project[v]['Value']=filename
            self.RefreshValues()
    def onFileView(self,v):
        pass

    def onImportFromScript(self):
        from SignalIntegrity.App.WaveformProcessorScript import ParseWaveformProcessorInterface, ReconcileProcessorVariables

        try:
            inputPorts,outputPorts,importedVariables=ParseWaveformProcessorInterface(
                self.device['script'].GetValue() or '')
            reconciledVariables,removedNames=ReconcileProcessorVariables(self.project,importedVariables)
        except ValueError as error:
            messagebox.showerror('Import Processor Interface',str(error),parent=self)
            return

        if removedNames and not messagebox.askyesno(
                'Import Processor Interface',
                'Remove variables not declared by the script?\n\n'+', '.join(removedNames),
                parent=self):
            return

        self.project[:]=reconciledVariables
        self.device.variablesList=self.project
        self.device['inputports']['Value']=inputPorts
        self.device['outputports']['Value']=outputPorts
        self.device.UpdatePortConfiguration()
        for propertyFrame in self.parent.DeviceProperties.propertyFrameList:
            if propertyFrame.partProperty['Keyword'] in ['inputports','outputports']:
                propertyFrame.propertyString.set(propertyFrame.partProperty.PropertyString(stype='entry'))
        self.DrawVariables()
        self.parent.DeviceProperties.UpdatePicture()
        self.top.statusbar.set('Processor interface imported')
        self.top.history.Event('import waveform processor interface')

    def onParameterizeProject(self):
        device = self.parent.device
        variables=SignalIntegrity.App.Project['Variables']
        ref=device['ref']
        if ref != None:
            prefix=ref['Value']
            if prefix == None:
                prefix=''
            else:
                prefix += '_'
            for prop in device.propertiesList:
                if (not SignalIntegrity.App.Preferences['Variables.ParameterizeOnlyVisible'] or prop['Visible']) and (not prop['Hidden']) and prop['InProjectFile'] and (not prop['Keyword'] in ['ref','ports','file']):
                    varName=prefix+prop['Keyword']
                    varValue=prop['Value']
                    if (not ((len(varValue)>1) and (varValue[0]=='='))):
                        if not (varName in variables.Names()):
                            variable=VariableConfiguration().InitFromPartProperty(varName,prop)
                            variables['Items'].append(variable)
                        prop.SetValueFromString('='+varName)
            for variable in device.variablesList:
                varName=prefix+variable['Name']
                varValue=variable['Value']
                if (not ((len(varValue)>1) and (varValue[0]=='='))):
                    if not (varName in variables.Names()):
                        newVariable=copy.deepcopy(variable)
                        newVariable['Name']=varName
                        newVariable['Value']=varValue
                        variables['Items'].append(newVariable)
                    variable['Value']=('='+varName)
        self.DrawVariables()
        self.top.Drawing.DrawSchematic()

    def onUpVariable(self,v):
        variable=copy.deepcopy(self.project[v])
        del self.project[v]
        self.project.insert(max(v-1,0),variable)
        self.DrawVariables()
        self.Select(max(v-1,0))

    def onDownVariable(self,v):
        variable=copy.deepcopy(self.project[v])
        del self.project[v]
        self.project.insert(min(v+1,len(self.project)),variable)
        self.DrawVariables()
        self.Select(min(v+1,len(self.project)-1))

    def onVariableEntered(self, v, previousValue):
        if not self.systemVariables:
            OfferToAddSystemVariable(self.project[v],previousValue,self)

    @staticmethod
    def SystemVariableValue(variable,previousValue):
        """the value for a new system variable referenced by a device variable, which is the
        device variable's value before it was changed to reference the system variable"""
        previous=copy.deepcopy(variable)
        previous['Value']=previousValue
        value=previous.Value()
        if isinstance(value,str) and (len(value)>0) and (value[0]=='='):
            value=VariableConfiguration()['Value'] if variable['Type'] in ['float','int'] else ''
        return value

    def onAddVariable(self):
        self.CancelCellEdit()
        variablePropertyDialog = VariablePropertyDialog(self, VariableConfiguration(), self.top, add=True)
        variablePropertyDialog.grab_set()

    def AddVariable(self, variable, add):
        added=add and variable.CheckValidity()
        if added:
            self.project.append(variable)
        self.top.Drawing.DrawSchematic()
        self.DrawVariables()
        if added:
            self.Select(len(self.project)-1)

    def onEditVariable(self, v):
        self.CancelCellEdit()
        variablePropertyDialog = VariablePropertyDialog(self, self.project[v], self.top)
        variablePropertyDialog.grab_set()

    def onDeleteVariable(self, v):
        variableName=self.project[v]['Name']
        value=self.project[v]['Value']
        totalThisVariable=sum([1 if variable['Name']==variableName else 0 for variable in self.project])
        if totalThisVariable == 1:
            for device in self.top.Drawing.schematic.CircuitDevices():
                for prop in device.propertiesList:
                    if prop['Value']==('='+variableName):
                        prop.SetValueFromString(value)
                for variable in device.variablesList:
                    if variable['Value']==('='+variableName):
                        variable['Value']=value
        del self.project[v]
        self.DrawVariables()
        self.top.Drawing.DrawSchematic()

    def onPropertyVisible(self, v):
        self.project[v]['Visible'] = not self.project[v]['Visible']
        self.RefreshRow(v)

    def onImportFromProject(self):
        from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless
        app=SignalIntegrityAppHeadless()
        level=app.projectStack.Push()
        try:
            app.OpenProjectFile(os.path.abspath(self.filename))
            projectVariables=SignalIntegrity.App.Project['Variables.Items']
            currentNames=[variable['Name'] for variable in self.project]
            for variable in projectVariables:
                if (not variable['ReadOnly']) and (not variable['Name'] in currentNames):
                    self.project.append(variable)
        except:
            InformationMessage(self,"Schematic Variables Import","The project could not be opened and the import failed")
        app.projectStack.Pull(level)
        self.DrawVariables()

    def onClosing(self):
        self.ok(None)

    def ok(self, event):
        self.CommitCellEdit()
        for variable in self.project:
            if not variable.CheckValidity():
                self.cancel(event)
        self.top.statusbar.set('System Variables Modified')
        self.top.history.Event('modify system variables')
        try:
            self.parent.DeviceProperties.UpdatePicture()
        except AttributeError:
            pass
        self.top.Drawing.DrawSchematic()
        PropertiesDialog.destroy(self)

    def cancel(self, event):
        self.project=self.savedVariables
        PropertiesDialog.destroy(self)

def AskVariableFileName(filename,defaultFileParts,parent):
    """asks for a file to replace filename, filtered by its extension, returning '' if cancelled"""
    if isinstance(filename,str) and filename.startswith('='):
        project=SignalIntegrity.App.Project
        if project is not None and filename[1:] in project['Variables'].Names():
            filename=project['Variables'].VariableByName(filename[1:]).Value()
        if not isinstance(filename,str) or filename.startswith('='):
            filename=''
    filetypename,fileextension='all',('.*')
    if isinstance(filename,str):
        extension=os.path.splitext(filename)[-1]
        if (len(extension)>=4) and (extension[0:2] in ['.s','.S']) and (extension[-1] in ['p','P']):
            try:
                ports=int(extension[2:-1])
                filetypename='s-parameters'
                fileextension=('.s'+str(ports)+'p','.S'+str(ports)+'P')
            except ValueError:
                pass
        elif extension in ['.txt','.trc']:
            fileextension=('.txt','.trc')
            filetypename='waveforms'
        elif extension == '.cal':
            fileextension=('.cal')
            filetypename='calibration file'
    initialDirectory=defaultFileParts.AbsoluteFilePath()
    initialFile=''
    if filename:
        currentFileParts=FileParts(os.path.join(initialDirectory,filename))
        initialDirectory=currentFileParts.AbsoluteFilePath()
        initialFile=currentFileParts.FileNameWithExtension()
    filename=AskOpenFileName(parent=parent,
                             filetypes=[(filetypename,fileextension),('project','.si'),('all','.*')],
                             initialdir=initialDirectory,
                             initialfile=initialFile)
    if filename is None or isinstance(filename,tuple):
        filename=''
    filename=str(filename)
    if filename != '':
        filename=FileParts(filename).FullFilePathExtension()
    return filename

def OfferToAddSystemVariable(variable,previousValue,parent):
    """when a device variable now references a system variable that does not exist, offer to add it"""
    string=variable['Value']
    if isinstance(string,str) and (len(string)>1) and (string[0]=='=') and not (string[1:] in SignalIntegrity.App.Project['Variables'].Names()):
        doit =  messagebox.askyesnocancel('System Variables','Do you want to add the new variable: '+string[1:]+ ' to the system variables?',parent=parent)
        if doit:
            variableToAdd=copy.deepcopy(variable)
            variableToAdd['Name']=string[1:]
            variableToAdd['Value']=VariablesDialog.SystemVariableValue(variable,previousValue)
            SignalIntegrity.App.Project['Variables.Items'].append(variableToAdd)
