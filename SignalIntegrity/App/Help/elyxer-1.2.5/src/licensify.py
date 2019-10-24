#! /usr/bin/env python
# -*- coding: utf-8 -*-

#   eLyXer -- convert LyX source files to HTML output.
#
#   Copyright (C) 2009 Alex Fernández
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# --end--
# Alex 20090314
# Modifies the license of a Python source file

import sys
from elyxer.io.fileline import *
from elyxer.io.bulk import *
from elyxer.util.trace import Trace


mark = '--end--'

def process(reader, writer, license):
  "Conflate all Python files used in filein to fileout"
  for line in license:
    writer.writestring(line)
  while not mark in reader.currentline():
    reader.nextline()
  while not reader.finished():
    line = reader.currentline()
    writer.writeline(line)
    reader.nextline()
  reader.close()

def processall(args):
  "Process all arguments"
  del args[0]
  if len(args) == 0:
    Trace.error('Usage: licensify.py licensefile [file...]')
    return
  licensefile = BulkFile(args[0])
  license = licensefile.readall()
  del args[0]
  while len(args) > 0:
    pythonfile = BulkFile(args[0])
    reader, writer = pythonfile.getfiles()
    del args[0]
    process(reader, writer, license)
    pythonfile.swaptemp()

processall(sys.argv)

