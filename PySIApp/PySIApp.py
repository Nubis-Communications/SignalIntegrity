'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from Tkinter import Frame,PhotoImage,Menu,Button,Tk
from Tkinter import LEFT,NO,NONE,RAISED,X,TOP,SUNKEN,BOTTOM,BOTH,RIGHT,E,YES

import tkFont

import tkMessageBox
from tkMessageBox import askyesnocancel

import copy
import os
import sys

import xml.etree.ElementTree as et

from PartPicture import PartPicture
from PartProperty import PartPropertyPartName,PartPropertyDefaultReferenceDesignator,PartPropertyReferenceDesignator
from Device import DeviceList,DeviceListUnknown,DeviceListSystem
from Device import DeviceOutput,DeviceMeasurement,Port,DeviceStim
from DeviceProperties import DevicePropertiesDialog
from DevicePicker import DevicePickerDialog
from Schematic import Drawing,Wire,Vertex
from CalculationProperties import CalculationProperties
from Simulator import Simulator
from NetList import NetListDialog
from SParameterViewerWindow import SParametersDialog
from Files import FileParts,ConvertFileNameToRelativePath
from History import History
from MenuSystemHelpers import Doer,StatusBar
from BuildHelpSystem import HelpSystemKeys
from ProgressDialog import ProgressDialog
from About import AboutDialog
from Preferences import Preferences
from PreferencesDialog import PreferencesDialog
from FilePicker import AskSaveAsFilename,AskOpenFileName

class PySIApp(Frame):
    def __init__(self):
        # make absolutely sure the directory of this file is the first in the
        # python path
        thisFileDir=os.path.dirname(os.path.realpath(__file__))
        sys.path=[thisFileDir]+sys.path

        self.preferences=Preferences()
        self.root = Tk()

        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)

        self.UpdateColorsAndFonts()

        Frame.__init__(self, self.root)
        self.pack(fill=BOTH, expand=YES)
        self.installdir=os.path.dirname(os.path.abspath(__file__))

        versionString='1.0.0'

        self.root.title('PySI - '+versionString)

        img = PhotoImage(file=self.installdir+'/icons/png/AppIcon2.gif')
        self.root.tk.call('wm', 'iconphoto', self.root._w, '-default', img)

        # I believe this is totally obsolete
#         sys.path.append(self.installdir+'/..')
#         foundSignalIntegrity=False
#         while not foundSignalIntegrity:
#             foundSignalIntegrity = True
#             try:
#                 import SignalIntegrity as si
#             except ImportError:
#                 foundSignalIntegrity = False
#                 if tkMessageBox.askokcancel('SignalIntegrity Package',
#                     'In order to run this application, I need to know where the '+\
#                     'SignalIntegrity package is.  Please browse to the directory where '+\
#                     'it\'s installed.\n'+'You should only need to do this once'):
#                         dirname = askdirectory(parent=self.root,initialdir=os.path.dirname(os.path.abspath(__file__)),
#                             title='Please select a directory')
#                         sys.path.append(dirname)
#                 else:
#                     exit()

        self.helpSystemKeys = HelpSystemKeys(self.installdir)
        # status bar
        self.statusbar=StatusBar(self)

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.RecentProject0Doer = Doer(self.onRecentProject0).Activate(False)
        self.RecentProject1Doer = Doer(self.onRecentProject1).Activate(False)
        self.RecentProject2Doer = Doer(self.onRecentProject2).Activate(False)
        self.RecentProject3Doer = Doer(self.onRecentProject3).Activate(False)
        self.NewProjectDoer = Doer(self.onNewProject).AddKeyBindElement(self.root,'<Control-n>').AddHelpElement(self.helpSystemKeys['Control-Help:New-Project'])
        self.OpenProjectDoer = Doer(self.onReadProjectFromFile).AddKeyBindElement(self.root,'<Control-o>').AddHelpElement(self.helpSystemKeys['Control-Help:Open-Project'])
        self.SaveProjectDoer = Doer(self.onSaveProject).AddKeyBindElement(self.root,'<Control-s>').AddHelpElement(self.helpSystemKeys['Control-Help:Save-Project'])
        self.SaveAsProjectDoer = Doer(self.onSaveAsProject).AddKeyBindElement(self.root,'<Control-Shift-s>').AddHelpElement(self.helpSystemKeys['Control-Help:Save-As-Project'])
        self.ClearProjectDoer = Doer(self.onClearSchematic).AddHelpElement(self.helpSystemKeys['Control-Help:Clear-Schematic'])
        self.ExportNetListDoer = Doer(self.onExportNetlist).AddHelpElement(self.helpSystemKeys['Control-Help:Export-Netlist'])
        self.ExportTpXDoer = Doer(self.onExportTpX).AddHelpElement(self.helpSystemKeys['Control-Help:Export-LaTeX'])
        # ------
        self.UndoDoer = Doer(self.onUndo).AddKeyBindElement(self.root,'<Control-z>').AddHelpElement(self.helpSystemKeys['Control-Help:Undo'])
        self.RedoDoer = Doer(self.onRedo).AddKeyBindElement(self.root,'<Control-Z>').AddHelpElement(self.helpSystemKeys['Control-Help:Redo'])
        self.DeleteSelectedDoer = Doer(self.onDeleteSelected).AddKeyBindElement(self.root,'<Delete>').AddHelpElement(self.helpSystemKeys['Control-Help:Delete-Selected'])
        self.DuplicateSelectedDoer = Doer(self.onDuplicateSelected).AddKeyBindElement(self.root,'<Control-c>').AddHelpElement(self.helpSystemKeys['Control-Help:Duplicate-Selected'])
        self.CutSelectedDoer = Doer(self.onCutMultipleSelections).AddKeyBindElement(self.root,'<Control-x>').AddHelpElement(self.helpSystemKeys['Control-Help:Cut-Selected'])
        # ------
        self.AddPartDoer = Doer(self.onAddPart).AddHelpElement(self.helpSystemKeys['Control-Help:Add-Part'])
        self.AddPortDoer = Doer(self.onAddPort).AddHelpElement(self.helpSystemKeys['Control-Help:Add-Port'])
        self.AddMeasureProbeDoer = Doer(self.onAddMeasureProbe).AddHelpElement(self.helpSystemKeys['Control-Help:Add-Measure-Probe'])
        self.AddOutputProbeDoer = Doer(self.onAddOutputProbe).AddHelpElement(self.helpSystemKeys['Control-Help:Add-Output-Probe'])
        self.AddStimDoer = Doer(self.onAddStim).AddHelpElement(self.helpSystemKeys['Control-Help:Add-Stim'])
        self.AddUnknownDoer = Doer(self.onAddUnknown).AddHelpElement(self.helpSystemKeys['Control-Help:Add-Unknown'])
        self.AddSystemDoer = Doer(self.onAddSystem).AddHelpElement(self.helpSystemKeys['Control-Help:Add-System'])
        self.DeletePartDoer = Doer(self.onDeletePart).AddHelpElement(self.helpSystemKeys['Control-Help:Delete-Part'])
        self.EditPropertiesDoer = Doer(self.onEditProperties).AddHelpElement(self.helpSystemKeys['Control-Help:Edit-Properties'])
        self.DuplicatePartDoer = Doer(self.onDuplicate).AddHelpElement(self.helpSystemKeys['Control-Help:Duplicate-Part'])
        self.RotatePartDoer = Doer(self.onRotatePart).AddHelpElement(self.helpSystemKeys['Control-Help:Rotate-Part'])
        self.FlipPartHorizontallyDoer = Doer(self.onFlipPartHorizontally).AddHelpElement(self.helpSystemKeys['Control-Help:Flip-Horizontally'])
        self.FlipPartVerticallyDoer = Doer(self.onFlipPartVertically).AddHelpElement(self.helpSystemKeys['Control-Help:Flip-Vertically'])
        # ------
        self.AddWireDoer = Doer(self.onAddWire).AddHelpElement(self.helpSystemKeys['Control-Help:Add-Wire'])
        self.DeleteVertexDoer = Doer(self.onDeleteSelectedVertex).AddHelpElement(self.helpSystemKeys['Control-Help:Delete-Vertex'])
        self.DuplicateVertexDoer = Doer(self.onDuplicateSelectedVertex).AddHelpElement(self.helpSystemKeys['Control-Help:Duplicate-Vertex'])
        self.DeleteWireDoer = Doer(self.onDeleteSelectedWire).AddHelpElement(self.helpSystemKeys['Control-Help:Delete-Wire'])
        # ------
        self.ZoomInDoer = Doer(self.onZoomIn).AddHelpElement(self.helpSystemKeys['Control-Help:Zoom-In'])
        self.ZoomOutDoer = Doer(self.onZoomOut).AddHelpElement(self.helpSystemKeys['Control-Help:Zoom-Out'])
        self.PanDoer = Doer(self.onPan).AddHelpElement(self.helpSystemKeys['Control-Help:Pan'])
        # ------
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties).AddHelpElement(self.helpSystemKeys['Control-Help:Calculation-Properties'])
        self.SParameterViewerDoer = Doer(self.onSParameterViewer).AddHelpElement(self.helpSystemKeys['Control-Help:S-parameter-Viewer'])
        self.CalculateDoer = Doer(self.onCalculate).AddHelpElement(self.helpSystemKeys['Control-Help:Calculate-Button'])
        self.CalculateSParametersDoer = Doer(self.onCalculateSParameters).AddHelpElement(self.helpSystemKeys['Control-Help:Calculate-S-parameters'])
        self.SimulateDoer = Doer(self.onSimulate).AddHelpElement(self.helpSystemKeys['Control-Help:Simulate'])
        self.VirtualProbeDoer = Doer(self.onVirtualProbe).AddHelpElement(self.helpSystemKeys['Control-Help:Virtual-Probe'])
        self.DeembedDoer = Doer(self.onDeembed).AddHelpElement(self.helpSystemKeys['Control-Help:Deembed'])
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement(self.helpSystemKeys['Control-Help:Open-Help-File'])
        self.PreferencesDoer=Doer(self.onPreferences)
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement(self.helpSystemKeys['Control-Help:Control-Help'])
        self.AboutDoer = Doer(self.onAbout).AddHelpElement(self.helpSystemKeys['Control-Help:About'])
        # ------
        self.EscapeDoer = Doer(self.onEscape).AddKeyBindElement(self.root, '<Escape>').DisableHelp()

        # The menu system
        TheMenu=Menu(self.root)
        self.root.config(menu=TheMenu)
        self.FileMenu=Menu(self)
        TheMenu.add_cascade(label='File',menu=self.FileMenu,underline=0)
        self.RecentsMenu=Menu(self.FileMenu)
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
        EditMenu=Menu(self)
        TheMenu.add_cascade(label='Edit',menu=EditMenu,underline=0)
        self.UndoDoer.AddMenuElement(EditMenu,label="Undo",accelerator='Ctrl+Z', underline=0)
        self.RedoDoer.AddMenuElement(EditMenu,label="Redo",accelerator='Ctrl+Shift+Z',underline=0)
        EditMenu.add_separator()
        # ------
        self.DeleteSelectedDoer.AddMenuElement(EditMenu,label='Delete Selected',accelerator='Del',underline=0)
        self.DuplicateSelectedDoer.AddMenuElement(EditMenu,label='Duplicate Selected',accelerator='Ctrl+C',underline=1)
        self.CutSelectedDoer.AddMenuElement(EditMenu,label='Cut Selected',accelerator='Ctrl+X',underline=0)
        # ------
        PartsMenu=Menu(self)
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
        WireMenu=Menu(self)
        TheMenu.add_cascade(label='Wires',menu=WireMenu,underline=0)
        self.AddWireDoer.AddMenuElement(WireMenu,label='Add Wire',underline=0)
        WireMenu.add_separator()
        self.DeleteVertexDoer.AddMenuElement(WireMenu,label='Delete Vertex',underline=7)
        self.DuplicateVertexDoer.AddMenuElement(WireMenu,label='Duplicate Vertex',underline=1)
        self.DeleteWireDoer.AddMenuElement(WireMenu,label='Delete Wire',underline=0)
        # ------
        ViewMenu=Menu(self)
        TheMenu.add_cascade(label='View',menu=ViewMenu,underline=0)
        self.ZoomInDoer.AddMenuElement(ViewMenu,label='Zoom In',underline=5)
        self.ZoomOutDoer.AddMenuElement(ViewMenu,label='Zoom Out',underline=5)
        self.PanDoer.AddMenuElement(ViewMenu,label='Pan',underline=0)
        # ------
        CalcMenu=Menu(self)
        TheMenu.add_cascade(label='Calculate',menu=CalcMenu,underline=0)
        self.CalculationPropertiesDoer.AddMenuElement(CalcMenu,label='Calculation Properties',underline=12)
        self.SParameterViewerDoer.AddMenuElement(CalcMenu,label='S-parameter Viewer',underline=12)
        CalcMenu.add_separator()
        self.CalculateSParametersDoer.AddMenuElement(CalcMenu,label='Calculate S-parameters',underline=0)
        self.SimulateDoer.AddMenuElement(CalcMenu,label='Simulate',underline=0)
        self.VirtualProbeDoer.AddMenuElement(CalcMenu,label='Virtual Probe',underline=9)
        self.DeembedDoer.AddMenuElement(CalcMenu,label='Deembed',underline=0)
        # ------
        HelpMenu=Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)
        self.PreferencesDoer.AddMenuElement(HelpMenu,label='Preferences',underline=0)
        self.AboutDoer.AddMenuElement(HelpMenu,label='About',underline=0)

        # The Toolbar
        ToolBarFrame = Frame(self)
        ToolBarFrame.pack(side=TOP,fill=X,expand=NO)
        self.NewProjectDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/document-new-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.OpenProjectDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/document-open-2.gif',).Pack(side=LEFT,fill=NONE,expand=NO)
        self.SaveProjectDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/document-save-2.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        Frame(ToolBarFrame,bd=2,relief=SUNKEN).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.AddPartDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/edit-add-2.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.DeleteSelectedDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/edit-delete-6.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.AddWireDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/draw-line-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.DuplicateSelectedDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/edit-copy-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.RotatePartDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/object-rotate-left-4.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.FlipPartHorizontallyDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/object-flip-horizontal-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.FlipPartVerticallyDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/object-flip-vertical-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        Frame(ToolBarFrame,height=2,bd=2,relief=RAISED).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.ZoomInDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/zoom-in-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.ZoomOutDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/zoom-out-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.PanDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/edit-move.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        Frame(ToolBarFrame,height=2,bd=2,relief=RAISED).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.CalculationPropertiesDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/tooloptions.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.CalculateDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/system-run-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        Frame(ToolBarFrame,height=2,bd=2,relief=RAISED).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.HelpDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/help-contents-5.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.ControlHelpDoer.AddToolBarElement(ToolBarFrame,iconfile=self.installdir+'/icons/png/16x16/actions/help-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        # ------
        UndoFrame=Frame(ToolBarFrame)
        UndoFrame.pack(side=RIGHT,fill=NONE,expand=NO,anchor=E)
        self.UndoDoer.AddToolBarElement(UndoFrame,iconfile=self.installdir+'/icons/png/16x16/actions/edit-undo-3.gif').Pack(side=LEFT,fill=NONE,expand=NO,anchor=E)
        self.RedoDoer.AddToolBarElement(UndoFrame,iconfile=self.installdir+'/icons/png/16x16/actions/edit-redo-3.gif').Pack(side=LEFT,fill=NONE,expand=NO,anchor=E)

        # The Drawing (which contains the schecmatic)
        self.Drawing=Drawing(self)
        self.Drawing.pack(side=TOP,fill=BOTH,expand=YES)

        self.statusbar.pack(side=BOTTOM,fill=X,expand=NO)
        self.root.bind('<Key>',self.onKey)

        # The Simulator Dialog
        self.simulator = Simulator(self)
        self.calculationProperties=CalculationProperties(self)
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

        projectFileName = self.preferences.GetLastFileOpened()

        if not projectFileName == None:
            self.OpenProjectFile(projectFileName)

        self.UpdateRecentProjectsMenu()

        self.root.mainloop()

    def onResize(self,event):
        if not self.knowDelta:
            self.deltaWidth=event.width-600
            self.deltaHeight=event.height-600
            self.knowDelta=True
        #print 'width: '+str(event.width)+', height'+str(event.height)
        self.Drawing.canvas.config(width=event.width-self.deltaWidth,height=event.height-self.deltaHeight)

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
        filename=AskOpenFileName(filetypes=[('xml', '.xml')],
                                 initialdir=self.fileparts.AbsoluteFilePath(),
                                 initialfile=self.fileparts.FileNameWithExtension('.xml'))

        if filename is None:
            return
        self.OpenProjectFile(filename)

    def OpenProjectFile(self,filename):
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
            tree=et.parse(self.fileparts.FullFilePathExtension('.xml'))
            root=tree.getroot()
            for child in root:
                if child.tag == 'drawing':
                    self.Drawing.InitFromXml(child)
                elif child.tag == 'calculation_properties':
                    self.calculationProperties.InitFromXml(child, self)
        except:
            tkMessageBox.showerror('read project file','file not found or unreadable')
            return
        self.Drawing.stateMachine.Nothing()
        self.Drawing.DrawSchematic()
        self.history.Event('read project')
        self.root.title('PySI: '+self.fileparts.FileNameTitle())
        self.AnotherFileOpened(self.fileparts.FullFilePathExtension('.xml'))

    def onNewProject(self):
        if not self.CheckSaveCurrentProject():
            return
        filename=AskSaveAsFilename(filetypes=[('xml', '.xml')],
                                   defaultextension='.xml',
                                   initialdir=self.fileparts.AbsoluteFilePath(),
                                   title='new project file')
        if filename is None:
            return
        self.Drawing.stateMachine.Nothing()
        self.Drawing.schematic.Clear()
        self.Drawing.DrawSchematic()
        self.history.Event('new project')
        self.SaveProjectToFile(filename)

    def SaveProjectToFile(self,filename):
        self.Drawing.stateMachine.Nothing()
        self.fileparts=FileParts(filename)
        os.chdir(self.fileparts.AbsoluteFilePath())
        self.fileparts=FileParts(filename)
        projectElement=et.Element('Project')
        drawingElement=self.Drawing.xml()
        calculationPropertiesElement=self.calculationProperties.xml()
        projectElement.extend([drawingElement,calculationPropertiesElement])
        et.ElementTree(projectElement).write(filename)
        filename=ConvertFileNameToRelativePath(filename)
        self.AnotherFileOpened(filename)
        self.root.title("PySI: "+self.fileparts.FileNameTitle())
        self.statusbar.set('Project Saved')

    def onSaveProject(self):
        if self.fileparts.filename=='':
            return
        filename=self.fileparts.AbsoluteFilePath()+'/'+self.fileparts.FileNameWithExtension(ext='.xml')
        self.SaveProjectToFile(filename)

    def onSaveAsProject(self):
        filename=AskSaveAsFilename(filetypes=[('xml', '.xml')],
                                   defaultextension='.xml',
                                   initialfile=self.fileparts.FileNameWithExtension('.xml'),
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
        #self.root.title('PySI')

    def AnotherFileOpened(self,filename):
        self.preferences.AnotherFileOpened(filename)
        self.UpdateRecentProjectsMenu()

    def UpdateRecentProjectsMenu(self):
        recentFileList=self.preferences.GetRecentFileList()
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
        self.OpenProjectFile(self.preferences.GetLastFileOpened(0))

    def onRecentProject1(self):
        if not self.CheckSaveCurrentProject():
            return False
        self.OpenProjectFile(self.preferences.GetLastFileOpened(1))

    def onRecentProject2(self):
        if not self.CheckSaveCurrentProject():
            return False
        self.OpenProjectFile(self.preferences.GetLastFileOpened(2))

    def onRecentProject3(self):
        if not self.CheckSaveCurrentProject():
            return False
        self.OpenProjectFile(self.preferences.GetLastFileOpened(3))

    def onExportNetlist(self):
        self.Drawing.stateMachine.Nothing()
        NetListDialog(self,self.Drawing.schematic.NetList().Text())

    def onExportTpX(self):
        from TpX import TpX
        from TikZ import TikZ
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
            tkMessageBox.showerror('Export LaTeX','LaTeX could not be generated or written ')

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
            if deviceList[dpd.result][PartPropertyPartName().propertyName].GetValue() == 'Port':
                self.onAddPort()
                return
            else:
                devicePicked=copy.deepcopy(deviceList[dpd.result])
                devicePicked.AddPartProperty(PartPropertyReferenceDesignator(''))
                defaultProperty = devicePicked[PartPropertyDefaultReferenceDesignator().propertyName]
                if defaultProperty != None:
                    defaultPropertyValue = defaultProperty.GetValue()
                    uniqueReferenceDesignator = self.Drawing.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
                    if uniqueReferenceDesignator != None:
                        devicePicked[PartPropertyReferenceDesignator().propertyName].SetValueFromString(uniqueReferenceDesignator)
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
        self.Drawing.wireLoaded=Wire([Vertex((0,0))])
        self.Drawing.schematic.wireList.append(self.Drawing.wireLoaded)
        self.Drawing.stateMachine.WireLoaded()
    def onAddPort(self):
        self.Drawing.stateMachine.Nothing()
        portNumber=1
        for device in self.Drawing.schematic.deviceList:
            if device['type'].GetValue() == 'Port':
                if portNumber <= int(device['portnumber'].GetValue()):
                    portNumber = int(device['portnumber'].GetValue())+1
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
        defaultProperty = devicePicked[PartPropertyDefaultReferenceDesignator().propertyName]
        if defaultProperty != None:
            defaultPropertyValue = defaultProperty.GetValue()
            uniqueReferenceDesignator = self.Drawing.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
            if uniqueReferenceDesignator != None:
                devicePicked[PartPropertyReferenceDesignator().propertyName].SetValueFromString(uniqueReferenceDesignator)
        dpe=DevicePropertiesDialog(self,devicePicked)
        if dpe.result != None:
            self.Drawing.partLoaded = dpe.result
            self.Drawing.stateMachine.PartLoaded()

    def onZoomIn(self):
        self.Drawing.grid = self.Drawing.grid*2
        self.Drawing.DrawSchematic()

    def onZoomOut(self):
        self.Drawing.grid = max(1,self.Drawing.grid/2)
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
        import SignalIntegrity as si
        spnp=si.p.SystemSParametersNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.calculationProperties.endFrequency,
                self.calculationProperties.frequencyPoints))
        spnp.AddLines(netList)
        progressDialog = ProgressDialog(self,self.installdir,"Calculating S-parameters",spnp,spnp.SParameters,granularity=10.0)
        try:
            sp=progressDialog.GetResult()
        except si.PySIException as e:
            tkMessageBox.showerror('S-parameter Calculator',e.parameter+': '+e.message)
            return
        SParametersDialog(self,sp,filename=self.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'))

    def onCalculationProperties(self):
        self.Drawing.stateMachine.Nothing()
        self.calculationProperties.ShowCalculationPropertiesDialog()
        self.calculationProperties.CalculationPropertiesDialog().grab_set()

    def onSimulate(self):
        self.Drawing.stateMachine.Nothing()
        self.simulator.Simulate()

    def onVirtualProbe(self):
        self.Drawing.stateMachine.Nothing()
        self.simulator.VirtualProbe()

    def onDeembed(self):
        self.Drawing.stateMachine.Nothing()
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity as si
        dnp=si.p.DeembedderNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.calculationProperties.endFrequency,
                self.calculationProperties.frequencyPoints))
        dnp.AddLines(netList)
        
        progressDialog = ProgressDialog(self,self.installdir,"Calculating De-embedded S-parameters",dnp,dnp.Deembed,granularity=10.0)
        try:
            sp=progressDialog.GetResult()
        except si.PySIException as e:
            tkMessageBox.showerror('Deembedder',e.parameter+': '+e.message)
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
        import SignalIntegrity as si
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
        import webbrowser
        helpfile=self.helpSystemKeys['sec:Introduction']
        if helpfile is None:
            tkMessageBox.showerror('Help System','Cannot find the help system')
            return
        url = self.installdir+'/Help/PySIHelp.html.LyXconv/'+helpfile
        webbrowser.open(url)

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
            self.preferencesDialog = PreferencesDialog(self,self.preferences)
        if self.preferencesDialog == None:
            self.preferencesDialog= PreferencesDialog(self,self.preferences)
        else:
            if not self.preferencesDialog.winfo_exists():
                self.preferencesDialog=PreferencesDialog(self,self.preferences)

    def UpdateColorsAndFonts(self):
        fontSizeDesired = self.preferences.GetValue('Appearance.FontSize')
        if not fontSizeDesired is None:
            default_font = tkFont.nametofont("TkDefaultFont")
            try:
                default_font.configure(size=fontSizeDesired)
                self.root.option_add("*Font", default_font)
                PartPicture.textSpacing=fontSizeDesired+5
            except:
                pass

        w=Button(self.root)

        backgroundColor=self.preferences.GetValue('Appearance.Color.Background')
        if backgroundColor is None:
            backgroundColor=w['background']

        foregroundColor=self.preferences.GetValue('Appearance.Color.Foreground')
        if foregroundColor is None:
            foregroundColor=w['foreground']

        activeForegroundColor=self.preferences.GetValue('Appearance.Color.ActiveForeground')
        if activeForegroundColor is None:
            activeForegroundColor=w['activeforeground']

        activeBackgroundColor=self.preferences.GetValue('Appearance.Color.ActiveBackground')
        if activeBackgroundColor is None:
            activeBackgroundColor=w['activebackground']

        disabledForegroundColor=self.preferences.GetValue('Appearance.Color.DisabledForeground')
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

        matPlotLibColor=self.preferences.GetValue('Appearance.Color.Plot')
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
        if not self.preferences.GetValue('ProjectFiles.AskToSaveCurrentFile'):
            return True

        doit =  askyesnocancel('Wait....','Do you want to save the current project first?')
        if doit is None:
            return False
        else:
            if doit:
                self.onSaveAsProject()
        return True

    def onClosing(self):
        if self.CheckSaveCurrentProject():
            self.root.destroy()

def main():
    PySIApp()

if __name__ == '__main__':
    main()