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
from SignalIntegrity.App.EyeDiagram import EyeDiagram

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
        foundACalibration=False
        foundANetworkAnalyzerModel=False
        for deviceIndex in range(len(self.schematic.deviceList)):
            device = self.schematic.deviceList[deviceIndex]
            foundSomething=True
            devicePinsConnected=devicePinConnectedList[deviceIndex]
            device.DrawDevice(canvas,grid,originx,originy,devicePinsConnected)
            deviceType = device['partname'].GetValue()
            if  deviceType == 'Port':
                foundAPort = True
            elif deviceType in ['Output','DifferentialVoltageOutput','CurrentOutput','EyeProbe','DifferentialEyeProbe']:
                foundAnOutput = True
            elif deviceType == 'Stim':
                foundAStim = True
            elif deviceType == 'Measure':
                foundAMeasure = True
            elif deviceType == 'System':
                foundASystem = True
            elif deviceType == 'Unknown':
                foundAnUnknown = True
            elif device.netlist['DeviceName'] in ['networkanalyzerport','voltagesource','currentsource']:
                foundASource = True
            elif device.netlist['DeviceName'] == 'calibration':
                foundACalibration=True
            elif deviceType == 'NetworkAnalyzerModel':
                foundANetworkAnalyzerModel=True
        for wireProject in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
            foundSomething=True
            wireProject.DrawWire(canvas,grid,originx,originy)
        for dot in self.schematic.DotList():
            size=grid/8
            canvas.create_oval((dot[0]+originx)*grid-size,(dot[1]+originy)*grid-size,
                                    (dot[0]+originx)*grid+size,(dot[1]+originy)*grid+size,
                                    fill='black',outline='black')
        self.foundSomething=foundSomething
        self.canSimulate = foundASource and foundAnOutput and not foundAPort and not foundAStim and not foundAMeasure and not foundAnUnknown and not foundASystem and not foundACalibration
        self.canCalculateSParameters = foundAPort and not foundAnOutput and not foundAMeasure and not foundAStim and not foundAnUnknown and not foundASystem and not foundACalibration
        self.canVirtualProbe = foundAStim and foundAnOutput and foundAMeasure and not foundAPort and not foundASource and not foundAnUnknown and not foundASystem and not foundACalibration
        self.canDeembed = foundAPort and foundAnUnknown and foundASystem and not foundAStim and not foundAMeasure and not foundAnOutput and not foundACalibration
        self.canCalculateErrorTerms = foundACalibration and not foundASource and not foundAnOutput and not foundAPort and not foundAStim and not foundAMeasure and not foundAnUnknown and not foundASystem
        self.canSimulateNetworkAnalyzerModel = foundANetworkAnalyzerModel and not foundAPort and not foundAnOutput and not foundAMeasure and not foundAStim and not foundAnUnknown and not foundASystem and not foundACalibration
        self.canCalculateSParametersFromNetworkAnalyzerModel = self.canSimulateNetworkAnalyzerModel
        self.canCalculate = self.canSimulate or self.canCalculateSParameters or self.canVirtualProbe or self.canDeembed or self.canCalculateErrorTerms or self.canSimulateNetworkAnalyzerModel or self.canCalculateSParametersFromNetworkAnalyzerModel
        self.canGenerateTransferMatrices = self.canSimulate or self.canVirtualProbe
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

    def CalculateSParameters(self,callback=None):
        import SignalIntegrity.Lib as si
        if not hasattr(self.Drawing,'canCalculate'):
            self.Drawing.DrawSchematic()
        if self.Drawing.canCalculateSParametersFromNetworkAnalyzerModel:
            try:
                sp=self.SimulateNetworkAnalyzerModel(SParameters=True)
            except si.SignalIntegrityException as e:
                return None
            return (sp,self.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'))
        elif not self.Drawing.canCalculateSParameters:
            return None
        netListText=self.NetListText()
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
        if not callback == None:
            spnp.InstallCallback(callback)
        spnp.AddLines(netListText)
        try:
            sp=spnp.SParameters()
        except si.SignalIntegrityException as e:
            return None
        return (sp,self.fileparts.FullFilePathExtension('s'+str(sp.m_P)+'p'))

    def Simulate(self,callback=None,TransferMatricesOnly=False,EyeDiagrams=False):
        if not hasattr(self.Drawing,'canCalculate'):
            self.Drawing.DrawSchematic()
        if self.Drawing.canSimulateNetworkAnalyzerModel:
            return self.SimulateNetworkAnalyzerModel(SParameters=False)
        elif not self.Drawing.canSimulate:
            return None
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
        if not callback == None:
            snp.InstallCallback(callback)
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

        if TransferMatricesOnly:
            return (sourceNames,outputWaveformLabels,transferMatrices)

        diresp=None
        for r in range(len(outputWaveformLabels)):
            for c in range(len(inputWaveformList)):
                if outputWaveformLabels[r][:3]=='di/' or outputWaveformLabels[r][:2]=='d/':
                    if diresp == None:
                        diresp=si.fd.Differentiator(fd).Response()
                    #print 'differentiate: '+outputWaveformLabels[r]
                    for n in range(len(transferMatrices)):
                        transferMatrices[n][r][c]=transferMatrices[n][r][c]*diresp[n]

        transferMatricesProcessor=si.td.f.TransferMatricesProcessor(transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='SinX' if SignalIntegrity.App.Preferences['Calculation.UseSinX'] else 'Linear'

        try:
            outputWaveformList = transferMatricesProcessor.ProcessWaveforms(inputWaveformList)
        except si.SignalIntegrityException as e:
            return None

        for r in range(len(outputWaveformList)):
            if outputWaveformLabels[r][:3]=='di/' or outputWaveformLabels[r][:2]=='i/':
                #print 'integrate: '+outputWaveformLabels[r]
                outputWaveformList[r]=outputWaveformList[r].Integral()

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = outputWaveformLabels[outputWaveformIndex]
            for device in self.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput','EyeProbe','DifferentialEyeProbe']:
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
        if not EyeDiagrams:
            return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)

        # gather up the eye probes and create a dialog for each one
        eyeDiagramDict=[]
        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = outputWaveformLabels[outputWaveformIndex]
            for device in self.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['EyeProbe','DifferentialEyeProbe']:
                    if device['ref'].GetValue() == outputWaveformLabel:
                        eyeDict={'Name':outputWaveformLabel,
                                 'BaudRate':device['br'].GetValue(),
                                 'Waveform':outputWaveformList[outputWaveformLabels.index(outputWaveformLabel)]}
                        eyeDiagramDict.append(eyeDict)
                        break

        eyeDiagramLabels=[eye['Name'] for eye in eyeDiagramDict]
        eyeDiagramImages=[]
        eyeDiagramBitmaps=[]
        for eye in eyeDiagramDict:
            eyeDiagram=EyeDiagram(None,headless=True)
            eyeDiagram.prbswf=eye['Waveform']
            eyeDiagram.baudrate=eye['BaudRate']
            eyeDiagram.CalculateEyeDiagram()
            eyeDiagramImages.append(eyeDiagram.img)
            eyeDiagramBitmaps.append(eyeDiagram.rawBitmap)
        return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList,eyeDiagramLabels,eyeDiagramImages,eyeDiagramBitmaps)

    def VirtualProbe(self,callback=None,TransferMatricesOnly=False,EyeDiagrams=False):
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
        if not callback == None:
            snp.InstallCallback(callback)
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

        if TransferMatricesOnly:
            return (sourceNames,outputWaveformLabels,transferMatrices)

        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = outputWaveformLabels[outputWaveformIndex]
            for device in self.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['Output','DifferentialVoltageOutput','CurrentOutput','EyeProbe','DifferentialEyeProbe']:
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
        if not EyeDiagrams:
            return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)

        # gather up the eye probes and create a dialog for each one
        eyeDiagramDict=[]
        for outputWaveformIndex in range(len(outputWaveformList)):
            outputWaveform=outputWaveformList[outputWaveformIndex]
            outputWaveformLabel = self.outputWaveformLabels[outputWaveformIndex]
            for device in self.parent.Drawing.schematic.deviceList:
                if device['partname'].GetValue() in ['EyeProbe','DifferentialEyeProbe']:
                    if device['ref'].GetValue() == outputWaveformLabel:
                        eyeDict={'Name':outputWaveformLabel,
                                 'BaudRate':device['br'].GetValue(),
                                 'Waveform':outputWaveformList[self.outputWaveformLabels.index(outputWaveformLabel)]}
                        eyeDiagramDict.append(eyeDict)
                        break

        eyeDiagramLabels=[eye['Name'] for eye in eyeDiagramDict]
        eyeDiagramImages=[]
        eyeDiagramBitmaps=[]
        for eye in eyeDiagramDict:
            eyeDiagram=EyeDiagram(None,headless=True)
            eyeDiagram.prbswf=eye['Waveform']
            eyeDiagram.baudrate=eye['BaudRate']
            eyeDiagram.CalculateEyeDiagram()
            eyeDiagramImages.append(eyeDiagram.img)
            eyeDiagramBitmaps.append(eyeDiagram.rawBitmap)
        return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList,eyeDiagramLabels,eyeDiagramImages,eyeDiagramBitmaps)

    def TransferParameters(self,callback=None,):
        if not hasattr(self.Drawing,'canGenerateTransferMatrices'):
            self.Drawing.DrawSchematic()
        if not self.Drawing.canGenerateTransferMatrices:
            return None
        if self.Drawing.canSimulate:
            return self.Simulate(callback,TransferMatricesOnly=True)
        elif self.Drawing.canVirtualProbe:
            return self.VirtualProbe(callback,TransferMatricesOnly=True)
        else:
            return None

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

    def CalculateErrorTerms(self):
        if not hasattr(self.Drawing,'canCalculate'):
            self.Drawing.DrawSchematic()
        if not self.Drawing.canCalculateErrorTerms:
            return None
        netList=self.Drawing.schematic.NetList()
        netListText=self.NetListText()
        import SignalIntegrity.Lib as si
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.fileparts.FileNameTitle()
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        etnp=si.p.CalibrationNumericParser(
            si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints']),
            cacheFileName=cacheFileName)
        etnp.AddLines(netListText)
        try:
            cal=etnp.CalculateCalibration()
        except si.SignalIntegrityException as e:
            return None
        return (cal,self.fileparts.FullFilePathExtension('cal'))

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
            if device['ref'] != None:
                if device['ref']['Value'] == ref:
                    return device
        return None

    def SimulateNetworkAnalyzerModel(self,SParameters=False):
        netList=self.Drawing.schematic.NetList().Text()
        import SignalIntegrity.Lib as si
        fd=si.fd.EvenlySpacedFrequencyList(
                SignalIntegrity.App.Project['CalculationProperties.EndFrequency'],
                SignalIntegrity.App.Project['CalculationProperties.FrequencyPoints'])
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.fileparts.FileNameTitle()+'_DUTSParameters'
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        spnp=si.p.DUTSParametersNumericParser(fd,cacheFileName=cacheFileName)
        spnp.AddLines(netList)
        try:
            (DUTSp,NetworkAnalyzerProjectFile)=spnp.SParameters()
        except si.SignalIntegrityException as e:
            return None
        netListText=None
        if NetworkAnalyzerProjectFile != None:
            level=SignalIntegrityAppHeadless.projectStack.Push()
            try:
                app=SignalIntegrityAppHeadless()
                if app.OpenProjectFile(os.path.realpath(NetworkAnalyzerProjectFile)):
                    app.Drawing.DrawSchematic()
                    netList=app.Drawing.schematic.NetList()
                    netListText=netList.Text()
                else:
                    pass
            except:
                pass
            finally:
                SignalIntegrityAppHeadless.projectStack.Pull(level)
        else:
            netList=self.Drawing.schematic.NetList()
            netListText=self.NetListText()

        if netListText==None:
            return None
        cacheFileName=None
        if SignalIntegrity.App.Preferences['Cache.CacheResults']:
            cacheFileName=self.fileparts.FileNameTitle()+'_TransferMatrices'
        si.sd.Numeric.trySVD=SignalIntegrity.App.Preferences['Calculation.TrySVD']
        snp=si.p.NetworkAnalyzerSimulationNumericParser(fd,DUTSp,spnp.NetworkAnalyzerPortConnectionList,cacheFileName=cacheFileName)
        snp.AddLines(netListText)
        level=SignalIntegrityAppHeadless.projectStack.Push()
        try:
            os.chdir(FileParts(os.path.abspath(NetworkAnalyzerProjectFile)).AbsoluteFilePath())
            transferMatrices=snp.TransferMatrices()
        except si.SignalIntegrityException as e:
            return None
        finally:
            SignalIntegrityAppHeadless.projectStack.Pull(level)

        sourceNames=snp.m_sd.SourceVector()

        gdoDict={}

        if NetworkAnalyzerProjectFile != None:
            level=SignalIntegrityAppHeadless.projectStack.Push()
            try:
                app=SignalIntegrityAppHeadless()
                if app.OpenProjectFile(os.path.realpath(NetworkAnalyzerProjectFile)):
                    app.Drawing.DrawSchematic()
                    # get output gain, offset, delay
                    for name in [rdn[2] for rdn in snp.m_sd.pOutputList]:
                        gdoDict[name]={'gain':float(app.Device(name)['gain']['Value']),
                            'offset':float(app.Device(name)['offset']['Value']),'delay':float(app.Device(name)['td']['Value'])}
                    stateList=[app.Device(sourceNames[port])['state']['Value'] for port in range(snp.simulationNumPorts)]
                    self.wflist=[]
                    for driven in range(snp.simulationNumPorts):
                        thiswflist=[]
                        for port in range(snp.simulationNumPorts):
                            app.Device(sourceNames[port])['state']['Value']='on' if port==driven else 'off'
                        for wfIndex in range(len(sourceNames)):
                            thiswflist.append(app.Device(sourceNames[wfIndex]).Waveform())
                        self.wflist.append(thiswflist)
                    for port in range(snp.simulationNumPorts):
                        app.Device(sourceNames[port])['state']['Value']=stateList[port]
                else:
                    pass
            except:
                pass
            finally:
                SignalIntegrityAppHeadless.projectStack.Pull(level)
        else:
            stateList=[app.Device(sourceNames[port])['state']['Value'] for port in range(snp.simulationNumPorts)]
            self.wflist=[]
            for name in [rdn[2] for rdn in snp.m_sd.pOutputList]:
                gdoDict[name]={'gain':float(app.Device()[name]['gain']['Value']),
                    'offset':float(app.Device()[name]['offset']['Value']),'delay':float(app.Device()[name]['td']['Value'])}
            for driven in range(snp.simulationNumPorts):
                thiswflist=[]
                for port in range(snp.simulationNumPorts):
                    app.Device(sourceNames[port])['state']['Value']='on' if port==driven else 'off'
                for wfIndex in range(len(sourceNames)):
                    thiswflist.append(app.Device(sourceNames[wfIndex]).Waveform())
                self.wflist.append(thiswflist)
            for port in range(snp.simulationNumPorts):
                app.Device(sourceNames[port])['state']['Value']=stateList[port]

        self.transferMatriceProcessor=si.td.f.TransferMatricesProcessor(transferMatrices)
        si.td.wf.Waveform.adaptionStrategy='SinX' if SignalIntegrity.App.Preferences['Calculation.UseSinX'] else 'Linear'

        try:
            outputwflist=[]
            for port in range(len(self.wflist)):
                outputwflist.append(self.transferMatriceProcessor.ProcessWaveforms(self.wflist[port],adaptToLargest=True))
        except si.SignalIntegrityException as e:
            return None
        #
        # The list of list of input waveforms have been processed processed, generating a list of list of output waveforms in 
        # self.outputwflist.  The names of the output waveforms are in snp.m_sd.pOutputList.
        #
        outputwflist = [[wf.Adapt(si.td.wf.TimeDescriptor(wf.td[wf.td.IndexOfTime(-5e-9)],fd.TimeDescriptor().K,wf.td.Fs)) for wf in driven] for driven in outputwflist]

        # The port connection list, which is a list of True or False for each port on the network analyzer, is
        # converted to a list of network port indices corresponding to the driven ports.
        #
        portConnections=[]
        for pci in range(len(snp.PortConnectionList)):
            if snp.PortConnectionList[pci]: portConnections.append(pci)

        outputWaveformList=[]
        outputWaveformLabels=[]
        for r in range(len(outputwflist)):
            wflist=outputwflist[r]
            for c in range(len(wflist)):
                wf=wflist[c]; wfName=snp.m_sd.pOutputList[c][2]
                gain=gdoDict[wfName]['gain']; offset=gdoDict[wfName]['offset']; delay=gdoDict[wfName]['delay']
                if gain != 1.0 or offset != 0.0 or delay != 0.0:
                    wf = wf.DelayBy(delay)*gain+offset
                outputWaveformList.append(wf)
                outputWaveformLabels.append(snp.m_sd.pOutputList[c][2]+str(portConnections[r]+1))

        userSampleRate=SignalIntegrity.App.Project['CalculationProperties.UserSampleRate']
        outputWaveformList = [wf.Adapt(
            si.td.wf.TimeDescriptor(wf.td.H,int(wf.td.K*userSampleRate/wf.td.Fs),userSampleRate))
                for wf in outputWaveformList]

        td=si.td.wf.TimeDescriptor(-5e-9,
           SignalIntegrity.App.Project['CalculationProperties.TimePoints'],
           SignalIntegrity.App.Project['CalculationProperties.BaseSampleRate'])

        if snp.simulationType != 'CW':
            # note this matrix is transposed from what is normally expected
            Vmat=[[outputWaveformList[outputWaveformLabels.index('V'+str(portConnections[r]+1)+str(portConnections[c]+1))]
                for r in range(len(portConnections))]
                    for c in range(len(portConnections))]

            for vli in range(len(Vmat)):
                tdr=si.m.tdr.TDRWaveformToSParameterConverter(
                    WindowForwardHalfWidthTime=200e-12,
                    WindowReverseHalfWidthTime=200e-12,
                    WindowRaisedCosineDuration=50e-12,
                    Step=(snp.simulationType=='TDRStep'),
                    Length=0,
                    Denoise=True,
                    DenoisePercent=20.,
                    Inverted=False,
                    fd=td.FrequencyList()
                 )

                tdr.Convert(Vmat[vli],vli)
                for r in range(len(portConnections)):
                    outputWaveformList.append(tdr.IncidentWaveform if r==vli else si.td.wf.Waveform(td))
                    outputWaveformLabels.append('A'+str(portConnections[r]+1)+str(portConnections[vli]+1))
                for r in range(len(portConnections)):
                    outputWaveformList.append(tdr.ReflectWaveforms[r])
                    outputWaveformLabels.append('B'+str(portConnections[r]+1)+str(portConnections[vli]+1))

        if not SParameters:
            return (sourceNames,outputWaveformLabels,transferMatrices,outputWaveformList)
        else:
            # waveforms are adapted this way to give the horizontal offset that it already has closest to
            #-5 ns, with the correct number of points without resampling the waveform in any way.
            frequencyContentList=[]
            for wf in outputWaveformList:
                td=si.td.wf.TimeDescriptor(-5e-9,
                                       SignalIntegrity.App.Project['CalculationProperties.TimePoints'],
                                       SignalIntegrity.App.Project['CalculationProperties.BaseSampleRate'])
                td.H=wf.TimeDescriptor()[wf.TimeDescriptor().IndexOfTime(td.H)]
                fc=wf.Adapt(td).FrequencyContent()
                frequencyContentList.append(fc)

            Afc=[[frequencyContentList[outputWaveformLabels.index('A'+str(portConnections[r]+1)+str(portConnections[c]+1))]
                for c in range(len(portConnections))] 
                    for r in range(len(portConnections))]
            Bfc=[[frequencyContentList[outputWaveformLabels.index('B'+str(portConnections[r]+1)+str(portConnections[c]+1))]
                for c in range(len(portConnections))] 
                    for r in range(len(portConnections))]

            from numpy import array
            from numpy.linalg import inv

            frequencyList=td.FrequencyList()
            data=[None for _ in range(len(frequencyList))]
            for n in range(len(frequencyList)):
                B=[[Bfc[r][c][n] for c in range(snp.simulationNumPorts)] for r in range(snp.simulationNumPorts)]
                A=[[Afc[r][c][n] for c in range(snp.simulationNumPorts)] for r in range(snp.simulationNumPorts)]
                data[n]=(array(B).dot(inv(array(A)))).tolist()
            sp=si.sp.SParameters(frequencyList,data)
            return sp

def ProjectSParameters(filename):
    level=SignalIntegrityAppHeadless.projectStack.Push()
    sp=None
    try:
        app=SignalIntegrityAppHeadless()
        if app.OpenProjectFile(os.path.realpath(filename)):
            app.Drawing.DrawSchematic()
            if app.Drawing.canCalculateSParametersFromNetworkAnalyzerModel:
                result = app.SimulateNetworkAnalyzerModel(SParameters=True)
                if not result is None:
                    sp=result
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
                result=app.CalculateErrorTerms()[0]
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

