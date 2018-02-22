# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from Port import Port
from SignalIntegrity.PySIException import PySIExceptionSystemDescription

class Device(object):
    def __init__(self,Name,Ports,Type='device'):
        self.Name = Name
        self.Ports = [Port() for p in range(Ports)]
        self.SParameters = self.SymbolicMatrix(Name,Ports)
        self.Type=Type
    def __getitem__(self,item):
        return self.Ports[item]
    def __len__(self):
        return len(self.Ports)
    def AssignSParameters(self,SParameters):
        # pragma: silent exclude
        if len(SParameters) != len(SParameters[0]) or len(SParameters) != len(self.Ports):
            raise PySIExceptionSystemDescription('illegal s-parameter assignment')
        # pragma: include
        self.SParameters=SParameters
    @staticmethod
    def SymbolicMatrix(Name,Rows,Columns=-1):
        if Columns == -1:
            Columns = Rows
        if Rows == 1 and Columns == 1:
            return [[Name]]
        return [[Name+'_'+(str(r+1)+str(c+1) if r<9 and c<9 else str(r+1)+','+str(c+1))
                for c in range(Columns)] for r in range(Rows)]
    def Print(self,level=0):
        if level==0:
            print '\n','Name','Port','Node','Name'
        for p in range(len(self)):
            if p==0:
                print repr(self.Name).rjust(4),
            else:
                if level==1:
                    print repr('').strip('\'').rjust(6),
                print repr('').strip('\'').rjust(4),
            print repr(p+1).rjust(4),
            self[p].Print(level+1)
