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
# Alex 20100606
# eLyXer BibTeX publication entries.

from elyxer.util.trace import Trace
from elyxer.out.output import *
from elyxer.conf.config import *
from elyxer.parse.position import *
from elyxer.ref.link import *
from elyxer.bib.tex import *
from elyxer.bib.tag import *


class PubEntry(BibEntry):
  "A publication entry"

  def __init__(self):
    self.output = TaggedOutput().settag('p class="biblio"', True)

  def detect(self, pos):
    "Detect a publication entry."
    return pos.checkfor('@')

  def parse(self, pos):
    "Parse the publication entry."
    self.parser = BibTagParser()
    self.parser.parse(pos)
    self.type = self.parser.type

  def isvisible(self):
    "A publication entry is always visible."
    return True

  def isreferenced(self):
    "Check if the entry is referenced."
    if not self.parser.key:
      return False
    return self.parser.key in BiblioReference.references

  def process(self):
    "Process the entry."
    self.index = NumberGenerator.generator.generate('pubentry')
    self.parser.tags['index'] = Constant(self.index)
    biblio = BiblioEntry()
    biblio.citeref = self.createref()
    biblio.processcites(self.parser.key)
    self.contents = [biblio, Constant(' ')]
    self.contents += self.entrycontents()

  def entrycontents(self):
    "Get the contents of the entry."
    return self.translatetemplate(self.template)

  def createref(self):
    "Create the reference to cite."
    return self.translatetemplate(self.citetemplate)

  def translatetemplate(self, template):
    "Translate a complete template into a list of contents."
    pos = TextPosition(template)
    part = BibPart(self.parser.tags).parse(pos)
    for variable in part.searchall(BibVariable):
      if variable.empty():
        Trace.error('Error parsing BibTeX template for ' + unicode(self) + ': '
            + unicode(variable) + ' is empty')
    return [part]

  def __unicode__(self):
    "Return a string representation"
    string = ''
    if 'author' in self.parser.tags:
      string += self.parser.gettagtext('author') + ': '
    if 'title' in self.parser.tags:
      string += '"' + self.parser.gettagtext('title') + '"'
    return string

class BibPart(Container):
  "A part of a BibTeX template."

  def __init__(self, tags):
    self.output = ContentsOutput()
    self.contents = []
    self.tags = tags
    self.quotes = 0

  def parse(self, pos):
    "Parse a part of a template, return a list of contents."
    while not pos.finished():
      self.add(self.parsepiece(pos))
    return self

  def parsepiece(self, pos):
    "Get the next piece of the template, return if it was empty."
    if pos.checkfor('{'):
      return self.parsebraces(pos)
    elif pos.checkfor('$'):
      return self.parsevariable(pos)
    result = ''
    while not pos.finished() and not pos.current() in '{$':
      if pos.current() == '"':
        self.quotes += 1
      result += pos.skipcurrent()
    return Constant(result)

  def parsebraces(self, pos):
    "Parse a pair of curly braces {}."
    if not pos.checkskip('{'):
      Trace.error('Missing { in braces.')
      return None
    pos.pushending('}')
    part = BibPart(self.tags).parse(pos)
    pos.popending('}')
    empty = part.emptyvariables()
    if empty:
      return None
    return part

  def parsevariable(self, pos):
    "Parse a variable $name."
    var = BibVariable(self.tags).parse(pos)
    if self.quotes % 2 == 1:
      # odd number of quotes; don't add spans in an attribute
      var.removetag()
    return var

  def emptyvariables(self):
    "Find out if there are only empty variables in the part."
    for variable in self.searchall(BibVariable):
      if not variable.empty():
        return False
    return True

  def add(self, piece):
    "Add a new piece to the current part."
    if not piece:
      return
    if self.redundantdot(piece):
      # remove extra dot
      piece.string = piece.string[1:]
    self.contents.append(piece)
    piece.parent = self

  def redundantdot(self, piece):
    "Find out if there is a redundant dot in the next piece."
    if not isinstance(piece, Constant):
      return False
    if not piece.string.startswith('.'):
      return False
    if len(self.contents) == 0:
      return False
    if not isinstance(self.contents[-1], BibVariable):
      return False
    if not self.contents[-1].extracttext().endswith('.'):
      return False
    return True

class BibVariable(Container):
  "A variable in a BibTeX template."
  
  def __init__(self, tags):
    self.output = TaggedOutput()
    self.contents = []
    self.tags = tags

  def parse(self, pos):
    "Parse the variable name."
    if not pos.checkskip('$'):
      Trace.error('Missing $ in variable name.')
      return self
    self.key = pos.globalpha()
    self.output.tag = 'span class="bib-' + self.key + '"'
    self.processtags()
    return self

  def processtags(self):
    "Find the tag with the appropriate key in the list of tags."
    if not self.key in self.tags:
      return
    result = self.tags[self.key]
    self.contents = [result]

  def empty(self):
    "Find out if the variable is empty."
    if not self.contents:
      return True
    if self.extracttext() == '':
      return True
    return False

  def removetag(self):
    "Remove the output tag and leave just the contents."
    self.output = ContentsOutput()

  def __unicode__(self):
    "Return a printable representation."
    result = 'variable ' + self.key
    if not self.empty():
      result += ':' + self.extracttext()
    return result

BibEntry.instances += [PubEntry()]

