"""
ParserFile.py
"""

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

import os
import sys

class ParserFile():
    """file handling base class for parsers"""
    def File(self,name):
        """reads a netlist from a file
        @param name string filename of file to read
        """
        with open(name,'rU' if sys.version_info.major < 3 else 'r') as f:
            for line in f.readlines(): self.AddLine(line)
        return self
    def WriteToFile(self,name,overWrite = True):
        """writes a netlist to a file
        @param name string name of file to write
        @param overWrite (optional) boolean whether to overwrite the file
        """
        if not os.path.exists(name) or overWrite:
            parserfile=open(name,'w')
            for line in self.m_lines: parserfile.write(line+'\n')
            parserfile.close()