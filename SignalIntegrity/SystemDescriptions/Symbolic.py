from SignalIntegrity.Symbolic import TeeThreePortSafe
from SignalIntegrity.Helpers import Matrix2LaTeX
from SignalIntegrity.Helpers import Matrix2Text

from textwrap import *

class Symbolic():
    def __init__(self,**args):
        self.m_lines=[]
        size = args['size'] if 'size' in args else 'normal'
        self.m_docStart = args['docstart'] if 'docstart' in args else\
        '\\documentclass[10pt]{article}\\usepackage{amsmath}\\begin{document}'
        self.m_docEnd = args['docend'] if 'docend' in args else '\\end{document}'
        self.m_eqPrefix = args['eqprefix'] if 'eqprefix' in args else '\\[ '
        self.m_eqSuffix = args['eqsuffix'] if 'eqsuffix' in args else ' \\]'
        self.m_identity = '\\mathbb{I} '
        self.m_eqEnvironment = args['eqenv'] if 'eqenv' in args else True
        self.m_small= (size == 'small')
    def Clear(self):
        self.m_lines=[]
        return self
    def Emit(self):
        for line in self.m_lines: print line
        return self
    def DocStart(self):
        self._AddLine(self.m_docStart)
        return self
    def DocEnd(self):
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
        with open(name,'w') as equationFile:
            for line in self.m_lines: equationFile.write(line+'\n')
    def _SmallMatrix(self):
        return self.m_small
    def _Identity(self):
        return self.m_identity
    def Get(self):
        lineBuffer=''
        for line in self.m_lines:
            lineBuffer=lineBuffer+line+'\n'
        return lineBuffer
    def InstallSafeTees(self,Z='\\varepsilon'):
        for d in range(len(self)):
            if '#' in self[d].pName:
                self[d].pSParameters = TeeThreePortSafe(Z)
    def _AddEq(self,text):
        self._AddLine(self._BeginEq() + text + self._EndEq())
    def _LaTeXMatrix(self,matrix):
        return Matrix2LaTeX(matrix,self._SmallMatrix())