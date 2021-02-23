"""
Projects.py
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
import sys
if sys.version_info.major < 3:
    import Tkinter as tk
    from Tkinter import ttk
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox

import os

import SignalIntegrity.App.Project

from SignalIntegrity.App.Schematic import Drawing
from SignalIntegrity.App.FilePicker import AskOpenFileName
from SignalIntegrity.App.Files import FileParts,ConvertFileNameToRelativePath
from SignalIntegrity.App.ProjectFile import ProjectFile

#         self.tabControl=ttk.Notebook(self)
#         self.tab1=ttk.Frame(self.tabControl)
#         self.tabControl.add(self.tab1,text='Page 1')
#         self.tabControl.pack(expand=1,fill=tk.BOTH)

class NameSelector(tk.Toplevel):
    def __init__(self,parent,names,namesChosen):
        super().__init__(parent)
        self.names=names
        self.namesChosen=namesChosen
        self.parent=parent
        self.ints=[0 for _ in names]
        self.vars=[tk.IntVar(value=self.ints[i]) for i in range(len(names))]
        self.checkButtons=[None for _ in names]
        self.transient(parent)
        self.title('Select tabs from other project file')
        self.result = None
        for n in range(len(self.names)):
            name=self.names[n]
            self.checkButtons[n]=tk.Checkbutton(self, text=name, variable=self.vars[n], onvalue=1, offvalue = 0)
            self.checkButtons[n].pack()
        self.buttonbox()
        self.wait_visibility(self)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))
        self.wait_window(self)

    def buttonbox(self):
        box = tk.Frame(self)
        w = tk.Button(box, text="OK", width=10, command=self.ok)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def ok(self, event=None):
        self.withdraw()
        self.update_idletasks()

        self.ints=[self.vars[i].get() for i in range(len(self.vars))]
        for i in range(len(self.ints)):
            if self.ints[i]==1:
                self.namesChosen.append(self.names[i])

        self.cancel()

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()

class Projects(tk.Frame):
    def __init__(self,parent):
        if hasattr(self, 'initialized'):
            if self.initialized == True:
                self.Drawing().pack_forget()
                self.tabControl.pack_forget()
                self.pack_forget()
        super().__init__(parent)
        self.parent=parent
        self.root=parent
        self.tabTearOffMenu=tk.Menu(self, tearoff=0)
        self.tabTearOffMenu.add_command(label="Open",command=self.OpenSelectedTab)
        self.tabTearOffMenu.add_command(label="Rename",command=self.RenameSelectedTab)
        self.tabTearOffMenu.add_command(label="Save Tab to Project File",command=self.OpenSelectedTab)
        self.tabTearOffMenu.add_command(label="New Tab To Right",command=self.NewTabToRight)
        self.tabTearOffMenu.add_command(label="New Tab To Left",command=self.NewTabToLeft)
        self.tabTearOffMenu.add_command(label="Duplicate",command=self.DuplicateSelectedTab)
        self.tabTearOffMenu.add_command(label="Delete",command=self.DeleteSelectedTab)
        self.noTabTearOffMenu=tk.Menu(self, tearoff=0)
        self.noTabTearOffMenu.add_command(label="Open Project File in New Tab",command=self.OpenNewProject)
        self.noTabTearOffMenu.add_command(label="Add Project File to New Tab",command=self.AddNewProject)
        self.noTabTearOffMenu.add_command(label="Delete Projects",command=self.DeleteProjects)
        numProjects=len(SignalIntegrity.App.Project['Projects'])
        self.tabControl=ttk.Notebook(self)
        self.projectList=[]
        if numProjects > 0:
            for i in range(len(SignalIntegrity.App.Project['Projects'])):
                projectFrame=Project(self,self.root)
                self.projectList.append(projectFrame)
                self.tabControl.add(projectFrame,text=SignalIntegrity.App.Project['Projects'][i]['Name'])
            self.selectedProject=SignalIntegrity.App.Project['Selected']
        else: # empty - just do something
            projectFrame=Project(self,self.root)
            self.projectList.append(projectFrame)
            self.tabControl.add(projectFrame,text='project')
            self.selectedProject=0
        self.tabControl.pack(expand=1,fill=tk.BOTH)
        self.tabControl.bind('<Button-3>', self.onTearOff)
        self.tabControl.bind('<Button-1>', self.onTouched)
        self.projectList[self.selectedProject].SelectProject()
        self.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        self.initialized=True
    def InitFromProject(self):
        self.__init__(self.parent)
        self.Drawing().InitFromProject()
    def Drawing(self):
        return self.projectList[self.selectedProject].Drawing
    def OpenSelectedTab(self):
        pass
    def RenameSelectedTab(self):
        pass
    def NewTabToRight(self):
        pass
    def NewTabToLeft(self):
        pass
    def DuplicateSelectedTab(self):
        pass
    def OpenNewProject(self):
        if self.AddNewProject():
            tab=len(SignalIntegrity.App.Project['Projects'])-1
            self.tabControl.select(tab)
            self.SelectTab(tab)
    def AddNewProject(self):
        filename=AskOpenFileName(filetypes=[('si', '.si')],
                                 initialdir=self.root.fileparts.AbsoluteFilePath(),
                                 initialfile=self.root.fileparts.FileNameWithExtension('.si'))
        if filename is None:
            return

        try:
            fileparts=FileParts(filename)
            proj=ProjectFile().Read(fileparts.FullFilePathExtension('.si'))
            mainName=fileparts.filename
            if len(proj['Projects']) == 1:
                newProject=proj['Projects'][0]
                newProject['Name']=mainName
                SignalIntegrity.App.Project['Projects'].append(newProject)
                projectFrame=Project(self,self.root)
                self.projectList.append(projectFrame)
                self.tabControl.add(projectFrame,text=mainName)
            else:
                names=[p['Name'] for p in proj['Projects']]
                namesChosen=[]
                NameSelector(self,names,namesChosen)
                for projectConfiguration in proj['Projects']:
                    if projectConfiguration['Name'] in namesChosen:
                        newProject=projectConfiguration
                        if newProject['Name']=='Main':
                            newProject['Name']=mainName
                        SignalIntegrity.App.Project['Projects'].append(newProject)
                        projectFrame=Project(self,self.root)
                        self.projectList.append(projectFrame)
                        self.tabControl.add(projectFrame,text=newProject['Name'])
            return True
        except Exception as e:
            messagebox.showerror('Project File:',fileparts.FileNameWithExtension()+' could not be opened')
            return False
    def DeleteProjects(self):
        names=[p['Name'] for p in SignalIntegrity.App.Project['Projects']]
        namesChosen=[]
        NameSelector(self,names,namesChosen)
        if namesChosen == []:
            return
        for name in namesChosen:
            for i in range(len(SignalIntegrity.App.Project['Projects'])):
                thisName=SignalIntegrity.App.Project['Projects'][i]['Name']
                if name != thisName:
                    continue
                if len(SignalIntegrity.App.Project['Projects'])==1:
                    SignalIntegrity.App.Project = ProjectFile().New()
                else:
                    del SignalIntegrity.App.Project['Projects'][i]
                    del self.projectList[i]
                    self.tabControl.forget(i)
                    break
        active_tab = self.tabControl.index(self.tabControl.select())
        SignalIntegrity.App.Project['Selected']=active_tab
        self.selectedProject=active_tab
        self.projectList[self.selectedProject].SelectProject()
        self.Drawing().InitFromProject()
        self.Drawing().stateMachine.Nothing()

    def DeleteSelectedTab(self):
        if len(SignalIntegrity.App.Project['Projects'])==1:
            SignalIntegrity.App.Project = ProjectFile().New()
        else:
            # a[0:selected]+a[selected+1:-1]
            del SignalIntegrity.App.Project['Projects'][SignalIntegrity.App.Project['Selected']]
            del self.projectList[SignalIntegrity.App.Project['Selected']]
            if SignalIntegrity.App.Project['Selected']>=len(SignalIntegrity.App.Project['Projects']):
                SignalIntegrity.App.Project['Selected']=len(SignalIntegrity.App.Project['Projects'])-1
                self.selectedProject=SignalIntegrity.App.Project['Selected']
            selectedProject=SignalIntegrity.App.Project['Projects'][SignalIntegrity.App.Project['Selected']]
            SignalIntegrity.App.Project.dict['CalculationProperties']=selectedProject['CalculationProperties']
            SignalIntegrity.App.Project.dict['PostProcessing']=selectedProject['PostProcessing']
            selectedPage=selectedProject['Pages'][selectedProject['Selected']]
            SignalIntegrity.App.Project.dict['Drawing']=selectedPage['Drawing']
            self.projectList[self.selectedProject].SelectProject()
            active_tab = self.tabControl.index(self.tabControl.select())
            self.tabControl.forget(active_tab)
        self.Drawing().InitFromProject()
        self.Drawing().stateMachine.Nothing()

    def onTearOff(self,event):
#         print('widget:', event.widget)
#         print('x:', event.x)
#         print('y:', event.y)
# 
#         #selected = nb.identify(event.x, event.y)
#         #print('selected:', selected) # it's not usefull
# 
        clicked_tab = self.tabControl.tk.call(self.tabControl._w, "identify", "tab", event.x, event.y)
#         print('clicked tab:', clicked_tab)
# 
        active_tab = self.tabControl.index(self.tabControl.select())
#         print(' active tab:', active_tab)
        if clicked_tab == '':
            self.parent.tk.call('tk_popup',self.noTabTearOffMenu, event.x_root, event.y_root)
        else:
            self.tabControl.focus_set()
            self.parent.tk.call('tk_popup',self.tabTearOffMenu, event.x_root, event.y_root)

    def onTouched(self,event):
        clicked_tab = self.tabControl.tk.call(self.tabControl._w, "identify", "tab", event.x, event.y)
        print('clicked tab:', clicked_tab)
        active_tab = self.tabControl.index(self.tabControl.select())
        print(' active tab:', active_tab)
        if clicked_tab == '':
            return
        if clicked_tab == active_tab:
            return
        self.SelectTab(clicked_tab)
    def SelectTab(self,tab):
        selectedProject=SignalIntegrity.App.Project['Projects'][SignalIntegrity.App.Project['Selected']]
        selectedProject.dict['CalculationProperties']=SignalIntegrity.App.Project['CalculationProperties']
        selectedProject.dict['PostProcessing']=SignalIntegrity.App.Project['PostProcessing']
        selectedPage=selectedProject['Pages'][selectedProject['Selected']]
        selectedPage.dict['Drawing']=SignalIntegrity.App.Project['Drawing']
        self.selectedProject=tab
        SignalIntegrity.App.Project['Selected']=self.selectedProject
        selectedProject=SignalIntegrity.App.Project['Projects'][SignalIntegrity.App.Project['Selected']]
        SignalIntegrity.App.Project.dict['CalculationProperties']=selectedProject['CalculationProperties']
        SignalIntegrity.App.Project.dict['PostProcessing']=selectedProject['PostProcessing']
        selectedPage=selectedProject['Pages'][selectedProject['Selected']]
        SignalIntegrity.App.Project.dict['Drawing']=selectedPage['Drawing']
        self.projectList[self.selectedProject].SelectProject()
        self.Drawing().InitFromProject()
        self.Drawing().stateMachine.Nothing()

class Project(ttk.Frame):
    def __init__(self,parent,root):
        super().__init__(parent.tabControl)
        self.parent=parent
        self.root=root
        self.Drawing = None
    def SelectProject(self):
        if self.Drawing == None:
            self.Drawing=Drawing(self,self.root)
            self.Drawing.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)