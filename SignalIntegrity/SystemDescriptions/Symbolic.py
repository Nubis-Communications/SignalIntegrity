from SignalIntegrity.Symbolic import TeeThreePortSafe
from SignalIntegrity.Helpers import Matrix2LaTeX
from textwrap import *

class Symbolic():
    def __init__(self,equationEnvironment=False,small=False):
        self.m_lines=[]
        self.m_docStart = '\\documentclass[10pt]{article}\\usepackage{amsmath}\\begin{document}'
        self.m_docEnd = '\\end{document}'
        self.m_eqPrefix='\\[ '
        self.m_eqSuffix=' \\]'
        self.m_identity = '\\mathbb{I} '
        self.m_eqEnvironment = equationEnvironment
        self.m_small=small
    @staticmethod
    def SubscriptedVector(v):
        lv=[]
        for node in v:
            if isinstance(node,str):
                if len(node)>1:
                    lv.append(node[0]+'_'+node[1:])
                else:
                    lv.append(node)
            else:
                lv.append(node)
        return [[i] for i in lv]
    def Clear(self):
        self.m_lines=[]
        return self
    def Emit(self):
        for line in self.m_lines:
            print line
        return self
    def SymbolicMatrices(self):
        for i in range(len(self)):
            self[i].m_S =\
                Device.SymbolicMatrix(self[i].pName,len(self[i]))
    def DocStart(self):
        self.AddLine(self.m_docStart)
        return self
    def DocEnd(self):
        self.AddLine(self.m_docEnd)
        return self
    def BeginEq(self):
        if self.m_eqEnvironment:
            return self.m_eqPrefix
        else:
            return ''
    def EndEq(self):
        if self.m_eqEnvironment:
            return self.m_eqSuffix
        else:
            return ''
    def AddLine(self,line):
        if len(line) == 0:
            return
        wlinelist=wrap(line)
        for wline in wlinelist:
            self.m_lines.append(wline)
        return self
    def AddLines(self,lines):
        for line in lines:
            self.AddLine(line)
        return self
    def WriteToFile(self,name):
        equationFile=open(name,'w')
        for line in self.m_lines:
            equationFile.write(line+'\n')
        equationFile.close()
    def SmallMatrix(self):
        return self.m_small
    def Identity(self):
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
        self.AddLine(self.BeginEq() + text + self.EndEq())
    def _LaTeXMatrix(self,matrix):
        return Matrix2LaTeX(matrix,self.SmallMatrix())



