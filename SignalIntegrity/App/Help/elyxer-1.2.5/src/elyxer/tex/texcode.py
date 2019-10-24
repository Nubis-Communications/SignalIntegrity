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
# Alex 20110105
# eLyXer TeX (LyX ERT) parser.

from elyxer.util.trace import Trace
from elyxer.util.clone import *
from elyxer.conf.config import *
from elyxer.parse.position import *
from elyxer.gen.layout import *
from elyxer.maths.formula import *
from elyxer.maths.command import *


class ERT(FirstWord):
  "Evil Red Text: embedded TeX code."
  "Considered as a first word for descriptions."

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def process(self):
    "Process all TeX code, formulas, commands."
    text = ''
    separator = ''
    for container in self.contents:
      text += separator + container.extracttext()
      separator = '\n'
    pos = TextPosition(text)
    pos.leavepending = True
    code = TeXCode()
    code.parse(pos)
    self.contents = [code]

  def isempty(self):
    "Find out if the ERT is empty or not."
    if len(self.contents) == 0:
      return True
    if len(self.contents) > 1:
      Trace.error('Unknown ERT length 2')
      return False
    texcode = self.contents[0]
    return len(texcode.contents) == 0

class TeXCode(Container):
  "A parser and processor for TeX code."

  texseparators = ['{', '\\', '}', '$', '%']
  replaced = BibTeXConfig.replaced
  factory = FormulaFactory()
  endinglist = EndingList()

  def __init__(self):
    self.contents = []
    self.output = ContentsOutput()

  def parse(self, pos):
    "Parse some TeX code."
    self.parserecursive(pos)
    if pos.leavepending:
      self.endinglist.pickpending(pos)

  def findlaststring(self):
    "Find the last string in the contents."
    if len(self.contents) == 0:
      return None
    string = self.contents[-1]
    if not isinstance(string, StringContainer):
      return None
    return string

  def add(self, piece):
    "Add a new piece to the tag."
    if isinstance(piece, basestring):
      self.addtext(piece)
    else:
      self.contents.append(piece)

  def addtext(self, piece):
    "Add a text string to the tag."
    last = self.findlaststring()
    if last:
      last.string += piece
      return
    self.contents.append(Constant(piece))

  def parserecursive(self, pos):
    "Parse brackets or quotes recursively."
    while not pos.finished():
      self.parsetext(pos)
      if pos.finished():
        return
      elif pos.checkfor('{'):
        self.parseopenbracket(pos)
      elif pos.checkfor('}'):
        self.parseclosebracket(pos)
      elif pos.checkfor('\\'):
        self.parseescaped(pos)
      elif pos.checkfor('$'):
        self.parseformula(pos)
      elif pos.checkfor('%'):
        self.parsecomment(pos)
      else:
        pos.error('Unexpected character ' + pos.current())
        pos.skipcurrent()

  def parsetext(self, pos):
    "Parse a bit of text, excluding separators and compressing spaces."
    text = self.parsecompressingspace(pos)
    if text == '':
      return
    for key in self.replaced:
      if key in text:
        text = text.replace(key, self.replaced[key])
    self.add(text)

  def parsecompressingspace(self, pos):
    "Parse some text excluding value separators and compressing spaces."
    parsed = ''
    while not pos.finished():
      parsed += pos.glob(lambda: self.excludespaces(pos))
      if not pos.finished() and pos.current().isspace():
        parsed += ' '
        pos.skipspace()
      else:
        return parsed
    return parsed

  def excludespaces(self, pos):
    "Exclude value separators and spaces."
    current = pos.current()
    if current in self.texseparators:
      return False
    if current.isspace():
      return False
    return True

  def parseescaped(self, pos):
    "Parse an escaped string \\*."
    if pos.checkfor('\\(') or pos.checkfor('\\['):
      # start of formula commands
      self.parseformula(pos)
      return
    if not self.factory.detecttype(FormulaCommand, pos):
      pos.error('Not an escape sequence')
      return
    self.add(self.factory.parsetype(FormulaCommand, pos))

  def parseopenbracket(self, pos):
    "Parse a { bracket."
    if not pos.checkskip('{'):
      pos.error('Missing opening { bracket')
      return
    pos.pushending('}')
    self.parserecursive(pos)
    pos.popending('}')

  def parseclosebracket(self, pos):
    "Parse a } bracket."
    ending = self.endinglist.findending(pos)
    if not ending:
      Trace.error('Unexpected closing } bracket')
    else:
      self.endinglist.pop(pos)
    if not pos.checkskip('}'):
      pos.error('Missing closing } bracket')
      return

  def parseformula(self, pos):
    "Parse a whole formula."
    formula = Formula().parse(pos)
    self.add(formula)

  def parsecomment(self, pos):
    "Parse a TeX comment: % to the end of the line."
    pos.globexcluding('\n')

  def __unicode__(self):
    "Return a printable representation."
    return 'TeX code: ' + self.extracttext()

