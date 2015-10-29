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

class TheApp(Frame):
    def __init__(self):
        self.root = Tk()
        Frame.__init__(self, self.root)
        self.pack(fill=BOTH, expand=YES)

        self.root.title("PySI App")

        menu=Menu(self.root)
        self.root.config(menu=menu)
        FileMenu=Menu(menu)
        menu.add_cascade(label='File',menu=FileMenu)
        FileMenu.add_command(label="Open Project",command=self.onReadProjectFromFile)
        FileMenu.add_command(label="Save Project",command=self.onWriteProjectToFile)
        FileMenu.add_separator()
        FileMenu.add_command(label="Clear Schematic",command=self.onClearSchematic)
        FileMenu.add_separator()
        FileMenu.add_command(label="Export NetList",command=self.onExportNetlist)

        PartsMenu=Menu(menu)
        menu.add_cascade(label='Add',menu=PartsMenu)
        PartsMenu.add_command(label='Add Part',command=self.onAddPart)
        PartsMenu.add_command(label='Add Wire',command=self.onAddWire)
        PartsMenu.add_command(label='Add Port',command=self.onAddPort)
        PartsMenu.add_command(label='Duplicate',command=self.onDuplicate)

        ZoomMenu=Menu(menu)
        menu.add_cascade(label='Zoom',menu=ZoomMenu)
        ZoomMenu.add_command(label='Zoom In',command=self.onZoomIn)
        ZoomMenu.add_command(label='Zoom Out',command=self.onZoomOut)

        CalcMenu=Menu(menu)
        menu.add_cascade(label='Calculate',menu=CalcMenu)
        CalcMenu.add_command(label='Calculate S-parameters',command=self.onCalculateSParameters)
        CalcMenu.add_command(label='Simulate',command=self.onSimulate)

        self.Drawing=Drawing(self)
        self.Drawing.pack(side=LEFT,fill=BOTH,expand=YES)

        self.root.bind('<Key>',self.onKey)

        self.plotDialog=None

        self.simulator = Simulator(self)
        self.root.mainloop()

    def onKey(self,event):
        print "pressed", repr(event.keycode), repr(event.keysym)
        if event.keysym == 'Delete': # delete
            if self.Drawing.wireSelected:
                self.Drawing.schematic.wireList[self.Drawing.w].selected=False
                self.Drawing.wireSelected=False
                del self.Drawing.schematic.wireList[self.Drawing.w]
                self.Drawing.DrawSchematic()
            elif self.Drawing.deviceSelected != None:
                self.Drawing.deviceSelected.selected=False
                self.Drawing.deviceSelected = None
                del self.Drawing.schematic.deviceList[self.Drawing.deviceSelectedIndex]
                self.Drawing.DrawSchematic()

    def onReadProjectFromFile(self):
        if not self.Drawing.deviceSelected == None:
            self.Drawing.deviceSelected.selected=False
            self.Drawing.deviceSelected=None
        if self.Drawing.wireSelected:
            self.schematic.wireList[self.Drawing.w].selected=False
            self.Drawing.wireSelected = False
        extension='.xml'
        filename=askopenfilename(filetypes=[('xml', extension)])
        if filename == '':
            return
        filenametokens=filename.split('.')
        if len(filenametokens)==0:
            return
        if len(filenametokens)==1:
            filename=filename+extension
        tree=et.parse(filename)
        root=tree.getroot()
        for child in root:
            if child.tag == 'drawing':
                self.Drawing.InitFromXml(child)
            elif child.tag == 'simulator':
                self.simulator.InitFromXml(child, self)
        self.Drawing.DrawSchematic()

    def onWriteProjectToFile(self):
        if not self.Drawing.deviceSelected == None:
            self.Drawing.deviceSelected.selected=False
            self.Drawing.deviceSelected=None
        if self.Drawing.wireSelected:
            self.schematic.wireList[self.Drawing.w].selected=False
            self.Drawing.wireSelected = False
        extension='.xml'
        filename=asksaveasfilename(filetypes=[('xml', extension)],defaultextension='.xml')
        if filename=='':
            return
        projectElement=et.Element('Project')
        drawingElement=self.Drawing.xml()
        simulatorElement=self.simulator.xml()
        projectElement.extend([drawingElement,simulatorElement])
        et.ElementTree(projectElement).write(filename)

    def onClearSchematic(self):
        if not self.Drawing.deviceSelected == None:
            self.Drawing.deviceSelected.selected=False
            self.Drawing.deviceSelected=None
        if self.Drawing.wireSelected:
            self.schematic.wireList[self.Drawing.w].selected=False
            self.Drawing.wireSelected = False
        self.Drawing.schematic.Clear()
        self.Drawing.DrawSchematic()

    def onExportNetlist(self):
        if not self.Drawing.deviceSelected == None:
            self.Drawing.deviceSelected.selected=False
            self.Drawing.deviceSelected=None
        if self.Drawing.wireSelected:
            self.schematic.wireList[self.Drawing.w].selected=False
            self.Drawing.wireSelected = False
        nld = NetListDialog(self,self.Drawing.schematic.NetList().Text())

    def onAddPart(self):
        if not self.Drawing.deviceSelected == None:
            self.Drawing.deviceSelected.selected=False
            self.Drawing.deviceSelected=None
        if self.Drawing.wireSelected:
            self.schematic.wireList[self.Drawing.w].selected=False
            self.Drawing.wireSelected = False
        dpd=DevicePickerDialog(self)
        if dpd.result != None:
            devicePicked=copy.deepcopy(DeviceList[dpd.result])
            devicePicked.AddPartProperty(PartPropertyReferenceDesignator(''))
            dpe=DevicePropertiesDialog(self,devicePicked)
            self.Drawing.partLoaded = dpe.result

    def onDuplicate(self):
        if not self.Drawing.deviceSelected == None:
            self.Drawing.partLoaded=copy.deepcopy(self.Drawing.deviceSelected)
        if not self.Drawing.deviceSelected == None:
            self.Drawing.deviceSelected.selected=False
            self.Drawing.deviceSelected=None
        if self.Drawing.wireSelected:
            self.schematic.wireList[self.Drawing.w].selected=False
            self.Drawing.wireSelected = False

    def onAddWire(self):
        if not self.Drawing.deviceSelected == None:
            self.Drawing.deviceSelected.selected=False
            self.Drawing.deviceSelected=None
        if self.Drawing.wireSelected:
            self.schematic.wireList[self.Drawing.w].selected=False
            self.Drawing.wireSelected = False
        self.Drawing.wireLoaded=Wire([(0,0)])
        self.Drawing.schematic.wireList.append(self.Drawing.wireLoaded)

    def onAddPort(self):
        if not self.Drawing.deviceSelected == None:
            self.Drawing.deviceSelected.selected=False
            self.Drawing.deviceSelected=None
        if self.Drawing.wireSelected:
            self.schematic.wireList[self.Drawing.w].selected=False
            self.Drawing.wireSelected = False
        portNumber=1
        for device in self.Drawing.schematic.deviceList:
            if device['type'].value == 'Port':
                if portNumber <= int(device['portnumber'].value):
                    portNumber = int(device['portnumber'].value)+1
        dpe=DevicePropertiesDialog(self,Port(portNumber))
        self.Drawing.partLoaded = dpe.result

    def onZoomIn(self):
        self.Drawing.grid = self.Drawing.grid*2
        self.Drawing.DrawSchematic()

    def onZoomOut(self):
        self.Drawing.grid = max(1,self.Drawing.grid/2)
        self.Drawing.DrawSchematic()

    def onCalculateSParameters(self):
        if not self.Drawing.deviceSelected == None:
            self.Drawing.deviceSelected.selected=False
            self.Drawing.deviceSelected=None
        if self.Drawing.wireSelected:
            self.schematic.wireList[self.Drawing.w].selected=False
            self.Drawing.wireSelected = False
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
        if not self.Drawing.deviceSelected == None:
            self.Drawing.deviceSelected.selected=False
            self.Drawing.deviceSelected=None
        if self.Drawing.wireSelected:
            self.Drawing.schematic.wireList[self.Drawing.w].selected=False
            self.Drawing.wireSelected = False
        
        self.simulator.OpenSimulator()

def main():
    app=TheApp()

if __name__ == '__main__':
    main()