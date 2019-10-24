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
# Alex 20100713
# eLyXer: indexing entries

from elyxer.util.trace import Trace
from elyxer.util.translate import *
from elyxer.parse.parser import *
from elyxer.out.output import *
from elyxer.gen.container import *
from elyxer.gen.styles import *
from elyxer.ref.link import *
from elyxer.ref.partkey import *
from elyxer.proc.process import *


class ListInset(Container):
  "An inset with a list, normally made of links."

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def sortdictionary(self, dictionary):
    "Sort all entries in the dictionary"
    keys = dictionary.keys()
    # sort by name
    keys.sort()
    return keys

  sortdictionary = classmethod(sortdictionary)

class ListOf(ListInset):
  "A list of entities (figures, tables, algorithms)"

  def process(self):
    "Parse the header and get the type"
    self.type = self.header[2]
    text = Translator.translate('list-' + self.type)
    self.contents = [TaggedText().constant(text, 'div class="tocheader"', True)]

class TableOfContents(ListInset):
  "Table of contents"

  def process(self):
    "Parse the header and get the type"
    self.create(Translator.translate('toc'))

  def create(self, heading):
    "Create a table of contents with the given heading text."
    self.output = TaggedOutput().settag('div class="fulltoc"', True)
    self.contents = [TaggedText().constant(heading, 'div class="tocheader"', True)]
    return self

  def add(self, entry):
    "Add a new entry to the TOC."
    if entry:
      self.contents.append(entry)

class IndexReference(Link):
  "A reference to an entry in the alphabetical index."

  name = 'none'

  def process(self):
    "Put entry in index"
    name = self.getparameter('name')
    if name:
      self.name = name.strip()
    else:
      self.name = self.extracttext()
    IndexEntry.get(self.name).addref(self)

  def __unicode__(self):
    "Return a printable representation."
    return 'Reference to ' + self.name

class IndexHeader(Link):
  "The header line for an index entry. Keeps all arrows."

  keyescapes = {'!':'', '|':'-', ' ':'-', '--':'-', ',':'', '\\':'', '@':'_', u'°':''}

  def create(self, names):
    "Create the header for the given index entry."
    self.output = TaggedOutput().settag('p class="printindex"', True)
    self.name = names[-1]
    keys = [self.escape(part, self.keyescapes) for part in names]
    self.key = '-'.join(keys)
    self.anchor = Link().complete('', 'index-' + self.key, None, 'printindex')
    self.contents = [self.anchor, Constant(self.name + ': ')]
    self.arrows = []
    return self

  def addref(self, reference):
    "Create an arrow pointing to a reference."
    reference.index = unicode(len(self.arrows))
    reference.destination = self.anchor
    reference.complete(u'↓', 'entry-' + self.key + '-' + reference.index)
    arrow = Link().complete(u'↑', type = 'IndexArrow')
    arrow.destination = reference
    if len(self.arrows) > 0:
      self.contents.append(Constant(u', '))
    self.arrows.append(arrow)
    self.contents.append(arrow)

  def __unicode__(self):
    "Return a printable representation."
    return 'Index header for ' + self.name

class IndexGroup(Container):
  "A group of entries in the alphabetical index, for an entry."

  root = None

  def create(self):
    "Create an index group."
    self.entries = dict()
    self.output = EmptyOutput()
    return self

  def findentry(self, names):
    "Find the entry with the given names."
    if self == IndexGroup.root:
      self.output = ContentsOutput()
    else:
      self.output = TaggedOutput().settag('div class="indexgroup"', True)
    lastname = names[-1]
    if not lastname in self.entries:
      self.entries[lastname] = IndexEntry().create(names)
    return self.entries[lastname]

  def sort(self):
    "Sort all entries in the group."
    for key in ListInset.sortdictionary(self.entries):
      entry = self.entries[key]
      entry.group.sort()
      self.contents.append(entry)

  def __unicode__(self):
    "Return a printable representation."
    return 'Index group'

IndexGroup.root = IndexGroup().create()

class IndexEntry(Container):
  "An entry in the alphabetical index."
  "When an index entry is of the form 'part1 ! part2 ...', "
  "a hierarchical structure in the form of an IndexGroup is constructed."
  "An index entry contains a mandatory header, and an optional group."

  def create(self, names):
    "Create an index entry with the given name."
    self.output = ContentsOutput()
    self.header = IndexHeader().create(names)
    self.group = IndexGroup().create()
    self.contents = [self.header, self.group]
    return self

  def addref(self, reference):
    "Add a reference to the entry."
    self.header.addref(reference)

  def get(cls, name):
    "Get the index entry for the given name."
    group = IndexGroup.root
    parts = IndexEntry.splitname(name)
    readparts = []
    for part in parts:
      readparts.append(part)
      entry = group.findentry(readparts)
      group = entry.group
    return entry

  def splitname(cls, name):
    "Split a name in parts divided by !."
    return [part.strip() for part in name.split('!')]

  def __unicode__(self):
    "Return a printable representation."
    return 'Index entry for ' + self.header.name

  get = classmethod(get)
  splitname = classmethod(splitname)

class PrintIndex(ListInset):
  "Command to print an index"

  def process(self):
    "Create the alphabetic index"
    self.name = Translator.translate('index')
    self.partkey = PartKeyGenerator.forindex(self)
    if not self.partkey:
      return
    self.contents = [TaggedText().constant(self.name, 'h1 class="index"')]
    self.partkey.addtoclabel(self)
    IndexGroup.root.sort()
    self.contents.append(IndexGroup.root)

class NomenclatureEntry(Link):
  "An entry of LyX nomenclature"

  entries = dict()

  def process(self):
    "Put entry in index"
    symbol = self.getparameter('symbol')
    description = self.getparameter('description')
    key = symbol.replace(' ', '-').lower()
    if key in NomenclatureEntry.entries:
      Trace.error('Duplicated nomenclature entry ' + key)
    self.complete(u'↓', 'noment-' + key)
    entry = Link().complete(u'↑', 'nom-' + key)
    entry.symbol = symbol
    entry.description = description
    self.setmutualdestination(entry)
    NomenclatureEntry.entries[key] = entry

class PrintNomenclature(ListInset):
  "Print all nomenclature entries"

  def process(self):
    "Create the nomenclature."
    self.name = Translator.translate('nomenclature')
    self.partkey = PartKeyGenerator.forindex(self)
    if not self.partkey:
      return
    self.contents = [TaggedText().constant(self.name, 'h1 class="nomenclature"')]
    self.partkey.addtoclabel(self)
    for key in self.sortdictionary(NomenclatureEntry.entries):
      entry = NomenclatureEntry.entries[key]
      contents = [entry, Constant(entry.symbol + u' ' + entry.description)]
      text = TaggedText().complete(contents, 'div class="Nomenclated"', True)
      self.contents.append(text)

class PreListInset(object):
  "Preprocess any container that contains a list inset."

  def preprocess(self, container):
    "Preprocess a container, extract any list inset and return it."
    listinsets = container.searchall(ListInset)
    if len(listinsets) == 0:
      return container
    if len(container.contents) > 1:
      return container
    return listinsets[0]

Processor.prestages += [PreListInset()]

