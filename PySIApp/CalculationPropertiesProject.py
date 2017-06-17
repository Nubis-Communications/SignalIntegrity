'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2017 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from Tkinter import Toplevel,PhotoImage,Frame,Button,Label,StringVar,Entry,Radiobutton
from Tkinter import TOP,YES,LEFT,X,NO,NORMAL,RAISED,W,RIDGE

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

class ImpedanceMeasurementPropertiesDialog(PropertiesDialog):
    andorChoices=[('Or (most common)','OR'),('And (highly restrictive)','AND')]
    def __init__(self, parent,project):
        PropertiesDialog.__init__(self,parent,project,parent,'Impedance Measurement Properties')
        averagesFrame = Frame(self.propertyListFrame, relief=RIDGE, borderwidth=5)
        averagesFrame.pack(side=TOP,fill=X,expand=NO)
        self.maxAveragesPerFrequencyFrame=CalculationProperty(averagesFrame,'max averages per frequency point',None,None,project,'ImpedanceMeasurement.MaxAveragesPerFrequency')
        self.averagesPerStepFrame=CalculationProperty(averagesFrame,'averages per step',None,None,project,'ImpedanceMeasurement.AveragesPerStep')
        errorFrame = Frame(self.propertyListFrame, relief=RIDGE, borderwidth=5)
        errorFrame.pack(side=TOP,fill=X,expand=NO)
        self.errorInPercentOfValueFrame=CalculationPropertyTrueFalseButton(errorFrame,'maximum error in percent of value',None,self.UpdateError,project,'ImpedanceMeasurement.ErrorInPercentOfValue')
        self.percentErrorDesiredFrame=CalculationPropertySI(errorFrame,'maximum percent error desired',None,None,project,'ImpedanceMeasurement.PercentErrorDesired','%')
        self.errorInAbsoluteValueFrame=CalculationPropertyTrueFalseButton(errorFrame,'max error in absolute impedance',None,self.UpdateError,project,'ImpedanceMeasurement.ErrorInAbsoluteLimits')
        self.hiLimitFrame=CalculationPropertySI(errorFrame,'absolute high error desired',None,None,project,'ImpedanceMeasurement.PlusLimitDesired','Ohm')
        self.lowLimitFrame=CalculationPropertySI(errorFrame,'absolute low error desired',None,None,project,'ImpedanceMeasurement.MinusLimitDesired','Ohm')
        self.andOrFrame=CalculationPropertyChoices(errorFrame,'absolute/percent error specification',None,None,self.andorChoices,project,'ImpedanceMeasurement.PlusMinusAndOr')
        self.floorFrame=CalculationPropertySI(errorFrame,'absolute impedance floor',None,None,project,'ImpedanceMeasurement.LowLimitDesired','Ohm')
        limitsFrame = Frame(self.propertyListFrame, relief=RIDGE, borderwidth=5)
        limitsFrame.pack(side=TOP,fill=X,expand=NO)
        self.setZViewFrame=CalculationPropertyTrueFalseButton(limitsFrame,'specify limits on impedance plot',None,self.UpdateZView,project,'ImpedanceMeasurement.SetZView')
        self.minZFrame=CalculationPropertySI(limitsFrame,'minimum impedance',None,None,project,'ImpedanceMeasurement.MinZ','Ohm')
        self.maxZFrame=CalculationPropertySI(limitsFrame,'maximum impedance',None,None,project,'ImpedanceMeasurement.MaxZ','Ohm')
        self.UpdateError()
        self.UpdateZView()
        self.Finish()
    def UpdateZView(self):
        showMinMax=self.project.GetValue('ImpedanceMeasurement.SetZView')
        self.minZFrame.Show(showMinMax)
        self.maxZFrame.Show(showMinMax)
    def UpdateError(self):
        self.errorInPercentOfValueFrame.Show(False)
        self.percentErrorDesiredFrame.Show(False)
        self.errorInAbsoluteValueFrame.Show(False)
        self.hiLimitFrame.Show(False)
        self.lowLimitFrame.Show(False)
        self.andOrFrame.Show(False)
        self.floorFrame.Show(False)
        specifyPercentError=self.project.GetValue('ImpedanceMeasurement.ErrorInPercentOfValue')
        specifyAbsoluteError=self.project.GetValue('ImpedanceMeasurement.ErrorInAbsoluteLimits')
        self.errorInPercentOfValueFrame.Show(True)
        self.percentErrorDesiredFrame.Show(specifyPercentError)
        self.errorInAbsoluteValueFrame.Show(True)
        self.hiLimitFrame.Show(specifyAbsoluteError)
        self.lowLimitFrame.Show(specifyAbsoluteError)
        self.andOrFrame.Show(specifyAbsoluteError and specifyPercentError)
        self.floorFrame.Show(True)

class ScopeChannelSelectionDialog(Toplevel):
    def __init__(self, parent, project):
        self.parent=parent
        self.project=project
        self.selectedColor='white'
        Toplevel.__init__(self, parent)
        self.title('Scope Channel')
        self.buttonsFrame=Frame(self)
        self.buttonsFrame.pack()
        buttonWidth=5
        self.button1=Button(self.buttonsFrame)
        self.button1.configure(width=buttonWidth,text='1',command=self.on1)
        self.defaultBackgroundColor = self.button1.cget("background")
        self.button1.pack(side=LEFT)
        self.button2=Button(self.buttonsFrame)
        self.button2.configure(width=buttonWidth,text='2',command=self.on2)
        self.button2.pack(side=LEFT)
        self.button3=Button(self.buttonsFrame)
        self.button3.configure(width=buttonWidth,text='3',command=self.on3)
        self.button3.pack(side=LEFT)
        self.button4=Button(self.buttonsFrame)
        self.button4.configure(width=buttonWidth,text='4',command=self.on4)
        self.button4.pack(side=LEFT)
        self.button5=Button(self.buttonsFrame)
        self.button5.configure(width=buttonWidth,text='5',command=self.on5)
        self.button5.pack(side=LEFT)
        self.button6=Button(self.buttonsFrame)
        self.button6.configure(width=buttonWidth,text='6',command=self.on6)
        self.button6.pack(side=LEFT)
        self.button7=Button(self.buttonsFrame)
        self.button7.configure(width=buttonWidth,text='7',command=self.on7)
        self.button7.pack(side=LEFT)
        self.button8=Button(self.buttonsFrame)
        self.button8.configure(width=buttonWidth,text='8',command=self.on8)
        self.button8.pack(side=LEFT)
        self.SetButtonColorsBasedOnSelected()
        (x,y)=(self.parent.winfo_x()+self.parent.winfo_width()/2-self.winfo_width()/2,
            self.parent.winfo_y()+self.parent.winfo_height()/2-self.winfo_height()/2)
        self.geometry("%+d%+d" % (x,y))
    
    def SetButtonColorsBasedOnSelected(self):
        channel=self.GetChannel()
        self.button1.configure(bg=self.selectedColor if channel == 1 else self.defaultBackgroundColor)
        self.button2.configure(bg=self.selectedColor if channel == 2 else self.defaultBackgroundColor)
        self.button3.configure(bg=self.selectedColor if channel == 3 else self.defaultBackgroundColor)
        self.button4.configure(bg=self.selectedColor if channel == 4 else self.defaultBackgroundColor)
        self.button5.configure(bg=self.selectedColor if channel == 5 else self.defaultBackgroundColor)
        self.button6.configure(bg=self.selectedColor if channel == 6 else self.defaultBackgroundColor)
        self.button7.configure(bg=self.selectedColor if channel == 7 else self.defaultBackgroundColor)
        self.button8.configure(bg=self.selectedColor if channel == 8 else self.defaultBackgroundColor)

    def on1(self):
        self.ChangeSelection(1)
    def on2(self):
        self.ChangeSelection(2)
    def on3(self):
        self.ChangeSelection(3)
    def on4(self):
        self.ChangeSelection(4)
    def on5(self):
        self.ChangeSelection(5)
    def on6(self):
        self.ChangeSelection(6)
    def on7(self):
        self.ChangeSelection(7)
    def on8(self):
        self.ChangeSelection(8)
    def ChangeSelection(self,channel):
        self.SetChannel(channel)
        self.SetButtonColorsBasedOnSelected()

class VoutScopeChannelSelectionDialog(ScopeChannelSelectionDialog):
    def __init__(self,parent,project):
        ScopeChannelSelectionDialog.__init__(self,parent,project)
    def GetChannel(self):
        return self.project.GetValue('VoutMeasurement.Channel')
    def SetChannel(self,channel):
        self.project.SetValue('VoutMeasurement.Channel',channel)

class VoutPropertiesDialog(PropertiesDialog):
    def __init__(self, parent,project):
        PropertiesDialog.__init__(self,parent,project,parent.parent,'Vout Properties')
        otherPropertiesFrame = Frame(self.propertyListFrame, relief=RIDGE, borderwidth=5) 
        otherPropertiesFrame.pack(side=TOP,fill=X,expand=NO)
        scopeChannelFrame = Frame(self.propertyListFrame, relief=RIDGE, borderwidth=5) 
        scopeChannelFrame.pack(side=TOP,fill=X,expand=NO)
        self.voutFrame=CalculationPropertySI(otherPropertiesFrame,'Output Voltage',None,None,project,'DUT.Vout','V')
        self.scopeSerialNumberFrame=CalculationProperty(scopeChannelFrame,'scope serial number',None,None,project,'Instrument.Scope.SerialNumber')
        self.scopeChannelButton=Button(scopeChannelFrame)
        self.scopeChannelButton.config(text='Scope Channel '+str(self.project.GetValue('VoutMeasurement.Channel')),command=self.onChannelSelect)
        self.scopeChannelButton.pack()
        self.vdivFrame=CalculationPropertySI(scopeChannelFrame,'vdiv',None,None,project,'VoutMeasurement.Vdiv','V')
        self.couplingFrame=CalculationPropertyChoices(scopeChannelFrame,'coupling',None,None,CalculationPropertyChoices.couplingChoices,project,'VoutMeasurement.Coupling')
        self.bandwidthLimitFrame=CalculationPropertyChoices(scopeChannelFrame,'bandwidth limit',None,None,CalculationPropertyChoices.bandwidthChoices,project,'VoutMeasurement.BandwidthLimit')
        self.Finish()
    def onChannelSelect(self):
        scopeDialog=VoutScopeChannelSelectionDialog(self,self.project)
        scopeDialog.wait_window()
        self.scopeChannelButton.config(text='Scope Channel '+str(self.project.GetValue('VoutMeasurement.Channel')))

class ElectronicLoadPropertiesDialog(PropertiesDialog):
    electronicLoadChoices = [('None','None'),('Manual','Manual'),('Fixed','Fixed'),('Keysight','Keysight')]
    modeChoices=[('Fixed','Fixed'),('Swept','Swept')]
    def __init__(self, parent,project):
        PropertiesDialog.__init__(self,parent,project,parent.parent,'Electronic Load Properties')
        electronicLoadFrame = Frame(self.propertyListFrame, relief=RIDGE, borderwidth=5) 
        electronicLoadFrame.pack(side=TOP,fill=X,expand=NO)
        self.currentSweepFrame = Frame(self.propertyListFrame, relief=RIDGE, borderwidth=5) 
        self.currentSweepFrame.pack(side=TOP,fill=X,expand=NO)
        self.electronicLoadTypeFrame=CalculationPropertyChoices(electronicLoadFrame,'Electronic Load type',None,self.UpdateConfiguration,self.electronicLoadChoices,project,'Instrument.ElectronicLoad.Type')
        self.electronicLoadSerialNumberFrame=CalculationProperty(electronicLoadFrame,'Electronic Load serial number',None,None,project,'Instrument.ElectronicLoad.SerialNumber')
        self.modeFrame=CalculationPropertyChoices(electronicLoadFrame,'Mode',None,self.UpdateConfiguration,self.modeChoices,project,'Instrument.ElectronicLoad.Mode')
        self.loadCurrentFrame=CalculationPropertySI(self.currentSweepFrame,'Fixed Load Current',None,None,project,'Instrument.ElectronicLoad.Current','A')
        self.startCurrentFrame=CalculationPropertySI(self.currentSweepFrame,'Start Current',None,None,project,'Instrument.ElectronicLoad.StartCurrent','A')
        self.endCurrentFrame=CalculationPropertySI(self.currentSweepFrame,'End Current',None,None,project,'Instrument.ElectronicLoad.EndCurrent','A')
        self.currentStepFrame=CalculationPropertySI(self.currentSweepFrame,'Current Step',None,None,project,'Instrument.ElectronicLoad.CurrentStep','A')
        self.UpdateConfiguration()
        self.Finish()
    def UpdateConfiguration(self):
        loadType=self.project.GetValue('Instrument.ElectronicLoad.Type')
        if loadType is None:
            self.currentSweepFrame.pack_forget()
        else:
            self.currentSweepFrame.pack(side=TOP,fill=X,expand=NO)
        self.modeFrame.Show(loadType != None)
        currentFixed=(self.project.GetValue('Instrument.ElectronicLoad.Mode')=='Fixed') or (loadType=='Fixed')
        self.electronicLoadSerialNumberFrame.Show(loadType=='Keysight')
        self.loadCurrentFrame.Show(currentFixed and not (loadType is None))
        self.startCurrentFrame.Show(not currentFixed and not (loadType is None))
        self.endCurrentFrame.Show(not currentFixed and not (loadType is None))
        self.currentStepFrame.Show(not currentFixed and not (loadType is None))
