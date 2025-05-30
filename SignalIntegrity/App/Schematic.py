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
import sys

if sys.version_info.major < 3:
    import Tkinter as tk
else:
    import tkinter as tk

import copy

from SignalIntegrity.App.NetList import NetList
from SignalIntegrity.App.Wire import WireList

import SignalIntegrity.App.Project
from SignalIntegrity.Lib.CallBacker import CallBacker

class Schematic(CallBacker):
    def __init__(self):
        self.deviceList = []
        super().__init__()

    def InitFromProject(self):
        self.__init__()
        if SignalIntegrity.App.Project is None:
            return
        deviceListProject=SignalIntegrity.App.Project['Drawing.Schematic.Devices']
        for d in range(len(deviceListProject)):
            try:
                from SignalIntegrity.App.Device import DeviceFromProject
                returnedDevice=DeviceFromProject(deviceListProject[d]).result
            except NameError: # part picture doesn't exist
                returnedDevice=None
            if not returnedDevice is None:
                self.deviceList.append(returnedDevice)
        # global eye diagram configurations are allowed to get into the project for backwards compatibility
        # Once the schematic has been initialized, this can be removed
        if 'EyeDiagram' in SignalIntegrity.App.Project.dict.keys():
            del(SignalIntegrity.App.Project.dict['EyeDiagram'])
    def NetList(self):
        self.Consolidate()
        return NetList(self)
    def InputWaveforms(self):
        inputWaveformList=[]
        for device in self.deviceList:
            if not device['partname']['Value'] in ['ImpulseResponseFilter','EyeWaveform','Waveform']:
                wf = device.Waveform(self.callback)
                if not wf is None:
                    inputWaveformList.append(wf)
        return inputWaveformList
    def ThereAreOtherWaveforms(self):
        for device in self.deviceList:
            if device['partname']['Value'] in ['EyeWaveform','Waveform']:
                if device['state']['Value'] == 'on':
                    return True
        return False
    def OtherWaveforms(self):
        otherWaveformList=[]
        for device in self.deviceList:
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
            for device in self.deviceList:
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
