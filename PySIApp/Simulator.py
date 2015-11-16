'''
Created on Oct 29, 2015

@author: peterp
'''

from Tkinter import *
import xml.etree.ElementTree as et
import tkMessageBox

from PlotWindow import *
from ToSI import *
from PartProperty import *

class Simulator(object):
    def __init__(self,parent):
        self.parent=parent
    def PlotDialog(self):
        if not hasattr(self,'plotDialog'):
            self.plotDialog=PlotDialog(self.parent)
        if self.plotDialog == None:
            self.plotDialog=PlotDialog(self.parent)
        else:
            if not self.plotDialog.winfo_exists():
                self.plotDialog=PlotDialog(self.parent)
        return self.plotDialog
    def UpdateWaveforms(self,outputWaveformList,outputWaveformLabels):
        self.PlotDialog().UpdateWaveforms(outputWaveformList,outputWaveformLabels).state('normal')
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
        #tm=snp.TransferMatrices()
        try:
            tmp=si.td.f.TransferMatricesProcessor(snp.TransferMatrices())
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