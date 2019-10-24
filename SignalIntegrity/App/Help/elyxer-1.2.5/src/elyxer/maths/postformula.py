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
# Alex 20090422
# eLyXer postprocessor for formulae

from elyxer.util.numbering import *
from elyxer.maths.command import *
from elyxer.maths.array import *
from elyxer.maths.misc import *
from elyxer.proc.postprocess import *
from elyxer.ref.link import *
from elyxer.ref.label import *
from elyxer.ref.partkey import *


class PostFormula(object):
  "Postprocess a formula"

  processedclass = Formula

  def postprocess(self, last, formula, next):
    "Postprocess any formulae"
    if Options.jsmath or Options.mathjax:
      return formula
    self.postnumbering(formula)
    return formula

  def postnumbering(self, formula):
    "Check if it's a numbered equation, insert number."
    if formula.header[0] != 'numbered':
      return
    functions = formula.searchremove(LabelFunction)
    if len(functions) == 0:
      label = self.createlabel(formula)
    elif len(functions) == 1:
      label = self.createlabel(formula, functions[0])
    if len(functions) <= 1:
      label.parent = formula
      formula.contents.insert(0, label)
      return
    for function in functions:
      label = self.createlabel(formula, function)
      row = self.searchrow(function)
      label.parent = row
      row.contents.insert(0, label)

  def createlabel(self, formula, function = None):
    "Create a new label for a formula."
    "Add a label to a formula."
    tag = self.createtag(formula)
    partkey = PartKey().createformula(tag)
    if not formula.partkey:
      formula.partkey = partkey
    if not function:
      label = Label()
      label.create(partkey.tocentry + ' ', 'eq-' + tag, type="eqnumber")
    else:
      label = function.label
      label.complete(partkey.tocentry + ' ')
    return label

  def createtag(self, formula):
    "Create the label tag."
    tags = formula.searchall(FormulaTag)
    if len(tags) == 0:
      return NumberGenerator.chaptered.generate('formula')
    if len(tags) > 1:
      Trace.error('More than one tag in formula: ' + unicode(formula))
    return tags[0].tag

  def searchrow(self, function):
    "Search for the row that contains the label function."
    if isinstance(function.parent, Formula) or isinstance(function.parent, FormulaRow):
      return function.parent
    return self.searchrow(function.parent)

Postprocessor.stages.append(PostFormula)

