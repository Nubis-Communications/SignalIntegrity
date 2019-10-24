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
# eLyXer tables

from elyxer.util.trace import Trace
from elyxer.gen.container import *
from elyxer.gen.layout import *
from elyxer.parse.parser import *
from elyxer.out.output import *
from elyxer.parse.tableparse import *
from elyxer.proc.postprocess import *


class Table(Container):
  "A lyx table"

  def __init__(self):
    self.parser = TableParser()
    self.output = TaggedOutput().settag('table', True)
    self.columns = []

  def process(self):
    "Set the columns on every row"
    index = 0
    while index < len(self.contents):
      element = self.contents[index]
      if isinstance(element, Column):
        self.columns.append(element)
        del self.contents[index]
      elif isinstance(element, BlackBox):
        del self.contents[index]
      elif isinstance(element, Row):
        element.setcolumns(self.columns)
        index += 1
      else:
        Trace.error('Unknown element type ' + element.__class__.__name__ +
            ' in table: ' + unicode(element.contents[0]))
        index += 1

class Row(Container):
  "A row in a table"

  def __init__(self):
    self.parser = TablePartParser()
    self.output = TaggedOutput().settag('tr', True)
    self.columns = list()

  def setcolumns(self, columns):
    "Process alignments for every column"
    if len(columns) != len(self.contents):
      Trace.error('Columns: ' + unicode(len(columns)) + ', cells: ' + unicode(len(self.contents)))
      return
    for index, cell in enumerate(self.contents):
      columns[index].set(cell)

class Column(Container):
  "A column definition in a table"

  def __init__(self):
    self.parser = ColumnParser()
    self.output = EmptyOutput()

  def process(self):
    "Read size parameters if present."
    self.size = ContainerSize().readparameters(self)

  def set(self, cell):
    "Set alignments in the corresponding cell"
    alignment = self.getparameter('alignment')
    if alignment == 'block':
      alignment = 'justify'
    cell.setattribute('align', alignment)
    valignment = self.getparameter('valignment')
    cell.setattribute('valign', valignment)
    self.size.addstyle(cell)

class Cell(Container):
  "A cell in a table"

  def __init__(self):
    self.parser = TablePartParser()
    self.output = TaggedOutput().settag('td', True)

  def setmulticolumn(self, span):
    "Set the cell as multicolumn"
    self.setattribute('colspan', span)

  def setattribute(self, attribute, value):
    "Set a cell attribute in the tag"
    self.output.tag += ' ' + attribute + '="' + unicode(value) + '"'

class PostTable(object):
  "Postprocess a table"

  processedclass = Table

  def postprocess(self, last, table, next):
    "Postprocess a table: long table, multicolumn rows"
    self.longtable(table)
    for row in table.contents:
      index = 0
      while index < len(row.contents):
        self.checkforplain(row, index)
        self.checkmulticolumn(row, index)
        index += 1
    return table

  def longtable(self, table):
    "Postprocess a long table, removing unwanted rows"
    features = table.getparameter('features')
    if not features:
      return
    if not 'islongtable' in features:
      return
    if features['islongtable'] != 'true':
      return
    if self.hasrow(table, 'endfirsthead'):
      self.removerows(table, 'endhead')
    if self.hasrow(table, 'endlastfoot'):
      self.removerows(table, 'endfoot')

  def hasrow(self, table, attrname):
    "Find out if the table has a row of first heads"
    for row in table.contents:
      if row.getparameter(attrname):
        return True
    return False

  def removerows(self, table, attrname):
    "Remove the head rows, since the table has first head rows."
    for row in table.contents:
      if row.getparameter(attrname):
        row.output = EmptyOutput()

  def checkforplain(self, row, index):
    "Make plain layouts visible if necessary."
    cell = row.contents[index]
    plainlayouts = cell.searchall(PlainLayout)
    if len(plainlayouts) <= 1:
      return
    for plain in plainlayouts:
      plain.makevisible()

  def checkmulticolumn(self, row, index):
    "Process a multicolumn attribute"
    cell = row.contents[index]
    mc = cell.getparameter('multicolumn')
    if not mc:
      return
    if mc != '1':
      Trace.error('Unprocessed multicolumn=' + unicode(multicolumn) +
          ' cell ' + unicode(cell))
      return
    total = 1
    index += 1
    while self.checkbounds(row, index):
      del row.contents[index]
      total += 1
    cell.setmulticolumn(total)

  def checkbounds(self, row, index):
    "Check if the index is within bounds for the row"
    if index >= len(row.contents):
      return False
    mc = row.contents[index].getparameter('multicolumn')
    if mc != '2':
      return False
    return True

Postprocessor.stages.append(PostTable)

