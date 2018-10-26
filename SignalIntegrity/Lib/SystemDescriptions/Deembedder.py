"""
 Numeric Deembedder Housekeeping Functions
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

from SignalIntegrity.Lib.SystemDescriptions.SystemSParameters import SystemSParameters

class Deembedder(SystemSParameters):
    """housekeeping base class for deembedders"""
    def __init__(self,sd=None):
        SystemSParameters.__init__(self,sd)
    def AddUnknown(self,Name,Ports):
        """Adds a device to the system with the given name and number of ports
        The type is 'unknown'
        @param Name string name of device to add
        @param Ports integer number of ports in the device
        This is like a call on the SystemDescription class to AddDevice()
        with the type set to 'unknown'."""
        self.AddDevice(Name,Ports,SParams=None,Type='unknown')
    def DutANames(self):
        return [p.A for d in self for p in d if d.Type=='unknown']
    def DutBNames(self):
        return [p.B for d in self for p in d if d.Type=='unknown']
    def UnknownNames(self):
        return [d.Name for d in self if d.Type=='unknown']
    def UnknownPorts(self):
        return [len(d) for d in self if d.Type=='unknown']
    def Partition(self,A):#a list of arrays, one per unknown device
        PL=self.UnknownPorts()
        Result=[]
        S=0
        for d in range(len(PL)):
            Result.append(A[S:S+PL[d],])
            S=S+PL[d]
        return Result