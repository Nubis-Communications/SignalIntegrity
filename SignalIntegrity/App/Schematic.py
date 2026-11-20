"""
Schematic.py
"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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

from SignalIntegrity.App.NetList import NetList
from SignalIntegrity.App.Wire import WireList

import SignalIntegrity.App.Project
from SignalIntegrity.Lib.CallBacker import CallBacker

class Schematic(CallBacker):
    def __init__(self):
        self.deviceList = []
        self.otherPages={}
        super().__init__()

    def InitFromProject(self):
        self.__init__()
        if SignalIntegrity.App.Project is None:
            return
        project=SignalIntegrity.App.Project
        self.LoadDevices(project['Drawing.Schematic.Devices'])
        for index,drawing in enumerate(project.PageDrawings()):
            if index != project.activePage:
                page=Schematic()
                page.LoadDevices(drawing['Schematic.Devices'])
                self.otherPages[index]=page
        # Legacy eye settings are needed until every page has been loaded.
        if 'EyeDiagram' in project.dict:
            del(project.dict['EyeDiagram'])

    def LoadDevices(self,deviceListProject):
        from SignalIntegrity.App.Device import DeviceFromProject
        for deviceProject in deviceListProject:
            try:
                returnedDevice=DeviceFromProject(deviceProject).result
            except NameError: # part picture doesn't exist
                returnedDevice=None
            if not returnedDevice is None:
                self.deviceList.append(returnedDevice)

    def SelectPage(self,index):
        project=SignalIntegrity.App.Project
        previousIndex=project.activePage
        if index != previousIndex:
            page=self.otherPages.pop(index)
            self.deviceList,page.deviceList=page.deviceList,self.deviceList
            self.otherPages[previousIndex]=page
            project.activePage=index

    def CircuitPages(self):
        project=SignalIntegrity.App.Project
        return [(self if index == project.activePage else self.otherPages[index],
                 drawing['Schematic'].dict['Wires'])
                for index,drawing in enumerate(project.PageDrawings())]

    def CircuitDevices(self):
        if not self.otherPages:
            return self.deviceList
        return [device for page,_ in self.CircuitPages() for device in page.deviceList]

    def NetList(self):
        for page,wires in self.CircuitPages():
            wires.ConsolidateWires(page)
        return NetList(self)
    def InputWaveforms(self):
        inputWaveformList=[]
        deferredNoiseWaveforms=[]
        for device in self.CircuitDevices():
            if not device['partname']['Value'] in ['ImpulseResponseFilter','FrequencyResponseFilter','EyeWaveform','Waveform']:
                waveforms=device.Waveforms(self.callback)
                # NetList emits four-port noise sources after the other sources.
                if (device.netlist['DeviceName'] in ['voltagenoisesource','currentnoisesource']
                        and device['ports']['Value'] == '4'):
                    deferredNoiseWaveforms.extend(waveforms)
                else:
                    inputWaveformList.extend(waveforms)
        return inputWaveformList+deferredNoiseWaveforms
    
    def DependentSourceCount(self):
        count = 0
        for device in self.CircuitDevices():
            if device['partname']['Value'] in ['ImpulseResponseFilter','EyeWaveform','Waveform']:
                continue
            wftype = device['wftype']
            if wftype != None and wftype.GetValue() == 'Dependent':
                count += 1
        return count
    def HasDependentSource(self):
        return self.DependentSourceCount() > 0
    def ProcessingIterationCount(self,stopOnConvergence,maximumProcessingIterations):
        dependentSourceCount = self.DependentSourceCount()
        if dependentSourceCount == 0:
            return 1
        if stopOnConvergence:
            try:
                maximumProcessingIterations = int(maximumProcessingIterations)
            except (TypeError,ValueError):
                maximumProcessingIterations = 100
            return max(2,maximumProcessingIterations)
        return dependentSourceCount + 1
    def OtherWaveforms(self):
        otherWaveformList=[]
        for device in self.CircuitDevices():
            if device['partname']['Value'] in ['EyeWaveform','Waveform']:
                if device['state']['Value'] == 'on':
                    try:
                        wf = device.Waveform()
                    except Exception as e:
                        import SignalIntegrity.App.Project
                        if SignalIntegrity.App.Preferences['Calculation.IgnoreMissingOtherWaveforms']:
                            otherWaveformList.append(None)
                            break
                        else:
                            raise
                    if not wf is None:
                        otherWaveformList.append(wf)
        return otherWaveformList
    def Clear(self):
        self.deviceList = []
        if not SignalIntegrity.App.Project is None:
            SignalIntegrity.App.Project['Drawing.Schematic'].dict['Wires']=WireList()
    def NewUniqueReferenceDesignator(self,defaultDesignator):
        if defaultDesignator != None and '?' in defaultDesignator:
            referenceDesignatorList=[]
            for device in self.CircuitDevices():
                deviceReferenceDesignatorProperty = device['ref']
                if deviceReferenceDesignatorProperty != None:
                    deviceReferenceDesignator = deviceReferenceDesignatorProperty.GetValue()
                    if deviceReferenceDesignator != None:
                        referenceDesignatorList.append(deviceReferenceDesignator)
            num = 1
            while defaultDesignator.replace('?',str(num)) in referenceDesignatorList:
                num=num+1
            return defaultDesignator.replace('?',str(num))
        else:
            return None
    def DevicePinConnectedList(self):
        devicePinConnectedList=[]
        if SignalIntegrity.App.Project is None:
            return devicePinConnectedList
        for thisDeviceIndex in range(len(self.deviceList)):
            thisDeviceConnectedList=[]
            for thisPinCoordinate in self.deviceList[thisDeviceIndex].partPicture.current.PinCoordinates():
                thisPinConnected=False
                for otherDeviceIndex in range(len(self.deviceList)):
                    if thisPinConnected:
                        break
                    if thisDeviceIndex != otherDeviceIndex:
                        if thisPinConnected:
                            break
                        for otherPinCoordinate in self.deviceList[otherDeviceIndex].partPicture.current.PinCoordinates():
                            if thisPinCoordinate == otherPinCoordinate:
                                thisPinConnected=True
                                break
                if not thisPinConnected:
                    for wire in SignalIntegrity.App.Project['Drawing.Schematic.Wires']:
                        if thisPinConnected:
                            break
                        for vertex in wire['Vertices']:
                            if thisPinCoordinate == vertex['Coord']:
                                thisPinConnected=True
                                break
                thisDeviceConnectedList.append(thisPinConnected)
            devicePinConnectedList.append(thisDeviceConnectedList)
        return devicePinConnectedList
    def Consolidate(self):
        if SignalIntegrity.App.Project is None:
            return
        SignalIntegrity.App.Project['Drawing.Schematic'].dict['Wires'].ConsolidateWires(self)
    def DotList(self):
        dotList=[]
        if SignalIntegrity.App.Project is None:
            return dotList
        # make a list of all coordinates
        coordList=[]
        for device in self.deviceList:
            coordList=coordList+device.PinCoordinates()
        wireListProject = SignalIntegrity.App.Project['Drawing.Schematic.Wires']
        for wireProject in wireListProject:
            vertexCoordinates=[vertexProject['Coord'] for vertexProject in wireProject['Vertices']]
            #vertex coordinates count as two except for the endpoints
            coordList=coordList+vertexCoordinates+vertexCoordinates[1:-1]
        uniqueCoordList=list(set(coordList))
        for coord in uniqueCoordList:
            if coordList.count(coord)>2:
                dotList.append(coord)
        return dotList
