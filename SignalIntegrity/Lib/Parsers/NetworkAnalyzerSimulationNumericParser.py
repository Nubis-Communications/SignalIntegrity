"""
transfer matrix generation from network analyzer model netlists
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

from SignalIntegrity.Lib.Parsers.SimulatorNumericParser import SimulatorNumericParser
from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionNetworkAnalyzer
from SignalIntegrity.Lib.SParameters.SParameters import SParameters

class NetworkAnalyzerSimulationNumericParser(SimulatorNumericParser):
    """performs numeric simulations from netlists"""
    def __init__(self, f=None, DUTSParameters=None, PortConnectionList=None ,args=None,  callback=None, cacheFileName=None):
        """constructor  
        frequencies may be provided at construction time (or not for symbolic solutions).
        @param f (optional) list of frequencies
        @param DUTSParameters (optional) instance of class SParameters containing the DUT.
        If None is supplied, the file already in the schematic will be used, otherwise these
        will replace the DUT s-parameters.
        @param PortConnectionList (optional) list of True or False for each port in the
        network analyzer indicating a DUT port connection.  If None is supplied, then all
        network analyzer ports are used.
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback
        @param cacheFileName (optional) string name of file used to cache results

        Arguments are provided on a line as pairs of names and values separated by a space.

        The optional callback is used as described in the class CallBacker.

        The use of the cacheFileName is described in the class LineCache

        """
        self.PortConnectionList=PortConnectionList
        self.DutSParameters=SParameters(DUTSParameters.m_f,DUTSParameters.m_d)
        SimulatorNumericParser.__init__(self,f,args,callback,cacheFileName)
    def HashValue(self,stuffToHash=''):
        """Generates the hash for a definition  
        It is formed by hashing the port connection with whatever else is hashed
        @param stuffToHash repr of stuff to hash
        @remark derived classes should override this method and call the base class HashValue with their stuff added
        @return integer hash value
        """
        return SimulatorNumericParser.HashValue(self,repr(self.m_args)+repr(self.DutSParameters.Text())+repr(self.PortConnectionList)+stuffToHash)
    def ArrangeSimulation(self):
        from SignalIntegrity.Lib.Helpers.LineSplitter import LineSplitter
        self.simulationType=None
        naPortDictList=[]
        outputDict={}
        otherSourceList=[]
        dutList=[]
        newNetList=[]
        dutFound=False
        for line in self.m_lines:
            tokens=LineSplitter(line)
            if tokens[0] in ['voltagesource','networkanalyzerport']:
                isNetworkAnalyzerPort=False
                if len(tokens)>3:
                    sourceDict={'ref':tokens[1],'port':tokens[2],'line':line}
                    for tokenIndex in range(3,len(tokens),2):
                        sourceDict[tokens[tokenIndex]]=tokens[tokenIndex+1]
                    if tokens[0]:
                        naPortDictList.append(sourceDict)
                        isNetworkAnalyzerPort=True
                if not isNetworkAnalyzerPort:
                    otherSourceList.append(line)
            elif tokens[0]=='currentsource':
                otherSourceList.append(line)
            elif tokens[0]=='device':
                if len(tokens)>=3:
                    if tokens[3]=='dut':
                        if dutFound:
                            raise SignalIntegrityExceptionNetworkAnalyzer('multiple DUTs found')
                        dutFound=True
                        if self.DutSParameters == None:
                            self.dutknown={}
                            newNetList.append(line)
                            self.simulationNumPorts=int(tokens[2])
                            if self.PortConnectionList == None:
                                self.PortConnectionList = [True for _ in range(self.simulationNumPorts)]
                            if self.PortConnectionList != [True for _ in range(self.simulationNumPorts)]:
                                raise SignalIntegrityExceptionNetworkAnalyzer('port connection list inconsistent with DUT')
                        else:
                            self.simulationNumPorts=self.DutSParameters.m_P
                            if self.PortConnectionList == None:
                                self.PortConnectionList = [True for _ in range(self.simulationNumPorts)]
                            schematicDutPorts=int(tokens[2])
                            if self.PortConnectionList.count(True) != self.simulationNumPorts:
                                raise SignalIntegrityExceptionNetworkAnalyzer('port connection list inconsistent with DUT')
                            if schematicDutPorts < self.simulationNumPorts:
                                raise SignalIntegrityExceptionNetworkAnalyzer('DUT ports supplied ('+str(self.simulationNumPorts)+') are too large for the DUT, which has '+str(schematicDutPorts)+' ports')
                            elif schematicDutPorts > self.simulationNumPorts:
                                # DUT s-parameters supplied to the schematic need to be adjusted based on
                                # the actual s-parameters supplied and their connection
                                from numpy import identity
                                data=[identity(schematicDutPorts).tolist() for _ in range(len(self.DutSParameters))]
                                dutmap=[]
                                for p in range(len(self.PortConnectionList)):
                                    if self.PortConnectionList[p]:
                                        dutmap.append(p)
                                for n in range(len(data)):
                                    for r in range(len(dutmap)):
                                        for c in range(len(dutmap)):
                                            data[n][dutmap[r]][dutmap[c]]=self.DutSParameters[n][r][c]
                                self.dutknown={' '.join(tokens[2:4]):SParameters(self.DutSParameters.m_f,data)}
                            else:
                                self.dutknown={' '.join(tokens[2:4]):self.DutSParameters}
                            newNetList.append(' '.join(tokens[0:4]))
                    else: newNetList.append(line)
                else: newNetList.append(line)
            elif tokens[0]=='voltageoutput':
                for tokenIndex in range(1,len(tokens),3):
                    outputDict[tokens[tokenIndex]]={'ref':tokens[tokenIndex+1],'port':tokens[tokenIndex+2]}
            elif tokens[0]=='output':
                pass # remove unnamed outputs from the netlist
            else:
                newNetList.append(line)
        # at this point, we have:
        # a new netlist with all sources and outputs removed and the file (if any) stripped from the DUT
        # we have a list of dictionaries for all network analyzer ports and we have a list of dictionaries
        # for all of the named outputs (we don't know which ones we will keep yet).
        # we also have a list of other sources, that we will put back later, along with the outputs we want
        # to keep.
        #
        # determine the simulation type
        if not dutFound:
            raise SignalIntegrityExceptionNetworkAnalyzer('no DUT found')
        if len(naPortDictList)==0:
            raise SignalIntegrityExceptionNetworkAnalyzer('no network analyzer ports found')
        simulationTypesFound=[]
        simulationPortsFound=[]
        for naPortDict in naPortDictList:
            if not 'pn' in naPortDict:
                raise SignalIntegrityExceptionNetworkAnalyzer('a network analyzer port has no port number')
            else:
                simulationPortsFound.append(int(naPortDict['pn']))
            if not 'st' in naPortDict:
                raise SignalIntegrityExceptionNetworkAnalyzer('a network analyzer port has no type specified')
            if not naPortDict['st'] in ['CW','TDRStep','TDRImpulse']:
                raise SignalIntegrityExceptionNetworkAnalyzer('network analyzer port type not recognized: '+naPortDict['st'])
            if not naPortDict['st'] in simulationTypesFound:
                simulationTypesFound.append(naPortDict['st'])
        if len(simulationTypesFound)>1:
            raise SignalIntegrityExceptionNetworkAnalyzer('multiple network analyzer port types found')
        self.simulationType=simulationTypesFound[0]
        if sorted(simulationPortsFound) != [i for i in range(1,len(simulationPortsFound)+1)]:
            raise SignalIntegrityExceptionNetworkAnalyzer('incorrect port number assignment')
        if len(self.PortConnectionList) != len(simulationPortsFound):
            raise SignalIntegrityExceptionNetworkAnalyzer('DUT ports do not match network analyzer ports')
        #
        # at this point, we know the simulation type and the number of ports
        #
        # append the output lines
        if self.simulationType == 'CW':
            for p in range(len(self.PortConnectionList)):
                name='A'+str(p+1)
                if not name in outputDict:
                    raise SignalIntegrityExceptionNetworkAnalyzer('missing network analyzer output: '+name)
                else:
                    if self.PortConnectionList[p]:
                        newNetList.append('voltageoutput '+name+' '+outputDict[name]['ref']+' '+outputDict[name]['port'])
            for p in range(len(self.PortConnectionList)):
                name='B'+str(p+1)
                if not name in outputDict:
                    raise SignalIntegrityExceptionNetworkAnalyzer('missing network analyzer output: '+name)
                else:
                    if self.PortConnectionList[p]:
                        newNetList.append('voltageoutput '+name+' '+outputDict[name]['ref']+' '+outputDict[name]['port'])

        else:
            for p in range(len(self.PortConnectionList)):
                name='V'+str(p+1)
                if not name in outputDict:
                    raise SignalIntegrityExceptionNetworkAnalyzer('missing network analyzer output: '+name)
                else:
                    if self.PortConnectionList[p]:
                        newNetList.append('voltageoutput '+name+' '+outputDict[name]['ref']+' '+outputDict[name]['port'])
        # append the network analyzer sources in port order followed by the remaining ones.
        for p in range(len(self.PortConnectionList)):
            portStr=str(p+1)
            for naPortDict in naPortDictList:
                if naPortDict['pn']==portStr:
                    if self.PortConnectionList[p]:
                        newNetList.append(' '.join(LineSplitter(naPortDict['line'])[0:3]))
                    else:
                        newNetList.append('device '+naPortDict['ref']+' '+naPortDict['port']+' ground')
                    break
        newNetList.extend(otherSourceList)
        self.m_lines=newNetList
        self.AddKnownDevices(self.dutknown)
    def TransferMatrices(self):
        """Calculates transfer matrices for simulation  
        Simulation, insofar as this class is concerned means generating transfer matrices for
        processing waveforms with.
        @return instance of class TransferMatrices
        @remark TransferMatrices are used with a TransferMatricesProcessor to process waveforms for
        simulation.
        """
        self.ArrangeSimulation()
        return SimulatorNumericParser.TransferMatrices(self)