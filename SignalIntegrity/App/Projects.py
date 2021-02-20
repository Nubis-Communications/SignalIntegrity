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
                self.Dwg.pack_forget()
                self.tabControl.pack_forget()
                self.pack_forget()
        super().__init__(parent)
        self.parent=parent
        self.root=parent
        numProjects=len(SignalIntegrity.App.Project['Projects'])
        self.tabControl=ttk.Notebook(self)
        self.projectList=[]
        if numProjects > 0:
            for i in range(len(SignalIntegrity.App.Project['Projects'])):
                projectFrame=ttk.Frame(self.tabControl)
                self.projectList.append(projectFrame)
                self.tabControl.add(projectFrame,text=SignalIntegrity.App.Project['Projects'][i]['Name'])
        else: # empty - just do something
            projectFrame=ttk.Frame(self.tabControl)
            self.projectList.append(projectFrame)
            self.tabControl.add(projectFrame,text='project')
        self.tabControl.pack(expand=1,fill=tk.BOTH)
        self.selectedProject=0
        self.Dwg=Drawing(self.projectList[self.selectedProject],self.root)
        self.Dwg.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        self.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        self.initialized=True
    def InitFromProject(self):
        self.__init__(self.parent)
        self.Drawing().InitFromProject()
    def Drawing(self):
        return self.Dwg

class Project(ttk.Frame):
    def __init__(self,i,parent,root):
        super().__init__(parent.tabControl)
        self.parent=parent
        self.root=root
        self.projectNumber=i
        self.Drawing = None
    def SelectProject(self):
        if self.Drawing == None:
            self.Drawing=Drawing(self,self.root)
            self.Drawing.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)

