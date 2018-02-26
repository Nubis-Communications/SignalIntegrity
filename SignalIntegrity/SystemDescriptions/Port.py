# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

class Port(object):
    """port connections of a device
    
    a port defines the node names of the incident, reflect and stimulus
    on a port of a device."""
    def __init__(self):
        """Constructor"""
        self.A=''
        self.B=''
        self.M=''
    def IsConnected(self):
        """whether a device port is connected
        @return boolean whether port is connected to anything.
        """
        return self.A != ''
    def Print(self,level=0):
        """print an ascii description of the port connections
        @param level (optional) level to print at.  This affects the indentation.
        when called to just print a port, use the default argument, otherwise, when
        it's printed by printing a system description, it will be indented for each
        port in each device.
        """
        if level==0:
            print '\n','Node','Name'
        for t in range(3):
            if not t==0:
                if level >= 2:
                    print repr('').strip('\'').rjust(6),
                if level >= 1:
                    print repr('').strip('\'').rjust(4),
                    print repr('').strip('\'').rjust(4),
            if t==0:
                print repr('A').rjust(4),repr(self.A).rjust(4)
            elif t==1:
                print repr('B').rjust(4),repr(self.B).rjust(4)
            else:
                print repr('M').rjust(4),repr(self.M).rjust(4)
