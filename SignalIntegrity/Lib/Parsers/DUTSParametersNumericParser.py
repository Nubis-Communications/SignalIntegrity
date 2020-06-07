"""
 network analyzer simulation DUT s-parameters from netlists
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

from SignalIntegrity.Lib.Parsers.SystemSParametersParser import SystemSParametersNumericParser
from SignalIntegrity.Lib.Exception import SignalIntegrityException,SignalIntegrityExceptionNetworkAnalyzer

class DUTSParametersNumericParser(SystemSParametersNumericParser):
    """generates s-parameters of a DUT from a network analyzer model netlist"""
    def __init__(self, f=None, args=None, callback=None, cacheFileName=None):
        """constructor  
        frequencies may be provided at construction time (or not for symbolic solutions).
        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback
        @param cacheFileName (optional) string name of file used to cache results
        @remark Arguments are provided on a line as pairs of names and values separated by a space.  
        The optional callback is used as described in the class CallBacker.  
        The use of the cacheFileName is described in the class LineCache  
        """
        self.NetworkAnalyzerProjectFile=None
        self.NetworkAnalyzerPortConnectionList=None
        SystemSParametersNumericParser.__init__(self, f, args, callback, cacheFileName)
    def HashValue(self,stuffToHash=''):
        """Generates the hash for a definition.  
        It is formed by hashing the port connection with whatever else is hashed.
        @param stuffToHash repr of stuff to hash
        @remark derived classes should override this method and call the base class HashValue with their stuff added
        @return integer hash value
        """
        return SystemSParametersNumericParser.HashValue(self,repr(self.NetworkAnalyzerPortConnectionList)+stuffToHash)
    def ConfigureForDUTCalculation(self):
        from SignalIntegrity.Lib.Helpers.LineSplitter import LineSplitter
        numPorts=0
        # first find the network analyzer model device
        spNetList=[]
        for line in self.m_lines:
            token=LineSplitter(line)
            if token[0]=='device':
                if token[3]=='networkanalyzermodel':
                    naRefDeg=token[1]
                    numPorts=int(token[2])
                    for tokenIndex in range(len(token)):
                        if token[tokenIndex]=='file':
                            self.NetworkAnalyzerProjectFile=token[tokenIndex+1] 
                else: spNetList.append(line)
            else: spNetList.append(line)
        if numPorts==0:
            return None
        # the network analyzer model has been removed from the netlist
        # find all of the device ports connected to the network analyzer model device ports
        naPortConnections=[[] for _ in range(numPorts)]
        spNetList2=[]
        for line in spNetList:
            token=LineSplitter(line)
            if token[0]=='connect':
                theseConnections=[(token[2*i+1],token[2*i+2]) for i in range(0,(len(token)-1)//2)]
                if any([device==naRefDeg for (device,port) in theseConnections]):
                    for (device,port) in theseConnections:
                        if device==naRefDeg:
                            devicePortIndex=int(port)-1
                            for (d,p) in theseConnections:
                                if d!=naRefDeg:
                                    naPortConnections[devicePortIndex].append((d,p))
                            break
                else: spNetList2.append(line)
            else: spNetList2.append(line)
        # all of the connections to network analyzer model have been removed
        # add back connections of other devices that are connected together
        for pci in range(len(naPortConnections)):
            if len(naPortConnections[pci]) > 1:
                spNetList2.append('connect '+' '.join([' '.join(dp) for dp in naPortConnections[pci]]))
        # connect ports to the system that was connected to the network analyzer model
        portNumber=1
        self.NetworkAnalyzerPortConnectionList=[False for _ in range(len(naPortConnections))]
        for pci in range(len(naPortConnections)):
            if len(naPortConnections[pci])>0:
                spNetList2.append('port '+str(portNumber)+' '+' '.join(naPortConnections[pci][0]))
                self.NetworkAnalyzerPortConnectionList[pci]=True
                portNumber=portNumber+1
        self.m_lines=spNetList2
    def SParameters(self,solvetype='block'):
        """Compute the s-parameters of the DUT in a network analyzer simulation netlist.
        @param solvetype (optional) string how to solve it. (defaults to 'block').
        @return instance of class SParameters as the solution of the network.
        @remark valid solvetype strings are:
        - 'block' - use the block matrix solution method.
        - 'direct' - use the direct method.  
        'block' is faster and preferred, but direct is provided as an alternative and
        for testing. (Previously, instances were found where the block method failed,
        but the direct method did not - but this possibility is thought to be impossible
        now.
        """
        self.ConfigureForDUTCalculation()
        if self.NetworkAnalyzerProjectFile != None:
            try:
                return (SystemSParametersNumericParser.SParameters(self,solvetype),self.NetworkAnalyzerProjectFile)
            except SignalIntegrityException as e:
                raise SignalIntegrityExceptionNetworkAnalyzer(e.message)
        return (None,None)
