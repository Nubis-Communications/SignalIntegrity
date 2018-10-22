"""
PySIAppHeadless.py
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of PySI.
#
# PySI is free software: You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version
# 3 of the License, or any later version.
#
# This program is distrbuted in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import os
import sys

import xml.etree.ElementTree as et
from Tkinter import ALL

from CalculationProperties import CalculationProperties
from Files import FileParts,ConvertFileNameToRelativePath
from Schematic import Schematic
from Preferences import Preferences

class DrawingHeadless(object):
    def __init__(self,parent):
        self.parent=parent
        self.canvas = None
        self.grid=32
        self.originx=0
        self.originy=0
        self.schematic = Schematic()
    def DrawSchematic(self,canvas=None):
        if canvas==None:
            canvas=self.canvas
            canvas.delete(ALL)
        devicePinConnectedList=self.schematic.DevicePinConnectedList()
        for deviceIndex in range(len(self.schematic.deviceList)):
            device = self.schematic.deviceList[deviceIndex]
            devicePinsConnected=devicePinConnectedList[deviceIndex]
            device.DrawDevice(canvas,self.grid,self.originx,self.originy,devicePinsConnected)
        for wire in self.schematic.wireList:
            wire.DrawWire(canvas,self.grid,self.originx,self.originy)
        for dot in self.schematic.DotList():
            size=self.grid/8
            canvas.create_oval((dot[0]+self.originx)*self.grid-size,(dot[1]+self.originy)*self.grid-size,
                                    (dot[0]+self.originx)*self.grid+size,(dot[1]+self.originy)*self.grid+size,
                                    fill='black',outline='black')
        return canvas
    def InitFromXml(self,drawingElement):
        self.grid=32
        self.originx=0
        self.originy=0
        self.schematic = Schematic()
        for child in drawingElement:
            if child.tag == 'schematic':
                self.schematic.InitFromXml(child)
            elif child.tag == 'drawing_properties':
                for drawingPropertyElement in child:
                    if drawingPropertyElement.tag == 'grid':
                        self.grid = int(drawingPropertyElement.text)
                    elif drawingPropertyElement.tag == 'originx':
                        self.originx = int(drawingPropertyElement.text)
                    elif drawingPropertyElement.tag == 'originy':
                        self.originy = int(drawingPropertyElement.text)
    def xml(self):
        drawingElement=et.Element('drawing')
        drawingPropertiesElement=et.Element('drawing_properties')
        drawingPropertiesElementList=[]
        drawingProperty=et.Element('grid')
        drawingProperty.text=str(self.grid)
        drawingPropertiesElementList.append(drawingProperty)
        drawingProperty=et.Element('originx')
        drawingProperty.text=str(self.originx)
        drawingPropertiesElementList.append(drawingProperty)
        drawingProperty=et.Element('originy')
        drawingProperty.text=str(self.originy)
        drawingPropertiesElementList.append(drawingProperty)
#         drawingProperty=et.Element('width')
#         drawingProperty.text=str(self.canvas.winfo_width())
#         drawingPropertiesElementList.append(drawingProperty)
#         drawingProperty=et.Element('height')
#         drawingProperty.text=str(self.canvas.winfo_height())
#         drawingPropertiesElementList.append(drawingProperty)
#         drawingProperty=et.Element('geometry')
#         drawingProperty.text=self.parent.root.geometry()
#         drawingPropertiesElementList.append(drawingProperty)
        drawingPropertiesElement.extend(drawingPropertiesElementList)
        schematicPropertiesElement=self.schematic.xml()
        drawingElement.extend([drawingPropertiesElement,schematicPropertiesElement])
        return drawingElement

class PySIAppHeadless(object):
    def __init__(self):
        # make absolutely sure the directory of this file is the first in the
        # python path
        thisFileDir=os.path.dirname(os.path.realpath(__file__))
        sys.path=[thisFileDir]+sys.path
        self.preferences=Preferences()
        self.installdir=os.path.dirname(os.path.abspath(__file__))
        self.Drawing=DrawingHeadless(self)
        self.calculationProperties=CalculationProperties(self)

    def NullCommand(self):
        pass

    def OpenProjectFile(self,filename):
        if filename is None:
            filename=''
        if isinstance(filename,tuple):
            filename=''
        filename=str(filename)
        if filename=='':
            return False
        try:
            self.fileparts=FileParts(filename)
            os.chdir(self.fileparts.AbsoluteFilePath())
            self.fileparts=FileParts(filename)
            tree=et.parse(self.fileparts.FullFilePathExtension('.xml'))
            root=tree.getroot()
            for child in root:
                if child.tag == 'drawing':
                    self.Drawing.InitFromXml(child)
                elif child.tag == 'calculation_properties':
                    self.calculationProperties.InitFromXml(child, self)
        except:
            return False
        return True

    def SaveProjectToFile(self,filename):
        self.fileparts=FileParts(filename)
        os.chdir(self.fileparts.AbsoluteFilePath())
        self.fileparts=FileParts(filename)
        projectElement=et.Element('Project')
        drawingElement=self.Drawing.xml()
        calculationPropertiesElement=self.calculationProperties.xml()
        projectElement.extend([drawingElement,calculationPropertiesElement])
        et.ElementTree(projectElement).write(filename)

    def config(self,cursor=None):
        pass

    def CalculateSParameters(self):
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity as si
        cacheFileName=None
        if self.preferences.GetValue('Cache.CacheResults'):
            cacheFileName=self.fileparts.FileNameTitle()
        spnp=si.p.SystemSParametersNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.calculationProperties.endFrequency,
                self.calculationProperties.frequencyPoints),
                cacheFileName=cacheFileName)
        spnp.AddLines(netList)
        try:
            sp=spnp.SParameters()
        except si.PySIException as e:
            return None
        return (sp,self.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'))

    def Simulate(self):
        netList=self.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity as si
        fd=si.fd.EvenlySpacedFrequencyList(
            self.calculationProperties.endFrequency,
            self.calculationProperties.frequencyPoints)
        cacheFileName=None
        if self.preferences.GetValue('Cache.CacheResults'):
            cacheFileName=self.fileparts.FileNameTitle()
        snp=si.p.SimulatorNumericParser(fd,cacheFileName=cacheFileName)
        snp.AddLines(netListText)
        try:
            transferMatrices=snp.TransferMatrices()
        except si.PySIException as e:
            return None

        outputWaveformLabels=netList.OutputNames()

        try:
            inputWaveformList=self.Drawing.schematic.InputWaveforms()
            sourceNames=netList.SourceNames()
        except si.PySIException as e:
            return None

        transferMatricesProcessor=si.td.f.TransferMatricesProcessor(transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='Linear'

        try:
            outputWaveformList = transferMatricesProcessor.ProcessWaveforms(inputWaveformList)
        except si.PySIException as e:
            return None

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = outputWaveformLabels[outputWaveformIndex]
            for device in self.Drawing.schematic.deviceList:
                if device['type'].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput']:
                    if device['reference'].GetValue() == outputWaveformLabel:
                        # probes may have different kinds of gain specified
                        gainProperty = device['gain']
                        if gainProperty is None:
                            gainProperty = device['transresistance']
                        gain=gainProperty.GetValue()
                        offset=device['offset'].GetValue()
                        delay=device['delay'].GetValue()
                        if gain != 1.0 or offset != 0.0 or delay != 0.0:
                            outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,wf.td.K,self.calculationProperties.userSampleRate))
                for wf in outputWaveformList]
        return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)

    def VirtualProbe(self):
        netList=self.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity as si
        cacheFileName=None
        if self.preferences.GetValue('Cache.CacheResults'):
            cacheFileName=self.fileparts.FileNameTitle()
        snp=si.p.VirtualProbeNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.calculationProperties.endFrequency,
                self.calculationProperties.frequencyPoints),
            cacheFileName=cacheFileName)
        snp.AddLines(netListText)       
        try:
            transferMatrices=snp.TransferMatrices()
        except si.PySIException as e:
            return None

        transferMatricesProcessor=si.td.f.TransferMatricesProcessor(transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='Linear'

        try:
            inputWaveformList=self.Drawing.schematic.InputWaveforms()
            sourceNames=netList.MeasureNames()
        except si.PySIException as e:
            return None

        try:
            outputWaveformList = transferMatricesProcessor.ProcessWaveforms(inputWaveformList)
        except si.PySIException as e:
            return None

        outputWaveformLabels=netList.OutputNames()

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = outputWaveformLabels[outputWaveformIndex]
            for device in self.Drawing.schematic.deviceList:
                if device['type'].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput']:
                    if device['reference'].GetValue() == outputWaveformLabel:
                        # probes may have different kinds of gain specified
                        gainProperty = device['gain']
                        if gainProperty is None:
                            gainProperty = device['transresistance']
                        gain=gainProperty.GetValue()
                        offset=device['offset'].GetValue()
                        delay=device['delay'].GetValue()
                        if gain != 1.0 or offset != 0.0 or delay != 0.0:
                            outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,wf.td.K,self.calculationProperties.userSampleRate))
                for wf in outputWaveformList]
        return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)

    def Deembed(self):
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity as si
        cacheFileName=None
        if self.preferences.GetValue('Cache.CacheResults'):
            cacheFileName=self.fileparts.FileNameTitle()
        dnp=si.p.DeembedderNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.calculationProperties.endFrequency,
                self.calculationProperties.frequencyPoints),
                cacheFileName=cacheFileName)
        dnp.AddLines(netList)

        try:
            sp=dnp.Deembed()
        except si.PySIException as e:
            return None

        unknownNames=dnp.m_sd.UnknownNames()
        if len(unknownNames)==1:
            sp=[sp]

        return (unknownNames,sp)

        filename=[]
        for u in range(len(unknownNames)):
            extension='.s'+str(sp[u].m_P)+'p'
            filename=unknownNames[u]+extension
            if self.fileparts.filename != '':
                filename.append(self.fileparts.filename+'_'+filename)
        return (unknownNames,sp,filename)
