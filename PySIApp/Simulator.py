'''
Created on Oct 29, 2015

@author: peterp
'''

from Tkinter import *
import tkMessageBox
from PartProperty import *
from SParameterViewerWindow import *

import matplotlib

if not 'matplotlib.backends' in sys.modules:
    matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from matplotlib.figure import Figure

class SimulatorDialogMenu(Menu):
    def __init__(self,parent):
        self.parent=parent
        Menu.__init__(self,self.parent)
        self.parent.config(menu=self)
        self.FileMenu=Menu(self)
        self.add_cascade(label='File',menu=self.FileMenu)
        self.FileMenu.add_command(label="Save Waveforms",command=self.parent.onWriteSimulatorToFile)
        self.FileMenu.add_command(label="Read Waveforms",command=self.parent.onReadSimulatorFromFile)
        self.CalcMenu=Menu(self)
        self.add_cascade(label='Calculate',menu=self.CalcMenu)
        self.CalcMenu.add_command(label='Calculation Properties',command=self.parent.onCalculationProperties)
        self.CalcMenu.add_command(label='Examine Transfer Matrices',command=self.parent.onExamineTransferMatrices)
        self.CalcMenu.add_separator()
        self.CalcMenu.add_command(label='Simulate',command=self.parent.parent.Simulate)

class SimulatorDialogToolBar(Frame):
    def __init__(self,parent):
        self.parent=parent
        Frame.__init__(self,self.parent)
        self.pack(side=TOP,fill=X,expand=NO)
        filesFrame=self
        self.openProjectButtonIcon = PhotoImage(file='./icons/png/16x16/actions/document-open-2.gif')
        self.openProjectButton = Button(filesFrame,command=self.parent.onReadSimulatorFromFile,image=self.openProjectButtonIcon)
        self.openProjectButton.pack(side=LEFT,fill=NONE,expand=NO)
        self.saveProjectButtonIcon = PhotoImage(file='./icons/png/16x16/actions/document-save-2.gif')
        self.saveProjectButton = Button(filesFrame,command=self.parent.onWriteSimulatorToFile,image=self.saveProjectButtonIcon)
        self.saveProjectButton.pack(side=LEFT,fill=NONE,expand=NO)
        separator=Frame(self,height=2,bd=2,relief=RAISED).pack(side=LEFT,fill=X,padx=5,pady=5)
        calcFrame=self
        self.calcPropertiesButtonIcon = PhotoImage(file='./icons/png/16x16/actions/tooloptions.gif')
        self.calcPropertiesButton = Button(calcFrame,command=self.parent.onCalculationProperties,image=self.calcPropertiesButtonIcon)
        self.calcPropertiesButton.pack(side=LEFT,fill=NONE,expand=NO)
        self.calculateButtonIcon = PhotoImage(file='./icons/png/16x16/actions/system-run-3.gif')
        self.calculateButton = Button(calcFrame,command=self.parent.parent.Simulate,image=self.calculateButtonIcon)
        self.calculateButton.pack(side=LEFT,fill=NONE,expand=NO)


class SimulatorDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent.parent)
        self.parent=parent
        self.withdraw()
        self.title('PySI Simulation')
        img = PhotoImage(file='./icons/png/AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.menu=SimulatorDialogMenu(self)
        self.toolbar=SimulatorDialogToolBar(self)

        self.f = Figure(figsize=(5,4), dpi=100)
        self.plt = self.f.add_subplot(111)
        self.plt.set_xlabel('time (ns)')
        self.plt.set_ylabel('amplitude')

        self.waveformList=None
        self.waveformNamesList=None
        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        #canvas.show()
        self.canvas.get_tk_widget().pack(side=TOP, fill=X, expand=1)

        toolbar = NavigationToolbar2TkAgg( self.canvas, self )
        toolbar.update()
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        controlsFrame = Frame(self)
        Button(controlsFrame,text='autoscale',command=self.onAutoscale).pack(side=LEFT,expand=NO,fill=X)
        controlsFrame.pack(side=TOP,fill=X,expand=NO)

    def onAutoscale(self):
        self.plt.autoscale(True)
        self.f.canvas.draw()

    def UpdateWaveforms(self,waveformList, waveformNamesList):
        self.lift(self.parent.parent)
        self.plt.cla()
        self.plt.set_xlabel('time (ns)',fontsize=10)
        self.plt.set_ylabel('amplitude',fontsize=10)

        if not self.waveformList == None:
            self.plt.autoscale(False)

        self.waveformList=waveformList
        self.waveformNamesList=waveformNamesList

        for wfi in range(len(self.waveformList)):
            self.plt.plot(self.waveformList[wfi].Times('ns'),self.waveformList[wfi].Values(),label=str(self.waveformNamesList[wfi]))

        self.plt.legend(loc='upper right',labelspacing=0.1)
        self.f.canvas.draw()
        return self

    def onWriteSimulatorToFile(self):
        pass
    def onReadSimulatorFromFile(self):
        pass
    def onCalculationProperties(self):
        self.parent.parent.onCalculationProperties()
        self.parent.parent.calculationProperties.CalculationPropertiesDialog().lift(self)
    def onExamineTransferMatrices(self):
        SParametersDialog(self,self.parent.transferMatrices.SParameters())

class Simulator(object):
    def __init__(self,parent):
        self.parent=parent
    def SimulatorDialog(self):
        if not hasattr(self,'simulatorDialog'):
            self.simulatorDialog=SimulatorDialog(self)
        if self.simulatorDialog == None:
            self.simulatorDialog=SimulatorDialog(self)
        else:
            if not self.simulatorDialog.winfo_exists():
                self.simulatorDialog=SimulatorDialog(self)
        return self.simulatorDialog
    def UpdateWaveforms(self,outputWaveformList,outputWaveformLabels):
        self.SimulatorDialog().UpdateWaveforms(outputWaveformList,outputWaveformLabels).state('normal')
    def Simulate(self):
        #self.ShowCalculationPropertiesDialog()
        netList=self.parent.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity as si
        snp=si.p.SimulatorNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.parent.calculationProperties.endFrequency,
                self.parent.calculationProperties.frequencyPoints))
        snp.AddLines(netListText)
        try:
            self.transferMatrices=snp.TransferMatrices()
        except si.PySIException as e:
            if e == si.PySIExceptionCheckConnections:
                tkMessageBox.showerror('Simulator','Unconnected devices error: '+e.message)
            elif e == si.PySIExceptionSParameterFile:
                tkMessageBox.showerror('Simulator','s-parameter file error: '+e.message)
            elif e == si.PySIExceptionSimulator:
                tkMessageBox.showerror('Simulator','Simulator Error: '+e.message)
            elif e == si.PySIExceptionSystemDescriptionBuildError:
                tkMessageBox.showerror('Simulator','Schematic Error: '+e.message)
            else:
                tkMessageBox.showerror('Simulator','Unhandled PySI Exception: '+str(e)+' '+e.message)
            return
        tmp=si.td.f.TransferMatricesProcessor(self.transferMatrices)
        try:
            inputWaveformList=self.parent.Drawing.schematic.InputWaveforms()
        except si.PySIException as e:
            if e == si.PySIExceptionWaveformFile:
                tkMessageBox.showerror('Simulator','Waveform file error: '+e.message)
                return

        outputWaveformList = tmp.ProcessWaveforms(inputWaveformList)
        outputWaveformLabels=netList.OutputNames()

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = outputWaveformLabels[outputWaveformIndex]
            for device in self.parent.Drawing.schematic.deviceList:
                if device[PartPropertyPartName().propertyName].GetValue() == 'Output':
                    if device[PartPropertyReferenceDesignator().propertyName].GetValue() == outputWaveformLabel:
                        gain=device[PartPropertyVoltageGain().propertyName].GetValue()
                        offset=device[PartPropertyVoltageOffset().propertyName].GetValue()
                        delay=device[PartPropertyDelay().propertyName].GetValue()
                        outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.TimeDescriptor().H,wf.TimeDescriptor().N,self.parent.calculationProperties.userSampleRate))
                for wf in outputWaveformList]
        self.UpdateWaveforms(outputWaveformList, outputWaveformLabels)

