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
# Alex 20090614
# eLyXer formula bits

from elyxer.util.trace import Trace
from elyxer.conf.config import *
from elyxer.maths.formula import *


class FormulaBit(Container):
  "A bit of a formula"

  type = None
  size = 1
  original = ''

  def __init__(self):
    "The formula bit type can be 'alpha', 'number', 'font'."
    self.contents = []
    self.output = ContentsOutput()

  def setfactory(self, factory):
    "Set the internal formula factory."
    self.factory = factory
    return self

  def add(self, bit):
    "Add any kind of formula bit already processed"
    self.contents.append(bit)
    self.original += bit.original
    bit.parent = self

  def skiporiginal(self, string, pos):
    "Skip a string and add it to the original formula"
    self.original += string
    if not pos.checkskip(string):
      Trace.error('String ' + string + ' not at ' + pos.identifier())

  def computesize(self):
    "Compute the size of the bit as the max of the sizes of all contents."
    if len(self.contents) == 0:
      return 1
    self.size = max([element.size for element in self.contents])
    return self.size

  def clone(self):
    "Return a copy of itself."
    return self.factory.parseformula(self.original)

  def __unicode__(self):
    "Get a string representation"
    return self.__class__.__name__ + ' read in ' + self.original

class TaggedBit(FormulaBit):
  "A tagged string in a formula"

  def constant(self, constant, tag):
    "Set the constant and the tag"
    self.output = TaggedOutput().settag(tag)
    self.add(FormulaConstant(constant))
    return self

  def complete(self, contents, tag, breaklines = False):
    "Set the constant and the tag"
    self.contents = contents
    self.output = TaggedOutput().settag(tag, breaklines)
    return self

  def selfcomplete(self, tag):
    "Set the self-closing tag, no contents (as in <hr/>)."
    self.output = TaggedOutput().settag(tag, empty = True)
    return self

class FormulaConstant(Constant):
  "A constant string in a formula"

  def __init__(self, string):
    "Set the constant string"
    Constant.__init__(self, string)
    self.original = string
    self.size = 1
    self.type = None

  def computesize(self):
    "Compute the size of the constant: always 1."
    return self.size

  def clone(self):
    "Return a copy of itself."
    return FormulaConstant(self.original)

  def __unicode__(self):
    "Return a printable representation."
    return 'Formula constant: ' + self.string

class RawText(FormulaBit):
  "A bit of text inside a formula"

  def detect(self, pos):
    "Detect a bit of raw text"
    return pos.current().isalpha()

  def parsebit(self, pos):
    "Parse alphabetic text"
    alpha = pos.globalpha()
    self.add(FormulaConstant(alpha))
    self.type = 'alpha'

class FormulaSymbol(FormulaBit):
  "A symbol inside a formula"

  modified = FormulaConfig.modified
  unmodified = FormulaConfig.unmodified['characters']

  def detect(self, pos):
    "Detect a symbol"
    if pos.current() in FormulaSymbol.unmodified:
      return True
    if pos.current() in FormulaSymbol.modified:
      return True
    return False

  def parsebit(self, pos):
    "Parse the symbol"
    if pos.current() in FormulaSymbol.unmodified:
      self.addsymbol(pos.current(), pos)
      return
    if pos.current() in FormulaSymbol.modified:
      self.addsymbol(FormulaSymbol.modified[pos.current()], pos)
      return
    Trace.error('Symbol ' + pos.current() + ' not found')

  def addsymbol(self, symbol, pos):
    "Add a symbol"
    self.skiporiginal(pos.current(), pos)
    self.contents.append(FormulaConstant(symbol))

class FormulaNumber(FormulaBit):
  "A string of digits in a formula"

  def detect(self, pos):
    "Detect a digit"
    return pos.current().isdigit()

  def parsebit(self, pos):
    "Parse a bunch of digits"
    digits = pos.glob(lambda: pos.current().isdigit())
    self.add(FormulaConstant(digits))
    self.type = 'number'

class Comment(FormulaBit):
  "A LaTeX comment: % to the end of the line."

  start = FormulaConfig.starts['comment']

  def detect(self, pos):
    "Detect the %."
    return pos.current() == self.start

  def parsebit(self, pos):
    "Parse to the end of the line."
    self.original += pos.globincluding('\n')

class WhiteSpace(FormulaBit):
  "Some white space inside a formula."

  def detect(self, pos):
    "Detect the white space."
    return pos.current().isspace()

  def parsebit(self, pos):
    "Parse all whitespace."
    self.original += pos.skipspace()

  def __unicode__(self):
    "Return a printable representation."
    return 'Whitespace: *' + self.original + '*'

class Bracket(FormulaBit):
  "A {} bracket inside a formula"

  start = FormulaConfig.starts['bracket']
  ending = FormulaConfig.endings['bracket']

  def __init__(self):
    "Create a (possibly literal) new bracket"
    FormulaBit.__init__(self)
    self.inner = None

  def detect(self, pos):
    "Detect the start of a bracket"
    return pos.checkfor(self.start)

  def parsebit(self, pos):
    "Parse the bracket"
    self.parsecomplete(pos, self.innerformula)
    return self

  def parsetext(self, pos):
    "Parse a text bracket"
    self.parsecomplete(pos, self.innertext)
    return self

  def parseliteral(self, pos):
    "Parse a literal bracket"
    self.parsecomplete(pos, self.innerliteral)
    return self

  def parsecomplete(self, pos, innerparser):
    "Parse the start and end marks"
    if not pos.checkfor(self.start):
      Trace.error('Bracket should start with ' + self.start + ' at ' + pos.identifier())
      return None
    self.skiporiginal(self.start, pos)
    pos.pushending(self.ending)
    innerparser(pos)
    self.original += pos.popending(self.ending)
    self.computesize()

  def innerformula(self, pos):
    "Parse a whole formula inside the bracket"
    while not pos.finished():
      self.add(self.factory.parseany(pos))

  def innertext(self, pos):
    "Parse some text inside the bracket, following textual rules."
    specialchars = FormulaConfig.symbolfunctions.keys()
    specialchars.append(FormulaConfig.starts['command'])
    specialchars.append(FormulaConfig.starts['bracket'])
    specialchars.append(Comment.start)
    while not pos.finished():
      if pos.current() in specialchars:
        self.add(self.factory.parseany(pos))
        if pos.checkskip(' '):
          self.original += ' '
      else:
        self.add(FormulaConstant(pos.skipcurrent()))

  def innerliteral(self, pos):
    "Parse a literal inside the bracket, which does not generate HTML."
    self.literal = ''
    while not pos.finished() and not pos.current() == self.ending:
      if pos.current() == self.start:
        self.parseliteral(pos)
      else:
        self.literal += pos.skipcurrent()
    self.original += self.literal

class SquareBracket(Bracket):
  "A [] bracket inside a formula"

  start = FormulaConfig.starts['squarebracket']
  ending = FormulaConfig.endings['squarebracket']

  def clone(self):
    "Return a new square bracket with the same contents."
    bracket = SquareBracket()
    bracket.contents = self.contents
    return bracket

