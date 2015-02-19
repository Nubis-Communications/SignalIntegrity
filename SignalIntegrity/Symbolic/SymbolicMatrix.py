from SignalIntegrity.Helpers import Matrix2LaTeX

class SymbolicMatrix():
    def __init__(self,matrix,varname=None,equationEnvironment=False,small=False,doc=False):
        self.m_lines=[]
        self.m_docStart = '\\documentclass[10pt]{article}\\usepackage{amsmath}\\begin{document}'
        self.m_docEnd = '\\end{document}'
        self.m_eqPrefix='\\[ '
        self.m_eqSuffix=' \\]'
        self.m_eqEnvironment = equationEnvironment
        self.m_small=small
        self.m_doc=doc
        self.m_matrix=matrix
        self.m_varname=varname
    def _BuildString(self):
        self._Clear()
        if (self.m_doc):
            self._AddLine(self.m_docStart)
        line=''
        if (self.m_eqEnvironment):
            line = line + self.m_eqPrefix
        if not self.m_varname is None:
            line = line + self.m_varname + ' = '
        line = line +  Matrix2LaTeX(self.m_matrix,self.m_small)
        if (self.m_eqEnvironment):
            line = line + self.m_eqSuffix
        self._AddLine(line)
        if (self.m_doc):
            self._AddLine(self.m_docEnd)
    def _Clear(self):
        self.m_lines=[]
        return self
    def Emit(self):
        self._BuildString()
        for line in self.m_lines:
            print line
        return self
    def _AddLine(self,line):
        if len(line) == 0:
            return
        self.m_lines.append(line)
        return self
    def WriteToFile(self,name):
        self._BuildString()
        equationFile=open(name,'w')
        for line in self.m_lines:
            equationFile.write(line+'\n')
        equationFile.close()
    def Get(self):
        self._BuildString()
        lineBuffer=''
        for line in self.m_lines:
            lineBuffer=lineBuffer+line+'\n'
        return lineBuffer

