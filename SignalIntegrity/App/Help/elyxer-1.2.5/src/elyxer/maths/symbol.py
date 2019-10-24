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
# Alex 20101218
# eLyXer big symbol generation.

from elyxer.util.trace import Trace
from elyxer.util.docparams import *
from elyxer.conf.config import *
from elyxer.maths.bits import *


class BigSymbol(object):
  "A big symbol generator."

  symbols = FormulaConfig.bigsymbols

  def __init__(self, symbol):
    "Create the big symbol."
    self.symbol = symbol

  def getpieces(self):
    "Get an array with all pieces."
    if not self.symbol in self.symbols:
      return [self.symbol]
    if self.smalllimit():
      return [self.symbol]
    return self.symbols[self.symbol]

  def smalllimit(self):
    "Decide if the limit should be a small, one-line symbol."
    if not DocumentParameters.displaymode:
      return True
    if len(self.symbols[self.symbol]) == 1:
      return True
    return Options.simplemath

class BigBracket(BigSymbol):
  "A big bracket generator."

  def __init__(self, size, bracket, alignment='l'):
    "Set the size and symbol for the bracket."
    self.size = size
    self.original = bracket
    self.alignment = alignment
    self.pieces = None
    if bracket in FormulaConfig.bigbrackets:
      self.pieces = FormulaConfig.bigbrackets[bracket]

  def getpiece(self, index):
    "Return the nth piece for the bracket."
    function = getattr(self, 'getpiece' + unicode(len(self.pieces)))
    return function(index)

  def getpiece1(self, index):
    "Return the only piece for a single-piece bracket."
    return self.pieces[0]

  def getpiece3(self, index):
    "Get the nth piece for a 3-piece bracket: parenthesis or square bracket."
    if index == 0:
      return self.pieces[0]
    if index == self.size - 1:
      return self.pieces[-1]
    return self.pieces[1]

  def getpiece4(self, index):
    "Get the nth piece for a 4-piece bracket: curly bracket."
    if index == 0:
      return self.pieces[0]
    if index == self.size - 1:
      return self.pieces[3]
    if index == (self.size - 1)/2:
      return self.pieces[2]
    return self.pieces[1]

  def getcell(self, index):
    "Get the bracket piece as an array cell."
    piece = self.getpiece(index)
    span = 'span class="bracket align-' + self.alignment + '"'
    return TaggedBit().constant(piece, span)

  def getcontents(self):
    "Get the bracket as an array or as a single bracket."
    if self.size == 1 or not self.pieces:
      return self.getsinglebracket()
    rows = []
    for index in range(self.size):
      cell = self.getcell(index)
      rows.append(TaggedBit().complete([cell], 'span class="arrayrow"'))
    return [TaggedBit().complete(rows, 'span class="array"')]

  def getsinglebracket(self):
    "Return the bracket as a single sign."
    if self.original == '.':
      return [TaggedBit().constant('', 'span class="emptydot"')]
    return [TaggedBit().constant(self.original, 'span class="symbol"')]

