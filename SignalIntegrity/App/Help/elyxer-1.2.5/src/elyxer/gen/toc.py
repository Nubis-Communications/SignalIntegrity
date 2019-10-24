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
# Alex 20091006
# eLyXer TOC generation
# http://www.nongnu.org/elyxer/


from elyxer.gen.header import *
from elyxer.ref.label import *
from elyxer.util.docparams import *


class TOCEntry(Container):
  "A container for a TOC entry."

  def __init__(self):
    Container.__init__(self)
    self.branches = []

  def create(self, container):
    "Create the TOC entry for a container, consisting of a single link."
    if container.partkey.header:
      return self.header(container)
    self.contents = [self.createlink(container)]
    self.output = TaggedOutput().settag('div class="toc"', True)
    self.partkey = container.partkey
    return self

  def header(self, container):
    "Create a TOC entry for header and footer (0 depth)."
    self.partkey = container.partkey
    self.output = EmptyOutput()
    return self

  def createlink(self, container):
    "Create the link that will make the whole TOC entry."
    labels = container.searchall(Label)
    link = Link()
    if self.isanchor(labels):
      link.url = '#' + container.partkey.partkey
      if Options.tocfor:
        link.url = Options.tocfor + link.url
    else:
      label = labels[0]
      link.destination = label
    if container.partkey.tocentry:
      link.complete(container.partkey.tocentry)
    if container.partkey.titlecontents:
      if Options.notoclabels:
        separator = u' '
      else:
        separator = u': '
      if container.partkey.tocentry:
        link.contents.append(Constant(separator))
      link.contents += container.partkey.titlecontents
    return link

  def isanchor(self, labels):
    "Decide if the link is an anchor based on a set of labels."
    if len(labels) == 0:
      return True
    if not Options.tocfor:
      return False
    if Options.splitpart:
      return False
    return True

  def __unicode__(self):
    "Return a printable representation."
    if not self.partkey.tocentry:
      return 'Unnamed TOC entry'
    return 'TOC entry: ' + self.partkey.tocentry

class Indenter(object):
  "Manages and writes indentation for the TOC."

  def __init__(self):
    self.depth = 0

  def getindent(self, depth):
    indent = ''
    if depth > self.depth:
      indent = self.openindent(depth - self.depth)
    elif depth < self.depth:
      indent = self.closeindent(self.depth - depth)
    self.depth = depth
    return Constant(indent)

  def openindent(self, times):
    "Open the indenting div a few times."
    indent = ''
    for i in range(times):
      indent += '<div class="tocindent">\n'
    return indent

  def closeindent(self, times):
    "Close the indenting div a few times."
    indent = ''
    for i in range(times):
      indent += '</div>\n'
    return indent

class IndentedEntry(Container):
  "An entry with an indentation."

  def __init__(self):
    self.output = ContentsOutput()

  def create(self, indent, entry):
    "Create the indented entry."
    self.entry = entry
    self.contents = [indent, entry]
    return self

  def __unicode__(self):
    "Return a printable documentation."
    return 'Indented ' + unicode(self.entry)

class TOCTree(object):
  "A tree that contains the full TOC."

  def __init__(self):
    self.tree = []
    self.branches = []

  def store(self, entry):
    "Place the entry in a tree of entries."
    while len(self.tree) < entry.partkey.level:
      self.tree.append(None)
    if len(self.tree) > entry.partkey.level:
      self.tree = self.tree[:entry.partkey.level]
    stem = self.findstem()
    if len(self.tree) == 0:
      self.branches.append(entry)
    self.tree.append(entry)
    if stem:
      entry.stem = stem
      stem.branches.append(entry)

  def findstem(self):
    "Find the stem where our next element will be inserted."
    for element in reversed(self.tree):
      if element:
        return element
    return None

class TOCConverter(object):
  "A converter from elyxer.containers to TOC entries."

  cache = dict()
  tree = TOCTree()

  def __init__(self):
    self.indenter = Indenter()

  def convertindented(self, container):
    "Convert a container into an indented TOC entry."
    entry = self.convert(container)
    if not entry:
      return None
    return self.indent(entry)

  def indent(self, entry):
    "Indent a TOC entry."
    indent = self.indenter.getindent(entry.partkey.level)
    return IndentedEntry().create(indent, entry)

  def convert(self, container):
    "Convert a container to a TOC entry."
    if not container.partkey:
      return None
    if container.partkey.partkey in self.cache:
      return TOCConverter.cache[container.partkey.partkey]
    if container.partkey.level > DocumentParameters.tocdepth:
      return None
    entry = TOCEntry().create(container)
    TOCConverter.cache[container.partkey.partkey] = entry
    TOCConverter.tree.store(entry)
    return entry

