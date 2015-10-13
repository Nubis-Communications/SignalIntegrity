from Tkinter import *
import ttk
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename
from libxml2mod import properties
import keyword

class Property(object):
    def __init__(self,keyword=None,description=None,value=None):
        self.keyword=keyword
        self.description=description
        self.value=value
        
class Device(object):
    def __init__(self,name='',description='',ports=None,category=None,propertiesList=None):
        self.name=name
        self.description=description
        self.ports=ports
        self.category=category
        self.propertiesList=propertiesList

DeviceList = [
              Device(name='File',description='One\ Port\ File',ports=1,category='Files',propertiesList=[Property(keyword='',description='file name',value='')]),
              Device(name='File',description='Two\ Port\ File',ports=2,category='Files',propertiesList=[Property(keyword='',description='file name',value='')]),
              Device(name='File',description='Three\ Port\ File',ports=3,category='Files',propertiesList=[Property(keyword='',description='file name',value='')]),
              Device(name='File',description='Four\ Port\ File',ports=4,category='Files',propertiesList=[Property(keyword='',description='file name',value='')]),
              Device(name='Resistor',description='One\ Port\ Resistor\ to\ Ground',ports=1,category='Resistors',propertiesList=[Property(keyword='r',description='resistance (Ohms)',value=50)]),
              Device(name='Resistor',description='Two\ Port\ Resistor',ports=2,category='Resistors',propertiesList=[Property(keyword='r',description='resistance (Ohms)',value=50)]),
              Device(name='Capacitor',description='One\ Port\ Capacitor\ to\ Ground',ports=1,category='Capacitors',propertiesList=[Property(keyword='c',description='capacitance (F)',value=1e-12)]),
              Device(name='Capacitor',description='Two\ Port\ Capacitor',ports=2,category='Capacitors',propertiesList=[Property(keyword='c',description='capacitance (F)',value=1e-12)]),
              Device(name='Inductor',description='One\ Port\ Inductor\ to\ Ground',ports=1,category='Inductors',propertiesList=[Property(keyword='l',description='inductance (H)',value=1e-15)]),
              Device(name='Inductor',description='Two\ Port\ Inductor',ports=2,category='Inductors',propertiesList=[Property(keyword='l',description='inductance (H)',value=1e-15)]),
              Device(name='Mutual',description='Four\ Port\ Mutual\ Inductance',ports=4,category='Inductors',propertiesList=[Property(keyword='l',description='inductance (H)',value=1e-15)])
              ]            
# 
#         
# DeviceList = [
#               ['File','One\ Port\ File',1,'Files',[['','file name','']]],
#               ['File','Two\ Port\ File',2,'Files',[['','file name','']]],
#               ['File','Three\ Port\ File',3,'Files',[['','file name','']]],
#               ['File','Four\ Port\ File',4,'Files',[['','file name','']]],
#               ['Resistor','One\ Port\ Resistor\ to\ Ground',1,'Resistors',[['r','resistance (Ohms)',50]]],
#               ['Resistor','Two\ Port\ Resistor',2,'Resistors',[['r','resistance (Ohms)',50]]],
#               ['Capacitor','One\ Port\ Capacitor\ to\ Ground',1,'Capacitors',[['c','capacitance (F)',1e-12]]],
#               ['Capacitor','Two\ Port\ Capacitor',2,'Capacitors',[['c','capacitance (F)',1e-12]]],
#               ['Inductor','One\ Port\ Inductor\ to\ Ground',1,'Inductors',[['c','inductance (H)',1e-15]]],
#               ['Inductor','Two\ Port\ Inductor',2,'Inductors',[['c','inductance (H)',1e-15]]],
#               ['Mutual','Four\ Port\ Mutual\ Inductance',4,'Inductors',[['m','mutual inductance (H)',1e-15]]]
#               ]            

class DeviceProperties(Frame):
    def __init__(self,parent,device):
        Frame.__init__(self,parent)
        self.title = 'Add '+device.name
        self.properties=[Property(keyword='',description='ports',value=device.ports)]+device.propertiesList
        self.propertyStrings=[StringVar(value=str(prop.value)) for prop in self.properties]
        
        for p in range(len(self.properties)):
            prop=self.properties[p]
            propertyFrame = Frame(self)
            propertyFrame.pack(side=TOP,fill=BOTH,expand=YES)
            propertyLabel = Label(propertyFrame,width=20,text=prop.description+': ',anchor='e')
            propertyLabel.pack(side=LEFT, expand=NO, fill=X)
            propertyEntry = Entry(propertyFrame,textvariable=self.propertyStrings[p])
            propertyEntry.config(width=10)
            propertyEntry.pack(side=LEFT, expand=YES, fill=X)

class DevicePropertiesDialog(Toplevel):
    def __init__(self,parent,device):
        Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Add '+device.description)

        self.parent = parent

        self.result = None

        self.DeviceProperties = DeviceProperties(self,device)
        self.initial_focus = self.body(self.DeviceProperties)
        self.DeviceProperties.pack(side=TOP,fill=BOTH,expand=YES,padx=5, pady=5)

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
        if (self.DevicePicker.selected != None):
            if self.DevicePicker.selected != 'category':
                self.result = int(self.DevicePicker.selected)

class DevicePicker(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.tree = ttk.Treeview(self)
        self.tree.pack(fill=BOTH,expand=YES)
        self.tree["columns"]=("description")
        self.tree.column("description")
        self.tree.heading("description", text="description")
        categories=[]
        indexIntoDeviceList=0
        for device in DeviceList:
            name=device.name
            description=device.description
            ports=device.ports
            category=device.category
            properties=device.propertiesList
            if category not in categories:
                self.tree.insert('','end',category,text=category,values=(category),tags='category')
                categories.append(category)
            self.tree.insert(category,'end',text=name,values=(description),tags=str(indexIntoDeviceList))
            indexIntoDeviceList=indexIntoDeviceList+1
        self.selected=None
        self.tree.bind('<<TreeviewSelect>>',self.onPartSelection)

    def onPartSelection(self,event):
        item = self.tree.selection()[0]
        self.selected=self.tree.item(item,'tags')[0]
        print "selected: " + str(self.selected)

class DevicePickerDialog(Toplevel):
    def __init__(self,parent):
        Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('Add Part')

        self.parent = parent

        self.result = None

        self.DevicePicker = DevicePicker(self)
        self.initial_focus = self.body(self.DevicePicker)
        self.DevicePicker.pack(side=TOP,fill=BOTH,expand=YES,padx=5, pady=5)

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
        if (self.DevicePicker.selected != None):
            if self.DevicePicker.selected != 'category':
                self.result = int(self.DevicePicker.selected)

class DeviceFrame(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.Picker = DevicePicker(self)
        self.Picker.pack()

class SchematicFrame(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.canvas = Canvas(self)
        self.canvas.pack(side=TOP, fill=BOTH, expand=YES)
        self.canvas.create_rectangle(1,1,self.canvas.winfo_reqheight(),self.canvas.winfo_reqwidth())
        self.canvas.bind("<Configure>", self.on_resize)
    def on_resize(self,event):
        self.canvas.delete(ALL)
        self.canvas.create_rectangle(1,1,event.width-5,event.height-5)
        
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
        FileMenu.add_command(label="Export NetList",command=self.onExportNetlist)
        
        PartsMenu=Menu(menu)
        menu.add_cascade(label='Parts',menu=PartsMenu)
        PartsMenu.add_command(label='Add Part',command=self.onAddPart)

#         self.DeviceFrame = DeviceFrame(self)
#         self.DeviceFrame.pack(side=LEFT, fill=Y, expand=NO)
        self.SchematicFrame=SchematicFrame(self)
        self.SchematicFrame.pack(side=LEFT,fill=BOTH,expand=YES)

#         self.DeviceFrame.Picker.tree.bind('<<TreeviewSelect>>',self.onPartSelection)
        root.mainloop()

        
        
    def onReadSchematic(self):
        pass

    def onWriteSchematic(self):
        pass

    def onExportNetlist(self):
        pass
    
    def onAddPart(self):
        dpd=DevicePickerDialog(self)
        if dpd.result != None:
            dpe=DevicePropertiesDialog(self,DeviceList[dpd.result])
        pass
        
def main():
    app=TheApp()

if __name__ == '__main__':
    main()