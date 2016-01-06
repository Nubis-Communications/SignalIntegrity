'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SystemDescriptions import Simulator
from SignalIntegrity.Parsers import SystemDescriptionParser
import copy

class SimulatorParser(SystemDescriptionParser):
    def __init__(self, f=None, args=None):
        SystemDescriptionParser.__init__(self, f, args)
    def _ProcessSimulatorLine(self,line):
        lineList=self.ReplaceArgs(line.split())
        if len(lineList) == 0:
            return # pragma: no cover
        elif lineList[0] == 'output':
            if self.m_sd.pOutputList is None:
                self.m_sd.pOutputList = []
            for i in range(1,len(lineList),2):
                self.m_sd.pOutputList.append((lineList[i],int(lineList[i+1])))
        elif lineList[0] == 'voltagesource':
            self.m_sd.AddVoltageSource(lineList[1],int(lineList[2]))
        elif lineList[0] == 'currentsource':
            self.m_sd.AddCurrentSource(lineList[1],int(lineList[2]))
        else:
            self.m_ul.append(line)
    def _ProcessLines(self):
        SystemDescriptionParser._ProcessLines(self,['connect','port'])
        self.m_sd = Simulator(self.m_sd)
        lines=copy.deepcopy(self.m_ul)
        self.m_ul=[]
        for line in lines:
            self._ProcessSimulatorLine(line)
        lines=copy.deepcopy(self.m_ul)
        self.m_ul=[]
        for line in lines:
            SystemDescriptionParser._ProcessLine(self,line,['port'])
        return self