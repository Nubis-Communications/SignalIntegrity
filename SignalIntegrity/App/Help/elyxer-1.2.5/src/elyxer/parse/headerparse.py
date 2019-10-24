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
# Alex 20100509
# eLyXer: LyX header parsing.

from elyxer.util.trace import Trace
from elyxer.util.options import *
from elyxer.conf.config import *
from elyxer.parse.parser import *


class HeaderParser(Parser):
  "Parses the LyX header"

  def parse(self, reader):
    "Parse header parameters into a dictionary, return the preamble."
    contents = []
    self.parseending(reader, lambda: self.parseline(reader, contents))
    # skip last line
    reader.nextline()
    return contents

  def parseline(self, reader, contents):
    "Parse a single line as a parameter or as a start"
    line = reader.currentline()
    if line.startswith(HeaderConfig.parameters['branch']):
      self.parsebranch(reader)
      return
    elif line.startswith(HeaderConfig.parameters['lstset']):
      LstParser().parselstset(reader)
      return
    elif line.startswith(HeaderConfig.parameters['beginpreamble']):
      contents.append(self.factory.createcontainer(reader))
      return
    # no match
    self.parseparameter(reader)

  def parsebranch(self, reader):
    "Parse all branch definitions."
    branch = reader.currentline().split()[1]
    reader.nextline()
    subparser = HeaderParser().complete(HeaderConfig.parameters['endbranch'])
    subparser.parse(reader)
    options = BranchOptions(branch)
    for key in subparser.parameters:
      options.set(key, subparser.parameters[key])
    Options.branches[branch] = options

  def complete(self, ending):
    "Complete the parser with the given ending."
    self.ending = ending
    return self

class PreambleParser(Parser):
  "A parser for the LyX preamble."

  preamble = []

  def parse(self, reader):
    "Parse the full preamble with all statements."
    self.ending = HeaderConfig.parameters['endpreamble']
    self.parseending(reader, lambda: self.parsepreambleline(reader))
    return []

  def parsepreambleline(self, reader):
    "Parse a single preamble line."
    PreambleParser.preamble.append(reader.currentline())
    reader.nextline()

class LstParser(object):
  "Parse global and local lstparams."

  globalparams = dict()

  def parselstset(self, reader):
    "Parse a declaration of lstparams in lstset."
    paramtext = self.extractlstset(reader)
    if not '{' in paramtext:
      Trace.error('Missing opening bracket in lstset: ' + paramtext)
      return
    lefttext = paramtext.split('{')[1]
    croppedtext = lefttext[:-1]
    LstParser.globalparams = self.parselstparams(croppedtext)

  def extractlstset(self, reader):
    "Extract the global lstset parameters."
    paramtext = ''
    while not reader.finished():
      paramtext += reader.currentline()
      reader.nextline()
      if paramtext.endswith('}'):
        return paramtext
    Trace.error('Could not find end of \\lstset settings; aborting')

  def parsecontainer(self, container):
    "Parse some lstparams from elyxer.a container."
    container.lstparams = LstParser.globalparams.copy()
    paramlist = container.getparameterlist('lstparams')
    container.lstparams.update(self.parselstparams(paramlist))

  def parselstparams(self, paramlist):
    "Process a number of lstparams from elyxer.a list."
    paramdict = dict()
    for param in paramlist:
      if not '=' in param:
        if len(param.strip()) > 0:
          Trace.error('Invalid listing parameter ' + param)
      else:
        key, value = param.split('=', 1)
        paramdict[key] = value
    return paramdict


