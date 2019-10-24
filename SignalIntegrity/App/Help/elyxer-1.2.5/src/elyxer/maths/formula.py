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
# Alex 20090207
# eLyXer formula processing

import urllib
from elyxer.gen.container import *
from elyxer.util.trace import Trace
from elyxer.util.clone import *
from elyxer.util.docparams import *
from elyxer.conf.config import *
from elyxer.parse.formulaparse import *
from elyxer.proc.formulaproc import *


class Formula(Container):
  "A LaTeX formula"

  def __init__(self):
    self.parser = FormulaParser()
    self.output = TaggedOutput().settag('span class="formula"')

  def process(self):
    "Convert the formula to tags"
    if self.header[0] == 'inline':
      DocumentParameters.displaymode = False
    else:
      DocumentParameters.displaymode = True
      self.output.settag('div class="formula"', True)
    if Options.jsmath:
      self.jsmath()
    elif Options.mathjax:
      self.mathjax()
    elif Options.googlecharts:
      self.googlecharts()
    else:
      self.classic()

  def jsmath(self):
    "Make the contents for jsMath."
    if self.header[0] != 'inline':
      self.output = TaggedOutput().settag('div class="math"')
    else:
      self.output = TaggedOutput().settag('span class="math"')
    self.contents = [Constant(self.parsed)]

  def mathjax(self):
    "Make the contents for MathJax."
    self.output.tag = 'span class="MathJax_Preview"'
    tag = 'script type="math/tex'
    if self.header[0] != 'inline':
      tag += ';mode=display'
    self.contents = [TaggedText().constant(self.parsed, tag + '"', True)]

  def googlecharts(self):
    "Make the contents using Google Charts http://code.google.com/apis/chart/."
    url = FormulaConfig.urls['googlecharts'] + urllib.quote_plus(self.parsed)
    img = '<img class="chart" src="' + url + '" alt="' + self.parsed + '"/>'
    self.contents = [Constant(img)]

  def classic(self):
    "Make the contents using classic output generation with XHTML and CSS."
    whole = FormulaFactory().parseformula(self.parsed)
    FormulaProcessor().process(whole)
    whole.parent = self
    self.contents = [whole]

  def parse(self, pos):
    "Parse using a parse position instead of self.parser."
    if pos.checkskip('$$'):
      self.parsedollarblock(pos)
    elif pos.checkskip('$'):
      self.parsedollarinline(pos)
    elif pos.checkskip('\\('):
      self.parseinlineto(pos, '\\)')
    elif pos.checkskip('\\['):
      self.parseblockto(pos, '\\]')
    else:
      pos.error('Unparseable formula')
    self.process()
    return self

  def parsedollarinline(self, pos):
    "Parse a $...$ formula."
    self.header = ['inline']
    self.parsedollar(pos)

  def parsedollarblock(self, pos):
    "Parse a $$...$$ formula."
    self.header = ['block']
    self.parsedollar(pos)
    if not pos.checkskip('$'):
      pos.error('Formula should be $$...$$, but last $ is missing.')

  def parsedollar(self, pos):
    "Parse to the next $."
    pos.pushending('$')
    self.parsed = pos.globexcluding('$')
    pos.popending('$')

  def parseinlineto(self, pos, limit):
    "Parse a \\(...\\) formula."
    self.header = ['inline']
    self.parseupto(pos, limit)

  def parseblockto(self, pos, limit):
    "Parse a \\[...\\] formula."
    self.header = ['block']
    self.parseupto(pos, limit)

  def parseupto(self, pos, limit):
    "Parse a formula that ends with the given command."
    pos.pushending(limit)
    self.parsed = pos.glob(lambda: True)
    pos.popending(limit)

  def __unicode__(self):
    "Return a printable representation."
    if self.partkey and self.partkey.number:
      return 'Formula (' + self.partkey.number + ')'
    return 'Unnumbered formula'

class WholeFormula(FormulaBit):
  "Parse a whole formula"

  def detect(self, pos):
    "Not outside the formula is enough."
    return not pos.finished()

  def parsebit(self, pos):
    "Parse with any formula bit"
    while not pos.finished():
      self.add(self.factory.parseany(pos))

class FormulaFactory(object):
  "Construct bits of formula"

  # bit types will be appended later
  types = [FormulaSymbol, RawText, FormulaNumber, Bracket, Comment, WhiteSpace]
  skippedtypes = [Comment, WhiteSpace]
  defining = False

  def __init__(self):
    "Initialize the map of instances."
    self.instances = dict()

  def detecttype(self, type, pos):
    "Detect a bit of a given type."
    if pos.finished():
      return False
    return self.instance(type).detect(pos)

  def instance(self, type):
    "Get an instance of the given type."
    if not type in self.instances or not self.instances[type]:
      self.instances[type] = self.create(type)
    return self.instances[type]

  def create(self, type):
    "Create a new formula bit of the given type."
    return Cloner.create(type).setfactory(self)

  def clearskipped(self, pos):
    "Clear any skipped types."
    while not pos.finished():
      if not self.skipany(pos):
        return
    return

  def skipany(self, pos):
    "Skip any skipped types."
    for type in self.skippedtypes:
      if self.instance(type).detect(pos):
        return self.parsetype(type, pos)
    return None

  def parseany(self, pos):
    "Parse any formula bit at the current location."
    for type in self.types + self.skippedtypes:
      if self.detecttype(type, pos):
        return self.parsetype(type, pos)
    Trace.error('Unrecognized formula at ' + pos.identifier())
    return FormulaConstant(pos.skipcurrent())

  def parsetype(self, type, pos):
    "Parse the given type and return it."
    bit = self.instance(type)
    self.instances[type] = None
    returnedbit = bit.parsebit(pos)
    if returnedbit:
      return returnedbit.setfactory(self)
    return bit

  def parseformula(self, formula):
    "Parse a string of text that contains a whole formula."
    pos = TextPosition(formula)
    whole = self.create(WholeFormula)
    if whole.detect(pos):
      whole.parsebit(pos)
      return whole
    # no formula found
    if not pos.finished():
      Trace.error('Unknown formula at: ' + pos.identifier())
      whole.add(TaggedBit().constant(formula, 'span class="unknown"'))
    return whole

