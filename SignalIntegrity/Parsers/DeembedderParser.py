'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.SystemDescriptions import Deembedder
from SignalIntegrity.Parsers import SystemDescriptionParser
from Devices.DeviceParser import DeviceParser
import copy

class DeembedderParser(SystemDescriptionParser):
    def __init__(self, f=None, args=None):
        SystemDescriptionParser.__init__(self, f, args)
    def _ProcessDeembedderLine(self,line):
        lineList=self.ReplaceArgs(line.split())
        if len(lineList) == 0: # pragma: no cover
            return
        if lineList[0] == 'system':
            dev=DeviceParser(self.m_f,None,lineList[1:])
            if not dev.m_spf is None:
                self.m_spc.append(('system',dev.m_spf))
        elif lineList[0] == 'unknown':
            self.m_sd.AddUnknown(lineList[1],int(lineList[2]))
        else:
            self.m_ul.append(line)
    def _ProcessLines(self):
        SystemDescriptionParser._ProcessLines(self,['connect','port'])
        self.m_sd = Deembedder(self.m_sd)
        lines=copy.deepcopy(self.m_ul)
        self.m_ul=[]
        for line in lines:
            self._ProcessDeembedderLine(line)
        lines=copy.deepcopy(self.m_ul)
        self.m_ul=[]
        for line in lines:
            SystemDescriptionParser._ProcessLine(self,line,[])
        return self
