"""
ParserArgs.py
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
from SignalIntegrity.Lib.Helpers.LineSplitter import LineSplitter

class ParserArgs():
    """argument handling base class for parsers"""
    def AssignArguments(self,args):
        """assigns arguments
        @param args list of arguments as name,value pairs
        The arguments are stored as a dictionary of values corresponding to the keyword names
        """
        self.m_vars=dict()
        if args is None:
            self.m_args=[]
        else:
            args=LineSplitter(args)
            self.m_args = dict([('$'+args[i]+'$',args[i+1])
                for i in range(0,len(args),2)])
    def ReplaceArgs(self,lineList):
        """replaces arguments in a line list with the actual values
        @param lineList list of tokens in a line to process
        If any token is surrounded by '$' and it's name is in the variable dictionary, then
        the token is replaced with the value in the variable dictionary.
        """
        replacedOne=False
        for i in range(len(lineList)):
            if lineList[i] in self.m_vars:
                replacedOne=True
                lineList[i] = self.m_vars[lineList[i]]
        if replacedOne:
            lineList=';'.join(lineList).split(';')
        return lineList
    def ReplaceArgsInLine(self,line):
        """replaces variables in a raw netlist line with the actual values.
        @param line string netlist line to process
        @return string the line with any variables replaced with their values.
        @remark This is used for lines that are not processed immediately, but are
        instead saved for later processing (i.e. the unknown lines list).  Such lines
        must have their variables resolved at the time that the variables are known,
        otherwise the variables are lost.
        @remark Unlike ReplaceArgs(), which operates on a token list produced by
        LineSplitter() (and therefore strips quotes), this operates on the raw line
        such that the line is returned unmolested if no variables are replaced.
        """
        if not hasattr(self,'m_vars') or not self.m_vars: return line
        tokens=line.split(' ')
        replacedOne=False
        for i in range(len(tokens)):
            if tokens[i] in self.m_vars:
                tokens[i]=self.m_vars[tokens[i]]
                replacedOne=True
        return ' '.join(tokens) if replacedOne else line
    def ProcessVariables(self,lineList):
        """processes lines insofar as arguments are concerned.
        @param lineList list of tokens in a line to process
        If the first token is 'var', then the keyword,value pairs are placed in
        the variable dictionary
        """
        if lineList[0] == 'var':
            variables=dict([(lineList[i*2+1],lineList[i*2+2])
                for i in range((len(lineList)-1)//2)])
            for key in self.m_args:
                if key in variables:
                    variables[key]=self.m_args[key]
            self.m_vars=dict(list(self.m_vars.items())+list(variables.items()))
            return True
        else:
            return False
