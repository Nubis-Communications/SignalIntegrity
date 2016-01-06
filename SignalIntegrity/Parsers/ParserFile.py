'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
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