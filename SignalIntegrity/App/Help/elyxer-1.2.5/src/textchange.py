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
# Alex 20090416
# Change text in some files at once

import sys
from elyxer.io.fileline import *
from elyxer.io.bulk import *
from elyxer.util.trace import Trace
from elyxer.util.clparse import *


class TextChange(object):
  "A change in some text"

  def __init__(self, key, value):
    self.key = key
    self.value = value

  def affects(self, line):
    "Decide if the change affects the line"
    if self.key in line:
      return True
    return False

  def do(self, line):
    "Change the text in the line"
    return line.replace(self.key, self.value)

def process(reader, writer, change):
  "Change all lines in the file"
  counter = 0
  while not reader.finished():
    line = reader.currentline()
    if change.affects(line):
      line = change.do(line)
      counter += 1
    writer.writeline(line)
    reader.nextline()
  reader.close()
  return counter

def processall(args):
  "Process all arguments"
  del args[0]
  if len(args) < 3:
    Trace.error('Usage: textchange.py original changed [file...]')
    return
  original = args[0]
  del args[0]
  changed = args[0]
  del args[0]
  Trace.message('Replacing ' + original + '->' + changed)
  change = TextChange(original, changed)
  total = 0
  while len(args) > 0:
    pythonfile = BulkFile(args[0])
    reader, writer = pythonfile.getfiles()
    del args[0]
    counter = process(reader, writer, change)
    total += counter
    Trace.message('  ' + unicode(counter) + ' occurrences in ' +
        unicode(pythonfile))
    pythonfile.swaptemp()
  Trace.message('Total replacements: ' + unicode(total))

processall(sys.argv)

