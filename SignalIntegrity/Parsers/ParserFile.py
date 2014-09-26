import os

class ParserFile():
    def File(self,name):
        spfile=open(name,'rU')
        for line in spfile:
            self.AddLine(line)
        return self
    def WriteToFile(self,name,overWrite = True):
        if not os.path.exists(name) or overWrite:
            parserfile=open(name,'w')
            for line in self.m_lines:
                parserfile.write(line+'\n')
            parserfile.close()