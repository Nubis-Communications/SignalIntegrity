"""
SignalIntegrityAppHeadless.py
"""
# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import os
import sys

import xml.etree.ElementTree as et

import sys
if sys.version_info.major < 3:
    from Tkinter import ALL
else:
    from tkinter import ALL

from SignalIntegrity.App.CalculationProperties import CalculationProperties
from SignalIntegrity.App.Files import FileParts
from SignalIntegrity.App.Schematic import Schematic
from SignalIntegrity.App.Preferences import Preferences

class DrawingHeadless(object):
    def __init__(self,parent):
        self.parent=parent
        self.canvas = None
        self.grid=32.
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
        if not hasattr(self.parent,'project'):
            return
        if self.parent.project is None:
            return
        for wireProject in self.parent.project.GetValue('Drawing.Schematic.Wires'):
            Wire().InitFromProject(wireProject).DrawWire(canvas,self.grid,self.originx,self.originy)
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

    def InitFromProject(self,project):
        drawingProperties=project.GetValue('Drawing.DrawingProperties')
        self.grid=drawingProperties.GetValue('Grid')
        self.originx=drawingProperties.GetValue('Originx')
        self.originy=drawingProperties.GetValue('Originy')
        self.schematic = Schematic()
        self.schematic.InitFromProject(project)

class SignalIntegrityAppHeadless(object):
    def __init__(self):
        # make absolutely sure the directory of this file is the first in the
        # python path
        thisFileDir=os.path.dirname(os.path.realpath(__file__))
        sys.path=[thisFileDir]+sys.path

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
            return

        try:
            self.fileparts=FileParts(filename)
            os.chdir(self.fileparts.AbsoluteFilePath())
            self.fileparts=FileParts(filename)

            if self.fileparts.fileext == '.xml':
                self.OpenProjectFileLegacy(self.fileparts.FullFilePathExtension('.xml'))
            else:
                self.project=ProjectFile().Read(self.fileparts.FullFilePathExtension('.pysi_project'),self.Drawing)
        except:
            return False
        self.Drawing.schematic.Consolidate()
        for device in self.Drawing.schematic.deviceList:
            device.selected=False
        for wireProject in self.Drawing.schematic.project.GetValue('Drawing.Schematic.Wires'):
            for vertexProject in wireProject.GetValue('Vertex'):
                vertexProject.SetValue('Selected',False)
        return True

    # Legacy File Format
    def OpenProjectFileLegacy(self,oldfilename):
            import xml.etree.ElementTree as et
            tree=et.parse(oldfilename)
            root=tree.getroot()
            for child in root:
                if child.tag == 'drawing':
                    self.Drawing.InitFromXml(child)
                elif child.tag == 'calculation_properties':
                    from CalculationProperties import CalculationProperties
                    self.calculationProperties=CalculationProperties(self)
                    self.calculationProperties.InitFromXml(child, self)
            project=ProjectFile()
            project.SetValue('Drawing.DrawingProperties.Grid',self.Drawing.grid)
            project.SetValue('Drawing.DrawingProperties.Originx',self.Drawing.originx)
            project.SetValue('Drawing.DrawingProperties.Originy',self.Drawing.originy)
            from ProjectFile import DeviceConfiguration
            project.SetValue('Drawing.Schematic.Devices',[DeviceConfiguration() for _ in range(len(self.Drawing.schematic.deviceList))])
            for d in range(len(project.GetValue('Drawing.Schematic.Devices'))):
                deviceProject=project.GetValue('Drawing.Schematic.Devices')[d]
                device=self.Drawing.schematic.deviceList[d]
                deviceProject.SetValue('ClassName',device.__class__.__name__)
                partPictureProject=deviceProject.GetValue('PartPicture')
                partPicture=device.partPicture
                partPictureProject.SetValue('ClassName',partPicture.partPictureClassList[partPicture.partPictureSelected])
                partPictureProject.SetValue('Origin',partPicture.current.origin)
                partPictureProject.SetValue('Orientation',partPicture.current.orientation)
                partPictureProject.SetValue('MirroredVertically',partPicture.current.mirroredVertically)
                partPictureProject.SetValue('MirroredHorizontally',partPicture.current.mirroredHorizontally)
                deviceProject.SetValue('PartProperties',device.propertiesList)
            from ProjectFile import WireConfiguration
            project.SetValue('Drawing.Schematic.Wires',[WireConfiguration() for _ in range(len(self.Drawing.schematic.wireList))])
            for w in range(len(project.GetValue('Drawing.Schematic.Wires'))):
                wireProject=project.GetValue('Drawing.Schematic.Wires')[w]
                wire=self.Drawing.schematic.wireList[w]
                from ProjectFile import VertexConfiguration
                wireProject.SetValue('Vertex',[VertexConfiguration() for vertex in wire])
                for v in range(len(wireProject.GetValue('Vertex'))):
                    vertexProject=wireProject.GetValue('Vertex')[v]
                    vertex=wire[v]
                    vertexProject.SetValue('Coord',vertex.coord)
            project.SetValue('CalculationProperties.EndFrequency',self.calculationProperties.endFrequency)
            project.SetValue('CalculationProperties.FrequencyPoints',self.calculationProperties.frequencyPoints)
            project.SetValue('CalculationProperties.UserSampleRate',self.calculationProperties.userSampleRate)
            # calculate certain calculation properties
            project.SetValue('CalculationProperties.BaseSampleRate', project.GetValue('CalculationProperties.EndFrequency')*2)
            project.SetValue('CalculationProperties.TimePoints',project.GetValue('CalculationProperties.FrequencyPoints')*2)
            project.SetValue('CalculationProperties.FrequencyResolution', project.GetValue('CalculationProperties.EndFrequency')/project.GetValue('CalculationProperties.FrequencyPoints'))
            project.SetValue('CalculationProperties.ImpulseResponseLength',1./project.GetValue('CalculationProperties.FrequencyResolution'))
            self.project=project
            del self.calculationProperties
            self.Drawing.InitFromProject(self.project)
            return self

    def SaveProjectToFile(self,filename):
        self.fileparts=FileParts(filename)
        os.chdir(self.fileparts.AbsoluteFilePath())
        self.fileparts=FileParts(filename)
        self.project.Write(filename,self)

    def SaveProject(self):
        if self.fileparts.filename=='':
            return
        filename=self.fileparts.AbsoluteFilePath()+'/'+self.fileparts.FileNameWithExtension(ext='.pysi_project')
        self.SaveProjectToFile(filename)

    def config(self,cursor=None):
        pass

    def CalculateSParameters(self):
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if self.preferences.GetValue('Cache.CacheResults'):
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=self.preferences.GetValue('Calculation.TrySVD')
        spnp=si.p.SystemSParametersNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.project.GetValue('CalculationProperties.EndFrequency'),
                self.project.GetValue('CalculationProperties.FrequencyPoints')
            ),
                cacheFileName=cacheFileName)
        spnp.AddLines(netList)
        try:
            sp=spnp.SParameters()
        except si.SignalIntegrityException as e:
            return None
        return (sp,self.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'))

    def Simulate(self):
        netList=self.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if self.preferences.GetValue('Cache.CacheResults'):
            cacheFileName=self.fileparts.FileNameTitle()
        fd=si.fd.EvenlySpacedFrequencyList(
            self.project.GetValue('CalculationProperties.EndFrequency'),
            self.project.GetValue('CalculationProperties.FrequencyPoints'))
        si.sd.Numeric.trySVD=self.preferences.GetValue('Calculation.TrySVD')
        snp=si.p.SimulatorNumericParser(fd,cacheFileName=cacheFileName)
        snp.AddLines(netListText)
        try:
            transferMatrices=snp.TransferMatrices()
        except si.SignalIntegrityException as e:
            return None

        outputWaveformLabels=netList.OutputNames()

        try:
            inputWaveformList=self.Drawing.schematic.InputWaveforms()
            sourceNames=netList.SourceNames()
        except si.SignalIntegrityException as e:
            return None

        transferMatricesProcessor=si.td.f.TransferMatricesProcessor(transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='Linear'

        try:
            outputWaveformList = transferMatricesProcessor.ProcessWaveforms(inputWaveformList)
        except si.SignalIntegrityException as e:
            return None

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = outputWaveformLabels[outputWaveformIndex]
            for device in self.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput']:
                    if device['ref'].GetValue() == outputWaveformLabel:
                        # probes may have different kinds of gain specified
                        gainProperty = device['gain']
                        gain=gainProperty.GetValue()
                        offset=device['offset'].GetValue()
                        delay=device['td'].GetValue()
                        if gain != 1.0 or offset != 0.0 or delay != 0.0:
                            outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,wf.td.K,self.project.GetValue('CalculationProperties.UserSampleRate')))
                for wf in outputWaveformList]
        return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)

    def VirtualProbe(self):
        netList=self.Drawing.schematic.NetList()
        netListText=netList.Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if self.preferences.GetValue('Cache.CacheResults'):
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=self.preferences.GetValue('Calculation.TrySVD')
        snp=si.p.VirtualProbeNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.project.GetValue('CalculationProperties.EndFrequency'),
                self.project.GetValue('CalculationProperties.FrequencyPoints')
            ),
            cacheFileName=cacheFileName)
        snp.AddLines(netListText)       
        try:
            transferMatrices=snp.TransferMatrices()
        except si.SignalIntegrityException as e:
            return None

        transferMatricesProcessor=si.td.f.TransferMatricesProcessor(transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='Linear'

        try:
            inputWaveformList=self.Drawing.schematic.InputWaveforms()
            sourceNames=netList.MeasureNames()
        except si.SignalIntegrityException as e:
            return None

        try:
            outputWaveformList = transferMatricesProcessor.ProcessWaveforms(inputWaveformList)
        except si.SignalIntegrityException as e:
            return None

        outputWaveformLabels=netList.OutputNames()

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = outputWaveformLabels[outputWaveformIndex]
            for device in self.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput']:
                    if device['ref'].GetValue() == outputWaveformLabel:
                        # probes may have different kinds of gain specified
                        gainProperty = device['gain']
                        gain=gainProperty.GetValue()
                        offset=device['offset'].GetValue()
                        delay=device['td'].GetValue()
                        if gain != 1.0 or offset != 0.0 or delay != 0.0:
                            outputWaveform = outputWaveform.DelayBy(delay)*gain+offset
                        outputWaveformList[outputWaveformIndex]=outputWaveform
                        break
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,wf.td.K,self.project.GetValue('CalculationProperties.UserSampleRate')))
                for wf in outputWaveformList]
        return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)

    def Deembed(self):
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if self.preferences.GetValue('Cache.CacheResults'):
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=self.preferences.GetValue('Calculation.TrySVD')
        dnp=si.p.DeembedderNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                self.project.GetValue('CalculationProperties.EndFrequency'),
                self.project.GetValue('CalculationProperties.FrequencyPoints')
            ),
                cacheFileName=cacheFileName)
        dnp.AddLines(netList)

        try:
            sp=dnp.Deembed()
        except si.SignalIntegrityException as e:
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
