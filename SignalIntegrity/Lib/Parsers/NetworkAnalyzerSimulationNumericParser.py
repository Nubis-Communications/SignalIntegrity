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

class NetworkAnalyzerSimulationNumericParser(SimulatorNumericParser):
    """performs numeric simulations from netlists"""
    def __init__(self, f=None, DUTSParameters=None, args=None,  callback=None, cacheFileName=None):
        """constructor

        frequencies may be provided at construction time (or not for symbolic solutions).

        @param f (optional) list of frequencies
        @param args (optional) string arguments for the circuit.
        @param callback (optional) function taking one argument as a callback
        @param cacheFileName (optional) string name of file used to cache results

        Arguments are provided on a line as pairs of names and values separated by a space.

        The optional callback is used as described in the class CallBacker.

        The use of the cacheFileName is described in the class LineCache

        """
        self.DutSParameters=DUTSParameters
        SimulatorNumericParser.__init__(self,f,args,callback,cacheFileName)
    def ArrangeSimulation(self):
        from SignalIntegrity.Lib.Helpers.LineSplitter import LineSplitter
        self.simulationType=None
        naPortDictList=[]
        outputDict={}
        otherSourceList=[]
        dutList=[]
        newNetList=[]
        for line in self.m_lines:
            tokens=LineSplitter(line)
            if tokens[0]=='voltagesource':
                isNetworkAnalyzerPort=False
                if len(tokens)>3:
                    sourceDict={'ref':tokens[1],'port':tokens[2],'line':line}
                    for tokenIndex in range(3,len(tokens),2):
                        sourceDict[tokens[tokenIndex]]=tokens[tokenIndex+1]
                    if 'wftype' in sourceDict:
                        if sourceDict['wftype']=='networkanalyzerport':
                            naPortDictList.append(sourceDict)
                            isNetworkAnalyzerPort=True
                if not isNetworkAnalyzerPort:
                    otherSourceList.append(line)
            elif tokens[0]=='currentsource':
                otherSourceList.append(line)
            elif tokens[0]=='device':
                if len(tokens)>=3:
                    if tokens[3]=='dut':
                        dutList.append(line)
                        self.simulationNumPorts=int(tokens[2])
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
        if len(dutList)==0:
            raise SignalIntegrityExceptionNetworkAnalyzer('no DUT found')
        elif len(dutList)>1:
            raise SignalIntegrityExceptionNetworkAnalyzer('multiple DUTs found')
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
        if self.simulationNumPorts != len(simulationPortsFound):
            raise SignalIntegrityExceptionNetworkAnalyzer('DUT ports do not match network analyzer ports')
        #
        # at this point, we know the simulation type and the number of ports
        #
        # append the output lines
        if self.simulationType == 'CW':
            for p in range(1,self.simulationNumPorts+1):
                name='A'+str(p)
                if not name in outputDict:
                    raise SignalIntegrityExceptionNetworkAnalyzer('missing network analyzer output: '+name)
                else:
                    newNetList.append('voltageoutput '+name+' '+outputDict[name]['ref']+' '+outputDict[name]['port'])
            for p in range(1,self.simulationNumPorts+1):
                name='B'+str(p)
                if not name in outputDict:
                    raise SignalIntegrityExceptionNetworkAnalyzer('missing network analyzer output: '+name)
                else:
                    newNetList.append('voltageoutput '+name+' '+outputDict[name]['ref']+' '+outputDict[name]['port'])
        else:
            for p in range(1,self.simulationNumPorts+1):
                name='V'+str(p)
                if not name in outputDict:
                    raise SignalIntegrityExceptionNetworkAnalyzer('missing network analyzer output: '+name)
                else:
                    newNetList.append('voltageoutput '+name+' '+outputDict[name]['ref']+' '+outputDict[name]['port'])
        # append the network analyzer sources in port order followed by the remaining ones.
        for p in range(1,self.simulationNumPorts+1):
            portStr=str(p)
            for naPortDict in naPortDictList:
                if naPortDict['pn']==portStr:
                    newNetList.append(' '.join(LineSplitter(naPortDict['line'])[0:3]))
                    break
        newNetList.extend(otherSourceList)
        self.m_lines=newNetList
        self.AddKnownDevices(self.dutknown)
    def TransferMatrices(self):
        """calculates transfer matrices for simulation

        Simulation, insofar as this class is concerned means generating transfer matrices for
        processing waveforms with.

        @return instance of class TransferMatrices

        @remark
        TransferMatrices are used with a TransferMatricesProcessor to process waveforms for
        simulation.
        """
        self.ArrangeSimulation()
        return SimulatorNumericParser.TransferMatrices(self)