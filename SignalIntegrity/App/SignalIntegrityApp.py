"""
SignalIntegrityApp.py
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
    import tkFont as font
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import font
    from tkinter import messagebox


import copy
import os

import matplotlib
matplotlib.use('TkAgg')

from SignalIntegrity.App.PartPicture import PartPicture
from SignalIntegrity.App.PartProperty import PartPropertyReferenceDesignator
from SignalIntegrity.App.Device import DeviceList,DeviceListUnknown,DeviceListSystem
from SignalIntegrity.App.Device import DeviceOutput,DeviceMeasurement,Port,DeviceStim
from SignalIntegrity.App.DeviceProperties import DevicePropertiesDialog
from SignalIntegrity.App.DevicePicker import DevicePickerDialog
from SignalIntegrity.App.Schematic import Drawing
from SignalIntegrity.App.Simulator import Simulator
from SignalIntegrity.App.NetList import NetListDialog
from SignalIntegrity.App.SParameterViewerWindow import SParametersDialog
from SignalIntegrity.App.Files import FileParts,ConvertFileNameToRelativePath
from SignalIntegrity.App.History import History
from SignalIntegrity.App.MenuSystemHelpers import Doer,StatusBar
from SignalIntegrity.App.BuildHelpSystem import HelpSystemKeys
from SignalIntegrity.App.ProgressDialog import ProgressDialog
from SignalIntegrity.App.About import AboutDialog
from SignalIntegrity.App.Preferences import Preferences
from SignalIntegrity.App.PreferencesDialog import PreferencesDialog
from SignalIntegrity.App.FilePicker import AskSaveAsFilename,AskOpenFileName
from SignalIntegrity.App.ProjectFile import ProjectFile
from SignalIntegrity.App.CalculationPropertiesDialog import CalculationPropertiesDialog
from SignalIntegrity.__about__ import __version__,__project__
import SignalIntegrity.App.Project

class SignalIntegrityApp(tk.Frame):
    def __init__(self,projectFileName=None,runMainLoop=True,external=False):
        thisFileDir=os.path.dirname(os.path.realpath(__file__))
        sys.path=[thisFileDir]+sys.path

        SignalIntegrity.App.Preferences=Preferences()
        self.external=external
        self.root = tk.Tk()
        self.root.withdraw()

        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)

        self.UpdateColorsAndFonts()

        tk.Frame.__init__(self, self.root)
        self.pack(fill=tk.BOTH, expand=tk.YES)
        SignalIntegrity.App.Installdir=os.path.dirname(os.path.abspath(__file__))+'/'
        SignalIntegrity.App.IconsBaseDir=SignalIntegrity.App.Installdir+'icons/png/'
        SignalIntegrity.App.IconsDir=SignalIntegrity.App.IconsBaseDir+'16x16/actions/'

        self.root.title(__project__+' - '+__version__)

        img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.root.tk.call('wm', 'iconphoto', self.root._w, '-default', img)

        Doer.helpKeys = HelpSystemKeys(SignalIntegrity.App.Preferences['OnlineHelp.RebuildHelpKeys'])

        HelpSystemKeys.InstallHelpURLBase(SignalIntegrity.App.Preferences['OnlineHelp.UseOnlineHelp'],
                                          SignalIntegrity.App.Preferences['OnlineHelp.URL'])

        # status bar
        self.statusbar=StatusBar(self)

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.RecentProject0Doer = Doer(self.onRecentProject0).Activate(False)
        self.RecentProject1Doer = Doer(self.onRecentProject1).Activate(False)
        self.RecentProject2Doer = Doer(self.onRecentProject2).Activate(False)
        self.RecentProject3Doer = Doer(self.onRecentProject3).Activate(False)
        self.NewProjectDoer = Doer(self.onNewProject).AddKeyBindElement(self.root,'<Control-n>').AddHelpElement('Control-Help:New-Project')
        self.OpenProjectDoer = Doer(self.onReadProjectFromFile).AddKeyBindElement(self.root,'<Control-o>').AddHelpElement('Control-Help:Open-Project')
        self.SaveProjectDoer = Doer(self.onSaveProject).AddKeyBindElement(self.root,'<Control-s>').AddHelpElement('Control-Help:Save-Project')
        self.SaveAsProjectDoer = Doer(self.onSaveAsProject).AddKeyBindElement(self.root,'<Control-Shift-s>').AddHelpElement('Control-Help:Save-As-Project')
        self.ClearProjectDoer = Doer(self.onClearSchematic).AddHelpElement('Control-Help:Clear-Schematic')
        self.ExportNetListDoer = Doer(self.onExportNetlist).AddHelpElement('Control-Help:Export-Netlist')
        self.ExportTpXDoer = Doer(self.onExportTpX).AddHelpElement('Control-Help:Export-LaTeX')
        # ------
        self.UndoDoer = Doer(self.onUndo).AddKeyBindElement(self.root,'<Control-z>').AddHelpElement('Control-Help:Undo')
        self.RedoDoer = Doer(self.onRedo).AddKeyBindElement(self.root,'<Control-Z>').AddHelpElement('Control-Help:Redo')
        self.DeleteSelectedDoer = Doer(self.onDeleteSelected).AddKeyBindElement(self.root,'<Delete>').AddHelpElement('Control-Help:Delete-Selected')
        self.DuplicateSelectedDoer = Doer(self.onDuplicateSelected).AddKeyBindElement(self.root,'<Control-c>').AddHelpElement('Control-Help:Duplicate-Selected')
        self.CutSelectedDoer = Doer(self.onCutMultipleSelections).AddKeyBindElement(self.root,'<Control-x>').AddHelpElement('Control-Help:Cut-Selected')
        # ------
        self.AddPartDoer = Doer(self.onAddPart).AddHelpElement('Control-Help:Add-Part')
        self.AddPortDoer = Doer(self.onAddPort).AddHelpElement('Control-Help:Add-Port')
        self.AddMeasureProbeDoer = Doer(self.onAddMeasureProbe).AddHelpElement('Control-Help:Add-Measure-Probe')
        self.AddOutputProbeDoer = Doer(self.onAddOutputProbe).AddHelpElement('Control-Help:Add-Output-Probe')
        self.AddStimDoer = Doer(self.onAddStim).AddHelpElement('Control-Help:Add-Stim')
        self.AddUnknownDoer = Doer(self.onAddUnknown).AddHelpElement('Control-Help:Add-Unknown')
        self.AddSystemDoer = Doer(self.onAddSystem).AddHelpElement('Control-Help:Add-System')
        self.DeletePartDoer = Doer(self.onDeletePart).AddHelpElement('Control-Help:Delete-Part')
        self.EditPropertiesDoer = Doer(self.onEditProperties).AddHelpElement('Control-Help:Edit-Properties')
        self.DuplicatePartDoer = Doer(self.onDuplicate).AddHelpElement('Control-Help:Duplicate-Part')
        self.RotatePartDoer = Doer(self.onRotatePart).AddHelpElement('Control-Help:Rotate-Part')
        self.FlipPartHorizontallyDoer = Doer(self.onFlipPartHorizontally).AddHelpElement('Control-Help:Flip-Horizontally')
        self.FlipPartVerticallyDoer = Doer(self.onFlipPartVertically).AddHelpElement('Control-Help:Flip-Vertically')
        # ------
        self.AddWireDoer = Doer(self.onAddWire).AddHelpElement('Control-Help:Add-Wire')
        self.DeleteVertexDoer = Doer(self.onDeleteSelectedVertex).AddHelpElement('Control-Help:Delete-Vertex')
        self.DuplicateVertexDoer = Doer(self.onDuplicateSelectedVertex).AddHelpElement('Control-Help:Duplicate-Vertex')
        self.DeleteWireDoer = Doer(self.onDeleteSelectedWire).AddHelpElement('Control-Help:Delete-Wire')
        # ------
        self.ZoomInDoer = Doer(self.onZoomIn).AddHelpElement('Control-Help:Zoom-In')
        self.ZoomOutDoer = Doer(self.onZoomOut).AddHelpElement('Control-Help:Zoom-Out')
        self.PanDoer = Doer(self.onPan).AddHelpElement('Control-Help:Pan')
        # ------
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties).AddHelpElement('Control-Help:Calculation-Properties')
        self.SParameterViewerDoer = Doer(self.onSParameterViewer).AddHelpElement('Control-Help:S-parameter-Viewer')
        self.CalculateDoer = Doer(self.onCalculate).AddHelpElement('Control-Help:Calculate-tk.Button')
        self.CalculateSParametersDoer = Doer(self.onCalculateSParameters).AddHelpElement('Control-Help:Calculate-S-parameters')
        self.SimulateDoer = Doer(self.onSimulate).AddHelpElement('Control-Help:Simulate')
        self.VirtualProbeDoer = Doer(self.onVirtualProbe).AddHelpElement('Control-Help:Virtual-Probe')
        self.DeembedDoer = Doer(self.onDeembed).AddHelpElement('Control-Help:Deembed')
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement('Control-Help:Open-Help-File')
        self.PreferencesDoer=Doer(self.onPreferences).AddHelpElement('Control-Help:Preferences')
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement('Control-Help:Control-Help')
        self.AboutDoer = Doer(self.onAbout).AddHelpElement('Control-Help:About')
        # ------
        self.EscapeDoer = Doer(self.onEscape).AddKeyBindElement(self.root, '<Escape>').DisableHelp()

        # this is a secret key binding to build the help keys for the help system
        self.BuildHelpKeysDoer = Doer(self.onBuildHelpKeys).AddKeyBindElement(self.root,'<Control-Alt-h>').Activate(True)

        # The menu system
        TheMenu=tk.Menu(self.root)
        self.root.config(menu=TheMenu)
        self.FileMenu=tk.Menu(self)
        TheMenu.add_cascade(label='File',menu=self.FileMenu,underline=0)
        self.RecentsMenu=tk.Menu(self.FileMenu)
        self.FileMenu.add_cascade(label='Open Recent Projects',menu=self.RecentsMenu,underline=5)
        self.RecentProject0Doer.AddMenuElement(self.RecentsMenu,label='')
        self.RecentProject1Doer.AddMenuElement(self.RecentsMenu,label='')
        self.RecentProject2Doer.AddMenuElement(self.RecentsMenu,label='')
        self.RecentProject3Doer.AddMenuElement(self.RecentsMenu,label='')
        self.FileMenu.add_separator()
        self.NewProjectDoer.AddMenuElement(self.FileMenu,label="New Project",accelerator='Ctrl+N',underline=0)
        self.OpenProjectDoer.AddMenuElement(self.FileMenu,label="Open Project",accelerator='Ctrl+O',underline=0)
        self.SaveProjectDoer.AddMenuElement(self.FileMenu,label="Save Project",accelerator='Ctrl+S',underline=0)
        self.SaveAsProjectDoer.AddMenuElement(self.FileMenu,label="Save Project As...",accelerator='Ctrl+Shift-S',underline=1)
        self.FileMenu.add_separator()
        self.ClearProjectDoer.AddMenuElement(self.FileMenu,label="Clear Schematic",underline=0)
        self.FileMenu.add_separator()
        self.ExportNetListDoer.AddMenuElement(self.FileMenu,label="Export NetList",underline=0)
        self.ExportTpXDoer.AddMenuElement(self.FileMenu,label="Export LaTeX (TikZ)",underline=7)
        # ------
        EditMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Edit',menu=EditMenu,underline=0)
        self.UndoDoer.AddMenuElement(EditMenu,label="Undo",accelerator='Ctrl+Z', underline=0)
        self.RedoDoer.AddMenuElement(EditMenu,label="Redo",accelerator='Ctrl+Shift+Z',underline=0)
        EditMenu.add_separator()
        # ------
        self.DeleteSelectedDoer.AddMenuElement(EditMenu,label='Delete Selected',accelerator='Del',underline=0)
        self.DuplicateSelectedDoer.AddMenuElement(EditMenu,label='Duplicate Selected',accelerator='Ctrl+C',underline=1)
        self.CutSelectedDoer.AddMenuElement(EditMenu,label='Cut Selected',accelerator='Ctrl+tk.X',underline=0)
        # ------
        PartsMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Parts',menu=PartsMenu,underline=0)
        self.AddPartDoer.AddMenuElement(PartsMenu,label='Add Part',underline=0)
        self.AddPortDoer.AddMenuElement(PartsMenu,label='Add Port',underline=6)
        self.AddOutputProbeDoer.AddMenuElement(PartsMenu,label='Add Output Probe',underline=4)
        self.AddMeasureProbeDoer.AddMenuElement(PartsMenu,label='Add Measure Probe',underline=4)
        self.AddStimDoer.AddMenuElement(PartsMenu,label='Add Stim',underline=5)
        self.AddUnknownDoer.AddMenuElement(PartsMenu,label='Add Unknown',underline=4)
        self.AddSystemDoer.AddMenuElement(PartsMenu,label='Add System',underline=4)
        PartsMenu.add_separator()
        self.DeletePartDoer.AddMenuElement(PartsMenu,label='Delete Part',underline=0)
        PartsMenu.add_separator()
        self.EditPropertiesDoer.AddMenuElement(PartsMenu,label='Edit Properties',underline=0)
        self.DuplicatePartDoer.AddMenuElement(PartsMenu,label='Duplicate Part',accelerator='Ctrl+C',underline=0)
        self.RotatePartDoer.AddMenuElement(PartsMenu,label='Rotate Part',underline=0)
        self.FlipPartHorizontallyDoer.AddMenuElement(PartsMenu,label='Flip Horizontally',underline=5)
        self.FlipPartVerticallyDoer.AddMenuElement(PartsMenu,label='Flip Vertically',underline=5)
        # ------
        WireMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Wires',menu=WireMenu,underline=0)
        self.AddWireDoer.AddMenuElement(WireMenu,label='Add Wire',underline=0)
        WireMenu.add_separator()
        self.DeleteVertexDoer.AddMenuElement(WireMenu,label='Delete Vertex',underline=7)
        self.DuplicateVertexDoer.AddMenuElement(WireMenu,label='Duplicate Vertex',underline=1)
        self.DeleteWireDoer.AddMenuElement(WireMenu,label='Delete Wire',underline=0)
        # ------
        ViewMenu=tk.Menu(self)
        TheMenu.add_cascade(label='View',menu=ViewMenu,underline=0)
        self.ZoomInDoer.AddMenuElement(ViewMenu,label='Zoom In',underline=5)
        self.ZoomOutDoer.AddMenuElement(ViewMenu,label='Zoom Out',underline=5)
        self.PanDoer.AddMenuElement(ViewMenu,label='Pan',underline=0)
        # ------
        CalcMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Calculate',menu=CalcMenu,underline=0)
        self.CalculationPropertiesDoer.AddMenuElement(CalcMenu,label='Calculation Properties',underline=12)
        self.SParameterViewerDoer.AddMenuElement(CalcMenu,label='S-parameter Viewer',underline=12)
        CalcMenu.add_separator()
        self.CalculateSParametersDoer.AddMenuElement(CalcMenu,label='Calculate S-parameters',underline=0)
        self.SimulateDoer.AddMenuElement(CalcMenu,label='Simulate',underline=0)
        self.VirtualProbeDoer.AddMenuElement(CalcMenu,label='Virtual Probe',underline=9)
        self.DeembedDoer.AddMenuElement(CalcMenu,label='Deembed',underline=0)
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)
        self.PreferencesDoer.AddMenuElement(HelpMenu,label='Preferences',underline=0)
        self.AboutDoer.AddMenuElement(HelpMenu,label='About',underline=0)

        # The Toolbar
        ToolBarFrame = tk.Frame(self)
        ToolBarFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        iconsdir=SignalIntegrity.App.IconsDir+''
        self.NewProjectDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'document-new-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.OpenProjectDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'document-open-2.gif',).Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.SaveProjectDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'document-save-2.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(ToolBarFrame,bd=2,relief=tk.SUNKEN).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.AddPartDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'edit-add-2.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.DeleteSelectedDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'edit-delete-6.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.AddWireDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'draw-line-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.DuplicateSelectedDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'edit-copy-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.RotatePartDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'object-rotate-left-4.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.FlipPartHorizontallyDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'object-flip-horizontal-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.FlipPartVerticallyDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'object-flip-vertical-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(ToolBarFrame,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.ZoomInDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'zoom-in-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.ZoomOutDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'zoom-out-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.PanDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'edit-move.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(ToolBarFrame,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.CalculationPropertiesDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'tooloptions.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.CalculateDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'system-run-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(ToolBarFrame,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.SParameterViewerDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'sp-view.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(ToolBarFrame,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.HelpDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'help-contents-5.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.ControlHelpDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'help-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        # ------
        UndoFrame=tk.Frame(ToolBarFrame)
        UndoFrame.pack(side=tk.RIGHT,fill=tk.NONE,expand=tk.NO,anchor=tk.E)
        self.UndoDoer.AddToolBarElement(UndoFrame,iconfile=iconsdir+'edit-undo-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO,anchor=tk.E)
        self.RedoDoer.AddToolBarElement(UndoFrame,iconfile=iconsdir+'edit-redo-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO,anchor=tk.E)

        # The Drawing (which contains the schecmatic)
        self.Drawing=Drawing(self)
        self.Drawing.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)

        self.statusbar.pack(side=tk.BOTTOM,fill=tk.X,expand=tk.NO)
        self.root.bind('<Key>',self.onKey)

        SignalIntegrity.App.Project=ProjectFile()
        self.Drawing.InitFromProject()

        # The Simulator Dialog
        self.simulator = Simulator(self)
        self.fileparts=FileParts()

        # The edit history (for undo)
        self.history=History(self)

        # we capture resizing so we can resize the canvas a bit smaller to allow the user
        # to always see the status message bar.  But we don't know how much smaller initially.
        # so we capture the first call to resize which occurs when the canvas is sized.
        # the canvas is 600 x 600 so the difference between these amounts is the delta to apply on
        # subsequent resize calls.
        self.knowDelta=False
        self.deltaWidth=0
        self.deltaHeight=0
        self.bind('<Configure>',self.onResize)

        if projectFileName is None:
            projectFileName = SignalIntegrity.App.Preferences.GetLastFileOpened()

        if not projectFileName == None:
            try:
                self.OpenProjectFile(projectFileName,False)
            except:
                self.onClearSchematic()
                self.Drawing.stateMachine.NoProject(True)

        self.UpdateRecentProjectsMenu()
        self.root.deiconify()
        if runMainLoop:
            self.root.mainloop()

    def onResize(self,event):
        if not self.knowDelta:
            self.deltaWidth=event.width-600
            self.deltaHeight=event.height-600
            self.knowDelta=True
        #print 'width: '+str(event.width)+', height'+str(event.height)
        
        self.deltaWidth=4
        self.deltaHeight=50

        try:
            self.Drawing.canvas.config(width=event.width-self.deltaWidth,height=event.height-self.deltaHeight)
            SignalIntegrity.App.Project['Drawing.DrawingProperties.Width']=self.Drawing.canvas.winfo_width()
            SignalIntegrity.App.Project['Drawing.DrawingProperties.Height']=self.Drawing.canvas.winfo_height()
            SignalIntegrity.App.Project['Drawing.DrawingProperties.Geometry']=self.root.geometry()
        except tk.TclError:
            pass

    def onKey(self,event):
#       print "pressed", repr(event.keycode), repr(event.keysym)
        if event.keysym == 'Delete': # delete
            self.Drawing.DeleteSelected()

    def onUndo(self):
        self.history.Undo()
        self.Drawing.DrawSchematic()

    def onRedo(self):
        self.history.Redo()
        self.Drawing.DrawSchematic()

    def onReadProjectFromFile(self):
        if not self.CheckSaveCurrentProject():
            return

        filename=AskOpenFileName(filetypes=[('si', '.si')],
                                 initialdir=self.fileparts.AbsoluteFilePath(),
                                 initialfile=self.fileparts.FileNameWithExtension('.si'))
        if filename is None:
            return
        self.OpenProjectFile(filename)

    def OpenProjectFile(self,filename,showError=True):
        if filename is None:
            filename=''
        if isinstance(filename,tuple):
            filename=''
        filename=str(filename)
        if filename=='':
            return

        self.fileparts=FileParts(filename)
        os.chdir(self.fileparts.AbsoluteFilePath())
        self.fileparts=FileParts(filename)
        try:
            SignalIntegrity.App.Project=ProjectFile().Read(self.fileparts.FullFilePathExtension('.si'))
            self.Drawing.InitFromProject()
            self.AnotherFileOpened(self.fileparts.FullFilePathExtension('.si'))
            self.Drawing.stateMachine.Nothing()
            self.history.Event('read project')
            self.root.title('SignalIntegrity: '+self.fileparts.FileNameTitle())
        except:
            if showError:
                messagebox.showerror('Project File:',self.fileparts.FileNameWithExtension()+' could not be opened')

    def onNewProject(self):
        if not self.CheckSaveCurrentProject():
            return
        filename=AskSaveAsFilename(filetypes=[('si', '.si')],
                                   defaultextension='.si',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   title='new project file')
        if filename is None:
            return
        SignalIntegrity.App.Project=ProjectFile()
        self.Drawing.InitFromProject()
        self.Drawing.DrawSchematic()
        self.history.Event('new project')
        self.SaveProjectToFile(filename)

    def SaveProjectToFile(self,filename):
        self.Drawing.stateMachine.Nothing()
        self.fileparts=FileParts(filename)
        os.chdir(self.fileparts.AbsoluteFilePath())
        self.fileparts=FileParts(filename)
        SignalIntegrity.App.Project.Write(self,filename)
        filename=ConvertFileNameToRelativePath(filename)
        self.AnotherFileOpened(filename)
        self.root.title("SignalIntegrity: "+self.fileparts.FileNameTitle())
        self.statusbar.set('Project Saved')

    def onSaveProject(self):
        if self.fileparts.filename=='':
            return
        filename=self.fileparts.AbsoluteFilePath()+'/'+self.fileparts.FileNameWithExtension(ext='.si')
        self.SaveProjectToFile(filename)

    def onSaveAsProject(self):
        filename=AskSaveAsFilename(filetypes=[('si', '.si')],
                                   defaultextension='.si',
                                   initialfile=self.fileparts.FileNameWithExtension('.si'),
                                   initialdir=self.fileparts.AbsoluteFilePath())
        if filename is None:
            return
        self.SaveProjectToFile(filename)

    def onClearSchematic(self):
        self.Drawing.stateMachine.Nothing()
        self.Drawing.schematic.Clear()
        self.history.Event('clear project')
        self.Drawing.DrawSchematic()
        #self.fileparts=FileParts()
        #self.root.title('SignalIntegrity')

    def AnotherFileOpened(self,filename):
        SignalIntegrity.App.Preferences.AnotherFileOpened(filename,not self.external)
        self.UpdateRecentProjectsMenu()

    def UpdateRecentProjectsMenu(self):
        recentFileList=SignalIntegrity.App.Preferences.GetRecentFileList()
        if recentFileList is None:
            recentFileList=[None,None,None,None]
        if all(r is None for r in recentFileList):
            self.FileMenu.entryconfigure(1,state='disabled')
        else:
            self.FileMenu.entryconfigure(1,state='normal')

        if recentFileList[0] is None:
            self.RecentsMenu.entryconfig(1, label='')
            self.RecentProject0Doer.menuElement.label=''
            self.RecentProject0Doer.Activate(False)
        else:
            self.RecentsMenu.entryconfig(1, label=recentFileList[0])
            self.RecentProject0Doer.menuElement.label=recentFileList[0]
            self.RecentProject0Doer.Activate(True)
        if recentFileList[1] is None:
            self.RecentsMenu.entryconfig(2, label='')
            self.RecentProject1Doer.menuElement.label=''
            self.RecentProject1Doer.Activate(False)
        else:
            self.RecentsMenu.entryconfig(2, label=recentFileList[1])
            self.RecentProject1Doer.menuElement.label=recentFileList[1]
            self.RecentProject1Doer.Activate(True)
        if recentFileList[2] is None:
            self.RecentsMenu.entryconfig(3, label='')
            self.RecentProject2Doer.menuElement.label=''
            self.RecentProject2Doer.Activate(False)
        else:
            self.RecentsMenu.entryconfig(3, label=recentFileList[2])
            self.RecentProject2Doer.menuElement.label=recentFileList[2]
            self.RecentProject2Doer.Activate(True)
        if recentFileList[3] is None:
            self.RecentsMenu.entryconfig(4, label='')
            self.RecentProject3Doer.menuElement.label=''
            self.RecentProject3Doer.Activate(False)
        else:
            self.RecentsMenu.entryconfig(4, label=recentFileList[3])
            self.RecentProject3Doer.menuElement.label=recentFileList[3]
            self.RecentProject3Doer.Activate(True)

    def onRecentProject0(self):
        if not self.CheckSaveCurrentProject():
            return False
        self.OpenProjectFile(SignalIntegrity.App.Preferences.GetLastFileOpened(0))

    def onRecentProject1(self):
        if not self.CheckSaveCurrentProject():
            return False
        self.OpenProjectFile(SignalIntegrity.App.Preferences.GetLastFileOpened(1))

    def onRecentProject2(self):
        if not self.CheckSaveCurrentProject():
            return False
        self.OpenProjectFile(SignalIntegrity.App.Preferences.GetLastFileOpened(2))

    def onRecentProject3(self):
        if not self.CheckSaveCurrentProject():
            return False
        self.OpenProjectFile(SignalIntegrity.App.Preferences.GetLastFileOpened(3))

    def onExportNetlist(self):
        self.Drawing.stateMachine.Nothing()
        NetListDialog(self,self.Drawing.schematic.NetList().Text())

    def onExportTpX(self):
        from SignalIntegrity.App.TpX import TpX
        from SignalIntegrity.App.TikZ import TikZ
        self.Drawing.stateMachine.Nothing()
        filename=AskSaveAsFilename(filetypes=[('tpx', '.TpX')],
                                   defaultextension='.TpX',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   initialfile=self.fileparts.filename+'.TpX')
        if filename is None:
            return
        try:
            tpx=self.Drawing.DrawSchematic(TpX()).Finish()
            tikz=self.Drawing.DrawSchematic(TikZ()).Finish()
            #tikz.Document()
            tpx.lineList=tpx.lineList+tikz.lineList
            tpx.WriteToFile(filename)
        except:
            messagebox.showerror('Export LaTeX','LaTeX could not be generated or written ')

    def onAddPart(self):
        self.onAddPartFromSpecificList(DeviceList+DeviceListUnknown+DeviceListSystem)

    def onAddUnknown(self):
        self.onAddPartFromSpecificList(DeviceListUnknown)

    def onAddSystem(self):
        self.onAddPartFromSpecificList(DeviceListSystem)

    def onAddPartFromSpecificList(self,deviceList):
        self.Drawing.stateMachine.Nothing()
        dpd=DevicePickerDialog(self,deviceList)
        if dpd.result != None:
            if deviceList[dpd.result]['partname'].GetValue() == 'Port':
                self.onAddPort()
                return
            else:
                devicePicked=copy.deepcopy(deviceList[dpd.result])
                devicePicked.AddPartProperty(PartPropertyReferenceDesignator(''))
                defaultProperty = devicePicked['defref']
                if defaultProperty != None:
                    defaultPropertyValue = defaultProperty.GetValue()
                    uniqueReferenceDesignator = self.Drawing.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
                    if uniqueReferenceDesignator != None:
                        devicePicked['ref'].SetValueFromString(uniqueReferenceDesignator)
                dpe=DevicePropertiesDialog(self,devicePicked)
            if dpe.result != None:
                self.Drawing.partLoaded = dpe.result
                self.Drawing.stateMachine.PartLoaded()

    def onDeletePart(self):
        self.Drawing.DeleteSelectedDevice()
    def onDeleteSelected(self):
        self.Drawing.DeleteSelected()
    def onEditProperties(self):
        self.Drawing.EditSelectedDevice()
    def onRotatePart(self):
        if self.Drawing.stateMachine.state == 'DeviceSelected':
            self.Drawing.deviceSelected.partPicture.current.Rotate()
            self.Drawing.DrawSchematic()
            self.history.Event('rotate')
    def onFlipPartHorizontally(self):
        if self.Drawing.stateMachine.state == 'DeviceSelected':
            orientation = self.Drawing.deviceSelected.partPicture.current.orientation
            mirroredHorizontally = self.Drawing.deviceSelected.partPicture.current.mirroredHorizontally
            mirroredVertically = self.Drawing.deviceSelected.partPicture.current.mirroredVertically
            self.Drawing.deviceSelected.partPicture.current.ApplyOrientation(orientation,not mirroredHorizontally,mirroredVertically)
            self.Drawing.DrawSchematic()
            self.history.Event('flip horizontally')
    def onFlipPartVertically(self):
        if self.Drawing.stateMachine.state == 'DeviceSelected':
            orientation = self.Drawing.deviceSelected.partPicture.current.orientation
            mirroredHorizontally = self.Drawing.deviceSelected.partPicture.current.mirroredHorizontally
            mirroredVertically = self.Drawing.deviceSelected.partPicture.current.mirroredVertically
            self.Drawing.deviceSelected.partPicture.current.ApplyOrientation(orientation,mirroredHorizontally,not mirroredVertically)
            self.Drawing.DrawSchematic()
            self.history.Event('flip vertically')
    def onDuplicateSelected(self):
        self.Drawing.DuplicateSelected()
    def onCutMultipleSelections(self):
        self.Drawing.CutMultipleSelections()
    def onDuplicate(self):
        self.Drawing.DuplicateSelectedDevice()
    def onAddWire(self):
        from SignalIntegrity.App.Wire import Vertex,Wire
        wireProject=Wire()
        wireProject['Vertices']=[Vertex((0,0),False)]
        self.Drawing.wireLoaded=wireProject
        wireListProject=SignalIntegrity.App.Project['Drawing.Schematic.Wires']
        wireListProject.append(self.Drawing.wireLoaded)
        self.Drawing.stateMachine.WireLoaded()
    def onAddPort(self):
        self.Drawing.stateMachine.Nothing()
        portNumber=1
        for device in self.Drawing.schematic.deviceList:
            if device['partname'].GetValue() == 'Port':
                if portNumber <= int(device['pn'].GetValue()):
                    portNumber = int(device['pn'].GetValue())+1
        dpe=DevicePropertiesDialog(self,Port(portNumber))
        if dpe.result != None:
            self.Drawing.partLoaded = dpe.result
            self.Drawing.stateMachine.PartLoaded()

    def onAddOutputProbe(self):
        self.AddSpecificPart(DeviceOutput())

    def onAddMeasureProbe(self):
        self.AddSpecificPart(DeviceMeasurement())

    def onAddStim(self):
        self.AddSpecificPart(DeviceStim())

    def AddSpecificPart(self,part):
        self.Drawing.stateMachine.Nothing()
        devicePicked=part
        devicePicked.AddPartProperty(PartPropertyReferenceDesignator(''))
        defaultProperty = devicePicked['defref']
        if defaultProperty != None:
            defaultPropertyValue = defaultProperty.GetValue()
            uniqueReferenceDesignator = self.Drawing.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
            if uniqueReferenceDesignator != None:
                devicePicked['ref'].SetValueFromString(uniqueReferenceDesignator)
        dpe=DevicePropertiesDialog(self,devicePicked)
        if dpe.result != None:
            self.Drawing.partLoaded = dpe.result
            self.Drawing.stateMachine.PartLoaded()

    def onZoomIn(self):
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        drawingPropertiesProject['Grid']=drawingPropertiesProject['Grid']+1.
        self.Drawing.DrawSchematic()

    def onZoomOut(self):
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        drawingPropertiesProject['Grid'] = max(1,drawingPropertiesProject['Grid']-1.)
        self.Drawing.DrawSchematic()

    def onPan(self):
        self.Drawing.stateMachine.Panning()

    def onDeleteSelectedVertex(self):
        self.Drawing.DeleteSelectedVertex()

    def onDuplicateSelectedVertex(self):
        self.Drawing.DuplicateSelectedVertex()

    def onDeleteSelectedWire(self):
        self.Drawing.DeleteSelectedWire()

    def onCalculateSParameters(self):
        self.Drawing.stateMachine.Nothing()
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        spnp=si.p.SystemSParametersNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']),
            cacheFileName=cacheFileName)
        spnp.AddLines(netList)
        progressDialog = ProgressDialog(self,"Calculating S-parameters",spnp,spnp.SParameters,granularity=1.0)
        try:
            sp=progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('S-parameter Calculator',e.parameter+': '+e.message)                
            return
        SParametersDialog(self,sp,filename=self.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'))

    def onCalculationProperties(self):
        self.Drawing.stateMachine.Nothing()
        if not hasattr(self, 'calculationPropertiesDialog'):
            self.calculationPropertiesDialog = CalculationPropertiesDialog(self)
        if self.calculationPropertiesDialog == None:
            self.calculationPropertiesDialog= CalculationPropertiesDialog(self)
        else:
            if not self.calculationPropertiesDialog.winfo_exists():
                self.calculationPropertiesDialog=CalculationPropertiesDialog(self)
        self.calculationPropertiesDialog.grab_set()

    def onSimulate(self):
        self.Drawing.stateMachine.Nothing()
        self.simulator.Simulate()

    def onVirtualProbe(self):
        self.Drawing.stateMachine.Nothing()
        self.simulator.VirtualProbe()

    def onDeembed(self):
        self.Drawing.stateMachine.Nothing()
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        dnp=si.p.DeembedderNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']),
                cacheFileName=cacheFileName)
        dnp.AddLines(netList)

        progressDialog = ProgressDialog(self,"Calculating De-embedded S-parameters",dnp,dnp.Deembed,granularity=1.0)
        try:
            sp=progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Deembedder',e.parameter+': '+e.message)
            return
        unknownNames=dnp.m_sd.UnknownNames()
        if len(unknownNames)==1:
            sp=[sp]
        for u in range(len(unknownNames)):
            extension='.s'+str(sp[u].m_P)+'p'
            filename=unknownNames[u]+extension
            if self.fileparts.filename != '':
                filename=self.fileparts.filename+'_'+filename
            SParametersDialog(self,sp[u],filename=filename)

    def onCalculate(self):
        self.Drawing.stateMachine.Nothing()
        self.Drawing.DrawSchematic()
        self.SimulateDoer.Execute()
        self.CalculateSParametersDoer.Execute()
        self.VirtualProbeDoer.Execute()
        self.DeembedDoer.Execute()

    def onSParameterViewer(self):
        import SignalIntegrity.Lib as si
        filename=AskOpenFileName(filetypes=[('s-parameter files', ('*.s*p'))],
                                 parent=self,
                                 initialdir=self.fileparts.AbsoluteFilePath())
        if filename is None:
            return
        fileparts=FileParts(filename)
        if fileparts.fileext is None or fileparts.fileext == '':
            return
        sp=si.sp.SParameterFile(fileparts.FullFilePathExtension())
        SParametersDialog(self,sp,fileparts.FullFilePathExtension())

    def onHelp(self):
        if Doer.helpKeys is None:
            messagebox.showerror('Help System','Cannot find or open this help element')            
            return
        Doer.helpKeys.Open('sec:Introduction')

    def onControlHelp(self):
        Doer.inHelp = not Doer.inHelp
        if Doer.inHelp:
            self.NewProjectDoer.Activate(True)
            self.OpenProjectDoer.Activate(True)
            self.SaveProjectDoer.Activate(True)
            self.SaveAsProjectDoer.Activate(True)
            self.ClearProjectDoer.Activate(True)
            self.ExportNetListDoer.Activate(True)
            self.ExportTpXDoer.Activate(True)
            # ------
            self.UndoDoer.Activate(True)
            self.RedoDoer.Activate(True)
            # ------
            self.AddPartDoer.Activate(True)
            self.AddPortDoer.Activate(True)
            self.AddMeasureProbeDoer.Activate(True)
            self.AddOutputProbeDoer.Activate(True)
            self.AddStimDoer.Activate(True)
            self.AddUnknownDoer.Activate(True)
            self.AddSystemDoer.Activate(True)
            self.DeletePartDoer.Activate(True)
            self.DeleteSelectedDoer.Activate(True)
            self.EditPropertiesDoer.Activate(True)
            self.DuplicatePartDoer.Activate(True)
            self.DuplicateSelectedDoer.Activate(True)
            self.CutSelectedDoer.Activate(True)
            self.RotatePartDoer.Activate(True)
            self.FlipPartHorizontallyDoer.Activate(True)
            self.FlipPartVerticallyDoer.Activate(True)
            # ------
            self.AddWireDoer.Activate(True)
            self.DeleteVertexDoer.Activate(True)
            self.DuplicateVertexDoer.Activate(True)
            self.DeleteWireDoer.Activate(True)
            # ------
            self.ZoomInDoer.Activate(True)
            self.ZoomOutDoer.Activate(True)
            self.PanDoer.Activate(True)
            # ------
            self.CalculationPropertiesDoer.Activate(True)
            self.SParameterViewerDoer.Activate(True)
            self.CalculateDoer.Activate(True)
            self.CalculateSParametersDoer.Activate(True)
            self.VirtualProbeDoer.Activate(True)
            self.SimulateDoer.Activate(True)
            self.DeembedDoer.Activate(True)
            # ------
            self.HelpDoer.Activate(True)
            self.ControlHelpDoer.Activate(True)
            # ------
            self.EscapeDoer.Activate(True)

            self.config(cursor='question_arrow')

            self.statusbar.set('Control Help')

    def onEscape(self):
        if self.Drawing.stateMachine.state != 'NoProject':
            self.Drawing.stateMachine.Nothing(True)
        else:
            self.Drawing.stateMachine.NoProject(True)
        self.config(cursor='left_ptr')

    def onAbout(self):
        AboutDialog(self)

    def onPreferences(self):
        if not hasattr(self, 'preferencesDialog'):
            self.preferencesDialog = PreferencesDialog(self,SignalIntegrity.App.Preferences)
        if self.preferencesDialog == None:
            self.preferencesDialog= PreferencesDialog(self,SignalIntegrity.App.Preferences)
        else:
            if not self.preferencesDialog.winfo_exists():
                self.preferencesDialog=PreferencesDialog(self,SignalIntegrity.App.Preferences)

    def UpdateColorsAndFonts(self):
        fontSizeDesired = SignalIntegrity.App.Preferences['Appearance.FontSize']
        if not fontSizeDesired is None:
            default_font = font.nametofont("TkDefaultFont")
            try:
                default_font.configure(size=fontSizeDesired)
                self.root.option_add("*Font", default_font)
                PartPicture.textSpacing=fontSizeDesired+5
            except:
                pass

        w=tk.Button(self.root)

        backgroundColor=SignalIntegrity.App.Preferences['Appearance.Color.Background']
        if backgroundColor is None:
            backgroundColor=w['background']

        foregroundColor=SignalIntegrity.App.Preferences['Appearance.Color.Foreground']
        if foregroundColor is None:
            foregroundColor=w['foreground']

        activeForegroundColor=SignalIntegrity.App.Preferences['Appearance.Color.ActiveForeground']
        if activeForegroundColor is None:
            activeForegroundColor=w['activeforeground']

        activeBackgroundColor=SignalIntegrity.App.Preferences['Appearance.Color.ActiveBackground']
        if activeBackgroundColor is None:
            activeBackgroundColor=w['activebackground']

        disabledForegroundColor=SignalIntegrity.App.Preferences['Appearance.Color.DisabledForeground']
        if disabledForegroundColor is None:
            disabledForegroundColor=w['disabledforeground']

        try:
            self.root.tk_setPalette(
                foreground=foregroundColor,
                background=backgroundColor,
                activeforeground=activeForegroundColor,
                activebackground=activeBackgroundColor,
                disabledforeground=disabledForegroundColor
                )
        except:
            pass

        matPlotLibColor=SignalIntegrity.App.Preferences['Appearance.Color.Plot']
        if not matPlotLibColor is None:
            import matplotlib as mpl
            try:
                mpl.rc("figure", facecolor=matPlotLibColor)
            except:
                pass

        self.root.update_idletasks()

    def CheckSaveCurrentProject(self):
        if self.Drawing.stateMachine.state == 'NoProject':
            return True
        if not SignalIntegrity.App.Preferences['ProjectFiles.AskToSaveCurrentFile']:
            return True

        doit =  messagebox.askyesnocancel('Wait....','Do you want to save the current project first?')

        if doit is None:
            return False
        else:
            if doit:
                self.onSaveAsProject()
        return True

    def onClosing(self):
        if self.CheckSaveCurrentProject():
            self.root.withdraw()
            self.root.destroy()

    def onBuildHelpKeys(self):
        if Doer.helpKeys:
            Doer.helpKeys.Build()
            Doer.helpKeys.SaveToFile()

def main():
    projectFileName = None
    external=False
    if len(sys.argv) >= 2:
        projectFileName=sys.argv[1]
    for arg in sys.argv[2:]:
        if arg=='--external':
            external=True
    SignalIntegrityApp(projectFileName,external=external)

if __name__ == '__main__':
    main()
