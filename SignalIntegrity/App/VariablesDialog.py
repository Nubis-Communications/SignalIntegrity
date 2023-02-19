"""
VariablesDialog.py
"""
# Copyright (c) 2018 Teledyne LeCroy, Inc.
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
import sys
if sys.version_info.major < 3:
    import Tkinter as tk
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import messagebox

import copy

from SignalIntegrity.App.CalculationPropertiesProject import PropertiesDialog, CalculationPropertyTrueFalseButton, CalculationPropertySI, CalculationProperty
from SignalIntegrity.App.ProjectFile import VariableConfiguration
import SignalIntegrity.App.Project
from SignalIntegrity.App.InformationMessage import InformationMessage
from SignalIntegrity.App.MenuSystemHelpers import ScrollableFrame
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
        self.Type = CalculationProperty(self.propertyListFrame, 'Type', None, None, self.project, 'Type')
        self.Value = CalculationProperty(self.propertyListFrame, 'Value', None, None, self.project, 'Value')
        self.Units = CalculationProperty(self.propertyListFrame, 'Units', None, None, self.project, 'Units')
        self.ReadOnly = CalculationPropertyTrueFalseButton(self.propertyListFrame, 'Output Variable', None, None, self.project, 'ReadOnly')
        PropertiesDialog.bind(self, '<Return>', self.ok)
        PropertiesDialog.bind(self, '<Escape>', self.cancel)
        PropertiesDialog.protocol(self, "WM_DELETE_WINDOW", self.onClosing)
        self.attributes('-topmost', True)
        self.Finish()

    def onEnteredName(self,event):
        newVariableName=self.project['Name']
        oldVariableName=self.SavedName
        if not self.add and (oldVariableName != newVariableName):
            self.SavedName=newVariableName
            for device in self.top.Drawing.schematic.deviceList:
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

    def __init__(self, parent,project=None,top=None,title='System Variables',filename=None):
        if project == None: project = SignalIntegrity.App.Project['Variables.Items']
        if top == None: top = parent
        PropertiesDialog.__init__(self, parent, project, top, title)
        self.transient(self.top)

        self.filename=filename
        self.savedVariables=copy.deepcopy(self.project)

        self.useScrollbar=(len(self.project)>30)

        if self.useScrollbar:
            self.container=ScrollableFrame(self.propertyListFrame)
        else:
            self.container=tk.Frame(self.propertyListFrame)
        self.container.pack(side=tk.TOP, fill=tk.BOTH,expand=tk.YES)

        if self.useScrollbar:
            self.controlFrame = tk.Frame(self.container.scrollable_frame)
        else:
            self.controlFrame = tk.Frame(self.container)

        self.controlFrame.pack(side=tk.TOP, fill=tk.X, expand=tk.YES)

        self.addButtonGraphic=tk.PhotoImage(file=SignalIntegrity.App.IconsDir+'edit-add-2.gif')
        self.upButtonGraphic=tk.PhotoImage(file=SignalIntegrity.App.IconsDir+'up.gif')
        self.downButtonGraphic=tk.PhotoImage(file=SignalIntegrity.App.IconsDir+'down.gif')
        self.delButtonGraphic=tk.PhotoImage(file=SignalIntegrity.App.IconsDir+'edit-delete-6.gif')
        self.editButtonGraphic=tk.PhotoImage(file=SignalIntegrity.App.IconsDir+'edit-3.gif')
        self.DrawVariables()

        addButton = tk.Button(self.controlFrame)
        addButton.configure(width=self.addButtonGraphic.width(),height=self.addButtonGraphic.height(), image=self.addButtonGraphic, command=self.onAddVariable)
        addButton.pack(side=tk.LEFT)

        if self.filename != None:
            tk.Button(self.controlFrame, text='import from project', command=self.onImportFromProject).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
            tk.Button(self.controlFrame, text='parameterize project', command=self.onParameterizeProject).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)

        PropertiesDialog.bind(self, '<Return>', self.ok)
        PropertiesDialog.bind(self, '<Escape>', self.cancel)
        PropertiesDialog.protocol(self, "WM_DELETE_WINDOW", self.onClosing)
        self.attributes('-topmost', True)
        self.minsize(200, 1)
        # self.Save()
        self.Finish()

    def DrawVariables(self):
        if hasattr(self, 'variablesFrame'):
            self.variablesFrame.pack_forget()

        if self.useScrollbar:
            self.variablesFrame = tk.Frame(self.container.scrollable_frame)
        else:
            self.variablesFrame = tk.Frame(self.container)
        self.variablesFrame.pack(side=tk.TOP, fill=tk.X, expand=tk.NO)

        self.variableFrameList = []

        for v in range(len(self.project)):
            variable = self.project[v]

            variableFrame = tk.Frame(self.variablesFrame)
            variableFrame.pack(side=tk.TOP, fill=tk.X, expand=tk.YES)

            editButton = tk.Button(variableFrame)
            editButton.configure(width=self.editButtonGraphic.width(),height=self.editButtonGraphic.height(), image=self.editButtonGraphic, command=lambda v=v: self.onEditVariable(v))
            editButton.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

            delButton = tk.Button(variableFrame)
            delButton.configure(width=self.delButtonGraphic.width(),height=self.delButtonGraphic.height(), image=self.delButtonGraphic, command=lambda v=v: self.onDeleteVariable(v))
            delButton.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

            upButton = tk.Button(variableFrame)
            upButton.configure(width=self.upButtonGraphic.width(),height=self.upButtonGraphic.height(), image=self.upButtonGraphic, command=lambda v=v: self.onUpVariable(v))
            upButton.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

            downButton = tk.Button(variableFrame)
            downButton.configure(width=self.downButtonGraphic.width(),height=self.downButtonGraphic.height(), image=self.downButtonGraphic, command=lambda v=v: self.onDownVariable(v))
            downButton.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)

            visible=tk.Checkbutton(variableFrame,variable=lambda v=v: variable['Visible'],onvalue=True,offvalue=False,command=lambda v=v: self.onPropertyVisible(v))
            visible.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            if variable['Visible']: visible.select()
            else: visible.deselect()

            if (variable['Type'] == 'float'):
                self.variableFrameList.append(CalculationPropertySI(variableFrame,
                                          variable['Name'],
                                          self.onVariableEntered,
                                          None, self.project[v],
                                          'Value',
                                          variable['Units'], variable['Description'],
                                          allowEquals=True))
            elif (variable['Type'] in ['int','string','enum','file']):
                if variable['Type'] == 'file':
                    # Don't expose file view because it's difficult to determine how the best way to deal with this is for variables.
                    # The main problem is for projects that are typically opened from devices with the device arguments.  Here, we have
                    # no real context for the arguments, so let them be viewed for now only from the device itself that references this
                    # variable.
                    # self.propertyFileViewButton = tk.Button(variableFrame,text='view',command=lambda v=v: self.onFileView(v))
                    # self.propertyFileViewButton.pack(side=tk.RIGHT,expand=tk.NO,fill=tk.X)
                    self.propertyFileBrowseButton = tk.Button(variableFrame,text='browse',command=lambda v=v: self.onFileBrowse(v))
                    self.propertyFileBrowseButton.pack(side=tk.RIGHT,expand=tk.NO,fill=tk.X)

                self.variableFrameList.append(CalculationProperty(variableFrame,
                                                                  variable['Name'],
                                                                  self.onVariableEntered,
                                                                  None, self.project[v],
                                                                  'Value', variable['Description']))
            self.variableFrameList[-1].SetReadOnly(variable['ReadOnly'])

    def onFileBrowse(self,v):
        variable=self.project[v]
        filename=variable['Value']
        if isinstance(filename,str):
            extension=os.path.splitext(filename)[-1]
            if (len(extension)>=4) and (extension[0:2] in ['.s','.S']) and (extension[-1] in ['p','P']):
                try:
                    ports=int(extension[2:-1])
                    filetypename='s-parameters'
                    fileextension=('.s'+str(ports)+'p','.S'+str(ports)+'P')
                except ValueError:
                    filetypename='all'
                    fileextension=('.*')
            elif extension in ['.txt','.trc']:
                fileextension=('.txt','.trc')
                filetypename='waveforms'
            elif extension == '.cal':
                fileextension=('.cal')
                filetypename='calibration file'
            else:
                filetypename='all'
                fileextension=('.*')
        else:
            filetypename='all'
            fileextension=('.*')
        currentFileParts=FileParts(filename)
        extension=currentFileParts.fileext
        if currentFileParts.filename=='':
            initialDirectory=self.top.fileparts.AbsoluteFilePath()
            initialFile=''
        else:
            initialDirectory=currentFileParts.AbsoluteFilePath()
            if currentFileParts.fileext in ['.si',extension]:
                initialFile=currentFileParts.FileNameWithExtension()
            else:
                initialFile=currentFileParts.filename+extension
        filename=AskOpenFileName(parent=self,
                                 filetypes=[(filetypename,fileextension),('project','.si'),('all','.*')],
                                 initialdir=initialDirectory,
                                 initialfile=initialFile)
        if filename is None:
            filename=''
        if isinstance(filename,tuple):
            filename=''
        filename=str(filename)
        if filename != '':
            filename=FileParts(filename).FullFilePathExtension()
            variable['Value']=filename
            self.variableFrameList[v].UpdateStrings()
    def onFileView(self,v):
        pass

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

    def onDownVariable(self,v):
        variable=copy.deepcopy(self.project[v])
        del self.project[v]
        self.project.insert(min(v+1,len(self.project)),variable)
        self.DrawVariables()

    def onVariableEntered(self, v):
        vc=v.widget.master.project
        string=vc['Value']
        if (self.filename != None) and isinstance(string,str) and (len(string)>0) and (string[0]=='=') and not (string[1:] in SignalIntegrity.App.Project['Variables'].Names()):
            doit =  messagebox.askyesnocancel('System Variables','Do you want to add the new variable: '+string[1:]+ ' to the system variables?')
            if doit:
                variableToAdd=copy.deepcopy(vc)
                variableToAdd['Name']=string[1:]
                SignalIntegrity.App.Project['Variables.Items'].append(variableToAdd)


    def onAddVariable(self):
        variablePropertyDialog = VariablePropertyDialog(self, VariableConfiguration(), self.top, add=True)
        variablePropertyDialog.grab_set()

    def AddVariable(self, variable, add):
        if add and variable.CheckValidity():
            self.project.append(variable)
        self.DrawVariables()

    def onEditVariable(self, v):
        variablePropertyDialog = VariablePropertyDialog(self, self.project[v], self.top)
        variablePropertyDialog.grab_set()

    def onDeleteVariable(self, v):
        variableName=self.project[v]['Name']
        value=self.project[v]['Value']
        totalThisVariable=sum([1 if variable['Name']==variableName else 0 for variable in self.project])
        if totalThisVariable == 1:
            for device in self.top.Drawing.schematic.deviceList:
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

