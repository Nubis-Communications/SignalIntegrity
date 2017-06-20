'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2017 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from Tkinter import Toplevel,PhotoImage,Frame,Button,Label,StringVar,Entry,Radiobutton
from Tkinter import TOP,YES,LEFT,X,NO,NORMAL,RAISED,W
from tkColorChooser import askcolor
from tkFileDialog import askopenfilename, asksaveasfilename

from ToSI import FromSI,ToSI
from Files import FileParts,ConvertFileNameToRelativePath

class CalculationProperty(Frame):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project=None,projectPath=None):
        Frame.__init__(self,parentFrame)
        self.parentFrame=parentFrame
        self.enteredCallback=enteredCallback
        self.updateStringsCallback=updateStringsCallback
        self.project=project
        self.projectPath=projectPath
        self.pack(side=TOP,fill=X,expand=YES)
        self.string=StringVar()
        self.label = Label(self,width=30,text=textLabel+': ',anchor='e')
        self.label.pack(side=LEFT, expand=NO, fill=X)
        self.entry = Entry(self,textvariable=self.string)
        self.entry.config(width=30,readonlybackground='light gray')
        self.entry.bind('<Return>',self.onEntered)
        self.entry.bind('<Tab>',self.onEntered)
        self.entry.bind('<Button-1>',self.onTouched)
        self.entry.bind('<Button-1>',self.onTouched)
        self.entry.bind('<Double-Button-1>',self.onCleared)
        self.entry.bind('<Button-3>',self.onUntouchedLoseFocus)
        self.entry.bind('<Escape>',self.onUntouchedLoseFocus)
        self.entry.bind('<FocusOut>',self.onUntouched)
        self.entry.pack(side=LEFT, expand=YES, fill=X)
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString((self.project.GetValue(self.projectPath)))
        self.SetReadOnly(False)
    def SetReadOnly(self,readOnly=False):
        self.entry.config(state='readonly' if readOnly else NORMAL)
    def SetString(self,value):
        self.string.set(value)
    def GetString(self):
        return self.string.get()
    def onEntered(self,event):
        if not ((self.project is None) or (self.projectPath is None)):
            if not self.GetString() is None:
                self.project.SetValue(self.projectPath,self.GetString())
        if not self.enteredCallback is None:
            self.enteredCallback(event)
        self.onUntouchedLoseFocus(event)
    def onTouched(self,event):
        self.UpdateStrings()
    def onCleared(self,event):
        self.string.set('')
    def onUntouched(self,event):
        self.UpdateStrings()
    def onUntouchedLoseFocus(self,event):
        self.parentFrame.focus()
    def Show(self,whetherTo=True):
        if whetherTo:
            self.pack(side=TOP,fill=X,expand=YES)
        else:
            self.pack_forget()
    def UpdateStrings(self):
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString((self.project.GetValue(self.projectPath)))
        if not self.updateStringsCallback is None:
            self.updateStringsCallback()

class CalculationPropertyFileName(CalculationProperty):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,fileparts,project=None,projectPath=None):
        self.fileparts=fileparts
        CalculationProperty.__init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project,projectPath)
    def onTouched(self,event):
        fp=FileParts(self.fileparts.AbsoluteFilePath()+'/'+self.project.GetValue(self.projectPath))
        filename=askopenfilename(filetypes=[('txt', '.txt')],initialdir=fp.AbsoluteFilePath(),
                                initialfile=fp.FileNameWithExtension('txt'))
        if filename is None:
            filename=''
        if isinstance(filename,tuple):
            filename=''
        filename=str(filename)
        if filename == '':
            return
        filename=ConvertFileNameToRelativePath(filename)
        self.project.SetValue(self.projectPath,filename)
        self.UpdateStrings()

class CalculationPropertyFileNameSaveAs(CalculationProperty):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,fileparts,project=None,projectPath=None):
        self.fileparts=fileparts
        CalculationProperty.__init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project,projectPath)
    def onTouched(self,event):
        fp=FileParts(self.fileparts.AbsoluteFilePath()+'/'+self.project.GetValue(self.projectPath))
        filename=asksaveasfilename(filetypes=[('txt', '.txt')],initialdir=fp.AbsoluteFilePath(),
                                initialfile=fp.FileNameWithExtension('txt'))
        if filename is None:
            filename=''
        if isinstance(filename,tuple):
            filename=''
        filename=str(filename)
        if filename == '':
            return
        filename=ConvertFileNameToRelativePath(filename)
        self.project.SetValue(self.projectPath,filename)
        self.UpdateStrings()

class CalculationPropertySI(CalculationProperty):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project=None,projectPath=None,unit=None):
        self.unitString=unit
        CalculationProperty.__init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project,projectPath)
    def SetString(self,value):
        try:
            self.string.set(ToSI(value,self.unitString))
        except:
            pass
    def GetString(self):
        return FromSI(self.string.get(),self.unitString)

class CalculationPropertyTrueFalseButton(Frame):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project=None,projectPath=None):
        Frame.__init__(self,parentFrame)
        self.parentFrame=parentFrame
        self.enteredCallback=enteredCallback
        self.updateStringsCallback=updateStringsCallback
        self.project=project
        self.projectPath=projectPath
        self.pack(side=TOP,fill=X,expand=YES)
        self.string=StringVar()
        self.label = Label(self,width=30,text=textLabel+': ',anchor='e')
        self.label.pack(side=LEFT, expand=NO, fill=X)
        self.entry = Button(self,text='None',command=self.onPressed)
        self.entry.config(width=30)
        self.entry.bind('<Return>',self.onPressed)
        self.entry.pack(side=LEFT, expand=YES, fill=X)
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project.GetValue(self.projectPath)))
    def SetString(self,value):
        self.string.set(value)
        self.entry.config(text=value)
    def GetString(self):
        return self.string.get()
    def onPressed(self,event=None):
        self.SetString('False' if self.GetString()=='True' else 'True')
        if not ((self.project is None) or (self.projectPath is None)):
            self.project.SetValue(self.projectPath,self.GetString())
        if not self.enteredCallback is None:
            self.enteredCallback(event)
        self.UpdateStrings()
    def Show(self,whetherTo=True):
        if whetherTo:
            self.pack(side=TOP,fill=X,expand=YES)
        else:
            self.pack_forget()
    def UpdateStrings(self):
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project.GetValue(self.projectPath)))
        if not self.updateStringsCallback is None:
            self.updateStringsCallback()

class CalculationPropertyChoices(Frame):
    couplingChoices = [('50 Ohm', 'DC50'),('1 MOhm', 'DC1M')]
    bandwidthChoices = [('20 MHz', '20MHz'),('200 MHz','200MHz')]
    
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,choiceStrings,project=None,projectPath=None):
        Frame.__init__(self,parentFrame)
        self.parentFrame=parentFrame
        self.enteredCallback=enteredCallback
        self.updateStringsCallback=updateStringsCallback
        self.choiceStrings=choiceStrings
        self.project=project
        self.projectPath=projectPath
        self.pack(side=TOP,fill=X,expand=YES)
        self.string=StringVar()
        self.label = Label(self,width=30,text=textLabel+': ',anchor='e')
        self.label.pack(side=LEFT, expand=NO, fill=X)
        self.entry = Frame(self)
        self.entry.config(width=30,borderwidth=1,relief=RAISED)
#         self.entry.bind('<Return>',self.onPressed)
#         self.entry.bind('<Tab>',self.onEntered)
        self.entry.bind('<Button-1>',self.onTouched)
#         self.entry.bind('<Double-Button-1>',self.onCleared)
#         self.entry.bind('<Button-3>',self.onUntouchedLoseFocus)
#         self.entry.bind('<Escape>',self.onUntouchedLoseFocus)
        self.entry.bind('<FocusOut>',self.onUntouched)
        self.entry.pack(side=LEFT, expand=YES, fill=X)
        for text,value in self.choiceStrings:
            b = Radiobutton(self.entry,text=text,variable=self.string,value=value,command=self.onPressed)
            b.pack(anchor=W)
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project.GetValue(self.projectPath)))
    def SetString(self,value):
        self.string.set(value)
        #self.entry.config(text=value)
    def GetString(self):
        return self.string.get()
    def onPressed(self,event=None):
        if not ((self.project is None) or (self.projectPath is None)):
            self.project.SetValue(self.projectPath,self.GetString())
        if not self.enteredCallback is None:
            self.enteredCallback(event)
        self.UpdateStrings()
    def onTouched(self,event):
        self.UpdateStrings()
    def onUntouched(self,event):
        self.UpdateStrings()
    def Show(self,whetherTo=True):
        if whetherTo:
            self.pack(side=TOP,fill=X,expand=YES)
        else:
            self.pack_forget()
    def UpdateStrings(self):
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project.GetValue(self.projectPath)))
        if not self.updateStringsCallback is None:
            self.updateStringsCallback()

class CalculationPropertyColor(Frame):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback,project=None,projectPath=None):
        Frame.__init__(self,parentFrame)
        self.parentFrame=parentFrame
        self.enteredCallback=enteredCallback
        self.updateStringsCallback=updateStringsCallback
        self.project=project
        self.projectPath=projectPath
        self.pack(side=TOP,fill=X,expand=YES)
        self.string=StringVar()
        self.label = Label(self,width=30,text=textLabel+': ',anchor='e')
        self.label.pack(side=LEFT, expand=NO, fill=X)
        self.entry = Button(self,command=self.onPressed)
        self.entry.config(width=30)
        self.entry.bind('<Return>',self.onPressed)
        self.entry.pack(side=LEFT, expand=YES, fill=X)
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project.GetValue(self.projectPath)))
    def SetString(self,value):
        self.string.set(value)
        try:
            self.entry.config(bg=value)
        except:
            pass
    def GetString(self):
        return self.string.get()
    def onPressed(self,event=None):
        color = askcolor()[1]
        if not color is None:
            self.SetString(color)
            if not ((self.project is None) or (self.projectPath is None)):
                self.project.SetValue(self.projectPath,self.GetString())
            if not self.enteredCallback is None:
                self.enteredCallback(event)
            self.UpdateStrings()
    def Show(self,whetherTo=True):
        if whetherTo:
            self.pack(side=TOP,fill=X,expand=YES)
        else:
            self.pack_forget()
    def UpdateStrings(self):
        if not ((self.project is None) or (self.projectPath is None)):
            self.SetString(str(self.project.GetValue(self.projectPath)))
        if not self.updateStringsCallback is None:
            self.updateStringsCallback()

class PropertiesDialog(Toplevel):
    def __init__(self,parent,project,top,title):
        Toplevel.__init__(self, parent)
        self.parent=parent
        self.top=top
        self.withdraw()
        self.title(title)
        img = PhotoImage(file=self.top.installdir+'/icons/png/AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.project=project
        self.propertyListFrame = Frame(self)
        self.propertyListFrame.pack(side=TOP,fill=X,expand=NO)
    def Finish(self):
        (x,y)=(self.top.root.winfo_x()+self.top.root.winfo_width()/2-self.winfo_width()/2,
            self.top.root.winfo_y()+self.top.root.winfo_height()/2-self.winfo_height()/2)
        self.geometry("%+d%+d" % (x,y))
        self.deiconify()
