class Symbolic():
    def __init__(self,equationEnvironment=False,small=False):
        self.m_lines=[]
        self.m_docStart = '\\documentclass[10pt]{article}\\usepackage{amsmath}\\begin{document}'
        self.m_docEnd = '\\end{document}'
        self.m_eqPrefix='\\[ '
        self.m_eqSuffix=' \\]'
        self.m_eqEnvironment = equationEnvironment
        self.m_small=False
    def Clear(self):
        self.m_lines=[]
        return self
    def Print(self):
        for line in self.m_lines:
            print line
        return self
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
        self.m_lines.append(line)
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
