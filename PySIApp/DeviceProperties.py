'''
Created on Oct 15, 2015

@author: peterp
'''
from Tkinter import *
import copy
from tkFileDialog import askopenfilename

from PartProperty import *

class DeviceProperties(Frame):
    def __init__(self,parent,device):
        Frame.__init__(self,parent)
        self.title = 'Add '+device.PartPropertyByName('type').value
        self.device=device
        self.propertyStrings=[StringVar(value=str(prop.value)) for prop in self.device.propertiesList]
        self.propertyVisible=[IntVar(value=int(prop.visible)) for prop in self.device.propertiesList]

        propertyListFrame = Frame(self)
        propertyListFrame.pack(side=TOP,fill=X,expand=NO)
        for p in range(len(self.device.propertiesList)):
            if not self.device.propertiesList[p].hidden:
                prop=self.device.propertiesList[p]
                propertyFrame = Frame(propertyListFrame)
                propertyFrame.pack(side=TOP,fill=X,expand=YES)
                propertyVisibleCheckBox = Checkbutton(propertyFrame,variable=self.propertyVisible[p],command=self.onPropertyVisible)
                propertyVisibleCheckBox.pack(side=LEFT,expand=NO,fill=X)
                propertyLabel = Label(propertyFrame,width=20,text=prop.description+': ',anchor='e')
                propertyLabel.pack(side=LEFT, expand=NO, fill=X)
                propertyEntry = Entry(propertyFrame,textvariable=self.propertyStrings[p])
                propertyEntry.config(width=10)
                propertyEntry.bind('<Button-1>',lambda event,arg=p: self.onMouseButton1(event,arg))
                propertyEntry.pack(side=LEFT, expand=YES, fill=X)
        orientationFrame = Frame(propertyListFrame)
        orientationFrame.pack(side=TOP,fill=X,expand=NO)
        self.orientationString=StringVar(value=str(self.device.partPicture.current.orientation))
        orientationLabel = Label(orientationFrame,text='rotation: ')
        orientationLabel.pack(side=LEFT,expand=NO,fill=X)
        Radiobutton(orientationFrame,text='0',variable=self.orientationString,value='0',command=self.onOrientationChange).pack(side=LEFT,expand=NO,fill=X)
        Radiobutton(orientationFrame,text='90',variable=self.orientationString,value='90',command=self.onOrientationChange).pack(side=LEFT,expand=NO,fill=X)
        Radiobutton(orientationFrame,text='180',variable=self.orientationString,value='180',command=self.onOrientationChange).pack(side=LEFT,expand=NO,fill=X)
        Radiobutton(orientationFrame,text='270',variable=self.orientationString,value='270',command=self.onOrientationChange).pack(side=LEFT,expand=NO,fill=X)
        Button(orientationFrame,text='toggle',command=self.onToggleOrientation).pack(side=LEFT,expand=NO,fill=X)
        partPictureFrame = Frame(self)
        partPictureFrame.pack(side=TOP,fill=BOTH,expand=YES)
        self.partPictureCanvas = Canvas(partPictureFrame)
        self.partPictureCanvas.config(relief=SUNKEN,borderwidth=1)
        self.partPictureCanvas.pack(side=TOP,fill=BOTH,expand=YES)
        self.partPictureCanvas.bind('<Button-1>',self.onMouseButton1InPartPicture)
        device.DrawDevice(self.partPictureCanvas,20,-device.partPicture.current.origin[0]+5,-device.partPicture.current.origin[1]+5)

    def onToggleOrientation(self):
        self.device.partPicture.current.Rotate()
        self.orientationString.set(str(self.device.partPicture.current.orientation))
        self.onOrientationChange()

    def onOrientationChange(self):
        self.device.partPicture.current.ApplyOrientation(self.orientationString.get())
        self.partPictureCanvas.delete(ALL)
        self.device.DrawDevice(self.partPictureCanvas,20,-self.device.partPicture.current.origin[0]+5,-self.device.partPicture.current.origin[1]+5)

    def onMouseButton1InPartPicture(self,event):
        numPictures=len(self.device.partPicture.partPictureClassList)
        current=self.device.partPicture.partPictureSelected
        origin=self.device.partPicture.current.origin
        selected=current+1
        if selected >= numPictures:
            selected = 0
        self.device.partPicture.SwitchPartPicture(selected)
        self.device.partPicture.current.SetOrigin(origin)
        self.partPictureCanvas.delete(ALL)
        self.device.DrawDevice(self.partPictureCanvas,20,-self.device.partPicture.current.origin[0]+5,-self.device.partPicture.current.origin[1]+5)

    def onPropertyVisible(self):
        for p in range(len(self.device.propertiesList)):
            self.device.propertiesList[p].visible=bool(self.propertyVisible[p].get())
        self.partPictureCanvas.delete(ALL)
        self.device.DrawDevice(self.partPictureCanvas,20,-self.device.partPicture.current.origin[0]+5,-self.device.partPicture.current.origin[1]+5)

    def onMouseButton1(self,event,arg):
        print 'entry clicked',arg
        if self.device.propertiesList[arg].propertyName == PartPropertyFileName().propertyName:
            extension='.s'+str(self.device['ports'].value)+'p'
            filename=askopenfilename(filetypes=[('s-parameters', extension)])
            self.propertyStrings[arg].set(filename)
        elif self.device.propertiesList[arg].propertyName == PartPropertyWaveformFileName().propertyName:
            extension='.txt'
            filename=askopenfilename(filetypes=[('waveforms', extension)])
            self.propertyStrings[arg].set(filename)

class DevicePropertiesDialog(Toplevel):
    def __init__(self,parent,device):
        Toplevel.__init__(self, parent)
        self.transient(parent)

        self.device = device

        self.title('Add '+device['description'].value)

        self.parent = parent

        self.result = None

        self.DeviceProperties = DeviceProperties(self,device)
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

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
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
        for p in range(len(self.device.propertiesList)):
            self.result.propertiesList[p].value=self.DeviceProperties.propertyStrings[p].get()
            self.result.propertiesList[p].visible=bool(self.DeviceProperties.propertyVisible[p].get())