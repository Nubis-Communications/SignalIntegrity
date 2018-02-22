# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
# 
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from SignalIntegrity.Symbolic import TeeThreePortSafe
from SignalIntegrity.Helpers import Matrix2LaTeX
from SignalIntegrity.Helpers import Matrix2Text

from textwrap import *

class Symbolic():
    """base class for all symbolic solutions."""
    def __init__(self,**args):
        """Constructor
        @param args (optional) named args (name=value)
        named arguments understood are:
        - 'size' - 'normal' or 'small' (defaults to 'normal')
        - 'docstart' - string for start of LaTeX document (defaults to a barebones
        article class document start.
        - 'docend' - string for end of document (defaults to normal LaTeX document end).
        - 'eqprefix' - prefix for equation start (defaults to \\[).
        - 'eqsuffix' - suffix for equation end (defaults to \\]).
        - 'eqenv' - boolean whether to enclose the equation in the equation environment
        Here, the size refers to the sizes of the output matrices.  'normal' means the
        normal size matrices and 'small' means the \\smallmatrix environment.
        """
        self.m_lines=[]
        size = args['size'] if 'size' in args else 'normal'
        self.m_docStart = args['docstart'] if 'docstart' in args else\
        '\\documentclass[10pt]{article}\n'+'\\usepackage{amsmath}\n'+\
        '\\usepackage{bbold}\n'+'\\begin{document}'
        self.m_docEnd = args['docend'] if 'docend' in args else '\\end{document}'
        self.m_eqPrefix = args['eqprefix'] if 'eqprefix' in args else '\\[ '
        self.m_eqSuffix = args['eqsuffix'] if 'eqsuffix' in args else ' \\]'
        self.m_identity = '\\mathbb{I} '
        self.m_eqEnvironment = args['eqenv'] if 'eqenv' in args else True
        self.m_small= (size == 'small')
    def Clear(self):
        """Clears any stored symbolic result
        @return self
        """
        self.m_lines=[]
        return self
    def Emit(self):
        """Writes the result out to the standard output
        @return self
        """
        for line in self.m_lines: print line
        return self
    def DocStart(self):
        """Appends the document start string to symbolic result.
        @return self
        @note For this to work properly, DocStart() should be called prior to calculating
        the symbolic result.
        """
        self._AddLine(self.m_docStart)
        return self
    def DocEnd(self):
        """Appends the document end string to symbolic result.
        @return self
        @note For this to work properly, DocEnd() should be called after calculating
        the symbolic result."""
        self._AddLine(self.m_docEnd)
        return self
    def _BeginEq(self):
        if self.m_eqEnvironment:
            return self.m_eqPrefix
        else: return ''
    def _EndEq(self):
        if self.m_eqEnvironment:
            return self.m_eqSuffix
        else: return ''
    def _AddLine(self,line):
        if len(line) == 0: return
        wlinelist=wrap(line)
        for wline in wlinelist: self.m_lines.append(wline)
        return self
    def _AddLines(self,lines):
        for line in lines: self._AddLine(line)
        return self
    def WriteToFile(self,name):
        """Writes the result to a file
        @param name filename for file to write
        """
        with open(name,'w') as equationFile:
            for line in self.m_lines: equationFile.write(line+'\n')
    def _SmallMatrix(self):
        return self.m_small
    def _Identity(self):
        return self.m_identity
    def Get(self):
        """@return list of \\n terminated lines containing the symbolic result."""
        lineBuffer=''
        for line in self.m_lines:
            lineBuffer=lineBuffer+line+'\n'
        return lineBuffer
    def InstallSafeTees(self,Z='\\varepsilon'):
        for d in range(len(self)):
            if '#' in self[d].Name:
                self[d].AssignSParameters(TeeThreePortSafe(Z))
        return self
    def _AddEq(self,text):
        self._AddLine(self._BeginEq() + text + self._EndEq())
        return self
    def _LaTeXMatrix(self,matrix):
        return Matrix2LaTeX(matrix,self._SmallMatrix())