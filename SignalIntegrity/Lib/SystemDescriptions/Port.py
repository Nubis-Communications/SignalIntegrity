"""
Port.py
"""
from __future__ import print_function

# Copyright (c) 2018 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

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
            print('\n','Node','Name')
        for t in range(3):
            if not t==0:
                if level >= 2:
                    print(repr('').strip('\'').rjust(6), end=' ')
                if level >= 1:
                    print(repr('').strip('\'').rjust(4), end=' ')
                    print(repr('').strip('\'').rjust(4), end=' ')
            if t==0:
                print(repr('A').rjust(4),repr(self.A).rjust(4))
            elif t==1:
                print(repr('B').rjust(4),repr(self.B).rjust(4))
            else:
                print(repr('M').rjust(4),repr(self.M).rjust(4))
