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
# Alex 20110109
# eLyXer misc commands, invoked by class name from the configuration file.

from elyxer.util.numbering import *
from elyxer.maths.command import *
from elyxer.maths.extracommand import *
from elyxer.maths.macro import *


class SetCounterFunction(CommandBit):
  "A function which is used in the preamble to set a counter."

  def parsebit(self, pos):
    "Parse a function with [] and {} parameters."
    counter = self.parseliteral(pos)
    value = self.parseliteral(pos)
    try:
      self.setcounter(counter, int(value))
    except:
      Trace.error('Counter ' + counter + ' cannot be set to ' + value)

  def setcounter(self, counter, value):
    "Set a global counter."
    Trace.debug('Setting counter ' + unicode(counter) + ' to ' + unicode(value))
    NumberGenerator.generator.getcounter(counter).init(value)

class FormulaTag(CommandBit):
  "A \\tag command."

  def parsebit(self, pos):
    "Parse the tag and apply it."
    self.output = EmptyOutput()
    self.tag = self.parseliteral(pos)

class MiscCommand(CommandBit):
  "A generic command which maps to a command class."

  commandmap = FormulaConfig.misccommands

  def parsebit(self, pos):
    "Find the right command to parse and parse it."
    commandtype = globals()[self.translated]
    return self.parsecommandtype(self.translated, commandtype, pos)

FormulaCommand.types += [MiscCommand]

