from Tkinter import *
import ttk
from tkFileDialog import askopenfilename
from tkFileDialog import asksaveasfilename

DeviceList = [['File','One\ Port\ File',1,'Files',[['','file name','']]],
              ['File','Two\ Port\ File',2,'Files',[['','file name','']]],
              ['File','Three\ Port\ File',3,'Files',[['','file name','']]],
              ['File','Four\ Port\ File',1,'Files',[['','file name','']]],
              ['Resistor','One\ Port\ Resistor\ to\ Ground',1,'Resistors',[['r','resistance (Ohms)',50]]],
              ['Resistor','Two\ Port\ Resistor',2,'Resistors',[['r','resistance (Ohms)',50]]],
              ['Capacitor','One\ Port\ Capacitor\ to\ Ground',1,'Capacitors',[['r','resistance (Ohms)',50]]],
              ['Capacitor','Two\ Port\ Capacitor',2,'Capacitors',[['r','resistance (Ohms)',50]]]]             

class DeviceLauncher(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        
class DevicePicker(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.tree = ttk.Treeview(self)
        self.tree.pack()
        self.tree["columns"]=("description")
        self.tree.column("description")
        self.tree.heading("description", text="description")
        categories=[]
        indexIntoDeviceList=0
        for device in DeviceList:
            name=device[0]
            description=device[1]
            ports=device[2]
            category=device[3]
            properties=device[4]
            if category not in categories:
                self.tree.insert('','end',category,text=category,values=(category),tags='category')
                categories.append(category)
            self.tree.insert(category,'end',text=name,values=(description),tags=str(indexIntoDeviceList))
            indexIntoDeviceList=indexIntoDeviceList+1

class DeviceFrame(Frame):
    def __init__(self,parent):
        Frame.__init__(self,parent)
        self.Picker = DevicePicker(self)
        self.Picker.pack()

class TheApp(Frame):
    def __init__(self): 
        root = Tk()
        Frame.__init__(self, root)
        self.pack(fill=BOTH, expand=YES)

        root.title("PySI App")

        menu=Menu(root)
        root.config(menu=menu)
        subMenu=Menu(menu)
        menu.add_cascade(label='File',menu=subMenu)
        subMenu.add_command(label="Read Schematic",command=self.onReadSchematic)
        subMenu.add_command(label="Write Schematic",command=self.onWriteSchematic)
        subMenu.add_separator()
        subMenu.add_command(label="Export NetList",command=self.onExportNetlist)

        self.DeviceFrame = DeviceFrame(self)
        self.DeviceFrame.pack(side=LEFT, fill=Y, expand=NO)

        self.canvas = Canvas(self)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.canvas.create_rectangle(1,1,self.canvas.winfo_reqheight(),self.canvas.winfo_reqwidth())
        self.canvas.bind("<Configure>", self.on_resize)
        
        self.DeviceFrame.Picker.tree.bind('<<TreeviewSelect>>',self.onPartSelection)
        root.mainloop()

    def on_resize(self,event):
        self.canvas.delete(ALL)
        self.canvas.create_rectangle(1,1,event.width-5,event.height-5)
        
    def onPartSelection(self,event):
        print 'selected'
        selection = self.DeviceFrame.Picker.tree.selection()
        item = self.DeviceFrame.Picker.tree.selection()[0]
        print self.DeviceFrame.Picker.tree.item(item,'tags')[0]
        print "you clicked on " + self.DeviceFrame.Picker.tree.item(item,"text")+' '+self.DeviceFrame.Picker.tree.item(item,"values")[0]
        
    def onReadSchematic(self):
        pass

    def onWriteSchematic(self):
        pass

    def onExportNetlist(self):
        pass

def main():
    app=TheApp()

if __name__ == '__main__':
    main()