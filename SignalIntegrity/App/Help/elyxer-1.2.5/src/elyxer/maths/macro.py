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
# Alex 20100615
# eLyXer macro processing

from elyxer.util.trace import Trace
from elyxer.conf.config import *
from elyxer.parse.formulaparse import *
from elyxer.parse.headerparse import *
from elyxer.maths.formula import *
from elyxer.maths.hybrid import *


class MacroDefinition(CommandBit):
  "A function that defines a new command (a macro)."

  macros = dict()

  def parsebit(self, pos):
    "Parse the function that defines the macro."
    self.output = EmptyOutput()
    self.parameternumber = 0
    self.defaults = []
    self.factory.defining = True
    self.parseparameters(pos)
    self.factory.defining = False
    Trace.debug('New command ' + self.newcommand + ' (' + \
        unicode(self.parameternumber) + ' parameters)')
    self.macros[self.newcommand] = self

  def parseparameters(self, pos):
    "Parse all optional parameters (number of parameters, default values)"
    "and the mandatory definition."
    self.newcommand = self.parsenewcommand(pos)
    # parse number of parameters
    literal = self.parsesquareliteral(pos)
    if literal:
      self.parameternumber = int(literal)
    # parse all default values
    bracket = self.parsesquare(pos)
    while bracket:
      self.defaults.append(bracket)
      bracket = self.parsesquare(pos)
    # parse mandatory definition
    self.definition = self.parseparameter(pos)

  def parsenewcommand(self, pos):
    "Parse the name of the new command."
    self.factory.clearskipped(pos)
    if self.factory.detecttype(Bracket, pos):
      return self.parseliteral(pos)
    if self.factory.detecttype(FormulaCommand, pos):
      return self.factory.create(FormulaCommand).extractcommand(pos)
    Trace.error('Unknown formula bit in defining function at ' + pos.identifier())
    return 'unknown'

  def instantiate(self):
    "Return an instance of the macro."
    return self.definition.clone()

class MacroParameter(FormulaBit):
  "A parameter from elyxer.a macro."

  def detect(self, pos):
    "Find a macro parameter: #n."
    return pos.checkfor('#')

  def parsebit(self, pos):
    "Parse the parameter: #n."
    if not pos.checkskip('#'):
      Trace.error('Missing parameter start #.')
      return
    self.number = int(pos.skipcurrent())
    self.original = '#' + unicode(self.number)
    self.contents = [TaggedBit().constant('#' + unicode(self.number), 'span class="unknown"')]

class MacroFunction(CommandBit):
  "A function that was defined using a macro."

  commandmap = MacroDefinition.macros

  def parsebit(self, pos):
    "Parse a number of input parameters."
    self.output = FilteredOutput()
    self.values = []
    macro = self.translated
    self.parseparameters(pos, macro)
    self.completemacro(macro)

  def parseparameters(self, pos, macro):
    "Parse as many parameters as are needed."
    self.parseoptional(pos, list(macro.defaults))
    self.parsemandatory(pos, macro.parameternumber - len(macro.defaults))
    if len(self.values) < macro.parameternumber:
      Trace.error('Missing parameters in macro ' + unicode(self))

  def parseoptional(self, pos, defaults):
    "Parse optional parameters."
    optional = []
    while self.factory.detecttype(SquareBracket, pos):
      optional.append(self.parsesquare(pos))
      if len(optional) > len(defaults):
        break
    for value in optional:
      default = defaults.pop()
      if len(value.contents) > 0:
        self.values.append(value)
      else:
        self.values.append(default)
    self.values += defaults

  def parsemandatory(self, pos, number):
    "Parse a number of mandatory parameters."
    for index in range(number):
      parameter = self.parsemacroparameter(pos, number - index)
      if not parameter:
        return
      self.values.append(parameter)

  def parsemacroparameter(self, pos, remaining):
    "Parse a macro parameter. Could be a bracket or a single letter."
    "If there are just two values remaining and there is a running number,"
    "parse as two separater numbers."
    self.factory.clearskipped(pos)
    if pos.finished():
      return None
    if self.factory.detecttype(FormulaNumber, pos):
      return self.parsenumbers(pos, remaining)
    return self.parseparameter(pos)

  def parsenumbers(self, pos, remaining):
    "Parse the remaining parameters as a running number."
    "For example, 12 would be {1}{2}."
    number = self.factory.parsetype(FormulaNumber, pos)
    if not len(number.original) == remaining:
      return number
    for digit in number.original:
      value = self.factory.create(FormulaNumber)
      value.add(FormulaConstant(digit))
      value.type = number
      self.values.append(value)
    return None

  def completemacro(self, macro):
    "Complete the macro with the parameters read."
    self.contents = [macro.instantiate()]
    replaced = [False] * len(self.values)
    for parameter in self.searchall(MacroParameter):
      index = parameter.number - 1
      if index >= len(self.values):
        Trace.error('Macro parameter index out of bounds: ' + unicode(index))
        return
      replaced[index] = True
      parameter.contents = [self.values[index].clone()]
    for index in range(len(self.values)):
      if not replaced[index]:
        self.addfilter(index, self.values[index])

  def addfilter(self, index, value):
    "Add a filter for the given parameter number and parameter value."
    original = '#' + unicode(index + 1)
    value = ''.join(self.values[0].gethtml())
    self.output.addfilter(original, value)

class FormulaMacro(Formula):
  "A math macro defined in an inset."

  def __init__(self):
    self.parser = MacroParser()
    self.output = EmptyOutput()

  def __unicode__(self):
    "Return a printable representation."
    return 'Math macro'

FormulaFactory.types += [ MacroParameter ]

FormulaCommand.types += [
    MacroFunction,
    ]

