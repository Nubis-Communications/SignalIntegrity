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
# Alex 20091109
# eLyXer integral processing
# http://www.nongnu.org/elyxer/

from elyxer.gen.layout import *
from elyxer.gen.float import *
from elyxer.ref.index import *
from elyxer.bib.biblio import *
from elyxer.gen.basket import *


class IntegralProcessor(object):
  "A processor for an integral document."

  def __init__(self):
    "Create the processor for the integral contents."
    self.storage = []

  def locate(self, container):
    "Locate only containers of the processed type."
    return isinstance(container, self.processedtype)

  def store(self, container):
    "Store a new container."
    self.storage.append(container)

  def process(self):
    "Process the whole storage."
    for container in self.storage:
      self.processeach(container)

class IntegralTOC(IntegralProcessor):
  "A processor for an integral TOC."

  processedtype = TableOfContents
  tocentries = []

  def processeach(self, toc):
    "Fill in a Table of Contents."
    converter = TOCConverter()
    for container in PartKeyGenerator.partkeyed:
      toc.add(converter.convertindented(container))
    # finish off with the footer to align indents
    toc.add(converter.convertindented(LyXFooter()))

  def writetotoc(self, entries, toc):
    "Write some entries to the TOC."
    for entry in entries:
      toc.contents.append(entry)

class IntegralBiblioEntry(IntegralProcessor):
  "A processor for an integral bibliography entry."

  processedtype = BiblioEntry

  def processeach(self, entry):
    "Process each entry."
    number = NumberGenerator.generator.generate('integralbib')
    link = Link().complete('cite', 'biblio-' + number, type='biblioentry')
    link.contents = entry.citeref
    entry.contents = [Constant('['), link, Constant('] ')]
    if entry.key in BiblioCite.cites:
      for cite in BiblioCite.cites[entry.key]:
        cite.contents = entry.citeref
        cite.anchor = 'cite-' + number
        cite.destination = link

class IntegralFloat(IntegralProcessor):
  "Store all floats in the document by type."

  processedtype = Float
  bytype = dict()

  def processeach(self, float):
    "Store each float by type."
    if not float.type in IntegralFloat.bytype:
      IntegralFloat.bytype[float.type] = []
    IntegralFloat.bytype[float.type].append(float)

class IntegralListOf(IntegralProcessor):
  "A processor for an integral list of floats."

  processedtype = ListOf

  def processeach(self, listof):
    "Fill in a list of floats."
    listof.output = TaggedOutput().settag('div class="fulltoc"', True)
    if not listof.type in IntegralFloat.bytype:
      Trace.message('No floats of type ' + listof.type)
      return
    for float in IntegralFloat.bytype[listof.type]:
      entry = self.processfloat(float)
      if entry:
        listof.contents.append(entry)

  def processfloat(self, float):
    "Get an entry for the list of floats."
    if not float.isparent():
      return None
    return TOCEntry().create(float)

class IntegralReference(IntegralProcessor):
  "A processor for a reference to a label."

  processedtype = Reference

  def processeach(self, reference):
    "Extract the text of the original label."
    reference.formatcontents()

class MemoryBasket(KeeperBasket):
  "A basket which stores everything in memory, processes it and writes it."

  def __init__(self):
    "Create all processors in one go."
    KeeperBasket.__init__(self)
    self.processors = [
        IntegralTOC(), IntegralBiblioEntry(),
        IntegralFloat(), IntegralListOf(), IntegralReference(),
        ]

  def finish(self):
    "Process everything which cannot be done in one pass and write to disk."
    self.process()
    self.flush()

  def process(self):
    "Process everything with the integral processors."
    self.searchintegral()
    for processor in self.processors:
      processor.process()

  def searchintegral(self):
    "Search for all containers for all integral processors."
    for container in self.contents:
      # container.tree()
      if self.integrallocate(container):
        self.integralstore(container)
      container.locateprocess(self.integrallocate, self.integralstore)

  def integrallocate(self, container):
    "Locate all integrals."
    for processor in self.processors:
      if processor.locate(container):
        return True
    return False

  def integralstore(self, container):
    "Store a container in one or more processors."
    for processor in self.processors:
      if processor.locate(container):
        processor.store(container)

