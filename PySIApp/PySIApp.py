from Tkinter import *

from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
from tkFileDialog import askdirectory
import tkMessageBox
import copy
import os

#from idlelib.ToolTip import *

from PartPin import *
from PartPicture import *
from PartProperty import *
from Device import *
from DeviceProperties import *
from DevicePicker import *
from Schematic import *
from PlotWindow import *
from CalculationProperties import *
from Simulator import *
from NetList import *
from SParameterViewerWindow import *
from Files import *
from History import *

class MenuElement(object):
    def __init__(self,menu,**kw):
        menu.add_command(kw)
        self.label=kw['label']
        self.menu=menu
        self.active=None
        if 'state' in kw:
            active=kw['state'] == 'normal'
        else:
            active=True
        self.Activate(active)
    def Activate(self,active):
        if active == self.active:
            return
        self.active=active
        self.menu.entryconfigure(self.label,state='normal' if self.active else 'disabled')

class ToolBarElement(object):
    def __init__(self,frame,**kw):
        if 'iconfile' in kw:
            self.icon = PhotoImage(file=kw['iconfile'])
            del kw['iconfile']
            kw['image']=self.icon
        self.button=Button(frame,kw)
        self.active=None
        if 'state' in kw:
            active=kw['state'] == 'normal'
        else:
            active=True
        self.Activate(active)
    def Activate(self,active):
        if active == self.active:
            return
        self.active=active
        self.button.config(state='normal' if self.active else 'disabled')
    def Pack(self,**kw):
        self.button.pack(kw)
        return self

class KeyBindElement(object):
    def __init__(self,bindTo,key,func):
        self.bindTo=bindTo
        self.key=key
        self.func=func
        self.active=False
    def Activate(self,active):
        if active == self.active:
            return
        self.active=active
        if self.active:
            self.bindTo.bind(self.key,self.func)
        else:
            self.bindTo.unbind(self.key)

class Doer(object):
    def __init__(self,command,active=True):
        self.active=active
        self.command=command
        self.menuElement=None
        self.toolBarElement=None
        self.keyBindElement=None
    def AddMenuElement(self,menu,**kw):
        kw['command']=self.Execute
        self.menuElement=MenuElement(menu,**kw)
        self.menuElement.Activate(self.active)
        return self.menuElement
    def AddToolBarElement(self,frame,**kw):
        kw['command']=self.Execute
        self.toolBarElement=ToolBarElement(frame,**kw)
        self.toolBarElement.Activate(self.active)
        return self.toolBarElement
    def AddKeyBindElement(self,bindTo,key):
        self.keyBindElement = KeyBindElement(bindTo,key,self.Execute)
        self.keyBindElement.Activate(self.active)
        return self
    def Execute(self,*args):
        if self.active:
            return self.command()
    def Activate(self,active):
        if self.active==active:
            return
        self.active=active
        if self.menuElement is not None:
            self.menuElement.Activate(active)
        if self.toolBarElement is not None:
            self.toolBarElement.Activate(active)
        if self.keyBindElement is not None:
            self.keyBindElement.Activate(active)

class TheMenu(Menu):
    def __init__(self,parent):
        self.parent=parent
        Menu.__init__(self,self.parent.root)
        self.parent.root.config(menu=self)
        FileMenu=Menu(self)
        self.add_cascade(label='File',menu=FileMenu,underline=0)
        self.parent.OpenProjectDoer.AddMenuElement(FileMenu,label="Open Project",accelerator='Ctrl+O',underline=0)
        self.parent.SaveProjectDoer.AddMenuElement(FileMenu,label="Save Project",accelerator='Ctrl+S',underline=0)
        FileMenu.add_separator()
        self.parent.ClearProjectDoer.AddMenuElement(FileMenu,label="Clear Schematic",underline=0)
        FileMenu.add_separator()
        self.parent.ExportNetListDoer.AddMenuElement(FileMenu,label="Export NetList",underline=7)
        self.parent.ExportTpXDoer.AddMenuElement(FileMenu,label="Export LaTeX (TikZ)",underline=7)

        EditMenu=Menu(self)
        self.add_cascade(label='Edit',menu=EditMenu,underline=0)
        self.parent.UndoDoer.AddMenuElement(EditMenu,label="Undo",accelerator='Ctrl+Z', underline=0)
        self.parent.RedoDoer.AddMenuElement(EditMenu,label="Redo",accelerator='Ctrl+Shift+Z',underline=0)
        EditMenu.add_separator()

        PartsMenu=Menu(self)
        self.add_cascade(label='Parts',menu=PartsMenu,underline=0)
        self.parent.AddPartDoer.AddMenuElement(PartsMenu,label='Add Part',underline=0)
        self.parent.AddPortDoer.AddMenuElement(PartsMenu,label='Add Port',underline=5)
        PartsMenu.add_separator()
        self.parent.DeletePartDoer.AddMenuElement(PartsMenu,label='Delete Part',underline=0)
        PartsMenu.add_separator()
        self.parent.EditPropertiesDoer.AddMenuElement(PartsMenu,label='Edit Properties',underline=0)
        self.parent.DuplicatePartDoer.AddMenuElement(PartsMenu,label='Duplicate Part',accelerator='Ctrl+C',underline=0)
        self.parent.RotatePartDoer.AddMenuElement(PartsMenu,label='Rotate Part',underline=0)
        self.parent.FlipPartHorizontallyDoer.AddMenuElement(PartsMenu,label='Flip Horizontally',underline=5)
        self.parent.FlipPartVerticallyDoer.AddMenuElement(PartsMenu,label='Flip Vertically',underline=5)

        WireMenu=Menu(self)
        self.add_cascade(label='Wires',menu=WireMenu,underline=0)
        self.parent.AddWireDoer.AddMenuElement(WireMenu,label='Add Wire',underline=0)
        WireMenu.add_separator()
        self.parent.DeleteVertexDoer.AddMenuElement(WireMenu,label='Delete Vertex',underline=7)
        self.parent.DuplicateVertexDoer.AddMenuElement(WireMenu,label='Duplicate Vertex',underline=1)
        self.parent.DeleteWireDoer.AddMenuElement(WireMenu,label='Delete Wire',underline=0)

        ViewMenu=Menu(self)
        self.add_cascade(label='View',menu=ViewMenu,underline=0)
        self.parent.ZoomInDoer.AddMenuElement(ViewMenu,label='Zoom In',underline=5)
        self.parent.ZoomOutDoer.AddMenuElement(ViewMenu,label='Zoom Out',underline=5)
        self.parent.PanDoer.AddMenuElement(ViewMenu,label='Pan',underline=0)

        CalcMenu=Menu(self)
        self.add_cascade(label='Calculate',menu=CalcMenu,underline=0)
        self.parent.CalculationPropertiesDoer.AddMenuElement(CalcMenu,label='Calculation Properties',underline=12)
        self.parent.SParameterViewerDoer.AddMenuElement(CalcMenu,label='S-parameter Viewer',underline=12)
        CalcMenu.add_separator()
        self.parent.CalculateSParametersDoer.AddMenuElement(CalcMenu,label='Calculate S-parameters',underline=0)
        self.parent.SimulateDoer.AddMenuElement(CalcMenu,label='Simulate',underline=0)

class ToolBar(Frame):
    def __init__(self,parent):
        self.parent=parent
        Frame.__init__(self,self.parent)
        self.pack(side=TOP,fill=X,expand=NO)
        self.parent.ClearProjectDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/document-new-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.OpenProjectDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/document-open-2.gif',).Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.SaveProjectDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/document-save-2.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        separator=Frame(self,bd=2,relief=SUNKEN)
        separator.pack(side=LEFT,fill=X,padx=5,pady=5)
        self.parent.AddPartDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/edit-add-2.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.DeleteSelectedDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/edit-delete-6.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.AddWireDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/draw-line-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.DuplicateSelectedDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/edit-copy-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.RotatePartDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/object-rotate-left-4.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.FlipPartHorizontallyDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/object-flip-horizontal-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.FlipPartVerticallyDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/object-flip-vertical-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        separator=Frame(self,height=2,bd=2,relief=RAISED).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.parent.ZoomInDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/zoom-in-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.ZoomOutDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/zoom-out-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.PanDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/edit-move.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        separator=Frame(self,height=2,bd=2,relief=RAISED).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.parent.CalculationPropertiesDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/tooloptions.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.parent.CalculateDoer.AddToolBarElement(self,iconfile='./icons/png/16x16/actions/system-run-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)

        undoFrame=Frame(self)
        undoFrame.pack(side=RIGHT,fill=NONE,expand=NO,anchor=E)
        self.parent.UndoDoer.AddToolBarElement(undoFrame,iconfile='./icons/png/16x16/actions/edit-undo-3.gif').Pack(side=LEFT,fill=NONE,expand=NO,anchor=E)
        self.parent.RedoDoer.AddToolBarElement(undoFrame,iconfile='./icons/png/16x16/actions/edit-redo-3.gif').Pack(side=LEFT,fill=NONE,expand=NO,anchor=E)

class StatusBar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)
    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()
    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

class TheApp(Frame):
    def __init__(self):
        self.root = Tk()
        Frame.__init__(self, self.root)
        self.pack(fill=BOTH, expand=YES)

        self.root.title("PySI")

        img = PhotoImage(file='./icons/png/AppIcon2.gif')
        self.root.tk.call('wm', 'iconphoto', self.root._w, '-default', img)

        sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/..')
        foundSignalIntegrity=False
        while not foundSignalIntegrity:
            foundSignalIntegrity = True
            try:
                import SignalIntegrity as si
            except ImportError:
                foundSignalIntegrity = False
                if tkMessageBox.askokcancel('SignalIntegrity Package',
                    'In order to run this application, I need to know where the '+\
                    'SignalIntegrity package is.  Please browse to the directory where '+\
                    'it\'s installed.\n'+'You should only need to do this once'):
                        dirname = askdirectory(parent=self.root,initialdir=os.path.dirname(os.path.abspath(__file__)),
                            title='Please select a directory')
                        sys.path.append(dirname)
                else:
                    exit()

        self.statusbar=StatusBar(self)

        self.UndoDoer = Doer(self.onUndo).AddKeyBindElement(self.root,'<Control-z>')
        self.RedoDoer = Doer(self.onRedo).AddKeyBindElement(self.root,'<Control-Z>')
        self.OpenProjectDoer = Doer(self.onReadProjectFromFile).AddKeyBindElement(self.root,'<Control-o>')
        self.SaveProjectDoer = Doer(self.onWriteProjectToFile).AddKeyBindElement(self.root,'<Control-s>')
        self.ClearProjectDoer = Doer(self.onClearSchematic)
        self.ExportNetListDoer = Doer(self.onExportNetlist)
        self.ExportTpXDoer = Doer(self.onExportTpX)

        self.AddPartDoer = Doer(self.onAddPart)
        self.AddPortDoer = Doer(self.onAddPort)
        self.DeletePartDoer = Doer(self.onDeletePart)
        self.DeleteSelectedDoer = Doer(self.onDeleteSelected).AddKeyBindElement(self.root,'<Delete>')
        self.EditPropertiesDoer = Doer(self.onEditProperties)
        self.DuplicatePartDoer = Doer(self.onDuplicate)
        self.DuplicateSelectedDoer = Doer(self.onDuplicateSelected).AddKeyBindElement(self.root,'<Control-c>')
        self.RotatePartDoer = Doer(self.onRotatePart)
        self.FlipPartHorizontallyDoer = Doer(self.onFlipPartHorizontally)
        self.FlipPartVerticallyDoer = Doer(self.onFlipPartVertically)

        self.AddWireDoer = Doer(self.onAddWire)
        self.DeleteVertexDoer = Doer(self.onDeleteSelectedVertex)
        self.DuplicateVertexDoer = Doer(self.onDuplicateSelectedVertex)
        self.DeleteWireDoer = Doer(self.onDeleteSelectedWire)

        self.ZoomInDoer = Doer(self.onZoomIn)
        self.ZoomOutDoer = Doer(self.onZoomOut)
        self.PanDoer = Doer(self.onPan)

        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties)
        self.SParameterViewerDoer = Doer(self.onSParameterViewer)
        self.CalculateDoer = Doer(self.onCalculate)
        self.CalculateSParametersDoer = Doer(self.onCalculateSParameters)
        self.SimulateDoer = Doer(self.onSimulate)

        self.menu=TheMenu(self)
        self.toolbar=ToolBar(self)

        self.Drawing=Drawing(self)
        self.Drawing.pack(side=TOP,fill=BOTH,expand=YES)

        self.statusbar.pack(side=BOTTOM,fill=X,expand=NO)
        self.root.bind('<Key>',self.onKey)

        self.simulator = Simulator(self)
        self.calculationProperties=CalculationProperties(self)
        self.filename=None

        self.history=History(self)

        self.root.mainloop()

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
            elif child.tag == 'calculation_properties':
                self.calculationProperties.InitFromXml(child, self)
        self.filename=filename
        self.Drawing.DrawSchematic()
        self.history.Event('read project')

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
        calculationPropertiesElement=self.calculationProperties.xml()
        projectElement.extend([drawingElement,calculationPropertiesElement])
        et.ElementTree(projectElement).write(filename)

    def onClearSchematic(self):
        self.Drawing.stateMachine.Nothing()
        self.Drawing.schematic.Clear()
        self.history.Event('new project')
        self.Drawing.DrawSchematic()
        self.filename=None

    def onExportNetlist(self):
        self.Drawing.stateMachine.Nothing()
        nld = NetListDialog(self,self.Drawing.schematic.NetList().Text())

    def onExportTpX(self):
        from TpX import TpX
        from TikZ import TikZ
        self.Drawing.stateMachine.Nothing()
        extension='.TpX'
        if self.filename == None:
            filename=asksaveasfilename(filetypes=[('tpx', extension)],defaultextension='.TpX',initialdir=os.getcwd())
        else:
            filename=asksaveasfilename(filetypes=[('tpx', extension)],defaultextension='.TpX',initialfile=self.filename.replace('.xml','.TpX'))
        if filename=='':
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
    def onFlipPartHorizontally(self):
        if self.Drawing.stateMachine.state == 'DeviceSelected':
            orientation = self.Drawing.deviceSelected.partPicture.current.orientation
            mirroredHorizontally = self.Drawing.deviceSelected.partPicture.current.mirroredHorizontally
            mirroredVertically = self.Drawing.deviceSelected.partPicture.current.mirroredVertically
            self.Drawing.deviceSelected.partPicture.current.ApplyOrientation(orientation,not mirroredHorizontally,mirroredVertically)
            self.Drawing.DrawSchematic()
    def onFlipPartVertically(self):
        if self.Drawing.stateMachine.state == 'DeviceSelected':
            orientation = self.Drawing.deviceSelected.partPicture.current.orientation
            mirroredHorizontally = self.Drawing.deviceSelected.partPicture.current.mirroredHorizontally
            mirroredVertically = self.Drawing.deviceSelected.partPicture.current.mirroredVertically
            self.Drawing.deviceSelected.partPicture.current.ApplyOrientation(orientation,mirroredHorizontally,not mirroredVertically)
            self.Drawing.DrawSchematic()
    def onDuplicateSelected(self):
        self.Drawing.DuplicateSelected()
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
        #self.onCalculationProperties()
        self.Drawing.stateMachine.Nothing()
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity as si
        spnp=si.p.SystemSParametersNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.calculationProperties.endFrequency,
                self.calculationProperties.frequencyPoints))
        spnp.AddLines(netList)
        try:
            sp=spnp.SParameters()
        except si.PySIException as e:
            if e == si.PySIExceptionCheckConnections:
                tkMessageBox.showerror('S-parameter Calculator','Unconnected devices error: '+e.message)
            elif e == si.PySIExceptionSParameterFile:
                tkMessageBox.showerror('S-parameter Calculator','s-parameter file error: '+e.message)
            elif e == si.PySIExceptionNumeric:
                tkMessageBox.showerror('S-parameter Calculator','S-parameter Calculator Numerical Error: '+e.message)
            elif e == si.PySIExceptionSystemDescriptionBuildError:
                tkMessageBox.showerror('S-parameter Calculator','Schematic Error: '+e.message)
            else:
                tkMessageBox.showerror('S-parameter Calculator','Unhandled PySI Exception: '+str(e)+' '+e.message)
            return
        SParametersDialog(self,sp)

    def onCalculationProperties(self):
        self.Drawing.stateMachine.Nothing()
        self.calculationProperties.ShowCalculationPropertiesDialog()

    def onSimulate(self):
        self.Drawing.stateMachine.Nothing()
        self.simulator.Simulate()

    def onCalculate(self):
        self.Drawing.stateMachine.Nothing()
        foundAPort=False
        foundASource=False
        foundAnOutput=False
        for deviceIndex in range(len(self.Drawing.schematic.deviceList)):
            device = self.Drawing.schematic.deviceList[deviceIndex]
            deviceType = device['type'].GetValue()
            if  deviceType == 'Port':
                foundAPort = True
            elif deviceType == 'Output':
                foundAnOutput = True
            else:
                netListLine = device.NetListLine()
                if not netListLine is None:
                    firstToken=netListLine.strip().split(' ')[0]
                    if firstToken == 'voltagesource':
                        foundASource = True
                    elif firstToken == 'currentsource':
                        foundASource = True
        canSimulate = foundASource and foundAnOutput and not foundAPort
        canCalculateSParameters = foundAPort and not foundAnOutput
        canCalculate = canSimulate or canCalculateSParameters
        if canCalculate:
            if canSimulate:
                self.onSimulate()
            elif canCalculateSParameters:
                self.onCalculateSParameters()

    def onSParameterViewer(self):
        import SignalIntegrity as si
        filetypes = [('s-parameter files', ('*.s*p'))]
        filename=askopenfilename(filetypes=filetypes,parent=self)
        if filename == '':
            return
        filenametokens=filename.split('.')
        if len(filenametokens)==0:
            return

        filename=ConvertFileNameToRelativePath(filename)
        sp=si.sp.File(filename)
        SParametersDialog(self,sp)

def main():
    app=TheApp()

if __name__ == '__main__':
    main()