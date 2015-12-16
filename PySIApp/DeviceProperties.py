'''
Created on Oct 15, 2015

@author: peterp
'''
from Tkinter import *
import copy
from tkFileDialog import askopenfilename
import os

from PartProperty import *
from Files import *
from SParameterViewerWindow import *

class DeviceProperty(Frame):
    def __init__(self,parentFrame,device,partProperty,callBack,hidden):
        Frame.__init__(self,parentFrame)
        if not hidden:
            self.pack(side=TOP,fill=X,expand=YES)
        self.parentFrame=parentFrame
        self.device=device
        self.partProperty=partProperty
        self.callBack=callBack
        self.propertyString=StringVar(value=str(self.partProperty.PropertyString(stype='entry')))
        self.propertyVisible=IntVar(value=int(self.partProperty.visible))
        self.keywordVisible=IntVar(value=int(self.partProperty.keywordVisible))
        propertyVisibleCheckBox = Checkbutton(self,variable=self.propertyVisible,command=self.onPropertyVisible)
        propertyVisibleCheckBox.pack(side=LEFT,expand=NO,fill=X)
        keywordVisibleCheckBox = Checkbutton(self,variable=self.keywordVisible,command=self.onKeywordVisible)
        keywordVisibleCheckBox.pack(side=LEFT,expand=NO,fill=X)
        propertyLabel = Label(self,width=25,text=self.partProperty.description+': ',anchor='e')
        propertyLabel.pack(side=LEFT, expand=NO, fill=X)
        self.propertyEntry = Entry(self,textvariable=self.propertyString)
        self.propertyEntry.config(width=15)
        self.propertyEntry.bind('<Return>',self.onEntered)
        self.propertyEntry.bind('<Button-1>',self.onTouched)
        self.propertyEntry.bind('<Button-1>',self.onTouched)
        self.propertyEntry.bind('<Double-Button-1>',self.onCleared)
        self.propertyEntry.bind('<Button-3>',self.onUntouchedLoseFocus)
        self.propertyEntry.bind('<Escape>',self.onUntouchedLoseFocus)
        self.propertyEntry.bind('<FocusOut>',self.onUntouched)
        self.propertyEntry.pack(side=LEFT, expand=YES, fill=X)
        if self.partProperty.type == 'file':
            propertyFileBrowseButton = Button(self,text='browse',command=self.onFileBrowse)
            propertyFileBrowseButton.pack(side=LEFT,expand=NO,fill=X)
            if self.partProperty.propertyName == PartPropertyFileName().propertyName:
                propertyFileBrowseButton = Button(self,text='view',command=self.onFileView)
                propertyFileBrowseButton.pack(side=LEFT,expand=NO,fill=X)
    def onFileBrowse(self):
        self.parentFrame.focus()
        if self.partProperty.propertyName == PartPropertyFileName().propertyName:
            extension='.s'+self.device['ports'].PropertyString(stype='raw')+'p'
            filetypename='s-parameters'
        elif self.partProperty.propertyName == PartPropertyWaveformFileName().propertyName:
            extension='.txt'
            filetypename='waveforms'
        else:
            extension=''
            filetypename='all'
        filename=askopenfilename(filetypes=[(filetypename,extension)])
        if filename != '':
            filename=ConvertFileNameToRelativePath(filename)
            self.propertyString.set(filename)
            self.partProperty.SetValueFromString(self.propertyString.get())
            self.callBack()
    def onFileView(self):
        self.parentFrame.focus()
        if self.partProperty.propertyName == PartPropertyFileName().propertyName:
            extension='.s'+self.device['ports'].PropertyString(stype='raw')+'p'
            filetypename='s-parameters'
        elif self.partProperty.propertyName == PartPropertyWaveformFileName().propertyName:
            extension='.txt'
            filetypename='waveforms'
        else:
            extension=''
            filetypename='all'
        #filename=askopenfilename(filetypes=[(filetypename,extension)])
        filename=self.partProperty.GetValue()
        if filename != '':
            import SignalIntegrity as si
            sp=si.sp.File(filename)
            SParametersDialog(self,sp,filename)
            #self.callBack()
    def onPropertyVisible(self):
        self.partProperty.visible=bool(self.propertyVisible.get())
        self.callBack()
    def onKeywordVisible(self):
        self.partProperty.keywordVisible=bool(self.keywordVisible.get())
        self.callBack()
    def onEntered(self,event):
        self.partProperty.SetValueFromString(self.propertyString.get())
        self.onUntouchedLoseFocus(event)
    def onTouched(self,event):
        self.propertyEntry.focus()
    def onCleared(self,event):
        self.propertyString.set('')
    def onUntouched(self,event):
        self.propertyString.set(self.partProperty.PropertyString(stype='entry'))
        self.callBack()
    def onUntouchedLoseFocus(self,event):
        self.parentFrame.focus()

class DeviceProperties(Frame):
    def __init__(self,parent,device):
        Frame.__init__(self,parent)
        self.title = device.PartPropertyByName('type').PropertyString(stype='raw')
        self.device=device
        propertyListFrame = Frame(self)
        propertyListFrame.pack(side=TOP,fill=X,expand=NO)
        propertyListFrame.bind("<Return>", parent.ok)
        self.propertyFrameList=[]
        for partProperty in self.device.propertiesList:
            self.propertyFrameList.append(DeviceProperty(propertyListFrame,self.device,partProperty,self.UpdatePicture,partProperty.hidden))
        rotationFrame = Frame(propertyListFrame)
        rotationFrame.pack(side=TOP,fill=X,expand=NO)
        self.rotationString=StringVar(value=str(self.device.partPicture.current.orientation))
        rotationLabel = Label(rotationFrame,text='rotation: ')
        rotationLabel.pack(side=LEFT,expand=NO,fill=X)
        Radiobutton(rotationFrame,text='0',variable=self.rotationString,value='0',command=self.onOrientationChange).pack(side=LEFT,expand=NO,fill=X)
        Radiobutton(rotationFrame,text='90',variable=self.rotationString,value='90',command=self.onOrientationChange).pack(side=LEFT,expand=NO,fill=X)
        Radiobutton(rotationFrame,text='180',variable=self.rotationString,value='180',command=self.onOrientationChange).pack(side=LEFT,expand=NO,fill=X)
        Radiobutton(rotationFrame,text='270',variable=self.rotationString,value='270',command=self.onOrientationChange).pack(side=LEFT,expand=NO,fill=X)
        Button(rotationFrame,text='toggle',command=self.onToggleRotation).pack(side=LEFT,expand=NO,fill=X)
        mirrorFrame=Frame(propertyListFrame)
        mirrorFrame.pack(side=TOP,fill=X,expand=NO)
        mirrorLabel = Label(mirrorFrame,text='mirror: ')
        mirrorLabel.pack(side=LEFT,expand=NO,fill=X)
        self.mirrorVerticallyVar=IntVar(value=int(self.device.partPicture.current.mirroredVertically))
        mirrorVerticallyCheckBox = Checkbutton(mirrorFrame,text='Vertically',variable=self.mirrorVerticallyVar,command=self.onOrientationChange)
        mirrorVerticallyCheckBox.pack(side=LEFT,expand=NO,fill=X)
        self.mirrorHorizontallyVar=IntVar(value=int(self.device.partPicture.current.mirroredHorizontally))
        mirrorHorizontallyCheckBox = Checkbutton(mirrorFrame,text='Horizontally',variable=self.mirrorHorizontallyVar,command=self.onOrientationChange)
        mirrorHorizontallyCheckBox.pack(side=LEFT,expand=NO,fill=X)
        partPictureFrame = Frame(self)
        partPictureFrame.pack(side=TOP,fill=BOTH,expand=YES)
        self.partPictureCanvas = Canvas(partPictureFrame)
        self.partPictureCanvas.config(relief=SUNKEN,borderwidth=1)
        self.partPictureCanvas.pack(side=TOP,fill=BOTH,expand=YES)
        self.partPictureCanvas.bind('<Button-1>',self.onMouseButton1InPartPicture)
        device.DrawDevice(self.partPictureCanvas,20,-device.partPicture.current.origin[0]+5,-device.partPicture.current.origin[1]+5)

    def UpdatePicture(self):
        self.partPictureCanvas.delete(ALL)
        self.device.DrawDevice(self.partPictureCanvas,20,-self.device.partPicture.current.origin[0]+5,-self.device.partPicture.current.origin[1]+5)

    def onToggleRotation(self):
        self.device.partPicture.current.Rotate()
        self.rotationString.set(str(self.device.partPicture.current.orientation))
        self.onOrientationChange()

    def onOrientationChange(self):
        self.device.partPicture.current.ApplyOrientation(self.rotationString.get(),bool(self.mirrorHorizontallyVar.get()),bool(self.mirrorVerticallyVar.get()))
        self.UpdatePicture()
    def onMouseButton1InPartPicture(self,event):
        numPictures=len(self.device.partPicture.partPictureClassList)
        current=self.device.partPicture.partPictureSelected
        origin=self.device.partPicture.current.origin
        selected=current+1
        if selected >= numPictures:
            selected = 0
        self.device.partPicture.SwitchPartPicture(selected)
        self.UpdatePicture()

class DevicePropertiesDialog(Toplevel):
    def __init__(self,parent,device):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        self.device = copy.deepcopy(device)
        self.title(self.device['description'].PropertyString(stype='raw'))
        self.parent = parent
        self.result = None
        self.DeviceProperties = DeviceProperties(self,self.device)
        self.initial_focus = self.DeviceProperties
        self.DeviceProperties.pack(side=TOP,fill=BOTH,expand=YES,padx=5, pady=5)
        self.buttonbox()
        self.wait_visibility(self)
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        #self.geometry("+%d+%d" % (parent.winfo_rootx()+50,parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)
    # construction hooks

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self)
        w = Button(box, text="OK", width=10, command=self.ok)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)
        #self.bind("<Return>", self.ok)
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
            self.result.propertiesList[pIndex]=propFrame.partProperty
        return