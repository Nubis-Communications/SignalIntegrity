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
import sys

if sys.version_info.major < 3:
    import Tkinter as tk
else:
    import tkinter as tk

import os

from SignalIntegrity.App.Files import FileParts
from SignalIntegrity.App.Schematic import Schematic
from SignalIntegrity.App.Preferences import Preferences
from SignalIntegrity.App.ProjectFile import ProjectFile,CalculationProperties
from SignalIntegrity.App.TikZ import TikZ

import SignalIntegrity.App.Project

class ProjectStack(object):
    def __init__(self):
        self.stack=[]
    def Push(self):
        import copy
        ProjectCopy=copy.deepcopy(SignalIntegrity.App.Project)
        cwdCopy=os.getcwd()
        self.stack.append((ProjectCopy,cwdCopy))
        #print('pushed - stack depth: ',len(self.stack))
        return len(self.stack)
    def Pull(self,level=0):
        import copy
        ProjectCopy,cwdCopy=self.stack[level-1]
        SignalIntegrity.App.Project=copy.deepcopy(ProjectCopy)
        os.chdir(cwdCopy)
        self.stack=self.stack[:level-1]
        #print('pulled - stack depth: ',len(self.stack))
        return self

class DrawingHeadless(object):
    def __init__(self,parent):
        self.parent=parent
        self.canvas = TikZ()
        self.schematic = Schematic()
    def DrawSchematic(self,canvas=None):
        if canvas==None:
            canvas=self.canvas
        if SignalIntegrity.App.Project is None:
            return
        drawingPropertiesProject=SignalIntegrity.App.Project['Drawing.DrawingProperties']
        grid=drawingPropertiesProject['Grid']
        originx=drawingPropertiesProject['Originx']
        originy=drawingPropertiesProject['Originy']
        devicePinConnectedList=self.schematic.DevicePinConnectedList()
        foundAPort=False
        foundASource=False
        foundAnOutput=False
        foundSomething=False
        foundAMeasure=False
        foundAStim=False
        foundAnUnknown=False
        foundASystem=False
        for deviceIndex in range(len(self.schematic.deviceList)):
            device = self.schematic.deviceList[deviceIndex]
            foundSomething=True
            devicePinsConnected=devicePinConnectedList[deviceIndex]
            device.DrawDevice(canvas,grid,originx,originy,devicePinsConnected)
            deviceType = device['partname'].GetValue()
            if  deviceType == 'Port':
                foundAPort = True
            elif deviceType in ['Output','DifferentialVoltageOutput','CurrentOutput']:
                foundAnOutput = True
            elif deviceType == 'Stim':
                foundAStim = True
            elif deviceType == 'Measure':
                foundAMeasure = True
            elif deviceType == 'System':
                foundASystem = True
            elif deviceType == 'Unknown':
                foundAnUnknown = True
            elif device.netlist['DeviceName'] in ['voltagesource','currentsource']:
                foundASource = True
        for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
            foundSomething=True
            wireProject.DrawWire(canvas,grid,originx,originy)
        for dot in self.schematic.DotList():
            size=grid/8
            canvas.create_oval((dot[0]+originx)*grid-size,(dot[1]+originy)*grid-size,
                                    (dot[0]+originx)*grid+size,(dot[1]+originy)*grid+size,
                                    fill='black',outline='black')
        self.foundSomething=foundSomething
        self.canSimulate = foundASource and foundAnOutput and not foundAPort and not foundAStim and not foundAMeasure and not foundAnUnknown and not foundASystem
        self.canCalculateSParameters = foundAPort and not foundAnOutput and not foundAMeasure and not foundAStim and not foundAnUnknown and not foundASystem
        self.canVirtualProbe = foundAStim and foundAnOutput and foundAMeasure and not foundAPort and not foundASource and not foundAnUnknown and not foundASystem
        self.canDeembed = foundAPort and foundAnUnknown and foundASystem and not foundAStim and not foundAMeasure and not foundAnOutput
        self.canCalculate = self.canSimulate or self.canCalculateSParameters or self.canVirtualProbe or self.canDeembed
        return canvas
    def InitFromProject(self):
        self.schematic = Schematic()
        self.schematic.InitFromProject()

class SignalIntegrityAppHeadless(object):
    projectStack = ProjectStack()
    def __init__(self):
        # make absolutely sure the directory of this file is the first in the
        # python path
        thisFileDir=os.path.dirname(os.path.realpath(__file__))
        sys.path=[thisFileDir]+sys.path
        SignalIntegrity.App.Preferences=Preferences()
        SignalIntegrity.App.InstallDir=os.path.dirname(os.path.abspath(__file__))
        self.Drawing=DrawingHeadless(self)

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
            SignalIntegrity.App.Project=ProjectFile().Read(self.fileparts.FullFilePathExtension('.si'))
            self.Drawing.InitFromProject()
        except:
            return False
        self.Drawing.schematic.Consolidate()
        for device in self.Drawing.schematic.deviceList:
            device.selected=False
        for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
            for vertexProject in wireProject['Vertices']:
                vertexProject['Selected']=False
        return True

    def SaveProjectToFile(self,filename):
        self.fileparts=FileParts(filename)
        os.chdir(self.fileparts.AbsoluteFilePath())
        self.fileparts=FileParts(filename)
        SignalIntegrity.App.Project.Write(self,filename)

    def SaveProject(self):
        if self.fileparts.filename=='':
            return
        filename=self.fileparts.AbsoluteFilePath()+'/'+self.fileparts.FileNameWithExtension(ext='.si')
        self.SaveProjectToFile(filename)

    def NetListText(self):
        return self.Drawing.schematic.NetList().Text()+SignalIntegrity.App.Project['PostProcessing'].NetListLines()

    def config(self,cursor=None):
        pass

    def CalculateSParameters(self):
        netListText=self.NetListText()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        spnp=si.p.SystemSParametersNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']
            ),
                cacheFileName=cacheFileName)
        spnp.AddLines(netListText)
        try:
            sp=spnp.SParameters()
        except si.SignalIntegrityException as e:
            return None
        return (sp,self.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'))

    def Simulate(self):
        netList=self.Drawing.schematic.NetList()
        netListText=self.NetListText()
        import SignalIntegrity.Lib as si
        fd=si.fd.EvenlySpacedFrequencyList(
            SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
            SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints'])
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
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
        si.td.wf.Waveform.adaptionStrategy='SinX' if SignalIntegrity.App.Preferences['Calculation.UseSinX'] else 'Linear'

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
        userSampleRate=SignalIntegrity.App.Project['CalculationProperties.UserSampleRate']
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                for wf in outputWaveformList]
        return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)

    def VirtualProbe(self):
        netList=self.Drawing.schematic.NetList()
        netListText=self.NetListText()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        snp=si.p.VirtualProbeNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']
            ),
            cacheFileName=cacheFileName)
        snp.AddLines(netListText)       
        try:
            transferMatrices=snp.TransferMatrices()
        except si.SignalIntegrityException as e:
            return None

        transferMatricesProcessor=si.td.f.TransferMatricesProcessor(transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='SinX' if SignalIntegrity.App.Preferences['Calculation.UseSinX'] else 'Linear'

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
        userSampleRate=SignalIntegrity.App.Project['CalculationProperties.UserSampleRate']
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                for wf in outputWaveformList]
        return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)

    def Deembed(self):
        netListText=self.NetListText()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        dnp=si.p.DeembedderNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']
            ),
                cacheFileName=cacheFileName)
        dnp.AddLines(netListText)

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

    def Device(self,ref):
        """
        accesses a device by it's reference string
        @param ref string reference designator
        @return device if found otherwise None

        Some examples of how to use this (proj is a project name)
        gain=proj.Device('U1')['gain']['Value']
        proj.Device('U1')['gain']['Value']=gain
        """
        devices=self.Drawing.schematic.deviceList
        for device in devices:
            if device['ref']['Value']==ref:
                return device
        return None
def ProjectSParameters(filename):
    level=SignalIntegrityAppHeadless.projectStack.Push()
    sp=None
    try:
        app=SignalIntegrityAppHeadless()
        if app.OpenProjectFile(os.path.realpath(filename)):
            app.Drawing.DrawSchematic()
            if app.Drawing.canCalculateSParameters:
                result=app.CalculateSParameters()
                if not result is None:
                    sp=result[0]
            elif app.Drawing.canDeembed:
                result=app.Deembed()
                if not result is None:
                    sp=result[1][0]
    except:
        pass
    SignalIntegrityAppHeadless.projectStack.Pull(level)
    return sp

def ProjectWaveform(filename,wfname):
    level=SignalIntegrityAppHeadless.projectStack.Push()
    wf=None
    try:
        app=SignalIntegrityAppHeadless()
        if app.OpenProjectFile(os.path.realpath(filename)):
            app.Drawing.DrawSchematic()
            result=None
            if app.Drawing.canSimulate:
                result=app.Simulate()
            elif app.Drawing.canVirtualProbe:
                result=app.VirtualProbe()
            if not result is None:
                (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)=result
                if wfname in outputWaveformLabels:
                    wf=outputWaveformList[outputWaveformLabels.index(wfname)]
    except:
        pass
    SignalIntegrityAppHeadless.projectStack.Pull(level)
    return wf

def ProjectCalibration(filename):
    level=SignalIntegrityAppHeadless.projectStack.Push()
    result=None
    try:
        app=SignalIntegrityAppHeadless()
        if app.OpenProjectFile(os.path.realpath(filename)):
            app.Drawing.DrawSchematic()
            if app.Drawing.canCalculateErrorTerms:
                result=app.CalculateErrorTerms()
    except:
        pass
    SignalIntegrityAppHeadless.projectStack.Pull(level)
    return result

def ProjectModificationTime(modificationTimeDict,fileName):
    #print(os.path.abspath(fileName))
    if modificationTimeDict == None:
        return None
    if os.path.abspath(fileName) in [file['name'] for file in modificationTimeDict]:
        if modificationTimeDict[[file['name'] for file in modificationTimeDict].index(os.path.abspath(fileName))]['traversed']==False:
            # this is a recursion problem
            return None
        else:
            return(modificationTimeDict)
    elif not fileName.endswith('.si'):
        modificationTimeDict.append({'name':os.path.abspath(fileName),'time':os.path.getmtime(os.path.abspath(fileName)),'traversed':True})
    else:
        modificationTimeDict.append({'name':os.path.abspath(fileName),'time':os.path.getmtime(os.path.abspath(fileName)),'traversed':False})
        filenamenoext=FileParts(fileName).FileNameTitle()
        for postfix in ['','_DUTSParameters','_TransferMatrices']:
            for cacheName in ['SParameters','TransferMatrices','Calibration']:
                cacheFileName=FileParts(filenamenoext+postfix+'_cached'+cacheName).FileNameWithExtension('.p')
                if os.path.exists(cacheFileName):
                    modificationTimeDict=ProjectModificationTime(modificationTimeDict,cacheFileName)
        level=SignalIntegrityAppHeadless.projectStack.Push()
        result=0
        try:
            app=SignalIntegrityAppHeadless()
            if not app.OpenProjectFile(os.path.realpath(fileName)):
                raise ValueError
            app.Drawing.DrawSchematic()
            if not app.Drawing.canCalculate:
                raise ValueError
            deviceList=app.Drawing.schematic.deviceList
            for device in deviceList:
                propertiesList = device.propertiesList
                for property in propertiesList:
                    if property['Type']=='file':
                        filename=property['Value']
                        if filename.endswith('.si'):
                            modificationTimeDict=ProjectModificationTime(modificationTimeDict,filename)
                            filenamenoext=FileParts(filename).FileNameTitle()
                            for postfix in ['','_DUTSParameters','_TransferMatrices']:
                                for cacheName in ['SParameters','TransferMatrices','Calibration']:
                                    cacheFileName=FileParts(filenamenoext+postfix+'_cached'+cacheName).FileNameWithExtension('.p')
                                    if os.path.exists(cacheFileName):
                                        modificationTimeDict=ProjectModificationTime(modificationTimeDict,cacheFileName)
                        else:
                            if '.' in filename:
                                modificationTimeDict.append({'name':os.path.abspath(filename),
                                                             'time':os.path.getmtime(os.path.abspath(filename)),
                                                             'traversed':True})
                        if modificationTimeDict==None:
                            raise ValueError
        except:
            result=None
        SignalIntegrityAppHeadless.projectStack.Pull(level)
        if result==None:
            return result
    modificationTimeDict[[file['name'] for file in modificationTimeDict].index(os.path.abspath(fileName))]['traversed']=True
    return modificationTimeDict

