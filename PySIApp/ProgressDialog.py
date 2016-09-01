'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from Tkinter import *
from math import floor
       
class ProgressDialog(Toplevel):
    def __init__(self, parent, installdir, title, classOfThing, thingToDo, granularity=1.0):
        Toplevel.__init__(self, parent)
        self.parent=parent
        self.title(title)
        img = PhotoImage(file=installdir+'/icons/png/AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.barFrame=Frame(self)
        self.barFrame.pack(side=TOP)
        self.bar = Canvas(self.barFrame,relief=SUNKEN,borderwidth=1,width=600,height=10)
        self.bar.pack(side=TOP,fill=BOTH,expand=YES)
        self.buttonFrame=Frame(self)
        self.buttonFrame.pack(side=TOP)
        self.stopButton = Button(self.buttonFrame,text='Stop',command=self.onStop)
        self.stopButton.pack(side=TOP,fill=BOTH,expand=NO)
        self.stopCommand=False
        self.isShowing=False
        self.thingToDo = thingToDo
        self.classOfThing = classOfThing
        self.currentPercent = -1
        self.granularity = granularity
        self.geometry("%+d%+d" % (self.parent.root.winfo_x()+self.parent.root.winfo_width()/2-self.winfo_width()/2,
            self.parent.root.winfo_y()+self.parent.root.winfo_height()/2-self.winfo_height()/2))
        self.grab_set()

    def onStop(self):
        self.stopCommand=True
    def Callback(self,number):
        #return True
        if self.stopCommand:
            self.destroy()
            return False
        if not self.isShowing:
            pass
        self.isShowing=True
        if floor(number/self.granularity) != self.currentPercent:
            self.currentPercent = floor(number/self.granularity)  
            self.bar.create_rectangle(0,0,600*number/100.0,10,fill='blue')
            self.update()
        return True
    def GetResult(self):
        self.classOfThing.InstallCallback(self.Callback)
        self.Callback(0)
        try:
            self.result = self.thingToDo()
        except:
            raise
        finally:
            self.destroy()
            self.classOfThing.RemoveCallback()
        return self.result