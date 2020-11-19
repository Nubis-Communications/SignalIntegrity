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

from SignalIntegrity.App.ToSI import ToSI
from SignalIntegrity.App.PartPicture import PartPicture
from SignalIntegrity.App.PartProperty import PartPropertyReferenceDesignator
from SignalIntegrity.App.Device import DeviceList,DeviceListUnknown,DeviceListSystem
from SignalIntegrity.App.Device import DeviceOutput,DeviceMeasurement,Port,DeviceStim,DeviceNetName
from SignalIntegrity.App.DeviceProperties import DevicePropertiesDialog
from SignalIntegrity.App.DevicePicker import DevicePickerDialog
from SignalIntegrity.App.Schematic import Drawing
from SignalIntegrity.App.Simulator import Simulator
from SignalIntegrity.App.NetworkAnalyzer import NetworkAnalyzerSimulator
from SignalIntegrity.App.NetList import NetListDialog
from SignalIntegrity.App.SParameterViewerWindow import SParametersDialog
from SignalIntegrity.App.PostProcessingDialog import PostProcessingDialog
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
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless

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
        self.UpdateFeatures()

        tk.Frame.__init__(self, self.root)
        self.pack(fill=tk.BOTH, expand=tk.YES)
        SignalIntegrity.App.InstallDir=os.path.dirname(os.path.abspath(__file__))+'/'
        SignalIntegrity.App.IconsBaseDir=SignalIntegrity.App.InstallDir+'icons/png/'
        SignalIntegrity.App.IconsDir=SignalIntegrity.App.IconsBaseDir+'16x16/actions/'

        self.root.title(__project__+' - '+__version__)

        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.root.tk.call('wm', 'iconphoto', self.root._w, '-default', self.img)

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
        self.NewProjectDoer = Doer(self.onNewProject).AddKeyBindElement(self.root,'<Control-n>').AddHelpElement('Control-Help:New-Project').AddToolTip('Creates a new project')
        self.OpenProjectDoer = Doer(self.onReadProjectFromFile).AddKeyBindElement(self.root,'<Control-o>').AddHelpElement('Control-Help:Open-Project').AddToolTip('Open an existing project')
        self.SaveProjectDoer = Doer(self.onSaveProject).AddKeyBindElement(self.root,'<Control-s>').AddHelpElement('Control-Help:Save-Project').AddToolTip('Save the project with existing file name')
        self.SaveAsProjectDoer = Doer(self.onSaveAsProject).AddKeyBindElement(self.root,'<Control-Shift-s>').AddHelpElement('Control-Help:Save-As-Project').AddToolTip('Save the project with a new file name')
        self.ClearProjectDoer = Doer(self.onClearSchematic).AddHelpElement('Control-Help:Clear-Schematic').AddToolTip('Clear the schematic')
        self.ExportNetListDoer = Doer(self.onExportNetlist).AddHelpElement('Control-Help:Export-Netlist').AddToolTip('Export the netlist')
        self.ExportTpXDoer = Doer(self.onExportTpX).AddHelpElement('Control-Help:Export-LaTeX').AddToolTip('Export schematic as LaTeX')
        # ------
        self.UndoDoer = Doer(self.onUndo).AddKeyBindElement(self.root,'<Control-z>').AddHelpElement('Control-Help:Undo').AddToolTip('Undo last edit')
        self.RedoDoer = Doer(self.onRedo).AddKeyBindElement(self.root,'<Control-Z>').AddHelpElement('Control-Help:Redo').AddToolTip('Redo undid edit')
        self.DeleteSelectedDoer = Doer(self.onDeleteSelected).AddKeyBindElement(self.root,'Delete').AddHelpElement('Control-Help:Delete-Selected').AddToolTip('Delete selected elements')
        self.DuplicateSelectedDoer = Doer(self.onDuplicateSelected).AddKeyBindElement(self.root,'<Control-c>').AddHelpElement('Control-Help:Duplicate-Selected').AddToolTip('Duplicate selected elements')
        self.CutSelectedDoer = Doer(self.onCutMultipleSelections).AddKeyBindElement(self.root,'<Control-x>').AddHelpElement('Control-Help:Cut-Selected').AddToolTip('Cut selected elements')
        # ------
        self.AddPartDoer = Doer(self.onAddPart).AddHelpElement('Control-Help:Add-Part').AddToolTip('Add a part to the schematic')
        self.AddNetNameDoer = Doer(self.onAddNetName).AddHelpElement('Control-Help:Add-Net-Name').AddToolTip('Add a net name to the schematic')
        self.AddPortDoer = Doer(self.onAddPort).AddHelpElement('Control-Help:Add-Port').AddToolTip('Add a port to the schematic')
        self.AddMeasureProbeDoer = Doer(self.onAddMeasureProbe).AddHelpElement('Control-Help:Add-Measure-Probe').AddToolTip('Add a measure probe to the schematic')
        self.AddOutputProbeDoer = Doer(self.onAddOutputProbe).AddHelpElement('Control-Help:Add-Output-Probe').AddToolTip('Add an output probe to the schematic')
        self.AddStimDoer = Doer(self.onAddStim).AddHelpElement('Control-Help:Add-Stim').AddToolTip('Add a stim to the schematic')
        self.AddUnknownDoer = Doer(self.onAddUnknown).AddHelpElement('Control-Help:Add-Unknown').AddToolTip('Add an unknown to the schematic')
        self.AddSystemDoer = Doer(self.onAddSystem).AddHelpElement('Control-Help:Add-System').AddToolTip('Add a system to the schematic')
        self.DeletePartDoer = Doer(self.onDeletePart).AddHelpElement('Control-Help:Delete-Part').AddToolTip('Delete parts from the schematic')
        self.EditPropertiesDoer = Doer(self.onEditProperties).AddHelpElement('Control-Help:Edit-Properties').AddToolTip('Edit the part properties')
        self.DuplicatePartDoer = Doer(self.onDuplicate).AddHelpElement('Control-Help:Duplicate-Part').AddToolTip('Duplicate parts in the schematic')
        self.RotatePartDoer = Doer(self.onRotatePart).AddHelpElement('Control-Help:Rotate-Part').AddToolTip('Rotate a part 90 degrees')
        self.FlipPartHorizontallyDoer = Doer(self.onFlipPartHorizontally).AddHelpElement('Control-Help:Flip-Horizontally').AddToolTip('Flip part horizontally')
        self.FlipPartVerticallyDoer = Doer(self.onFlipPartVertically).AddHelpElement('Control-Help:Flip-Vertically').AddToolTip('Flip part vertically')
        # ------
        self.AddWireDoer = Doer(self.onAddWire).AddHelpElement('Control-Help:Add-Wire').AddToolTip('Add wires to the schematic')
        self.DeleteVertexDoer = Doer(self.onDeleteSelectedVertex).AddHelpElement('Control-Help:Delete-Vertex').AddToolTip('Delete wire vertices from the schematic')
        self.DuplicateVertexDoer = Doer(self.onDuplicateSelectedVertex).AddHelpElement('Control-Help:Duplicate-Vertex').AddToolTip('Duplicate wire vertices')
        self.DeleteWireDoer = Doer(self.onDeleteSelectedWire).AddHelpElement('Control-Help:Delete-Wire').AddToolTip('Delete wire from the schematic')
        # ------
        self.ZoomInDoer = Doer(self.onZoomIn).AddHelpElement('Control-Help:Zoom-In').AddToolTip('Zoom in')
        self.ZoomOutDoer = Doer(self.onZoomOut).AddHelpElement('Control-Help:Zoom-Out').AddToolTip('Zoom out')
        self.PanDoer = Doer(self.onPan).AddHelpElement('Control-Help:Pan').AddToolTip('Pan the schematic')
        # ------
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties).AddHelpElement('Control-Help:Calculation-Properties').AddToolTip('Edit calculation properties')
        self.PostProcessingDoer = Doer(self.onPostProcessing).AddHelpElement('Control-Help:Post-Processing').AddToolTip('Edit calculation post processing')
        self.SParameterViewerDoer = Doer(self.onSParameterViewer).AddHelpElement('Control-Help:S-parameter-Viewer').AddToolTip('View s-parameters')
        self.CalculateDoer = Doer(self.onCalculate).AddHelpElement('Control-Help:Calculate-tk.Button').AddToolTip('Calculate the schematic')
        self.CalculateSParametersDoer = Doer(self.onCalculateSParameters).AddHelpElement('Control-Help:Calculate-S-parameters').AddToolTip('Calculate s-parameters')
        self.SimulateDoer = Doer(self.onSimulate).AddHelpElement('Control-Help:Simulate').AddToolTip('Simulate')
        self.VirtualProbeDoer = Doer(self.onVirtualProbe).AddHelpElement('Control-Help:Virtual-Probe').AddToolTip('Simulate with virtual probe')
        self.DeembedDoer = Doer(self.onDeembed).AddHelpElement('Control-Help:Deembed').AddToolTip('Calculate de-embedding solution')
        self.RLGCDoer = Doer(self.onRLGC).AddHelpElement('Control-Help:RLGC-Fit').AddToolTip('Fit the element to a RLGC model')
        self.CalculateErrorTermsDoer = Doer(self.onCalculateErrorTerms).AddHelpElement('Control-Help:Calculate-Error-Terms')
        self.SimulateNetworkAnalyzerModelDoer = Doer(self.onSimulateNetworkAnalyzerModel).AddHelpElement('Control-Help:Simulate-Network-Analyzer-Model')
        self.CalculateSParametersFromNetworkAnalyzerModelDoer = Doer(self.onCalculateSParametersFromNetworkAnalyzerModel).AddHelpElement('Control-Help:Calculate-S-Parameters-From-Network-Analyzer-Model').AddToolTip('Calculate s-parameters from a netowrk analyzer')
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement('Control-Help:Open-Help-File').AddToolTip('Open the help system in a browser')
        self.PreferencesDoer=Doer(self.onPreferences).AddHelpElement('Control-Help:Preferences').AddToolTip('Edit the preferences')
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement('Control-Help:Control-Help').AddToolTip('Get help on a control')
        self.SoftwareDocumentationDoer = Doer(self.onSoftwareDocumentation).AddHelpElement('Control-Help:Software-Documentation').AddToolTip('Open the online software documentation')
        self.AboutDoer = Doer(self.onAbout).AddHelpElement('Control-Help:About').AddToolTip('Find out about SignalIntegrity')
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
        self.AddNetNameDoer.AddMenuElement(PartsMenu, label='Add Net Name',underline=4)
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
        self.PostProcessingDoer.AddMenuElement(CalcMenu,label='Post-Processing',underline=1)
        self.SParameterViewerDoer.AddMenuElement(CalcMenu,label='S-parameter Viewer',underline=12)
        CalcMenu.add_separator()
        self.CalculateSParametersDoer.AddMenuElement(CalcMenu,label='Calculate S-parameters',underline=0)
        self.SimulateDoer.AddMenuElement(CalcMenu,label='Simulate',underline=0)
        self.VirtualProbeDoer.AddMenuElement(CalcMenu,label='Virtual Probe',underline=9)
        self.DeembedDoer.AddMenuElement(CalcMenu,label='Deembed',underline=0)
        self.RLGCDoer.AddMenuElement(CalcMenu,label='RLGC Fit',underline=5)
        self.CalculateErrorTermsDoer.AddMenuElement(CalcMenu,label='Calculate Error Terms',underline=10)
        #self.CalculateSParametersFromNetworkAnalyzerModelDoer.AddMenuElement(CalcMenu,label='Calculate S-parameters from VNA Model')
        #self.SimulateNetworkAnalyzerModelDoer.AddMenuElement(CalcMenu,label='Simulate VNA Model')
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)
        self.SoftwareDocumentationDoer.AddMenuElement(HelpMenu,label='Software Documentation',underline=0)
        HelpMenu.add_separator()
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
        self.networkanalyzersimulator = NetworkAnalyzerSimulator(self)
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

        try:
            self.fileparts=FileParts(filename)
            os.chdir(self.fileparts.AbsoluteFilePath())
            self.fileparts=FileParts(filename)
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
        SignalIntegrity.App.Project['Drawing.DrawingProperties.Grid']=SignalIntegrity.App.Preferences['Appearance.InitialGrid']
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

    def NetListText(self):
        return self.Drawing.schematic.NetList().Text()+SignalIntegrity.App.Project['PostProcessing'].NetListLines()

    def onExportNetlist(self):
        self.Drawing.stateMachine.Nothing()
        NetListDialog(self,self.NetListText())

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
            devicePicked=copy.deepcopy(deviceList[dpd.result])
            self.AddSpecificPart(devicePicked)
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

    def onAddNetName(self):
        self.AddSpecificPart(DeviceNetName())

    def onAddOutputProbe(self):
        self.AddSpecificPart(DeviceOutput())

    def onAddMeasureProbe(self):
        self.AddSpecificPart(DeviceMeasurement())

    def onAddStim(self):
        self.AddSpecificPart(DeviceStim())

    def AddSpecificPart(self,part,popDialog=True):
        self.Drawing.stateMachine.Nothing()
        devicePicked=part
        defaultProperty = devicePicked['defref']
        if defaultProperty != None:
            defaultPropertyValue = defaultProperty.GetValue()
            uniqueReferenceDesignator = self.Drawing.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
            if uniqueReferenceDesignator != None:
                devicePicked.AddPartProperty(PartPropertyReferenceDesignator(''))
                devicePicked['ref'].SetValueFromString(uniqueReferenceDesignator)
        if popDialog:
            dpe=DevicePropertiesDialog(self,devicePicked)
            if dpe.result != None:
                part=dpe.result
        if not part is None:
            self.Drawing.partLoaded = part
            self.Drawing.stateMachine.PartLoaded()

    def onZoomIn(self):
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        drawingPropertiesProject['Grid']=drawingPropertiesProject['Grid']+1.
        self.Drawing.DrawSchematic()
        self.statusbar.set('Zoomed to grid: '+str(drawingPropertiesProject['Grid']))

    def onZoomOut(self):
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        drawingPropertiesProject['Grid'] = max(1,drawingPropertiesProject['Grid']-1.)
        self.Drawing.DrawSchematic()
        self.statusbar.set('Zoomed to grid: '+str(drawingPropertiesProject['Grid']))

    def onPan(self):
        self.Drawing.stateMachine.Panning()

    def onDeleteSelectedVertex(self):
        self.Drawing.DeleteSelectedVertex()

    def onDuplicateSelectedVertex(self):
        self.Drawing.DuplicateSelectedVertex()

    def onDeleteSelectedWire(self):
        self.Drawing.DeleteSelectedWire()

    def CalculateSParameters(self,netList=None):
        if netList==None:
            self.Drawing.stateMachine.Nothing()
            netList=self.Drawing.schematic.NetList().Text()+SignalIntegrity.App.Project['PostProcessing'].NetListLines()
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
            return None
        return sp

    def onCalculateSParameters(self):
        self.Drawing.stateMachine.Nothing()
        if self.CalculateSParametersFromNetworkAnalyzerModelDoer.active:
            sp=self.networkanalyzersimulator.Simulate(SParameters=True)
        else:
            sp=self.CalculateSParameters()
        if sp is None:
            return
        self.spd=SParametersDialog(self,sp,filename=self.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'))

    def onPostProcessing(self):
        PostProcessingDialog(self)

    def PrintProgress(self,iteration):
        self.statusbar.set('Fitting - iteration:'+str(self.m_fitter.ccm._IterationsTaken)+' mse:'+str(self.m_fitter.m_mse))

    def PlotResult(self,iteration):
        self.PrintProgress(iteration)
        return

    def onRLGC(self):
        self.Drawing.stateMachine.Nothing()
        import SignalIntegrity.Lib as si
        sp=self.CalculateSParameters()
        if sp is None:
            return
        stepResponse=sp.FrequencyResponse(2,1).ImpulseResponse().Integral()
        threshold=(stepResponse[len(stepResponse)-1]+stepResponse[0])/2.0
        for k in range(len(stepResponse)):
            if stepResponse[k]>threshold: break
        dly=stepResponse.Times()[k]
        rho=sp.FrequencyResponse(1,1).ImpulseResponse().Integral(scale=False).Measure(dly)
        Z0=sp.m_Z0*(1.+rho)/(1.-rho)
        if sp.m_f[0]==0:
            S11_0=sp[0][0][0]; R=(2*S11_0*sp.m_Z0/(1.-S11_0)).real
        else:
            R=0
        L=dly*Z0; C=dly/Z0; guess=[R,L,0.,C,0.,0.]
        #pragma: silent exclude
        self.plotInitialized=False
        #pragma: include
        self.m_fitter=si.fit.RLGCFitter(sp,guess,self.PlotResult)
        #print(self.m_fitter.Results())
        (R,L,G,C,Rse,df)=self.m_fitter.Solve().Results()
#         print "series resistance: "+ToSI(R,'ohm')
#         print "series inductance: "+ToSI(L,'H')
#         print "shunt conductance: "+ToSI(G,'S')
#         print "shunt capacitance: "+ToSI(C,'F')
#         print "skin-effect resistance: "+ToSI(Rse,'ohm/sqrt(Hz)')
#         print "dissipation factor: "+ToSI(df,'')
        fitsp=si.sp.SParameters(sp.f(),[s for s in si.sp.dev.TLineTwoPortRLGC(sp.f(),R,Rse,L,G,C,df,sp.m_Z0)])
        SParametersDialog(self,fitsp,filename=self.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'))

        for deviceToCheck in DeviceList:
            if deviceToCheck['partname'].GetValue()=='Telegrapher':
                if deviceToCheck['ports'].GetValue()==2:
                    device=copy.deepcopy(deviceToCheck)
                    break

        device['r'].SetValueFromString(str(R)); device['r']['KeywordVisible']=True; device['r']['Visible']=True
        device['l'].SetValueFromString(str(L)); device['l']['KeywordVisible']=True; device['l']['Visible']=True
        device['g'].SetValueFromString(str(G)); device['g']['KeywordVisible']=True; device['g']['Visible']=True
        device['c'].SetValueFromString(str(C)); device['c']['KeywordVisible']=True; device['c']['Visible']=True
        device['rse'].SetValueFromString(str(Rse)); device['rse']['KeywordVisible']=True; device['rse']['Visible']=True
        device['df'].SetValueFromString(str(df)); device['df']['KeywordVisible']=True; device['df']['Visible']=True
        device['sect']['KeywordVisible']=False; device['sect']['Visible']=False
        self.AddSpecificPart(device,popDialog=False)

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
        if self.SimulateNetworkAnalyzerModelDoer.active:
            self.networkanalyzersimulator.Simulate()
        else:
            self.simulator.Simulate()

    def onVirtualProbe(self):
        self.Drawing.stateMachine.Nothing()
        self.simulator.VirtualProbe()

    def onDeembed(self):
        self.Drawing.stateMachine.Nothing()
        netList=self.Drawing.schematic.NetList().Text()+SignalIntegrity.App.Project['PostProcessing'].NetListLines()
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
        self.CalculateErrorTermsDoer.Execute()

    def onSParameterViewer(self):
        import SignalIntegrity.Lib as si
        filename=AskOpenFileName(filetypes=[('s-parameter files', ('*.s*p')),('calibration files', ('*.cal'))],
                                 parent=self,
                                 initialdir=self.fileparts.AbsoluteFilePath())
        if filename is None:
            return
        fileparts=FileParts(filename)
        if fileparts.fileext is None or fileparts.fileext == '':
            return
        elif fileparts.fileext == '.cal':
            self.calibration=self.OpenCalibrationFile(fileparts.FullFilePathExtension())
            self.ViewCalibration(self.calibration)
        else:
            sp=si.sp.SParameterFile(fileparts.FullFilePathExtension())
            SParametersDialog(self,sp,fileparts.FullFilePathExtension())

    def onHelp(self):
        if Doer.helpKeys is None:
            messagebox.showerror('Help System','Cannot find or open this help element')
            return
        Doer.helpKeys.Open('sec:Introduction')

    def onSoftwareDocumentation(self):
        if Doer.helpKeys is None:
            messagebox.showerror('Help System','Cannot find or open the software documentation')
            return
        try:
            import webbrowser
            url=Doer.helpKeys.controlHelpUrlBase+Doer.helpKeys['SoftwareDocumentation']
            webbrowser.open(url)
        except:
            messagebox.showerror('Help System','Cannot find or open the software documentation')
            return

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
            self.AddNetNameDoer.Activate(True)
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
            self.RLGCDoer.Activate(True)
            self.CalculateSParametersFromNetworkAnalyzerModelDoer.Activate(True)
            self.SimulateNetworkAnalyzerModelDoer.Activate(True)
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

    def UpdateFeatures(self):
        networkAnalyzerModelEnabled = SignalIntegrity.App.Preferences['Features.NetworkAnalyzerModel']
        from SignalIntegrity.App.Device import DeviceList
        DeviceList.Enable('NetworkAnalyzerStimulus',networkAnalyzerModelEnabled)
        DeviceList.Enable('NetworkAnalyzerModel',networkAnalyzerModelEnabled)
        DeviceList.Enable('DeviceUnderTest',networkAnalyzerModelEnabled)

    def CheckSaveCurrentProject(self):
        if self.Drawing.stateMachine.state == 'NoProject':
            return True
        if not SignalIntegrity.App.Preferences['ProjectFiles.AskToSaveCurrentFile']:
            return True

        filename=self.fileparts.AbsoluteFilePath()+'/'+self.fileparts.FileNameWithExtension(ext='.si')
        if not SignalIntegrity.App.Project.CheckFileChanged(filename):
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
            self.statusbar.set('help keys updated')

    def OpenCalibrationFile(self,filename):
        import SignalIntegrity.Lib as si
        calibration=si.m.cal.Calibration(0,0)
        try:
            calibration.ReadFromFile(filename)
        except:
            calibration=None
        return calibration

    def onOpenCalibrationFile(self):
        self.calibration=None
        filename=AskOpenFileName(filetypes=[('calibration files', ('*.cal'))],
                                 parent=self,
                                 initialdir=self.fileparts.AbsoluteFilePath())
        if filename is None:
            return
        fileparts=FileParts(filename)
        if fileparts.fileext is None or fileparts.fileext == '':
            return
        self.calibration=self.OpenCalibrationFile(fileparts.FullFilePathExtension())

    def onSaveCalibrationFile(self):
        extension='.cal'
        filename=AskSaveAsFilename(filetypes=[('calibration file', '.cal')],
                    defaultextension=extension,
                    initialdir=self.fileparts.AbsoluteFilePath(),
                    initialfile=self.fileparts.FileNameWithExtension(extension),
                    parent=self)
        if filename is None:
            return
        self.fileparts=FileParts(filename)
        self.calibration.WriteToFile(filename)

    def ViewCalibration(self,calibration):
        if self.calibration != None:
            self.spd=SParametersDialog(self,self.calibration,title='Calibration',filename=self.fileparts.FullFilePathExtension('s'+str(self.calibration.ports)+'p'))

    def onViewCalibrationFile(self):
        self.ViewCalibration(self.calibration)

    def CalculateErrorTerms(self):
        self.Drawing.stateMachine.Nothing()
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        etnp=si.p.CalibrationNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']),
            cacheFileName=cacheFileName)
        etnp.AddLines(netList)
        progressDialog = ProgressDialog(self,"Calculating Error Terms",etnp,etnp.CalculateCalibration,granularity=1.0)
        try:
            cal=progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Error Terms Calculator',e.parameter+': '+e.message)
            return None
        return cal

    def onCalculateErrorTerms(self):
        self.calibration=self.CalculateErrorTerms()
        self.onViewCalibrationFile()

    def onSimulateNetworkAnalyzerModel(self):
        self.onSimulate()

    def onCalculateSParametersFromNetworkAnalyzerModel(self):
        self.onCalculateSParameters()

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
