"""
DeviceProperties.py
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

from SignalIntegrity.App.FilePicker import AskOpenFileName
from SignalIntegrity.App.Files import FileParts
from SignalIntegrity.App.SParameterViewerWindow import SParametersDialog
from SignalIntegrity.App.Simulator import SimulatorDialog
from SignalIntegrity.App.Device import Device
import SignalIntegrity.App.Project

class DeviceProperty(tk.Frame):
    def __init__(self,parentFrame,parent,partProperty):
        tk.Frame.__init__(self,parentFrame)
        if not partProperty['Hidden']:
            self.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
        self.parent=parent
        self.parentFrame=parentFrame
        self.device=parent.device
        self.partProperty=partProperty
        self.callBack=parent.UpdatePicture
        self.propertyString=tk.StringVar(value=str(self.partProperty.PropertyString(stype='entry')))
        self.propertyVisible=tk.IntVar(value=int(self.partProperty['Visible']))
        self.keywordVisible=tk.IntVar(value=int(self.partProperty['KeywordVisible']))
        propertyVisibleCheckBox = tk.Checkbutton(self,variable=self.propertyVisible,command=self.onPropertyVisible)
        propertyVisibleCheckBox.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        keywordVisibleCheckBox = tk.Checkbutton(self,variable=self.keywordVisible,command=self.onKeywordVisible)
        keywordVisibleCheckBox.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        propertyLabel = tk.Label(self,width=35,text=self.partProperty['Description']+': ',anchor='e')
        propertyLabel.pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        self.propertyEntry = tk.Entry(self,textvariable=self.propertyString)
        self.propertyEntry.config(width=15)
        self.propertyEntry.bind('<Return>',self.onEntered)
        self.propertyEntry.bind('<Tab>',self.onEntered)
        self.propertyEntry.bind('<Button-1>',self.onTouched)
        self.propertyEntry.bind('<Button-1>',self.onTouched)
        self.propertyEntry.bind('<Double-Button-1>',self.onCleared)
        self.propertyEntry.bind('<Button-3>',self.onUntouchedLoseFocus)
        self.propertyEntry.bind('<Escape>',self.onUntouchedLoseFocus)
        self.propertyEntry.bind('<FocusOut>',self.onUntouched)
        self.propertyEntry.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        if self.partProperty['Type'] == 'file':
            self.propertyFileBrowseButton = tk.Button(self,text='browse',command=self.onFileBrowse)
            self.propertyFileBrowseButton.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            if self.partProperty['PropertyName'] == 'filename' or\
                self.partProperty['PropertyName'] == 'waveformfilename':
                self.propertyFileViewButton = tk.Button(self,text='view',command=self.onFileView)
                self.propertyFileViewButton.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
    def onFileBrowse(self):
        # this is a seemingly ugly workaround
        # I do this because when you change the number of ports and then touch the file
        # browse button, the ports are updated after this call based on the button press.
        # without this ugly thing, the file extension reflects the wrong number of ports
        # until the next time you press the button, when it is right.
        # This workaround forces the ports to be updated now.
        for pp in range(len(self.parent.device.propertiesList)):
            if self.parent.device.propertiesList[pp]['PropertyName'] == 'ports':
                self.parent.propertyFrameList[pp].onUntouched(None)
        # end of ugly workaround
        self.callBack()
        if self.partProperty['PropertyName'] == 'filename':
            extension='.s'+self.device['ports'].PropertyString(stype='raw')+'p'
            filetypename='s-parameters'
        elif self.partProperty['PropertyName'] == 'waveformfilename':
            extension='.txt'
            filetypename='waveforms'
        else:
            extension=''
            filetypename='all'
        currentFileParts=FileParts(self.partProperty.PropertyString(stype='raw'))
        if currentFileParts.filename=='':
            initialDirectory=self.parent.parent.parent.fileparts.AbsoluteFilePath()
            initialFile=''
        else:
            initialDirectory=currentFileParts.AbsoluteFilePath()
            if currentFileParts.fileext in ['.si',extension]:
                initialFile=currentFileParts.FileNameWithExtension()
            else:
                initialFile=currentFileParts.filename+extension
        filename=AskOpenFileName(parent=self,
                                 filetypes=[(filetypename,extension),('project','.si')],
                                 initialdir=initialDirectory,
                                 initialfile=initialFile)
        if filename is None:
            filename=''
        if isinstance(filename,tuple):
            filename=''
        filename=str(filename)
        if filename != '':
            filename=FileParts(filename).FullFilePathExtension()
            self.propertyString.set(filename)
            self.partProperty.SetValueFromString(self.propertyString.get())
            self.callBack()
        if self.partProperty['PropertyName'] == 'waveformfilename':
            filename=self.partProperty.GetValue()
            isProject=FileParts(filename).fileext == '.si'
            for propertyFrame in self.parent.propertyFrameList:
                if propertyFrame.partProperty['PropertyName']=='wfprojname':
                    propertyFrame.partProperty['Hidden']=not isProject
        self.callBack()

    def onFileView(self):
        self.parentFrame.focus()
        filename=self.partProperty.GetValue()
        if filename != '':
            import SignalIntegrity.Lib as si
            if self.partProperty['PropertyName'] == 'filename':
                fp=FileParts(filename)
                if fp.fileext == '.si':
                    result=os.system('SignalIntegrity '+os.path.abspath(filename)+' --external')
                    if result != 0:
                        messagebox.showerror('ProjectFile','could not be opened')
                        return
                else:
                    try:
                        sp=si.sp.SParameterFile(filename)
                    except si.SignalIntegrityException as e:
                        messagebox.showerror('S-parameter Viewer',e.parameter+': '+e.message)
                        return
                    spd=SParametersDialog(self.parent.parent.parent,sp,filename)
                    spd.grab_set()
            elif self.partProperty['PropertyName'] == 'waveformfilename':
                if FileParts(filename).fileext == '.si':
                    result=os.system('SignalIntegrity '+os.path.abspath(filename)+' --external')
                    if result != 0:
                        messagebox.showerror('ProjectFile','could not be opened')
                        return
                else:
                    filenametoshow=('/'.join(filename.split('\\'))).split('/')[-1]
                    if filenametoshow is None:
                        filenametoshow=''
                    try:
                        wf=self.parent.device.Waveform()
                    except si.SignalIntegrityException as e:
                        messagebox.showerror('Waveform Viewer',e.parameter+': '+e.message)
                        return
                    sd=SimulatorDialog(self.parent.parent)
                    sd.title(filenametoshow)
                    sd.UpdateWaveforms([wf],[filenametoshow])
                    sd.state('normal')
                    sd.grab_set()
    def onPropertyVisible(self):
        self.partProperty['Visible']=bool(self.propertyVisible.get())
        self.callBack()
    def onKeywordVisible(self):
        self.partProperty['KeywordVisible']=bool(self.keywordVisible.get())
        self.callBack()
    def onEntered(self,event):
        self.partProperty.SetValueFromString(self.propertyString.get())
        if self.partProperty['PropertyName'] == 'waveformfilename':
            filename=self.partProperty.GetValue()
            isProject=FileParts(filename).fileext == '.si'
            for propertyFrame in self.parent.propertyFrameList:
                if propertyFrame.partProperty['PropertyName']=='wfprojname':
                    propertyFrame.partProperty['Hidden']=not isProject
        self.callBack()
        self.onUntouchedLoseFocus(event)
    def onTouched(self,event):
        self.propertyEntry.focus()
    def onCleared(self,event):
        self.propertyString.set('')
    def onUntouched(self,event):
        self.partProperty.SetValueFromString(self.propertyString.get())
        self.propertyString.set(self.partProperty.PropertyString(stype='entry'))
        self.callBack()
    def onUntouchedLoseFocus(self,event):
        self.parentFrame.focus()

class DeviceProperties(tk.Frame):
    def __init__(self,parent,device,advancedMode=False):
        tk.Frame.__init__(self,parent)
        self.parent=parent
        self.title = device.PartPropertyByName('type').PropertyString(stype='raw')
        self.device=device
        if isinstance(self.device,Device): # part other than file - allow viewing
            if not 'file name' in [property['Description'] for property in self.device.propertiesList]:
                if self.device.netlist['DeviceName']=='device':
                    partViewFrame=tk.Frame(self)
                    partViewFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
                    self.partViewButton = tk.Button(partViewFrame,text='view s-parameters according to calc properties',command=self.onPartView)
                    self.partViewButton.pack(expand=tk.NO,fill=tk.NONE,anchor=tk.CENTER)
                elif self.device.netlist['DeviceName'] in ['voltagesource','currentsource']:
                    partViewFrame=tk.Frame(self)
                    partViewFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
                    self.waveformViewButton = tk.Button(partViewFrame,text='view waveform',command=self.onWaveformView)
                    self.waveformViewButton.pack(expand=tk.NO,fill=tk.NONE,anchor=tk.CENTER)
        keywords = [property['Keyword'] for property in self.device.propertiesList]
        if 'wffile' in keywords:
            fileName = self.device.propertiesList[keywords.index('wffile')].GetValue()
            ext=str.lower(fileName).split('.')[-1]
            self.device.propertiesList[keywords.index('wfprojname')]['Hidden']=(ext != 'si')
        propertyListFrame = tk.Frame(self)
        propertyListFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        propertyListFrame.bind("<Return>", parent.ok)
        self.propertyFrameList=[]
        for partProperty in self.device.propertiesList:
            self.propertyFrameList.append(DeviceProperty(propertyListFrame,self,partProperty))
        self.rotationFrame = tk.Frame(propertyListFrame)
        self.rotationFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.rotationString=tk.StringVar(value=str(self.device.partPicture.current.orientation))
        rotationLabel = tk.Label(self.rotationFrame,text='rotation: ')
        rotationLabel.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        tk.Radiobutton(self.rotationFrame,text='0',variable=self.rotationString,value='0',command=self.onOrientationChange).pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        tk.Radiobutton(self.rotationFrame,text='90',variable=self.rotationString,value='90',command=self.onOrientationChange).pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        tk.Radiobutton(self.rotationFrame,text='180',variable=self.rotationString,value='180',command=self.onOrientationChange).pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        tk.Radiobutton(self.rotationFrame,text='270',variable=self.rotationString,value='270',command=self.onOrientationChange).pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        tk.Button(self.rotationFrame,text='toggle',command=self.onToggleRotation).pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        self.mirrorFrame=tk.Frame(propertyListFrame)
        self.mirrorFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        mirrorLabel = tk.Label(self.mirrorFrame,text='mirror: ')
        mirrorLabel.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        self.mirrorVerticallyVar=tk.IntVar(value=int(self.device.partPicture.current.mirroredVertically))
        mirrorVerticallyCheckBox = tk.Checkbutton(self.mirrorFrame,text='Vertically',variable=self.mirrorVerticallyVar,command=self.onOrientationChange)
        mirrorVerticallyCheckBox.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        self.mirrorHorizontallyVar=tk.IntVar(value=int(self.device.partPicture.current.mirroredHorizontally))
        mirrorHorizontallyCheckBox = tk.Checkbutton(self.mirrorFrame,text='Horizontally',variable=self.mirrorHorizontallyVar,command=self.onOrientationChange)
        mirrorHorizontallyCheckBox.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        if advancedMode:
            advancedModeFrame=tk.Frame(propertyListFrame)
            advancedModeFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
            pinNumbersLabel = tk.Label(advancedModeFrame,text='pin numbers:')
            pinNumbersLabel.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            pinNumbersOnButton = tk.Button(advancedModeFrame,text='on',command=self.onPinNumbersOn)
            pinNumbersOnButton.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            pinNumbersOffButton = tk.Button(advancedModeFrame,text='off',command=self.onPinNumbersOff)
            pinNumbersOffButton.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            showBoxLabel = tk.Label(advancedModeFrame,text='  show box:')
            showBoxLabel.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            showBoxOnButton = tk.Button(advancedModeFrame,text='on',command=self.onShowBoxOn)
            showBoxOnButton.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
            showBoxOffButton = tk.Button(advancedModeFrame,text='off',command=self.onShowBoxOff)
            showBoxOffButton.pack(side=tk.LEFT,expand=tk.NO,fill=tk.X)
        partPictureFrame = tk.Frame(self)
        partPictureFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        self.partPictureCanvas = tk.Canvas(partPictureFrame)
        self.partPictureCanvas.config(relief=tk.SUNKEN,borderwidth=1)
        self.partPictureCanvas.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES)
        self.partPictureCanvas.bind('<Button-1>',self.onMouseButton1InPartPicture)
        device.DrawDevice(self.partPictureCanvas,20,-device.partPicture.current.origin[0]+5,-device.partPicture.current.origin[1]+5)
        (minx,miny,maxx,maxy)=self.partPictureCanvas.bbox(tk.ALL) # bounding box that contains part picture
        if minx < 0 or miny < 0: # the top or left side of the picture is clipped
            # adjust the picture so that the left and top of the picture is in the window
            offsetx=max(-minx,0)
            offsety=max(-miny,0)
            self.partPictureCanvas.move(tk.ALL,offsetx,offsety)

    def UpdatePicture(self):
        self.partPictureCanvas.delete(tk.ALL)
        if not self.device['ports'] is None:
            self.device.partPicture.ports=self.device['ports'].GetValue()
        self.device.partPicture.SwitchPartPicture(self.device.partPicture.partPictureSelected)
        self.device.DrawDevice(self.partPictureCanvas,20,-self.device.partPicture.current.origin[0]+5,-self.device.partPicture.current.origin[1]+5)
        (minx,miny,maxx,maxy)=self.partPictureCanvas.bbox(tk.ALL) # bounding box that contains part picture
        if minx < 0 or miny < 0: # the top or left side of the picture is clipped
            # adjust the picture so that the left and top of the picture is in the window
            offsetx=max(-minx,0)
            offsety=max(-miny,0)
            self.partPictureCanvas.move(tk.ALL,offsetx,offsety)
        # also update part properties as some may have become hidden or unhidden
        self.mirrorFrame.pack_forget()
        self.rotationFrame.pack_forget()
        for propertyFrame in self.propertyFrameList:
            propertyFrame.pack_forget()
        for propertyFrame in self.propertyFrameList:
            if not propertyFrame.partProperty['Hidden']:
                propertyFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.YES)
        self.rotationFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
        self.mirrorFrame.pack(side=tk.TOP,fill=tk.X,expand=tk.NO)
    def onToggleRotation(self):
        self.device.partPicture.current.Rotate()
        self.rotationString.set(str(self.device.partPicture.current.orientation))
        self.onOrientationChange()

    def onOrientationChange(self):
        self.device.partPicture.current.ApplyOrientation(self.rotationString.get(),bool(self.mirrorHorizontallyVar.get()),bool(self.mirrorVerticallyVar.get()))
        self.UpdatePicture()

    def onPinNumbersOn(self):
        for pin in self.device.partPicture.current.pinListSupplied:
            pin.pinNumberVisible = True
        for pin in self.device.partPicture.current.pinList:
            pin.pinNumberVisible = True
        self.UpdatePicture()

    def onPinNumbersOff(self):
        for pin in self.device.partPicture.current.pinListSupplied:
            pin.pinNumberVisible = False
        for pin in self.device.partPicture.current.pinList:
            pin.pinNumberVisible = False
        self.UpdatePicture()

    def onShowBoxOn(self):
        pass

    def onShowBoxOff(self):
        pass

    def onMouseButton1InPartPicture(self,event):
        numPictures=len(self.device.partPicture.partPictureClassList)
        current=self.device.partPicture.partPictureSelected
        selected=current+1
        if selected >= numPictures:
            selected = 0
        self.device.partPicture.SwitchPartPicture(selected)
        self.UpdatePicture()

    def onPartView(self):
        self.focus()
        device=self.device
        numPorts=device['ports'].GetValue()
        referenceDesignator=device['ref'].GetValue()
        portLine='port'
        for port in range(numPorts):
            portLine=portLine+' '+str(port+1)+' '+referenceDesignator+' '+str(port+1)
        deviceLine=device.NetListLine()
        netList=[deviceLine,portLine]
        import SignalIntegrity.Lib as si
        spnp=si.p.SystemSParametersNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']))
        spnp.AddLines(netList)
        try:
            sp=spnp.SParameters()
        except si.SignalIntegrityException as e:
            messagebox.showerror('S-parameter Calculator',e.parameter+': '+e.message)
            return
        fileParts=copy.copy(self.parent.parent.fileparts)
        fileParts.filename=fileParts.filename+'_'+referenceDesignator
        spd=SParametersDialog(self.parent.parent,sp,filename=fileParts.FullFilePathExtension('s'+str(sp.m_P)+'p'))
        spd.grab_set()

    def onWaveformView(self):
        self.focus()
        device=self.device
        referenceDesignator=device['ref'].GetValue()
        import SignalIntegrity as si
        try:
            wf=device.Waveform()
        except si.SignalIntegrityException as e:
            messagebox.showerror('Waveform Viewer',e.parameter+': '+e.message)
            return
        sim=self.parent.parent.simulator
        sd=sim.SimulatorDialog()
        sd.title('Waveform')
        sim.UpdateWaveforms([wf],[referenceDesignator])
        sd.grab_set()

class DevicePropertiesDialog(tk.Toplevel):
    def __init__(self,parent,device):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        self.device = copy.deepcopy(device)
        self.title(self.device['desc'].PropertyString(stype='raw'))
        self.parent = parent
        self.result = None
        self.DeviceProperties = DeviceProperties(self,self.device)
        self.initial_focus = self.DeviceProperties
        self.DeviceProperties.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES,padx=5, pady=5)
        self.buttonbox()
        self.wait_visibility(self)
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)
    # construction hooks

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = tk.Frame(self)
        w = tk.Button(box, text="OK", width=10, command=self.ok)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()
    #
    # standard button semantics
    def ok(self, event=None):
        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
    #
    # command hooks
    def apply(self):
        self.result=copy.deepcopy(self.device)
        for pIndex in range(len(self.DeviceProperties.propertyFrameList)):
            propFrame=self.DeviceProperties.propertyFrameList[pIndex]
            propFrame.partProperty.SetValueFromString(propFrame.propertyString.get())
            self.result.propertiesList[pIndex]=propFrame.partProperty
        if not self.device['ports'] is None:
            self.result.partPicture.ports=self.result['ports'].GetValue()
        self.result.partPicture.SwitchPartPicture(self.result.partPicture.partPictureSelected)
        return
