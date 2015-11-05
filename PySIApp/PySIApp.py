from Tkinter import *

from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
import keyword
import copy

from PartPin import *
from PartPicture import *
from PartProperty import *
from Device import *
from DeviceProperties import *
from DevicePicker import *
from Schematic import *
from PlotWindow import *
from Simulator import Simulator

class NetListFrame(Frame):
    def __init__(self,parent,textToShow):
        Frame.__init__(self,parent)
        self.title = 'NetList'
        self.text=Text(self)
        self.text.pack(side=TOP, fill=BOTH, expand=YES)
        for line in textToShow:
            self.text.insert(END,line+'\n')

class NetListDialog(Toplevel):
    def __init__(self,parent,textToShow):
        Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('NetList')

        self.parent = parent

        self.result = None

        self.NetListFrame = NetListFrame(self,textToShow)
        self.initial_focus = self.body(self.NetListFrame)
        self.NetListFrame.pack(side=TOP,fill=BOTH,expand=YES,padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

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
        pass

class TheMenu(Menu):
    def __init__(self,parent):
        self.parent=parent
        Menu.__init__(self,self.parent.root)
        self.parent.root.config(menu=self)
        self.FileMenu=Menu(self)
        self.add_cascade(label='File',menu=self.FileMenu)
        self.FileMenu.add_command(label="Open Project",command=self.parent.onReadProjectFromFile)
        self.FileMenu.add_command(label="Save Project",command=self.parent.onWriteProjectToFile)
        self.FileMenu.add_separator()
        self.FileMenu.add_command(label="Clear Schematic",command=self.parent.onClearSchematic)
        self.FileMenu.add_separator()
        self.FileMenu.add_command(label="Export NetList",command=self.parent.onExportNetlist)

        self.PartsMenu=Menu(self)
        self.add_cascade(label='Edit',menu=self.PartsMenu)
        self.PartsMenu.add_command(label='Add Part',command=self.parent.onAddPart)
        self.PartsMenu.add_command(label='Add Wire',command=self.parent.onAddWire)
        self.PartsMenu.add_command(label='Add Port',command=self.parent.onAddPort)
        self.PartsMenu.add_command(label='Duplicate',command=self.parent.onDuplicate)

        self.ZoomMenu=Menu(self)
        self.add_cascade(label='Zoom',menu=self.ZoomMenu)
        self.ZoomMenu.add_command(label='Zoom In',command=self.parent.onZoomIn)
        self.ZoomMenu.add_command(label='Zoom Out',command=self.parent.onZoomOut)

        self.CalcMenu=Menu(self)
        self.add_cascade(label='Calculate',menu=self.CalcMenu)
        self.CalcMenu.add_command(label='Calculate S-parameters',command=self.parent.onCalculateSParameters)
        self.CalcMenu.add_command(label='Simulate',command=self.parent.onSimulate)

class ToolBar(Frame):
    def __init__(self,parent):
        self.parent=parent
        Frame.__init__(self,self.parent)
        self.pack(side=TOP,fill=X,expand=NO)
        self.addPartButtonIcon = PhotoImage(file='./icons/png/16x16/actions/edit-add-2.gif')
        self.addPartButton = Button(self,command=self.parent.onAddPart,image=self.addPartButtonIcon).pack(side=LEFT,fill=NONE,expand=NO)
        self.addWireButtonIcon = PhotoImage(file='./icons/png/16x16/actions/draw-line-3.gif')
        self.addWireButton = Button(self,command=self.parent.onAddWire,image=self.addWireButtonIcon).pack(side=LEFT,fill=NONE,expand=NO)
        self.zoomInButtonIcon = PhotoImage(file='./icons/png/16x16/actions/zoom-in-3.gif')
        self.zoomInButton = Button(self,command=self.parent.onZoomIn,image=self.zoomInButtonIcon).pack(side=LEFT,fill=NONE,expand=NO)
        self.zoomOutButtonIcon = PhotoImage(file='./icons/png/16x16/actions/zoom-out-3.gif')
        self.zoomOutButton = Button(self,command=self.parent.onZoomOut,image=self.zoomOutButtonIcon).pack(side=LEFT,fill=NONE,expand=NO)

class TheApp(Frame):
    def __init__(self):
        self.root = Tk()
        Frame.__init__(self, self.root)
        self.pack(fill=BOTH, expand=YES)

        self.root.title("PySI")

        img = PhotoImage(file='./icons/png/AppIcon2.gif')
        self.root.tk.call('wm', 'iconphoto', self.root._w, '-default', img)

        self.menu=TheMenu(self)
        self.toolbar=ToolBar(self)

        self.Drawing=Drawing(self)
        self.Drawing.pack(side=LEFT,fill=BOTH,expand=YES)

        self.root.bind('<Key>',self.onKey)

        self.plotDialog=None

        self.simulator = Simulator(self)
        self.filename=None

        self.root.mainloop()

    def onKey(self,event):
        print "pressed", repr(event.keycode), repr(event.keysym)
        if event.keysym == 'Delete': # delete
            if self.Drawing.stateMachine.state == 'WireSelected':
                del self.Drawing.schematic.wireList[self.Drawing.w]
                self.Drawing.stateMachine.Nothing()
            elif self.Drawing.stateMachine.state == 'DeviceSelected':
                del self.Drawing.schematic.deviceList[self.Drawing.deviceSelectedIndex]
                self.Drawing.stateMachine.Nothing()

    def onReadProjectFromFile(self):
        self.Drawing.stateMachine.Nothing()
        extension='.xml'
        filename=askopenfilename(filetypes=[('xml', extension)])
        if filename == '':
            return
        filenametokens=filename.split('.')
        if len(filenametokens)==0:
            return
        if len(filenametokens)==1:
            filename=filename+extension
        filename=ConvertFileNameToRelativePath(filename)
        tree=et.parse(filename)
        root=tree.getroot()
        for child in root:
            if child.tag == 'drawing':
                self.Drawing.InitFromXml(child)
            elif child.tag == 'simulator':
                self.simulator.InitFromXml(child, self)
        self.filename=filename
        self.Drawing.DrawSchematic()

    def onWriteProjectToFile(self):
        self.Drawing.stateMachine.Nothing()
        extension='.xml'
        if self.filename == None:
            filename=asksaveasfilename(filetypes=[('xml', extension)],defaultextension='.xml',initialdir=os.getcwd())
        else:
            filename=asksaveasfilename(filetypes=[('xml', extension)],defaultextension='.xml',initialfile=self.filename)
        if filename=='':
            return
        self.filename=filename
        projectElement=et.Element('Project')
        drawingElement=self.Drawing.xml()
        simulatorElement=self.simulator.xml()
        projectElement.extend([drawingElement,simulatorElement])
        et.ElementTree(projectElement).write(filename)

    def onClearSchematic(self):
        self.Drawing.stateMachine.Nothing()
        self.Drawing.schematic.Clear()
        self.Drawing.DrawSchematic()
        self.filename=None

    def onExportNetlist(self):
        self.Drawing.stateMachine.Nothing()
        nld = NetListDialog(self,self.Drawing.schematic.NetList().Text())

    def onAddPart(self):
        self.Drawing.stateMachine.Nothing()
        dpd=DevicePickerDialog(self)
        if dpd.result != None:
            devicePicked=copy.deepcopy(DeviceList[dpd.result])
            devicePicked.AddPartProperty(PartPropertyReferenceDesignator(''))
            defaultProperty = devicePicked[PartPropertyDefaultReferenceDesignator().propertyName]
            if defaultProperty != None:
                defaultPropertyValue = defaultProperty.GetValue()
                uniqueReferenceDesignator = self.Drawing.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
                if uniqueReferenceDesignator != None:
                    devicePicked[PartPropertyReferenceDesignator().propertyName].SetValueFromString(uniqueReferenceDesignator)
            dpe=DevicePropertiesDialog(self,devicePicked)
            self.Drawing.partLoaded = dpe.result
            self.Drawing.stateMachine.PartLoaded()
    def onDuplicate(self):
        if self.Drawing.stateMachine.state == 'DeviceSelected':
            self.Drawing.partLoaded=copy.deepcopy(self.Drawing.deviceSelected)
            if self.Drawing.partLoaded['type'].GetValue() == 'Port':
                portNumberList=[]
                for device in self.Drawing.schematic.deviceList:
                    if device['type'].GetValue() == 'Port':
                        portNumberList.append(int(device['portnumber'].GetValue()))
                portNumber=1
                while portNumber in portNumberList:
                    portNumber=portNumber+1
                self.Drawing.partLoaded['portnumber'].SetValueFromString(str(portNumber))
            else:
                defaultProperty = self.Drawing.partLoaded[PartPropertyDefaultReferenceDesignator().propertyName]
                if defaultProperty != None:
                    defaultPropertyValue = defaultProperty.GetValue()
                    uniqueReferenceDesignator = self.Drawing.schematic.NewUniqueReferenceDesignator(defaultPropertyValue)
                    if uniqueReferenceDesignator != None:
                        self.Drawing.partLoaded[PartPropertyReferenceDesignator().propertyName].SetValueFromString(uniqueReferenceDesignator)
            self.Drawing.stateMachine.PartLoaded()
        else:
            self.Drawing.stateMachine.Nothing()

    def onAddWire(self):
        self.Drawing.wireLoaded=Wire([(0,0)])
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

    def onZoomIn(self):
        self.Drawing.grid = self.Drawing.grid*2
        self.Drawing.DrawSchematic()

    def onZoomOut(self):
        self.Drawing.grid = max(1,self.Drawing.grid/2)
        self.Drawing.DrawSchematic()

    def onCalculateSParameters(self):
        self.Drawing.stateMachine.Nothing()
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity as si
        spnp=si.p.SystemSParametersNumericParser(si.fd.EvenlySpacedFrequencyList(10e9,100))
        spnp.AddLines(netList)
        sp=spnp.SParameters()
        ports=sp.m_P
        extension='.s'+str(ports)+'p'
        filename=asksaveasfilename(filetypes=[('s-parameters', extension)],defaultextension=extension)
        if filename == '':
            return
        sp.WriteToFile(filename)

    def onSimulate(self):
        self.Drawing.stateMachine.Nothing()
        self.simulator.OpenSimulator()

def main():
    app=TheApp()

if __name__ == '__main__':
    main()