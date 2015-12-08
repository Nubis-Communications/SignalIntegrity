'''
Created on Oct 29, 2015

@author: peterp
'''

from Tkinter import *
import tkMessageBox
from PartProperty import *
from SParameterViewerWindow import *
from MenuSystemHelpers import *

import matplotlib

if not 'matplotlib.backends' in sys.modules:
    matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from matplotlib.figure import Figure

class SimulatorDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent.parent)
        self.parent=parent
        self.withdraw()
        self.title('PySI Simulation')
        img = PhotoImage(file='./icons/png/AppIcon2.gif')
        self.tk.call('wm', 'iconphoto', self._w, img)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        # the Doers - the holder of the commands, menu elements, toolbar elements, and key bindings
        self.WaveformSaveDoer = Doer(self.onWriteSimulatorToFile)
        self.WaveformReadDoer = Doer(self.onReadSimulatorFromFile)
        self.Matplotlib2tikzDoer = Doer(self.onMatplotlib2TikZ)
        # ------
        self.CalculationPropertiesDoer = Doer(self.onCalculationProperties)
        self.ExamineTransferMatricesDoer = Doer(self.onExamineTransferMatrices)
        self.SimulateDoer = Doer(self.parent.parent.onCalculate)

        # The menu system
        TheMenu=Menu(self)
        self.config(menu=TheMenu)
        FileMenu=Menu(self)
        TheMenu.add_cascade(label='File',menu=FileMenu,underline=0)
        self.WaveformSaveDoer.AddMenuElement(FileMenu,label="Save Waveforms",underline=0)
        self.WaveformReadDoer.AddMenuElement(FileMenu,label="Read Waveforms",underline=0)
        FileMenu.add_separator()
        self.Matplotlib2tikzDoer.AddMenuElement(FileMenu,label='Output to LaTeX (TikZ)',underline=10)
        # ------
        CalcMenu=Menu(self)
        TheMenu.add_cascade(label='Calculate',menu=CalcMenu,underline=0)
        self.CalculationPropertiesDoer.AddMenuElement(CalcMenu,label='Calculation Properties',underline=12)
        self.ExamineTransferMatricesDoer.AddMenuElement(CalcMenu,label='View Transfer Parameters',underline=0)
        CalcMenu.add_separator()
        self.SimulateDoer.AddMenuElement(CalcMenu,label='Recalculate',underline=0)

        # The Toolbar
        ToolBarFrame = Frame(self)
        ToolBarFrame.pack(side=TOP,fill=X,expand=NO)
        self.WaveformReadDoer.AddToolBarElement(ToolBarFrame,iconfile='./icons/png/16x16/actions/document-open-2.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.WaveformSaveDoer.AddToolBarElement(ToolBarFrame,iconfile='./icons/png/16x16/actions/document-save-2.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        Frame(self,height=2,bd=2,relief=RAISED).pack(side=LEFT,fill=X,padx=5,pady=5)
        self.CalculationPropertiesDoer.AddToolBarElement(ToolBarFrame,iconfile='./icons/png/16x16/actions/tooloptions.gif').Pack(side=LEFT,fill=NONE,expand=NO)
        self.SimulateDoer.AddToolBarElement(ToolBarFrame,iconfile='./icons/png/16x16/actions/system-run-3.gif').Pack(side=LEFT,fill=NONE,expand=NO)

        self.f = Figure(figsize=(6,4), dpi=100)
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

        try:
            from matplotlib2tikz import save as tikz_save
        except:
            self.Matplotlib2tikzDoer.Activate(False)

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
            if wfi==0:
                mint=self.waveformList[wfi].Times('ns')[0]
                maxt=self.waveformList[wfi].Times('ns')[-1]
            else:
                mint=max(mint,self.waveformList[wfi].Times('ns')[0])
                maxt=min(maxt,self.waveformList[wfi].Times('ns')[-1])
            self.plt.plot(self.waveformList[wfi].Times('ns'),self.waveformList[wfi].Values(),label=str(self.waveformNamesList[wfi]))

        if not self.waveformList is None:
            self.plt.set_xlim(xmin=mint)
            self.plt.set_xlim(xmax=maxt)

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
        buttonLabelList=[[out+' due to '+inp for inp in self.parent.sourceNames] for out in self.parent.outputWaveformLabels]
        maxLength=len(max([item for sublist in buttonLabelList for item in sublist],key=len))
        buttonLabelList=[[item.ljust(maxLength) for item in sublist] for sublist in buttonLabelList]
        SParametersDialog(self.parent.parent,self.parent.transferMatrices.SParameters(),'Transfer Parameters',buttonLabelList)

    def onMatplotlib2TikZ(self):
        import os
        extension='.tex'
        filename=asksaveasfilename(filetypes=[('tex', extension)],defaultextension='.tex',initialdir=os.getcwd())
        if filename=='':
            return
        try:
            from matplotlib2tikz import save as tikz_save
            tikz_save(filename,figure=self.f,show_info=False)
            texfile=open(filename,'rU')
            lines=[]
            for line in texfile:
                line=line.replace('\xe2\x88\x92','-')
                lines.append(str(line))
            texfile.close()
            texfile=open(filename,'w')
            for line in lines:
                texfile.write(line)
            texfile.close()
        except:
            tkMessageBox.showerror('Export LaTeX','LaTeX could not be generated or written ')

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
            self.inputWaveformList=self.parent.Drawing.schematic.InputWaveforms()
            self.sourceNames=netList.SourceNames()
        except si.PySIException as e:
            if e == si.PySIExceptionWaveformFile:
                tkMessageBox.showerror('Simulator','Waveform file error: '+e.message)
                return

        outputWaveformList = tmp.ProcessWaveforms(self.inputWaveformList)
        self.outputWaveformLabels=netList.OutputNames()

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = self.outputWaveformLabels[outputWaveformIndex]
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
        self.SimulatorDialog().title('PySI Simulation')
        self.UpdateWaveforms(outputWaveformList, self.outputWaveformLabels)

    def VirtualProbe(self):
        netList=self.parent.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity as si
        snp=si.p.VirtualProbeNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.parent.calculationProperties.endFrequency,
                self.parent.calculationProperties.frequencyPoints))
        snp.AddLines(netListText)
        try:
            self.transferMatrices=snp.TransferMatrices()
        except si.PySIException as e:
            if e == si.PySIExceptionCheckConnections:
                tkMessageBox.showerror('Virtual Probe','Unconnected devices error: '+e.message)
            elif e == si.PySIExceptionSParameterFile:
                tkMessageBox.showerror('Virtual Probe','s-parameter file error: '+e.message)
            elif e == si.PySIExceptionVirtualProbe:
                tkMessageBox.showerror('Virtual Probe','Virtual Probe Error: '+e.message)
            elif e == si.PySIExceptionSystemDescriptionBuildError:
                tkMessageBox.showerror('Virtual Probe','Schematic Error: '+e.message)
            else:
                tkMessageBox.showerror('Virtual Probe','Unhandled PySI Exception: '+str(e)+' '+e.message)
            return
        tmp=si.td.f.TransferMatricesProcessor(self.transferMatrices)
        try:
            self.inputWaveformList=self.parent.Drawing.schematic.InputWaveforms()
            self.sourceNames=netList.MeasureNames()
        except si.PySIException as e:
            if e == si.PySIExceptionWaveformFile:
                tkMessageBox.showerror('Virtual Probe','Waveform file error: '+e.message)
                return

        outputWaveformList = tmp.ProcessWaveforms(self.inputWaveformList)
        self.outputWaveformLabels=netList.OutputNames()

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = self.outputWaveformLabels[outputWaveformIndex]
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
        self.SimulatorDialog().title('PySI Virtual Probe')
        self.UpdateWaveforms(outputWaveformList, self.outputWaveformLabels)

