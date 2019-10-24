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
# Alex 20090415
# eLyXer bibliography

from elyxer.util.numbering import *
from elyxer.util.docparams import *
from elyxer.parse.parser import *
from elyxer.out.output import *
from elyxer.ref.link import *
from elyxer.gen.layout import *
from elyxer.proc.postprocess import *


class BiblioCitation(Container):
  "A complete bibliography citation (possibly with many cites)."

  citations = dict()

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="bibcites"')
    self.contents = []

  def process(self):
    "Process the complete citation and all cites within."
    self.contents = [Constant('[')]
    keys = self.getparameterlist('key')
    for key in keys:
      self.contents += [BiblioCite().create(key), Constant(', ')]
    if len(keys) > 0:
      # remove trailing ,
      self.contents.pop()
    self.contents.append(Constant(']'))

class BiblioCite(Link):
  "Cite of a bibliography entry"

  cites = dict()

  def create(self, key):
    "Create the cite to the given key."
    self.key = key
    number = NumberGenerator.generator.generate('bibliocite')
    ref = BiblioReference().create(key, number)
    self.complete(number, 'cite-' + number, type='bibliocite')
    self.setmutualdestination(ref)
    if not key in BiblioCite.cites:
      BiblioCite.cites[key] = []
    BiblioCite.cites[key].append(self)
    return self

class Bibliography(Container):
  "A bibliography layout containing an entry"

  def __init__(self):
    self.parser = BoundedParser()
    self.output = TaggedOutput().settag('p class="biblio"', True)

class BiblioHeader(Container):
  "The header of the bibliography."

  def __init__(self):
    "Create the header for the bibliography section."
    self.type = 'biblio'
    self.output = ContentsOutput()
    self.name = Translator.translate(DocumentParameters.bibliography)
    self.contents = [TaggedText().constant(self.name, 'h1 class="biblio"', True)]

  def addtotoc(self, parent):
    "Add the bibliography header to the TOC."
    self.parent = parent
    self.partkey = PartKeyGenerator.forindex(self)
    if not self.partkey:
      return
    self.partkey.addtoclabel(self)
    while parent:
      parent.partkey = self.partkey
      parent = parent.parent

class PostBiblio(object):
  "Insert a Bibliography legend before the first item"

  processedclass = Bibliography

  def postprocess(self, last, element, next):
    "If we have the first bibliography insert a tag"
    if isinstance(last, Bibliography) or Options.nobib:
      return element
    layout = StandardLayout()
    header = BiblioHeader()
    header.addtotoc(layout)
    layout.complete([header, element])
    return layout

Postprocessor.stages += [PostBiblio]

class BiblioReference(Link):
  "A reference to a bibliographical entry."

  references = dict()

  def create(self, key, number):
    "Create the reference with the given key and number."
    self.key = key
    self.complete(number, 'biblio-' + number, type='biblioentry')
    if not key in BiblioReference.references:
      BiblioReference.references[key] = []
    BiblioReference.references[key].append(self)
    return self

class BiblioEntry(Container):
  "A bibliography entry"

  entries = dict()

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="entry"')
    self.contents = []

  def process(self):
    "Process the cites for the entry's key"
    self.citeref = [Constant(NumberGenerator.generator.generate('biblioentry'))]
    self.processcites(self.getparameter('key'))

  def processcites(self, key):
    "Get all the cites of the entry"
    self.key = key
    if not key in BiblioReference.references:
      self.contents.append(Constant('[-] '))
      return
    self.contents = [Constant('[')]
    for ref in BiblioReference.references[key]:
      self.contents.append(ref)
      self.contents.append(Constant(','))
    self.contents.pop(-1)
    self.contents.append(Constant('] '))

