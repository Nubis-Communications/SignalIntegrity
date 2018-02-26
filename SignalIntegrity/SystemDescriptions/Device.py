# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from Port import Port
from SignalIntegrity.PySIException import PySIExceptionSystemDescription

class Device(list):
    """device in system descriptions

    a device is fundamentally a list of ports
    """
    def __init__(self,Name,Ports,Type='device'):
        """Constructor
        @param Name string unique name of device
        @param Ports integer number of ports in device
        @param Type (optional) string type of device
        @note valid types of devices are:
        - 'device' - a normal device in a system description.
        - 'unknown' - a device whose s-parameters are unknown used in a deembedding
        solution.
        """
        self.Name = Name
        list.__init__(self,[Port() for _ in range(Ports)])
        self.SParameters = self.SymbolicMatrix(Name,Ports)
        self.Type=Type
    def AssignSParameters(self,SParameters):
        """assign s-parameters to the device
        @param SParameters list of list s-parameter matrix
        @note SParameters can be either list of list of complex numbers for numeric
        solutions or list of list of strings for symbolic solutions.  Strings can
        be LaTeX strings.
        """
        # pragma: silent exclude
        if len(SParameters) != len(SParameters[0]) or len(SParameters) != len(self):
            raise PySIExceptionSystemDescription('illegal s-parameter assignment')
        # pragma: include
        self.SParameters=SParameters
    @staticmethod
    def SymbolicMatrix(Name,Rows,Columns=-1):
        """creates a symbolic matrix

        The matrix is of a simple form.  It is a list of list of strings where the
        string is either:
        - rows=columns=1 - [[name]]
        - rows <= 9 and columns <= 9 - list of list of name+'_'+str(r+1)+str(c+1)
        @note if a row or column goes above 9, a comma is inserted between the port numbers
        to remove ambiguity.
        @param Name string name of device
        @param Rows integer number of rows in the matrix
        @param Columns (optional) integer number of columns in the matrix (defaults
        to the number of rows).
        """
        if Columns == -1:
            Columns = Rows
        if Rows == 1 and Columns == 1:
            return [[Name]]
        return [[Name+'_'+(str(r+1)+str(c+1) if r<9 and c<9 else str(r+1)+','+str(c+1))
                for c in range(Columns)] for r in range(Rows)]
    def Print(self,level=0):
        """print an ascii description of the device
        @param level (optional) level to print at.  This affects the indentation.
        when called to just print a device, use the default argument, otherwise, when
        it's printed by printing a system description, it will be indented for each
        device.
        """
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
