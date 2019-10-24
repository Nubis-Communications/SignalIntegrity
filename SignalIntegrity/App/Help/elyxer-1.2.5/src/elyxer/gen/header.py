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
# Alex 20090312
# LyX structure in containers

from elyxer.util.docparams import *
from elyxer.parse.parser import *
from elyxer.parse.headerparse import *
from elyxer.out.output import *
from elyxer.out.template import *
from elyxer.gen.container import *
from elyxer.ref.partkey import *
from elyxer.maths.command import *
from elyxer.maths.macro import *
from elyxer.gen.notes import *


class LyXHeader(Container):
  "Reads the header, outputs the HTML header"

  def __init__(self):
    self.contents = []
    self.parser = HeaderParser()
    self.output = HeaderOutput()
    self.parameters = dict()
    self.partkey = PartKey().createheader('header')

  def process(self):
    "Find pdf title"
    DocumentParameters.pdftitle = self.getheaderparameter('pdftitle')
    documentclass = self.getheaderparameter('documentclass')
    if documentclass in HeaderConfig.styles['article']:
      DocumentParameters.startinglevel = 1
    if documentclass in HeaderConfig.styles['book']:
      DocumentParameters.bibliography = 'bibliography'
    else:
      DocumentParameters.bibliography = 'references'
    if self.getheaderparameter('paragraphseparation') == 'indent':
      DocumentParameters.indentstandard = True
    DocumentParameters.tocdepth = self.getlevel('tocdepth')
    DocumentParameters.maxdepth = self.getlevel('secnumdepth')
    DocumentParameters.language = self.getheaderparameter('language')
    if self.getheaderparameter('outputchanges') == 'true':
      DocumentParameters.outputchanges = True
    return self

  def getheaderparameter(self, configparam):
    "Get a parameter configured in HeaderConfig."
    key = HeaderConfig.parameters[configparam]
    if not key in self.parameters:
      return None
    return self.parameters[key]

  def getlevel(self, configparam):
    "Get a level read as a parameter from elyxer.HeaderConfig."
    paramvalue = self.getheaderparameter(configparam)
    if not paramvalue:
      return 0
    value = int(paramvalue)
    if DocumentParameters.startinglevel == 1:
      return value
    return value + 1

class LyXPreamble(Container):
  "The preamble at the beginning of a LyX file. Parsed for macros."

  def __init__(self):
    self.parser = PreambleParser()
    self.output = EmptyOutput()
    self.factory = FormulaFactory()

  def process(self):
    "Parse the LyX preamble, if needed."
    if len(PreambleParser.preamble) == 0:
      return
    pos = TextPosition('\n'.join(PreambleParser.preamble))
    while not pos.finished():
      if self.detectfunction(pos):
        self.parsefunction(pos)
      else:
        pos.globincluding('\n')
    PreambleParser.preamble = []

  def detectfunction(self, pos):
    "Detect a macro definition or a preamble function."
    for function in FormulaConfig.misccommands:
      if pos.checkfor(function):
        return True
    return False

  def parsefunction(self, pos):
    "Parse a single command."
    self.factory.parsetype(FormulaCommand, pos)

class LyXFooter(Container):
  "Reads the footer, outputs the HTML footer"

  def __init__(self):
    self.contents = []
    self.parser = BoundedDummy()
    self.output = FooterOutput()
    self.partkey = PartKey().createheader('footer')

  def process(self):
    "Include any footnotes at the end."
    if EndFootnotes.footnotes:
      endnotes = EndFootnotes()
      self.contents = [endnotes]

