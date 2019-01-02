"""
NetList.py
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
    import ScrolledText as scrolledtext
else:
    import tkinter as tk
    from tkinter import scrolledtext

from SignalIntegrity.App.FilePicker import AskSaveAsFilename
import SignalIntegrity.App.Project

class NetList(object):
    def __init__(self,schematic):
        self.textToShow=[]
        self.outputNames=[]
        self.measureNames=[]
        self.sourceNames=[]
        self.stimNames=[]
        self.definingStimList=[]
        deviceList = schematic.deviceList
        equiPotentialWireList=SignalIntegrity.App.Project['Drawing.Schematic'].dict['Wires'].EquiPotentialWireList()
        # put all devices in the net list
        for device in deviceList:
            if not device['partname'].GetValue() in ['Port','Measure','Output','Stim']:
                self.textToShow.append(device.NetListLine())
                if device.netlist['DeviceName'] in ['voltagesource','currentsource']:
                    self.sourceNames.append(device['ref'].GetValue())
        # gather up all device pin coordinates
        devicePinCoordinateList = [device.PinCoordinates() for device in deviceList]
        devicePinNeedToCheckList = [[True for pinIndex in range(len(devicePinCoordinateList[deviceIndex]))] for deviceIndex in range(len(devicePinCoordinateList))]
        deviceConnectionList = []
        for deviceIndex in range(len(devicePinCoordinateList)):
            devicePinConnectionList = []
            for pinIndex in range(len(devicePinCoordinateList[deviceIndex])):
                thisDevicePinCoordinate = devicePinCoordinateList[deviceIndex][pinIndex]
                thisListOfConnectedDevicePins=[]
                if devicePinNeedToCheckList[deviceIndex][pinIndex]:
                    # search all device pins and wire vertices for this coordinate
                    for deviceCheckIndex in range(len(devicePinCoordinateList)):
                        for pinCheckIndex in range(len(devicePinCoordinateList[deviceCheckIndex])):
                            thisDevicePinCheckCoordinate = devicePinCoordinateList[deviceCheckIndex][pinCheckIndex]
                            if thisDevicePinCoordinate == thisDevicePinCheckCoordinate:
                                thisListOfConnectedDevicePins.append((deviceCheckIndex,pinCheckIndex))
                    for wire in equiPotentialWireList:
                        thisWireConnectedToThisDevicePin = False
                        for vertex in wire:
                            if vertex['Coord'] == thisDevicePinCoordinate:
                                thisWireConnectedToThisDevicePin = True
                                break
                        if thisWireConnectedToThisDevicePin:
                            for vertex in wire:
                                for deviceCheckIndex in range(len(devicePinCoordinateList)):
                                    for pinCheckIndex in range(len(devicePinCoordinateList[deviceCheckIndex])):
                                        thisDevicePinCheckCoordinate = devicePinCoordinateList[deviceCheckIndex][pinCheckIndex]
                                        if vertex['Coord'] == thisDevicePinCheckCoordinate:
                                            thisListOfConnectedDevicePins.append((deviceCheckIndex,pinCheckIndex))
                    thisListOfConnectedDevicePins=list(set(thisListOfConnectedDevicePins))
                    for connectedDevicePins in thisListOfConnectedDevicePins:
                        connectedDeviceIndex=connectedDevicePins[0]
                        connectedPinIndex=connectedDevicePins[1]
                        devicePinNeedToCheckList[connectedDeviceIndex][connectedPinIndex]=False
                devicePinConnectionList.append(thisListOfConnectedDevicePins)
            deviceConnectionList.append(devicePinConnectionList)
        netList = []
        for deviceConnection in deviceConnectionList:
            for devicePinConnection in deviceConnection:
                if len(devicePinConnection) > 1:
                    netList.append(devicePinConnection)
        for net in netList:
            measureList=[]
            outputList=[]
            portList=[]
            stimList=[]
            # gather up list of all measures, outputs, and ports
            for devicePin in net:
                deviceIndex=devicePin[0]
                pinIndex=devicePin[1]
                thisDevice=schematic.deviceList[deviceIndex]
                thisDevicePartName = thisDevice['partname'].GetValue()
                if thisDevicePartName == 'Port':
                    portList.append(devicePin)
                elif thisDevicePartName == 'Output':
                    outputList.append(devicePin)
                elif thisDevicePartName == 'Measure':
                    measureList.append(devicePin)
                elif thisDevicePartName == 'Stim':
                    stimList.append(devicePin)
            #remove all of the ports, outputs, measures and stims from the net
            net = list(set(net)-set(measureList)-set(portList)-set(outputList)-set(stimList))
            if len(net) > 0:
                # for the measures, outputs and ports, we just need one device/port, so we use the first one
                deviceIndexOfFirstDeviceInNet = net[0][0]
                pinIndexOfFirstDeviceInNet = net[0][1]
                firstDeviceName = schematic.deviceList[deviceIndexOfFirstDeviceInNet]['ref'].GetValue()
                firstDevicePinNumber = schematic.deviceList[deviceIndexOfFirstDeviceInNet].partPicture.current.pinList[pinIndexOfFirstDeviceInNet]['Number']
                devicePinString = firstDeviceName + ' ' + str(firstDevicePinNumber)
                for measure in measureList:
                    deviceIndex = measure[0]
                    self.textToShow.append(schematic.deviceList[deviceIndex].NetListLine() + ' ' + devicePinString)
                    self.measureNames.append(schematic.deviceList[deviceIndex]['ref'].GetValue())
                for output in outputList:
                    deviceIndex = output[0]
                    self.textToShow.append(schematic.deviceList[deviceIndex].NetListLine() + ' ' + devicePinString)
                    self.outputNames.append(schematic.deviceList[deviceIndex]['ref'].GetValue())
                for port in portList:
                    deviceIndex = port[0]
                    self.textToShow.append(schematic.deviceList[deviceIndex].NetListLine() + ' ' + devicePinString)
            if len(net) > 1:
                # list the connections
                thisConnectionString = 'connect'
                for devicePortIndex in net:
                    deviceIndex = devicePortIndex[0]
                    pinIndex = devicePortIndex[1]
                    deviceName = schematic.deviceList[deviceIndex]['ref'].GetValue()
                    pinNumber = schematic.deviceList[deviceIndex].partPicture.current.pinList[pinIndex]['Number']
                    thisConnectionString = thisConnectionString + ' '+ str(deviceName) +' '+str(pinNumber)
                self.textToShow.append(thisConnectionString)
            if len(stimList)>0: # there is at least one stim on this net
                # stims fall into three categories
                # stims whose pin 1 is connected directly to a device port, and whose pin 2 is connected to port 1 of another stim.
                # this type is a stim that depends on another. This is called a dependent stim
                # stims whose pin 1 is connected directly to a device port, and whose pin 2 is unconnected.
                # this type of stim is independent. this is called an independent stim
                # stims whose pin 1 is connected to pin 2 of another stim and whose pin 2 is unconnected
                # this is a stim that others depend on. This is called a defining stim
                directStimListThisNet=[]
                definingStimListThisNet=[]
                if len(net) == 0: # there are only stims on this net
                    # one and only one of these stims better be a defining stim
                    # this is indicated by a pin 1 connection to the net
                    # and the rest of the stims with a pin 2 connection
                    for stim in stimList:
                        if deviceList[stim[0]].partPicture.current.pinList[stim[1]]['Number']==1:
                            definingStimListThisNet.append(stim)
                        else:
                            directStimListThisNet.append(stim)
                    if len(definingStimListThisNet) != 1: # this is an error
                        directStimListThisNet=[]
                        definingStimListThisNet=[]
                    elif len(directStimListThisNet) < 1: # this is an error
                        directStimListThisNet=[]
                        definingStimListThisNet=[]
                else: # there are stims and devices on this net
                    # all of the stim pins must be pin 1
                    # and the pin 1 must be connected directly to one of the device ports on the net
                    if all(deviceList[stim[0]].partPicture.current.pinList[stim[1]]['Number']==1 for stim in stimList): # all of the stim pins are pin 1
                        directStimListThisNet=stimList
                # okay - now that we're here, we either have one defining stim and one or more direct stims
                # which implies that this is a stim net used to define a stimdef or...
                # we have no defining stim and one or more direct stims which implies that these are
                # stimdef definitions
                if len(definingStimListThisNet)==0: # stim
                    for (stimDeviceIndex,stimPinIndex) in directStimListThisNet: # generate the stim for each stim
                        stimPin1Coordinate=deviceList[stimDeviceIndex].PinCoordinates()[stimPinIndex]
                        for (deviceIndex,devicePinIndex) in net: # find the device pin connected to this stim
                            devicePinCoordinate=deviceList[deviceIndex].PinCoordinates()[devicePinIndex]
                            if stimPin1Coordinate==devicePinCoordinate:
                                stimNameString=''
                                for stimNameIndex in range(len(self.stimNames)):
                                    if stimDeviceIndex == self.stimNames[stimNameIndex]:
                                        stimNameString = 'm'+str(stimNameIndex+1)
                                        break
                                if stimNameString=='':
                                    self.stimNames.append(stimDeviceIndex)
                                    stimNameString = 'm'+str(len(self.stimNames))
                                deviceName = deviceList[deviceIndex]['ref'].GetValue()
                                devicePinNumber = deviceList[deviceIndex].partPicture.current.pinList[devicePinIndex]['Number']
                                devicePinString = deviceName + ' ' + str(devicePinNumber)
                                self.textToShow.append(deviceList[stimDeviceIndex].NetListLine() + ' ' + stimNameString + ' ' + devicePinString)
                elif len(definingStimListThisNet)==1: #stimdef
                    (definingStimDeviceIndex,definingStimPinIndex) = definingStimListThisNet[0]
                    directStimDeviceIndexList=[directStimDevice[0] for directStimDevice in directStimListThisNet]
                    self.definingStimList.append((definingStimDeviceIndex,tuple(directStimDeviceIndexList)))
        # generate the stimdef if required
        if len(self.definingStimList) > 0: # need a stimdef
            # for now, if there is at least one defining stim, meaning there must be a stimdef, then all stims must be derived from the
            # defining stims
            stimdef=[[0 for j in self.definingStimList] for i in self.stimNames]
            for c in range(len(self.definingStimList)):
                determinesStimsDevicesIndexes=self.definingStimList[c][1]
                for determinesStimDeviceIndex in determinesStimsDevicesIndexes:
                    for r in range(len(self.stimNames)):
                        dependentStimDeviceIndex=self.stimNames[r]
                        if determinesStimDeviceIndex == dependentStimDeviceIndex:
                            stimdef[r][c]=deviceList[dependentStimDeviceIndex]['weight'].GetValue()
            self.textToShow.append('stimdef '+str(stimdef))

        # clean up everything to deal with special case current probes and differential voltage probes
        endinglines=[]
        textToShow=[]
        for line in self.textToShow:
            tokens = line.split(' ')
            if tokens[0] == 'currentoutput':
                line = 'device '+tokens[1]+' 4 currentcontrolledvoltagesource 1.0'
            if tokens[0] == 'differentialvoltageoutput':
                line = 'device '+tokens[1]+' 4 voltagecontrolledvoltagesource 1.0'
            if tokens[0] == 'currentoutput' or tokens[0] == 'differentialvoltageoutput':
                self.outputNames.append(tokens[1])
                endinglines.append('device '+tokens[1]+'_2 1 ground')
                endinglines.append('device '+tokens[1]+'_3 1 open')
                endinglines.append('connect '+tokens[1]+' 3 '+tokens[1]+'_2 1')
                endinglines.append('connect '+tokens[1]+' 4 '+tokens[1]+'_3 1')
                endinglines.append('output '+tokens[1]+' 4')
            textToShow.append(line)
        self.textToShow=textToShow+endinglines
    def Text(self):
        return self.textToShow
    def OutputNames(self):
        return self.outputNames
    def SourceNames(self):
        return self.sourceNames
    def MeasureNames(self):
        return self.measureNames

class NetListFrame(tk.Frame):
    def __init__(self,parent,textToShow):
        tk.Frame.__init__(self,parent)
        self.title = 'NetList'
        self.text=scrolledtext.ScrolledText(self)
        self.text.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        for line in textToShow:
            self.text.insert(tk.END,line+'\n')
        self.text.configure(state='disabled')

class NetListDialog(tk.Toplevel):
    def __init__(self,parent,textToShow):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title('NetList')
        self.textToShow=textToShow

        self.parent = parent

        self.result = None

        self.NetListFrame = NetListFrame(self,textToShow)
        self.initial_focus = self.body(self.NetListFrame)
        self.NetListFrame.pack(side=tk.TOP,fill=tk.BOTH,expand=tk.YES,padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):
        extension='.txt'
        filename=AskSaveAsFilename(parent=self,
                                   filetypes=[('text', extension)],
                                   defaultextension='.txt',
                                   initialdir=self.parent.fileparts.AbsoluteFilePath(),
                                   initialfile=self.parent.fileparts.filename+'.txt')
        if filename is None:
            self.initial_focus.focus_set() # put focus back
            return
        with open(filename,"w") as f:
            for line in self.textToShow:
                f.write(line+'\n')

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):
        pass

