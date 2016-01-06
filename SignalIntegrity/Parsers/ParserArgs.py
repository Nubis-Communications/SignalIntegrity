'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
from SignalIntegrity.Helpers.LineSplitter import LineSplitter

class ParserArgs():
    def AssignArguments(self,args):
        self.m_vars=dict()
        if args is None:
            self.m_args=[]
        else:
            args=LineSplitter(args)
            self.m_args = dict([('$'+args[i]+'$',args[i+1])
                for i in range(0,len(args),2)])
    def ReplaceArgs(self,lineList):
        for i in range(len(lineList)):
            if lineList[i] in self.m_vars:
                lineList[i] = self.m_vars[lineList[i]]
        return lineList
    def ProcessVariables(self,lineList):
        if lineList[0] == 'var':
            variables=dict([(lineList[i*2+1],lineList[i*2+2])
                for i in range((len(lineList)-1)/2)])
            for key in self.m_args:
                if key in variables:
                    variables[key]=self.m_args[key]
            self.m_vars=dict(self.m_vars.items()+variables.items())
            return True
        else:
            return False