'''
Created on Oct 29, 2015

@author: peterp
'''

from Tkinter import *
import xml.etree.ElementTree as et

from PlotWindow import *
from ToSI import *

class SimulatorProperty(Frame):
    def __init__(self,parentFrame,textLabel,enteredCallback,updateStringsCallback):
        Frame.__init__(self,parentFrame)
        self.parentFrame=parentFrame
        self.enteredCallback=enteredCallback
        self.updateStringsCallback=updateStringsCallback
        self.pack(side=TOP,fill=X,expand=YES)
        self.string=StringVar()
        self.label = Label(self,width=20,text=textLabel+': ',anchor='e')
        self.label.pack(side=LEFT, expand=NO, fill=X)
        self.entry = Entry(self,textvariable=self.string)
        self.entry.config(width=15)
        self.entry.bind('<Return>',self.onEntered)
        self.entry.bind('<FocusIn>',self.onTouched)
        self.entry.bind('<Button-3>',self.onUntouched)
        self.entry.bind('<Escape>',self.onUntouched)
        self.entry.bind('<FocusOut>',self.onUntouched)
        self.entry.pack(side=LEFT, expand=YES, fill=X)
    def SetString(self,value):
        self.string.set(value)
    def GetString(self):
        return self.string.get()
    def onEntered(self,event):
        self.enteredCallback(event)
        self.onUntouched(event)
    def onTouched(self,event):
        self.updateStringsCallback()
        self.string.set('')
    def onUntouched(self,event):
        self.updateStringsCallback()
        self.parentFrame.focus()

class SimulatorDialog(Toplevel):
    def __init__(self, parent,simulator):
        Toplevel.__init__(self, parent)
        self.parent=parent
        self.title('PySI Simulator')
        img = PhotoImage(file='./icons/png/AppIcon.png')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.withdraw()
        self.simulator=simulator
        propertyListFrame = Frame(self)
        propertyListFrame.pack(side=TOP,fill=X,expand=NO)
        self.endFrequencyFrame=SimulatorProperty(propertyListFrame,'end frequency',self.onendFrequencyEntered,self.updateStrings)
        self.frequencyPointsFrame=SimulatorProperty(propertyListFrame,'frequency points',self.onfrequencyPointsEntered,self.updateStrings)
        self.frequencyResolutionFrame=SimulatorProperty(propertyListFrame,'frequency resolution',self.onfrequencyResolutionEntered,self.updateStrings)
        self.userSampleRateFrame=SimulatorProperty(propertyListFrame,'user sample rate',self.onuserSampleRateEntered,self.updateStrings)
        self.baseSampleRateFrame=SimulatorProperty(propertyListFrame,'base sample rate',self.onbaseSampleRateEntered,self.updateStrings)
        self.timePointsFrame=SimulatorProperty(propertyListFrame,'time points',self.ontimePointsEntered,self.updateStrings)
        self.impulseLengthFrame=SimulatorProperty(propertyListFrame,'impulse response length',self.onimpulseLengthEntered,self.updateStrings)
        self.updateStrings()
        controlsFrame = Frame(self)
        Button(controlsFrame,text='simulate',command=self.onSimulate).pack(side=LEFT,expand=NO,fill=X)
        controlsFrame.pack(side=TOP,fill=X,expand=NO)

    def onendFrequencyEntered(self,event):
        self.simulator.endFrequency=nextHigher12458(float(self.endFrequencyFrame.GetString()))
        self.simulator.baseSampleRate=2.*self.simulator.endFrequency
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution

    def onfrequencyPointsEntered(self,event):
        self.simulator.frequencyPoints=int(nextHigher12458(float(self.frequencyPointsFrame.GetString())))
        self.simulator.timePoints=int(self.simulator.frequencyPoints*2)
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution

    def onfrequencyResolutionEntered(self,event):
        self.simulator.frequencyResolution=float(self.frequencyResolutionFrame.GetString())
        self.simulator.frequencyPoints=int(nextHigher12458(self.simulator.endFrequency/self.simulator.frequencyResolution))
        self.simulator.timePoints=self.simulator.frequencyPoints*2
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution

    def onuserSampleRateEntered(self,event):
        self.simulator.userSampleRate=nextHigher12458(float(self.userSampleRateFrame.GetString()))

    def onbaseSampleRateEntered(self,event):
        self.simulator.baseSampleRate=float(self.baseSampleRateFrame.GetString())
        self.simulator.endFrequency=nextHigher12458(self.simulator.baseSampleRate/2.)
        self.simulator.baseSampleRate=self.simulator.endFrequency*2
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution

    def ontimePointsEntered(self,event):
        self.simulator.timePoints=int(self.timePointsFrame.GetString())
        self.simulator.frequencyPoints=int(nextHigher12458(self.simulator.timePoints/2))
        self.simulator.timePoints=self.simulator.frequencyPoints*2
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution

    def onimpulseLengthEntered(self,event):
        self.simulator.impulseLength=float(self.impulseLengthFrame.GetString())
        self.simulator.timePoints=self.simulator.impulseLength*self.simulator.baseSampleRate
        self.simulator.frequencyPoints=int(nextHigher12458(self.simulator.timePoints/2.))
        self.simulator.timePoints=self.simulator.frequencyPoints*2
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution

    def onSimulate(self):
        self.simulator.Simulate()

    def updateStrings(self):
        self.endFrequencyFrame.SetString(ToSI(self.simulator.endFrequency,'Hz'))
        self.frequencyPointsFrame.SetString(ToSI(self.simulator.frequencyPoints,'pts'))
        self.userSampleRateFrame.SetString(ToSI(self.simulator.userSampleRate,'S/s'))
        self.baseSampleRateFrame.SetString(ToSI(self.simulator.baseSampleRate,'S/s'))
        self.timePointsFrame.SetString(ToSI(self.simulator.timePoints,'pts'))
        self.frequencyResolutionFrame.SetString(ToSI(self.simulator.frequencyResolution,'Hz/pt'))
        self.impulseLengthFrame.SetString(ToSI(self.simulator.impulseLength,'s'))

class Simulator(object):
    def __init__(self,parent,endFrequency=20e9,frequencyPoints=400,userSampleRate=40e9):
        self.parent=parent
        self.schematic=parent.Drawing.schematic
        self.endFrequency=endFrequency
        self.frequencyPoints=frequencyPoints
        self.userSampleRate=userSampleRate
        self.CalculateOthersFromBaseInformation()
    def CalculateOthersFromBaseInformation(self):
        self.baseSampleRate=self.endFrequency*2
        self.timePoints=self.frequencyPoints*2
        self.frequencyResolution=self.endFrequency/self.frequencyPoints
        self.impulseLength=1./self.frequencyResolution
    def ShowSimulatorDialog(self):
        self.SimulatorDialog().state('normal')
        self.SimulatorDialog().lift(self.parent)
    def PlotDialog(self):
        if not hasattr(self,'plotDialog'):
            self.plotDialog=PlotDialog(self.parent)
        if self.plotDialog == None:
            self.plotDialog=PlotDialog(self.parent)
        else:
            if not self.plotDialog.winfo_exists():
                self.plotDialog=PlotDialog(self.parent)
        return self.plotDialog
    def SimulatorDialog(self):
        if not hasattr(self, 'simulatorDialog'):
            self.simulatorDialog = SimulatorDialog(self.parent,self)
        if self.simulatorDialog == None:
            self.simulatorDialog= SimulatorDialog(self.parent,self)
        else:
            if not self.simulatorDialog.winfo_exists():
                self.simulatorDialog=SimulatorDialog(self.parent,self)
        return self.simulatorDialog
    def UpdateWaveforms(self,outputWaveformList,outputWaveformLabels):
        self.PlotDialog().UpdateWaveforms(outputWaveformList,outputWaveformLabels).state('normal')
    def xml(self):
        simulatorElement=et.Element('simulator')
        simulatorPropertiesElement=et.Element('simulation_properties')
        simulatorPropertiesElementList=[]
        simulatorProperty=et.Element('end_frequency')
        simulatorProperty.text=str(self.endFrequency)
        simulatorPropertiesElementList.append(simulatorProperty)
        simulatorProperty=et.Element('frequency_points')
        simulatorProperty.text=str(self.frequencyPoints)
        simulatorPropertiesElementList.append(simulatorProperty)
        simulatorProperty=et.Element('user_samplerate')
        simulatorProperty.text=str(self.userSampleRate)
        simulatorPropertiesElementList.append(simulatorProperty)
        simulatorPropertiesElement.extend(simulatorPropertiesElementList)
        schematicPropertiesElement=self.schematic.xml()
        simulatorElement.extend([simulatorPropertiesElement,schematicPropertiesElement])
        return simulatorElement
    def InitFromXml(self,simulatorElement,parent):
        endFrequency=20e9
        frequencyPoints=400
        userSampleRate=40e9
        for child in simulatorElement:
            if child.tag == 'simulation_properties':
                for simulatorProperty in child:
                    if simulatorProperty.tag == 'end_frequency':
                        endFrequency=float(simulatorProperty.text)
                    elif simulatorProperty.tag == 'frequency_points':
                        frequencyPoints=int(simulatorProperty.text)
                    elif simulatorProperty.tag == 'user_samplerate':
                        userSampleRate = float(simulatorProperty.text)
        self.__init__(parent,endFrequency,frequencyPoints,userSampleRate)
        self.SimulatorDialog().destroy()
        self.PlotDialog().destroy()
    def Simulate(self):
        self.schematic=self.parent.Drawing.schematic
        self.ShowSimulatorDialog()
        netList=self.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity as si
        snp=si.p.SimulatorNumericParser(si.fd.EvenlySpacedFrequencyList(self.endFrequency,self.frequencyPoints))
        snp.AddLines(netListText)
        #tm=snp.TransferMatrices()
        tmp=si.td.f.TransferMatricesProcessor(snp.TransferMatrices())
        inputWaveformList=self.schematic.InputWaveforms()
        outputWaveformList = tmp.ProcessWaveforms(inputWaveformList)
        outputWaveformList = [wf.Adapt(si.td.wf.TimeDescriptor(wf.TimeDescriptor().H,wf.TimeDescriptor().N,self.userSampleRate)) for wf in outputWaveformList]
        outputWaveformLabels=netList.OutputNames()
        self.UpdateWaveforms(outputWaveformList, outputWaveformLabels)
    def OpenSimulator(self):
        self.ShowSimulatorDialog()



