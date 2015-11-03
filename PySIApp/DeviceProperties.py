'''
Created on Oct 15, 2015

@author: peterp
'''
from Tkinter import *
import copy
from tkFileDialog import askopenfilename
import os

from PartProperty import *

def ConvertFileNameToRelativePath(filename):
    if filename!='':
        filenameList=filename.split('/')
        if len(filenameList)>1:
            currentWorkingDirectoryList=os.getcwd().split('/')
            atOrBelow=True
            for tokenIndex in range(min(len(filenameList),len(currentWorkingDirectoryList))):
                if filenameList[tokenIndex]!=currentWorkingDirectoryList[tokenIndex]:
                    atOrBelow=False
                    break
            if atOrBelow: tokenIndex=tokenIndex+1
            if tokenIndex > 0:
                filenameprefix=''
                for i in range(tokenIndex,len(currentWorkingDirectoryList)):
                    filenameprefix=filenameprefix+'../'
                filenamesuffix='/'.join(filenameList[tokenIndex:])
                filename=filenameprefix+filenamesuffix
    return filename

class DeviceProperty(Frame):
    def __init__(self,parentFrame,device,partProperty,callBack):
        Frame.__init__(self,parentFrame)
        self.pack(side=TOP,fill=X,expand=YES)
        self.parentFrame=parentFrame
        self.device=device
        self.partProperty=partProperty
        self.callBack=callBack
        self.pack(side=TOP,fill=X,expand=YES)
        self.propertyString=StringVar(value=str(self.partProperty.PropertyString(stype='entry')))
        self.propertyVisible=IntVar(value=int(self.partProperty.visible))
        self.keywordVisible=IntVar(value=int(self.partProperty.keywordVisible))
        propertyVisibleCheckBox = Checkbutton(self,variable=self.propertyVisible,command=self.onPropertyVisible)
        propertyVisibleCheckBox.pack(side=LEFT,expand=NO,fill=X)
        keywordVisibleCheckBox = Checkbutton(self,variable=self.keywordVisible,command=self.onKeywordVisible)
        keywordVisibleCheckBox.pack(side=LEFT,expand=NO,fill=X)
        propertyLabel = Label(self,width=25,text=self.partProperty.description+': ',anchor='e')
        propertyLabel.pack(side=LEFT, expand=NO, fill=X)
        propertyEntry = Entry(self,textvariable=self.propertyString)
        propertyEntry.config(width=15)
        propertyEntry.bind('<Return>',self.onEntered)
        propertyEntry.bind('<FocusIn>',self.onTouched)
        propertyEntry.bind('<Button-3>',self.onUntouched)
        propertyEntry.bind('<Escape>',self.onUntouched)
        propertyEntry.bind('<FocusOut>',self.onUntouched)
        propertyEntry.pack(side=LEFT, expand=YES, fill=X)
        if self.partProperty.type == 'file':
            propertyFileBrowseButton = Button(self,text='browse',command=self.onFileBrowse)
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
    def onPropertyVisible(self):
        self.partProperty.visible=bool(self.propertyVisible.get())
        self.callBack()
    def onKeywordVisible(self):
        self.partProperty.keywordVisible=bool(self.keywordVisible.get())
        self.callBack()
    def onEntered(self,event):
        self.partProperty.SetValueFromString(self.propertyString.get())
        self.onUntouched(event)
    def onTouched(self,event):
        self.propertyString.set('')
    def onUntouched(self,event):
        self.propertyString.set(self.partProperty.PropertyString(stype='entry'))
        self.callBack()
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
        for p in range(len(self.device.propertiesList)):
            if not self.device.propertiesList[p].hidden:
                self.propertyFrameList.append(DeviceProperty(propertyListFrame,self.device,self.device.propertiesList[p],self.UpdatePicture))
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
        self.initial_focus = self.body(self.DeviceProperties)
        self.DeviceProperties.pack(side=TOP,fill=BOTH,expand=YES,padx=5, pady=5)

        self.buttonbox()

        #self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

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

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

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

    def validate(self):

        return 1 # override

    def apply(self):
        self.result=copy.deepcopy(self.device)
        for propFrame in self.DeviceProperties.propertyFrameList:
            self.result[propFrame.partProperty.propertyName]=propFrame.partProperty
        return