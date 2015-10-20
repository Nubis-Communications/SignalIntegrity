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
        root = Tk()
        Frame.__init__(self, root)
        self.pack(fill=BOTH, expand=YES)

        root.title("PySI App")

        menu=Menu(root)
        root.config(menu=menu)
        FileMenu=Menu(menu)
        menu.add_cascade(label='File',menu=FileMenu)
        FileMenu.add_command(label="Read Schematic",command=self.onReadSchematic)
        FileMenu.add_command(label="Write Schematic",command=self.onWriteSchematic)
        FileMenu.add_separator()
        FileMenu.add_command(label="Clear Schematic",command=self.onClearSchematic)
        FileMenu.add_separator()
        FileMenu.add_command(label="Export NetList",command=self.onExportNetlist)

        PartsMenu=Menu(menu)
        menu.add_cascade(label='Add',menu=PartsMenu)
        PartsMenu.add_command(label='Add Part',command=self.onAddPart)
        PartsMenu.add_command(label='Add Wire',command=self.onAddWire)
        PartsMenu.add_command(label='Add Port',command=self.onAddPort)

        ZoomMenu=Menu(menu)
        menu.add_cascade(label='Zoom',menu=ZoomMenu)
        ZoomMenu.add_command(label='Zoom In',command=self.onZoomIn)
        ZoomMenu.add_command(label='Zoom Out',command=self.onZoomOut)

        CalcMenu=Menu(menu)
        menu.add_cascade(label='Calculate',menu=CalcMenu)
        CalcMenu.add_command(label='Calculate S-parameters',command=self.onCalculateSParameters)

#         self.DeviceFrame = DeviceFrame(self)
#         self.DeviceFrame.pack(side=LEFT, fill=Y, expand=NO)
        self.SchematicFrame=SchematicFrame(self)
        self.SchematicFrame.pack(side=LEFT,fill=BOTH,expand=YES)

#         self.DeviceFrame.Picker.tree.bind('<<TreeviewSelect>>',self.onPartSelection)
        root.bind('<Key>',self.onKey)

        root.mainloop()

    def onKey(self,event):
        print "pressed", repr(event.keycode), repr(event.keysym)
        if event.keysym == 'Delete': # delete
            if self.SchematicFrame.wireSelected:
                self.SchematicFrame.wireSelected=False
                del self.SchematicFrame.schematic.wireList[self.SchematicFrame.w]
                self.SchematicFrame.DrawSchematic()
            elif self.SchematicFrame.deviceSelected != None:
                self.SchematicFrame.deviceSelected = None
                del self.SchematicFrame.schematic.deviceList[self.SchematicFrame.deviceSelectedIndex]
                self.SchematicFrame.DrawSchematic()

    def onReadSchematic(self):
        extension='.xml'
        filename=askopenfilename(filetypes=[('xml', extension)])
        if filename == '':
            return
        filenametokens=filename.split('.')
        if len(filenametokens)==0:
            return
        if len(filenametokens)==1:
            filename=filename+extension
        self.SchematicFrame.schematic.ReadFromFile(filename)
        self.SchematicFrame.DrawSchematic()

    def onWriteSchematic(self):
        extension='.xml'
        filename=asksaveasfilename(filetypes=[('xml', extension)],defaultextension='.xml')
        if filename=='':
            return
        self.SchematicFrame.schematic.WriteToFile(filename)
        
    def onClearSchematic(self):
        self.SchematicFrame.schematic.Clear()
        self.SchematicFrame.DrawSchematic()

    def onExportNetlist(self):
        nld = NetListDialog(self,self.SchematicFrame.schematic.NetList())

    def onAddPart(self):
        self.SchematicFrame.deviceSelected = None
        self.SchematicFrame.wireSelected = False
        dpd=DevicePickerDialog(self)
        if dpd.result != None:
            devicePicked=copy.deepcopy(DeviceList[dpd.result])
            devicePicked.AddPartProperty(PartPropertyReferenceDesignator(''))
            dpe=DevicePropertiesDialog(self,devicePicked)
            self.SchematicFrame.partLoaded = dpe.result

    def onAddWire(self):
        self.SchematicFrame.deviceSelected = None
        self.SchematicFrame.wireSelected = False
        self.SchematicFrame.wireLoaded=[(0,0)]
        self.SchematicFrame.schematic.wireList.append(self.SchematicFrame.wireLoaded)

    def onAddPort(self):
        self.SchematicFrame.deviceSelected = None
        self.SchematicFrame.wireSelected = False
        portNumber=1
        for device in self.SchematicFrame.schematic.deviceList:
            if device['type'].value == 'Port':
                if portNumber <= int(device['portnumber'].value):
                    portNumber = int(device['portnumber'].value)+1
        dpe=DevicePropertiesDialog(self,Port(portNumber))
        self.SchematicFrame.partLoaded = dpe.result

    def onZoomIn(self):
        self.SchematicFrame.grid = self.SchematicFrame.grid*2
        self.SchematicFrame.DrawSchematic()

    def onZoomOut(self):
        self.SchematicFrame.grid = max(1,self.SchematicFrame.grid/2)
        self.SchematicFrame.DrawSchematic()

    def onCalculateSParameters(self):
        netList=self.SchematicFrame.schematic.NetList()
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
        pass
def main():
    app=TheApp()

if __name__ == '__main__':
    main()