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
else:
    import tkinter as tk
    from tkinter import ttk

import SignalIntegrity.App.Project

from SignalIntegrity.App.Schematic import Drawing

#         self.tabControl=ttk.Notebook(self)
#         self.tab1=ttk.Frame(self.tabControl)
#         self.tabControl.add(self.tab1,text='Page 1')
#         self.tabControl.pack(expand=1,fill=tk.BOTH)

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
        self.tabControl.bind('<Button-3>', self.onTouched)
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
    def DeleteSelectedTab(self):
        pass
    def OpenNewProject(self):
        pass
    def onTouched(self,event):
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