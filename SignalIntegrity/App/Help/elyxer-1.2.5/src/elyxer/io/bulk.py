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
# Bulk file processing

import os
import codecs
from elyxer.io.fileline import *
from elyxer.util.trace import Trace


class BulkFile(object):
  "A file to treat in bulk"

  encodings = ['utf-8','Cp1252']

  def __init__(self, filename):
    self.filename = filename
    self.temp = self.filename + '.temp'

  def readall(self):
    "Read the whole file"
    for encoding in BulkFile.encodings:
      try:
        return self.readcodec(encoding)
      except UnicodeDecodeError:
        pass
    Trace.error('No suitable encoding for ' + self.filename)
    return []

  def readcodec(self, encoding):
    "Read the whole file with the given encoding"
    filein = codecs.open(self.filename, 'rU', encoding)
    lines = filein.readlines()
    result = []
    for line in lines:
      result.append(line.strip('\r\n') + '\n')
    filein.close()
    return result

  def getfiles(self):
    "Get reader and writer for a file name"
    reader = LineReader(self.filename)
    writer = LineWriter(self.temp)
    return reader, writer

  def swaptemp(self):
    "Swap the temp file for the original"
    os.chmod(self.temp, os.stat(self.filename).st_mode)
    os.rename(self.temp, self.filename)

  def __unicode__(self):
    "Get the unicode representation"
    return 'file ' + self.filename

