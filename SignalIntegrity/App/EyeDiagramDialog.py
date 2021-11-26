"""
EyeDiagramDialog.py
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
    import tkMessageBox as messagebox
else:
    import tkinter as tk
    from tkinter import messagebox

from SignalIntegrity.App.MenuSystemHelpers import Doer,StatusBar
from SignalIntegrity.App.ProgressDialog import ProgressDialog
from SignalIntegrity.App.FilePicker import AskSaveAsFilename
from SignalIntegrity.App.EyeDiagramMeasurementsDialog import EyeDiagramMeasurementsDialog
from SignalIntegrity.App.EyeDiagram import EyeDiagram
from SignalIntegrity.App.BathtubCurveDialog import BathtubCurveDialog
from SignalIntegrity.App.ToSI import ToSI

import SignalIntegrity.App.Project
import SignalIntegrity.App.Preferences

from PIL import ImageTk

class EyeDiagramDialog(tk.Toplevel):
    def __init__(self, parent, name):
        tk.Toplevel.__init__(self, parent.parent)
        self.parent=parent
        self.withdraw()
        self.name=name
        self.title('Eye Diagram: '+name)
        self.img = tk.PhotoImage(file=SignalIntegrity.App.IconsBaseDir+'AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, self.img)
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.EyeDiagramSaveDoer = Doer(self.onWriteImageToFile).AddHelpElement('Control-Help:Save-Eye-Diagram-Image').AddToolTip('Save images to files')
        # ------
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties).AddHelpElement('Control-Help:Calculation-Properties').AddToolTip('Edit calculation properties')
        self.PropertiesDoer=Doer(self.onProperties).AddHelpElement('Control-Help:Eye-Diagram-Properties').AddToolTip('Edit eye diagram properties')
        self.SimulateDoer = Doer(self.onCalculate).AddHelpElement('Control-Help:Recalculate').AddToolTip('Recalculate simulation')
        self.OnlyRecalculateEyeDoer =Doer(self.onRecalculateEyeDiagram).AddHelpElement('Control-Help:Only-Recalculate-Eye-Diagram').AddToolTip('Recalculate eye diagram')
        # ------
        self.EyeMeasurementsDoer = Doer(self.onEyeMeasurements).AddHelpElement('Control-Help:Eye-Measurements').AddToolTip('View the eye measurements')
        self.BathtubCurveDoer = Doer(self.onBathtubCurve).AddHelpElement('Control-Help:Bathtub-Curve').AddToolTip('View the bathtub curves')
        # ------
        self.HelpDoer = Doer(self.onHelp).AddHelpElement('Control-Help:Eye-Diagram-Open-Help-File').AddToolTip('Open the help system in a browser')
        self.ControlHelpDoer = Doer(self.onControlHelp).AddHelpElement('Control-Help:Eye-Diagram-Control-Help').AddToolTip('Get help on a control')
        # ------
        self.EscapeDoer = Doer(self.onEscape).AddKeyBindElement(self,'<Escape>').DisableHelp()

        # The menu system
        TheMenu=tk.Menu(self)
        self.TheMenu=TheMenu
        self.config(menu=TheMenu)
        FileMenu=tk.Menu(self)
        TheMenu.add_cascade(label='File',menu=FileMenu,underline=0)
        self.EyeDiagramSaveDoer.AddMenuElement(FileMenu,label="Save Image to File",underline=0)
        FileMenu.add_separator()
        # ------
        CalcMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Calculate',menu=CalcMenu,underline=0)
        self.CalculationPropertiesDoer.AddMenuElement(CalcMenu,label='Calculation Properties',underline=0)
        self.PropertiesDoer.AddMenuElement(CalcMenu,label='Eye Diagram Properties',underline=0)
        CalcMenu.add_separator()
        self.SimulateDoer.AddMenuElement(CalcMenu,label='Recalculate',underline=0)
        self.OnlyRecalculateEyeDoer.AddMenuElement(CalcMenu,label='Only Recalculate Eye Diagram',underline=0)
        # ------
        ViewMenu=tk.Menu(self)
        TheMenu.add_cascade(label='View',menu=ViewMenu,underline=0)
        self.EyeMeasurementsDoer.AddMenuElement(ViewMenu,label='Eye Measurements',underline=0)
        self.BathtubCurveDoer.AddMenuElement(ViewMenu,label='Bathtub Curve',underline=0)
        # ------
        HelpMenu=tk.Menu(self)
        TheMenu.add_cascade(label='Help',menu=HelpMenu,underline=0)
        self.HelpDoer.AddMenuElement(HelpMenu,label='Open Help File',underline=0)
        self.ControlHelpDoer.AddMenuElement(HelpMenu,label='Control Help',underline=0)

        # The Toolbar
        ToolBarFrame = tk.Frame(self)
        ToolBarFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        iconsdir=SignalIntegrity.App.IconsDir+''
        self.EyeDiagramSaveDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'document-save-2.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(self,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.CalculationPropertiesDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'tooloptions.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.SimulateDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'system-run-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.OnlyRecalculateEyeDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'eye.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        tk.Frame(ToolBarFrame,height=2,bd=2,relief=tk.RAISED).pack(side=tk.LEFT,fill=tk.X,padx=5,pady=5)
        self.HelpDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'help-contents-5.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)
        self.ControlHelpDoer.AddToolBarElement(ToolBarFrame,iconfile=iconsdir+'help-3.gif').Pack(side=tk.LEFT,fill=tk.NONE,expand=tk.NO)

        self.eyeStatus=StatusBar(self)
        self.eyeStatus.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)

        self.eyeFrame=tk.Frame(self, relief=tk.RIDGE, borderwidth=5) 
        self.eyeCanvas=tk.Canvas(self.eyeFrame,width=0,height=0)
        self.eyeCanvas.pack()
        self.eyeFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)

        # status bar
        self.statusbar=StatusBar(self)
        self.statusbar.pack(side=tk.BOTTOM,fill=tk.X,expand=tk.NO)

        self.eyeDiagram=EyeDiagram(self,self.name)

        self.geometry("%+d%+d" % (self.parent.parent.root.winfo_x()+self.parent.parent.root.winfo_width()/2-self.winfo_width()/2,
            self.parent.parent.root.winfo_y()+self.parent.parent.root.winfo_height()/2-self.winfo_height()/2))

        # Allow resizing of the image
        self.knowDelta=False
        self.deltaWidth=0
        self.deltaHeight=0
        self.bind('<Configure>',self.onResize)
        self.bind('<FocusIn>',self.onFocus)

    def onFocus(self,event):
        if event.widget == self:
            if hasattr(self,'eyeDiagramMeasurementsDialog'):
                if self.eyeDiagramMeasurementsDialog != None:
                    if self.eyeDiagramMeasurementsDialog.winfo_exists():
                        self.eyeDiagramMeasurementsDialog.lift()
                        self.lift()

    def onResize(self,event):
        if not self.knowDelta:
            self.adjusting=False
            self.adjustCount=0
            self.deltaWidth=4
            self.deltaHeight=4
            self.knowDelta=True
        else:
            if self.adjusting:
                self.adjustCount+=1
            else:
                self.adjusting=True
                self.adjustCount=0
                self.after(100,self.AdjustImage)

    def AdjustImage(self):
        if self.adjustCount != 0:
            self.adjustCount=0
            self.after(100,self.AdjustImage)
        else:
            if hasattr(self, 'eyeImage'):
                newImageWidth=self.eyeCanvas.winfo_width()-self.deltaWidth
                newImageHeight=self.eyeCanvas.winfo_height()-self.deltaHeight
                if (newImageWidth != self.eyeImage.width()) or (newImageHeight != self.eyeImage.height()):
                    if (newImageHeight > 0) and (newImageWidth > 0):
                        img=self.eyeDiagram.img.resize((newImageWidth,newImageHeight))
                        self.eyeImage=ImageTk.PhotoImage(img)
                        self.eyeCanvas.create_image(newImageWidth/2,newImageHeight/2,image=self.eyeImage)
            self.adjusting=False

    def onClosing(self):
        self.withdraw()
        self.destroy()

    def destroy(self):
        tk.Toplevel.withdraw(self)
        tk.Toplevel.destroy(self)

    def onWriteImageToFile(self):
        if self.parent.parent.fileparts.filename=='':
            filename=self.name
        else:
            filename=self.parent.parent.fileparts.filename+'_'+self.name
        filename=AskSaveAsFilename(parent=self,filetypes=[('Images',('.png','.bmp','.jpg','.gif','.tiff'))],
                        defaultextension='.png',
                        initialdir=self.parent.parent.fileparts.AbsoluteFilePath(),
                        initialfile=filename+'.png')
        if filename is None:
            return
        self.eyeDiagram.img.save(filename)

    def onCalculate(self):
        self.statusbar.set('Calculation Started')
        self.parent.parent.onCalculate()

    def onRecalculateEyeDiagram(self):
        self.statusbar.set('Calculation Started')
        import SignalIntegrity.Lib as si
        progressDialog=ProgressDialog(self.parent.parent,"Eye Diagram Processing",self,self.CalculateEyeDiagram)
        try:
            progressDialog.GetResult()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Eye Diagram',e.parameter+': '+e.message)
            return

    def onCalculationProperties(self):
        self.parent.parent.onCalculationProperties()

    def onHelp(self):
        if Doer.helpKeys is None:
            messagebox.showerror('Help System','Cannot find or open this help element')
            return
        Doer.helpKeys.Open('sec:Eye-Diagram-Dialog')

    def onControlHelp(self):
        Doer.inHelp=True
        self.config(cursor='question_arrow')

    def onEscape(self):
        Doer.inHelp=False
        self.config(cursor='left_ptr')

    def onProperties(self):
        self.eyeArgs['Config'].onConfiguration(self)

    def SetEyeArgs(self,eyeArgs):
        self.eyeArgs=eyeArgs
        return self

    def InstallCallback(self,Callback=None):
        self.callback=Callback

    def RemoveCallback(self):
        self.callback=None

    def CalculateEyeDiagram(self):
        self.eyeDiagram.CalculateEyeDiagram(self.parent.parent.fileparts.FileNameTitle(),self.callback)
        if hasattr(self,'eyeDiagramMeasurementsDialog'):
            if self.eyeDiagramMeasurementsDialog != None:
                if self.eyeDiagramMeasurementsDialog.winfo_exists():
                    self.EyeDiagramMeasurementsDialog().UpdateMeasurements(self.eyeDiagram.measDict)
        if hasattr(self, 'bathtubCurveDialog'):
            if self.bathtubCurveDialog != None:
                if self.bathtubCurveDialog.winfo_exists():
                    self.BathtubCurveDialog().UpdateMeasurements(self.eyeDiagram.measDict)
        self.EyeMeasurementsDoer.Activate(not self.eyeDiagram.measDict is None)
        self.BathtubCurveDoer.Activate((not self.eyeDiagram.measDict is None) and ('Bathtub' in self.eyeDiagram.measDict.keys()))
        self.eyeCanvas.pack_forget()
        config=self.eyeArgs['Config']
        R=config['Rows']; C=config['Columns']
        C=int(C*config['ScaleX']/100.*config['UI']); R=int(R*config['ScaleY']/100.)
        self.eyeCanvas=tk.Canvas(self.eyeFrame,width=C,height=R)
        if not self.eyeDiagram.img is None:
            self.eyeStatus.set(ToSI(int(self.eyeDiagram.prbswf.td.K/self.eyeDiagram.prbswf.td.Fs*self.eyeDiagram.baudrate),'UI')+' at '+ToSI(self.eyeDiagram.baudrate,'Baud'))
            self.eyeImage=ImageTk.PhotoImage(self.eyeDiagram.img)
            self.eyeCanvas.create_image(C/2,R/2,image=self.eyeImage)
            self.eyeCanvas.pack(expand=tk.YES,fill=tk.BOTH)
            self.statusbar.set('Calculation complete')
        else:
            self.statusbar.set('Calculation failed or aborted')
            self.eyeStatus.set('No Eye')

    def EyeDiagramMeasurementsDialog(self):
        if not hasattr(self,'eyeDiagramMeasurementsDialog'):
            self.eyeDiagramMeasurementsDialog=EyeDiagramMeasurementsDialog(self,self.name)
        if self.eyeDiagramMeasurementsDialog == None:
            self.eyeDiagramMeasurementsDialog=EyeDiagramMeasurementsDialog(self,self.name)
        else:
            if not self.eyeDiagramMeasurementsDialog.winfo_exists():
                self.eyeDiagramMeasurementsDialog=EyeDiagramMeasurementsDialog(self,self.name)
        return self.eyeDiagramMeasurementsDialog


    def UpdateWaveforms(self):
        self.eyeDiagram.prbswf=self.eyeArgs['Waveform']
        self.eyeDiagram.baudrate=self.eyeArgs['BaudRate']
        self.eyeDiagram.config=self.eyeArgs['Config']
        self.CalculateEyeDiagram()
        self.deiconify()
        self.lift()
        return self

    def BathtubCurveDialog(self):
        if not hasattr(self,'bathtubCurveDialog'):
            self.bathtubCurveDialog=BathtubCurveDialog(self,self.name)
        if self.bathtubCurveDialog == None:
            self.bathtubCurveDialog=BathtubCurveDialog(self,self.name)
        else:
            if not self.bathtubCurveDialog.winfo_exists():
                self.bathtubCurveDialog=BathtubCurveDialog(self,self.name)
        return self.bathtubCurveDialog

    def onBathtubCurve(self):
        windowOpen=hasattr(self,'bathtubCurveDialog')\
            and (self.bathtubCurveDialog != None)\
            and bool(self.bathtubCurveDialog.winfo_exists())
        if not windowOpen:
            self.BathtubCurveDialog().UpdateMeasurements(self.eyeDiagram.measDict)
        self.BathtubCurveDialog().lift()

    def onEyeMeasurements(self):
        windowOpen=hasattr(self,'eyeDiagramMeasurementsDialog')\
            and (self.eyeDiagramMeasurementsDialog != None)\
            and bool(self.eyeDiagramMeasurementsDialog.winfo_exists())
        if not windowOpen:
            self.EyeDiagramMeasurementsDialog().UpdateMeasurements(self.eyeDiagram.measDict)
        self.EyeDiagramMeasurementsDialog().lift()