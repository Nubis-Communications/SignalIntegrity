'''
Created on Oct 29, 2015

@author: peterp
'''

from Tkinter import *
import xml.etree.ElementTree as et

from PlotWindow import *
from ToSI import *

class SimulatorDialog(Toplevel):
    def __init__(self, parent,simulator):
        Toplevel.__init__(self, parent)
        self.parent=parent
        self.title('PySI Simulator Window')
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.withdraw()
        self.simulator=simulator
        propertyListFrame = Frame(self)
        propertyListFrame.pack(side=TOP,fill=X,expand=NO)
        self.endFrequencyString=StringVar(value=ToSI(self.simulator.endFrequency,'Hz'))
        self.endFrequencyFrame=Frame(propertyListFrame)
        self.endFrequencyFrame.pack(side=TOP,fill=X,expand=YES)
        self.endFrequencyLabel = Label(self.endFrequencyFrame,width=20,text='end frequency: ',anchor='e')
        self.endFrequencyLabel.pack(side=LEFT, expand=NO, fill=X)
        self.endFrequencyEntry = Entry(self.endFrequencyFrame,textvariable=self.endFrequencyString)
        self.endFrequencyEntry.config(width=15)
        self.endFrequencyEntry.bind('<Return>',self.onendFrequencyEntered)
        self.endFrequencyEntry.bind('<FocusIn>',self.onendFrequencyTouched)
        self.endFrequencyEntry.bind('<Button-3>',self.onUntouched)
        self.endFrequencyEntry.bind('<Escape>',self.onUntouched)
        self.endFrequencyEntry.bind('<FocusOut>',self.onUntouched)
        self.endFrequencyEntry.pack(side=LEFT, expand=YES, fill=X)
        self.frequencyPointsString=StringVar(value=ToSI(self.simulator.frequencyPoints,'pts'))
        self.frequencyPointsFrame=Frame(propertyListFrame)
        self.frequencyPointsFrame.pack(side=TOP,fill=X,expand=YES)
        self.frequencyPointsLabel = Label(self.frequencyPointsFrame,width=20,text='frequency points: ',anchor='e')
        self.frequencyPointsLabel.pack(side=LEFT, expand=NO, fill=X)
        self.frequencyPointsEntry = Entry(self.frequencyPointsFrame,textvariable=self.frequencyPointsString)
        self.frequencyPointsEntry.config(width=15)
        self.frequencyPointsEntry.bind('<Return>',self.onfrequencyPointsEntered)
        self.frequencyPointsEntry.bind('<FocusIn>',self.onfrequencyPointsTouched)
        self.frequencyPointsEntry.bind('<Button-3>',self.onUntouched)
        self.frequencyPointsEntry.bind('<Escape>',self.onUntouched)
        self.frequencyPointsEntry.bind('<FocusOut>',self.onUntouched)
        self.frequencyPointsEntry.pack(side=LEFT, expand=YES, fill=X)
        self.frequencyResolutionString=StringVar(value=ToSI(self.simulator.frequencyResolution,'Hz/pt'))
        self.frequencyResolutionFrame=Frame(propertyListFrame)
        self.frequencyResolutionFrame.pack(side=TOP,fill=X,expand=YES)
        self.frequencyResolutionLabel = Label(self.frequencyResolutionFrame,width=20,text='frequency resolution: ',anchor='e')
        self.frequencyResolutionLabel.pack(side=LEFT, expand=NO, fill=X)
        self.frequencyResolutionEntry = Entry(self.frequencyResolutionFrame,textvariable=self.frequencyResolutionString)
        self.frequencyResolutionEntry.config(width=15)
        self.frequencyResolutionEntry.bind('<Return>',self.onfrequencyResolutionEntered)
        self.frequencyResolutionEntry.bind('<FocusIn>',self.onfrequencyResolutionTouched)
        self.frequencyResolutionEntry.bind('<Button-3>',self.onUntouched)
        self.frequencyResolutionEntry.bind('<Escape>',self.onUntouched)
        self.frequencyResolutionEntry.bind('<FocusOut>',self.onUntouched)
        self.frequencyResolutionEntry.pack(side=LEFT, expand=YES, fill=X)
        self.userSampleRateString=StringVar(value=ToSI(self.simulator.userSampleRate,'S/s'))
        self.userSampleRateFrame=Frame(propertyListFrame)
        self.userSampleRateFrame.pack(side=TOP,fill=X,expand=YES)
        self.userSampleRateLabel = Label(self.userSampleRateFrame,width=20,text='user sample rate: ',anchor='e')
        self.userSampleRateLabel.pack(side=LEFT, expand=NO, fill=X)
        self.userSampleRateEntry = Entry(self.userSampleRateFrame,textvariable=self.userSampleRateString)
        self.userSampleRateEntry.config(width=15)
        self.userSampleRateEntry.bind('<Return>',self.onuserSampleRateEntered)
        self.userSampleRateEntry.bind('<FocusIn>',self.onuserSampleRateTouched)
        self.userSampleRateEntry.bind('<Button-3>',self.onUntouched)
        self.userSampleRateEntry.bind('<Escape>',self.onUntouched)
        self.userSampleRateEntry.bind('<FocusOut>',self.onUntouched)
        self.userSampleRateEntry.pack(side=LEFT, expand=YES, fill=X)
        self.baseSampleRateString=StringVar(value=ToSI(self.simulator.baseSampleRate,'S/s'))
        self.baseSampleRateFrame=Frame(propertyListFrame)
        self.baseSampleRateFrame.pack(side=TOP,fill=X,expand=YES)
        self.baseSampleRateLabel = Label(self.baseSampleRateFrame,width=20,text='base sample rate: ',anchor='e')
        self.baseSampleRateLabel.pack(side=LEFT, expand=NO, fill=X)
        self.baseSampleRateEntry = Entry(self.baseSampleRateFrame,textvariable=self.baseSampleRateString)
        self.baseSampleRateEntry.config(width=15)
        self.baseSampleRateEntry.bind('<Return>',self.onbaseSampleRateEntered)
        self.baseSampleRateEntry.bind('<FocusIn>',self.onbaseSampleRateTouched)
        self.baseSampleRateEntry.bind('<Button-3>',self.onUntouched)
        self.baseSampleRateEntry.bind('<Escape>',self.onUntouched)
        self.baseSampleRateEntry.bind('<FocusOut>',self.onUntouched)
        self.baseSampleRateEntry.pack(side=LEFT, expand=YES, fill=X)
        self.timePointsString=StringVar(value=ToSI(self.simulator.timePoints,'pts'))
        self.timePointsFrame=Frame(propertyListFrame)
        self.timePointsFrame.pack(side=TOP,fill=X,expand=YES)
        self.timePointsLabel = Label(self.timePointsFrame,width=20,text='time points: ',anchor='e')
        self.timePointsLabel.pack(side=LEFT, expand=NO, fill=X)
        self.timePointsEntry = Entry(self.timePointsFrame,textvariable=self.timePointsString)
        self.timePointsEntry.config(width=15)
        self.timePointsEntry.bind('<Return>',self.ontimePointsEntered)
        self.timePointsEntry.bind('<FocusIn>',self.ontimePointsTouched)
        self.timePointsEntry.bind('<Button-3>',self.onUntouched)
        self.timePointsEntry.bind('<Escape>',self.onUntouched)
        self.timePointsEntry.bind('<FocusOut>',self.onUntouched)
        self.timePointsEntry.pack(side=LEFT, expand=YES, fill=X)
        self.impulseLengthString=StringVar(value=ToSI(self.simulator.impulseLength,'s'))
        self.impulseLengthFrame=Frame(propertyListFrame)
        self.impulseLengthFrame.pack(side=TOP,fill=X,expand=YES)
        self.impulseLengthLabel = Label(self.impulseLengthFrame,width=20,text='impulse response length: ',anchor='e')
        self.impulseLengthLabel.pack(side=LEFT, expand=NO, fill=X)
        self.impulseLengthEntry = Entry(self.impulseLengthFrame,textvariable=self.impulseLengthString)
        self.impulseLengthEntry.config(width=15)
        self.impulseLengthEntry.bind('<Return>',self.onimpulseLengthEntered)
        self.impulseLengthEntry.bind('<FocusIn>',self.onimpulseLengthTouched)
        self.impulseLengthEntry.bind('<Button-3>',self.onUntouched)
        self.impulseLengthEntry.bind('<Escape>',self.onUntouched)
        self.impulseLengthEntry.bind('<FocusOut>',self.onUntouched)
        self.impulseLengthEntry.pack(side=LEFT, expand=YES, fill=X)
        controlsFrame = Frame(self)
        Button(controlsFrame,text='simulate',command=self.onSimulate).pack(side=LEFT,expand=NO,fill=X)
        controlsFrame.pack(side=TOP,fill=X,expand=NO)

    def onendFrequencyEntered(self,event):
        self.simulator.endFrequency=nextHigher12458(float(self.endFrequencyString.get()))
        self.simulator.baseSampleRate=2.*self.simulator.endFrequency
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution
        self.onUntouched(event)

    def onendFrequencyTouched(self,event):
        self.updateStrings()
        self.endFrequencyString.set('')

    def onUntouched(self,event):
        self.updateStrings()
        self.focus()

    def onfrequencyPointsEntered(self,event):
        self.simulator.frequencyPoints=int(nextHigher12458(float(self.frequencyPointsString.get())))
        self.simulator.timePoints=int(self.simulator.frequencyPoints*2)
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution
        self.onUntouched(event)

    def onfrequencyPointsTouched(self,event):
        self.updateStrings()
        self.frequencyPointsString.set('')

    def onfrequencyResolutionEntered(self,event):
        self.simulator.frequencyResolution=float(self.frequencyResolutionString.get())
        self.simulator.frequencyPoints=int(nextHigher12458(self.simulator.endFrequency/self.simulator.frequencyResolution))
        self.simulator.timePoints=self.simulator.frequencyPoints*2
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution
        self.onUntouched(event)

    def onfrequencyResolutionTouched(self,event):
        self.updateStrings()
        self.frequencyResolutionString.set('')

    def onuserSampleRateEntered(self,event):
        self.simulator.userSampleRate=nextHigher12458(float(self.userSampleRateString.get()))
        self.onUntouched(event)

    def onuserSampleRateTouched(self,event):
        self.updateStrings()
        self.userSampleRateString.set('')

    def onbaseSampleRateEntered(self,event):
        self.simulator.baseSampleRate=float(self.baseSampleRateString.get())
        self.simulator.endFrequency=nextHigher12458(self.simulator.baseSampleRate/2.)
        self.simulator.baseSampleRate=self.simulator.endFrequency*2
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution
        self.onUntouched(event)

    def onbaseSampleRateTouched(self,event):
        self.updateStrings()
        self.baseSampleRateString.set('')

    def ontimePointsEntered(self,event):
        self.simulator.timePoints=int(self.timePointsString.get())
        self.simulator.frequencyPoints=int(nextHigher12458(self.simulator.timePoints/2))
        self.simulator.timePoints=self.simulator.frequencyPoints*2
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution
        self.onUntouched(event)

    def ontimePointsTouched(self,event):
        self.updateStrings()
        self.timePointsString.set('')

    def onimpulseLengthEntered(self,event):
        self.simulator.impulseLength=float(self.impulseLengthString.get())
        self.simulator.timePoints=self.simulator.impulseLength*self.simulator.baseSampleRate
        self.simulator.frequencyPoints=int(nextHigher12458(self.simulator.timePoints/2.))
        self.simulator.timePoints=self.simulator.frequencyPoints*2
        self.simulator.frequencyResolution=self.simulator.endFrequency/self.simulator.frequencyPoints
        self.simulator.impulseLength=1./self.simulator.frequencyResolution
        self.onUntouched(event)

    def onimpulseLengthTouched(self,event):
        self.updateStrings()
        self.impulseLengthString.set('')

    def onSimulate(self):
        self.simulator.Simulate()

    def updateStrings(self):
        self.endFrequencyString.set(ToSI(self.simulator.endFrequency,'Hz'))
        self.frequencyPointsString.set(ToSI(self.simulator.frequencyPoints,'pts'))
        self.userSampleRateString.set(ToSI(self.simulator.userSampleRate,'S/s'))
        self.baseSampleRateString.set(ToSI(self.simulator.baseSampleRate,'S/s'))
        self.timePointsString.set(ToSI(self.simulator.timePoints,'pts'))
        self.frequencyResolutionString.set(ToSI(self.simulator.frequencyResolution,'Hz/pt'))
        self.impulseLengthString.set(ToSI(self.simulator.impulseLength,'s'))

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



