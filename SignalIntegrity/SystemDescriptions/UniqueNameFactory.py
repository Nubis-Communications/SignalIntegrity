'''
 Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
 Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
 All Rights Reserved.

 Explicit license in accompanying README.txt file.  If you don't have that file
 or do not agree to the terms in that file, then you are not licensed to use
 this material whatsoever.
'''
class UniqueNameFactory:
    def __init__(self,prefix):
        self.m_UniqueNumber = 1
        self.m_Prefix = prefix
    def Name(self):
        Name = self.m_Prefix+str(self.m_UniqueNumber)
        self.m_UniqueNumber+=1
        return Name

