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
# Alex 20110201
# LyX child documents (included insets).

from elyxer.util.trace import Trace
from elyxer.parse.parser import *
from elyxer.parse.headerparse import *
from elyxer.out.output import *
from elyxer.io.bulk import *
from elyxer.gen.container import *
from elyxer.gen.styles import *
from elyxer.gen.layout import *
from elyxer.gen.float import *


class IncludeInset(Container):
  "A child document included within another."

  # the converter factory will be set in converter.py
  converterfactory = None
  filename = None

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def process(self):
    "Include the provided child document"
    self.filename = os.path.join(Options.directory, self.getparameter('filename'))
    Trace.debug('Child document: ' + self.filename)
    LstParser().parsecontainer(self)
    command = self.getparameter('LatexCommand')
    if command == 'verbatiminput':
      self.readverbatim()
      return
    elif command == 'lstinputlisting':
      self.readlisting()
      return
    self.processinclude()

  def processinclude(self):
    "Process a regular include: standard child document."
    self.contents = []
    olddir = Options.directory
    newdir = os.path.dirname(self.getparameter('filename'))
    if newdir != '':
      Trace.debug('Child dir: ' + newdir)
      Options.directory = os.path.join(Options.directory, newdir)
    try:
      self.convertinclude()
    finally:
      Options.directory = olddir

  def convertinclude(self):
    "Convert an included document."
    try:
      converter = IncludeInset.converterfactory.create(self)
    except:
      Trace.error('Could not read ' + self.filename + ', please check that the file exists and has read permissions.')
      return
    if self.hasemptyoutput():
      return
    converter.convert()
    self.contents = converter.getcontents()

  def readverbatim(self):
    "Read a verbatim document."
    self.contents = [TaggedText().complete(self.readcontents(), 'pre', True)]

  def readlisting(self):
    "Read a document as a listing."
    listing = Listing()
    listing.contents = self.readcontents()
    listing.parameters = self.parameters
    listing.process()
    self.contents = [listing]

  def readcontents(self):
    "Read the contents of a complete file."
    contents = list()
    lines = BulkFile(self.filename).readall()
    for line in lines:
      contents.append(Constant(line))
    return contents

  def __unicode__(self):
    "Return a printable description."
    if not self.filename:
      return 'Included unnamed file'
    return 'Included "' + self.filename + '"'

