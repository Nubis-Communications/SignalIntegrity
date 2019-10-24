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
# Alex 20090330
# eLyXer commands in formula processing

import unicodedata
from elyxer.gen.container import *
from elyxer.ref.label import *
from elyxer.util.trace import Trace
from elyxer.util.clone import *
from elyxer.conf.config import *
from elyxer.maths.formula import *
from elyxer.maths.bits import *


class FormulaCommand(FormulaBit):
  "A LaTeX command inside a formula"

  types = []
  start = FormulaConfig.starts['command']
  commandmap = None

  def detect(self, pos):
    "Find the current command."
    return pos.checkfor(FormulaCommand.start)

  def parsebit(self, pos):
    "Parse the command."
    command = self.extractcommand(pos)
    bit = self.parsewithcommand(command, pos)
    if bit:
      return bit
    if command.startswith('\\up') or command.startswith('\\Up'):
      upgreek = self.parseupgreek(command, pos)
      if upgreek:
        return upgreek
    if not self.factory.defining:
      Trace.error('Unknown command ' + command)
    self.output = TaggedOutput().settag('span class="unknown"')
    self.add(FormulaConstant(command))
    return None

  def parsewithcommand(self, command, pos):
    "Parse the command type once we have the command."
    for type in FormulaCommand.types:
      if command in type.commandmap:
        return self.parsecommandtype(command, type, pos)
    return None

  def parsecommandtype(self, command, type, pos):
    "Parse a given command type."
    bit = self.factory.create(type)
    bit.setcommand(command)
    returned = bit.parsebit(pos)
    if returned:
      return returned
    return bit

  def extractcommand(self, pos):
    "Extract the command from elyxer.the current position."
    if not pos.checkskip(FormulaCommand.start):
      pos.error('Missing command start ' + FormulaCommand.start)
      return
    if pos.finished():
      return self.emptycommand(pos)
    if pos.current().isalpha():
      # alpha command
      command = FormulaCommand.start + pos.globalpha()
      # skip mark of short command
      pos.checkskip('*')
      return command
    # symbol command
    return FormulaCommand.start + pos.skipcurrent()

  def emptycommand(self, pos):
    """Check for an empty command: look for command disguised as ending.
    Special case against '{ \{ \} }' situation."""
    command = ''
    if not pos.isout():
      ending = pos.nextending()
      if ending and pos.checkskip(ending):
        command = ending
    return FormulaCommand.start + command

  def parseupgreek(self, command, pos):
    "Parse the Greek \\up command.."
    if len(command) < 4:
      return None
    if command.startswith('\\up'):
      upcommand = '\\' + command[3:]
    elif pos.checkskip('\\Up'):
      upcommand = '\\' + command[3:4].upper() + command[4:]
    else:
      Trace.error('Impossible upgreek command: ' + command)
      return
    upgreek = self.parsewithcommand(upcommand, pos)
    if upgreek:
      upgreek.type = 'font'
    return upgreek

class CommandBit(FormulaCommand):
  "A formula bit that includes a command"

  def setcommand(self, command):
    "Set the command in the bit"
    self.command = command
    if self.commandmap:
      self.original += command
      self.translated = self.commandmap[self.command]
 
  def parseparameter(self, pos):
    "Parse a parameter at the current position"
    self.factory.clearskipped(pos)
    if pos.finished():
      return None
    parameter = self.factory.parseany(pos)
    self.add(parameter)
    return parameter

  def parsesquare(self, pos):
    "Parse a square bracket"
    self.factory.clearskipped(pos)
    if not self.factory.detecttype(SquareBracket, pos):
      return None
    bracket = self.factory.parsetype(SquareBracket, pos)
    self.add(bracket)
    return bracket

  def parseliteral(self, pos):
    "Parse a literal bracket."
    self.factory.clearskipped(pos)
    if not self.factory.detecttype(Bracket, pos):
      if not pos.isvalue():
        Trace.error('No literal parameter found at: ' + pos.identifier())
        return None
      return pos.globvalue()
    bracket = Bracket().setfactory(self.factory)
    self.add(bracket.parseliteral(pos))
    return bracket.literal

  def parsesquareliteral(self, pos):
    "Parse a square bracket literally."
    self.factory.clearskipped(pos)
    if not self.factory.detecttype(SquareBracket, pos):
      return None
    bracket = SquareBracket().setfactory(self.factory)
    self.add(bracket.parseliteral(pos))
    return bracket.literal

  def parsetext(self, pos):
    "Parse a text parameter."
    self.factory.clearskipped(pos)
    if not self.factory.detecttype(Bracket, pos):
      Trace.error('No text parameter for ' + self.command)
      return None
    bracket = Bracket().setfactory(self.factory).parsetext(pos)
    self.add(bracket)
    return bracket

class EmptyCommand(CommandBit):
  "An empty command (without parameters)"

  commandmap = FormulaConfig.commands

  def parsebit(self, pos):
    "Parse a command without parameters"
    self.contents = [FormulaConstant(self.translated)]

class SpacedCommand(CommandBit):
  "An empty command which should have math spacing in formulas."

  commandmap = FormulaConfig.spacedcommands

  def parsebit(self, pos):
    "Place as contents the command translated and spaced."
    self.contents = [FormulaConstant(u' ' + self.translated + u' ')]

class AlphaCommand(EmptyCommand):
  "A command without paramters whose result is alphabetical"

  commandmap = FormulaConfig.alphacommands

  def parsebit(self, pos):
    "Parse the command and set type to alpha"
    EmptyCommand.parsebit(self, pos)
    self.type = 'alpha'

class OneParamFunction(CommandBit):
  "A function of one parameter"

  commandmap = FormulaConfig.onefunctions
  simplified = False

  def parsebit(self, pos):
    "Parse a function with one parameter"
    self.output = TaggedOutput().settag(self.translated)
    self.parseparameter(pos)
    self.simplifyifpossible()

  def simplifyifpossible(self):
    "Try to simplify to a single character."
    if self.original in self.commandmap:
      self.output = FixedOutput()
      self.html = [self.commandmap[self.original]]
      self.simplified = True

class SymbolFunction(CommandBit):
  "Find a function which is represented by a symbol (like _ or ^)"

  commandmap = FormulaConfig.symbolfunctions

  def detect(self, pos):
    "Find the symbol"
    return pos.current() in SymbolFunction.commandmap

  def parsebit(self, pos):
    "Parse the symbol"
    self.setcommand(pos.current())
    pos.skip(self.command)
    self.output = TaggedOutput().settag(self.translated)
    self.parseparameter(pos)

class TextFunction(CommandBit):
  "A function where parameters are read as text."

  commandmap = FormulaConfig.textfunctions

  def parsebit(self, pos):
    "Parse a text parameter"
    self.output = TaggedOutput().settag(self.translated)
    self.parsetext(pos)

  def process(self):
    "Set the type to font"
    self.type = 'font'

class LabelFunction(CommandBit):
  "A function that acts as a label"

  commandmap = FormulaConfig.labelfunctions

  def parsebit(self, pos):
    "Parse a literal parameter"
    self.key = self.parseliteral(pos)

  def process(self):
    "Add an anchor with the label contents."
    self.type = 'font'
    self.label = Label().create(' ', self.key, type = 'eqnumber')
    self.contents = [self.label]
    # store as a Label so we know it's been seen
    Label.names[self.key] = self.label

class FontFunction(OneParamFunction):
  "A function of one parameter that changes the font"

  commandmap = FormulaConfig.fontfunctions

  def process(self):
    "Simplify if possible using a single character."
    self.type = 'font'
    self.simplifyifpossible()

FormulaFactory.types += [FormulaCommand, SymbolFunction]
FormulaCommand.types = [
    AlphaCommand, EmptyCommand, OneParamFunction, FontFunction, LabelFunction,
    TextFunction, SpacedCommand,
    ]

