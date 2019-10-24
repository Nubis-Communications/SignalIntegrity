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
# Alex 20090905
# eLyXer BibTeX processing

from elyxer.util.trace import Trace
from elyxer.util.clone import *
from elyxer.out.output import *
from elyxer.io.path import *
from elyxer.io.bulk import *
from elyxer.conf.config import *
from elyxer.parse.position import *
from elyxer.ref.link import *
from elyxer.bib.biblio import *
from elyxer.bib.tag import *


class BibTeX(Container):
  "Show a BibTeX bibliography and all referenced entries"

  def __init__(self):
    self.parser = InsetParser()
    self.output = ContentsOutput()

  def process(self):
    "Read all bibtex files and process them."
    self.entries = []
    self.contents = [self.createheader()]
    bibliography = Translator.translate('bibliography')
    files = self.getparameterlist('bibfiles')
    showall = False
    if self.getparameter('btprint') == 'btPrintAll':
      showall = True
    for file in files:
      bibfile = BibFile(file, showall)
      bibfile.parse()
      self.entries += bibfile.entries
      Trace.message('Parsed ' + unicode(bibfile))
    self.entries.sort(key = unicode)
    self.applystyle()

  def createheader(self):
    "Create the header for the bibliography."
    header = BiblioHeader()
    if 'bibtotoc' in self.getparameterlist('options'):
      header.addtotoc(self)
    return header

  def applystyle(self):
    "Read the style and apply it to all entries"
    style = self.readstyle()
    for entry in self.entries:
      entry.template = style['default']
      entry.citetemplate = style['cite']
      type = entry.type.lower()
      if type in style:
        entry.template = style[type]
      entry.process()
      self.contents.append(entry)

  def readstyle(self):
    "Read the style from elyxer.the bibliography options"
    for option in self.getparameterlist('options'):
      if hasattr(BibStylesConfig, option):
        return getattr(BibStylesConfig, option)
    return BibStylesConfig.default

class BibFile(object):
  "A BibTeX file"

  def __init__(self, filename, showall):
    "Create the BibTeX file"
    self.filename = filename + '.bib'
    self.showall = showall
    self.added = 0
    self.ignored = 0
    self.entries = []

  def parse(self):
    "Parse the BibTeX file and extract all entries."
    try:
      self.parsefile()
    except IOError:
      Trace.error('Error reading ' + self.filename + '; make sure the file exists and can be read.')

  def parsefile(self):
    "Parse the whole file."
    bibpath = InputPath(self.filename)
    if Options.lowmem:
      pos = FilePosition(bibpath.path)
    else:
      bulkfile = BulkFile(bibpath.path)
      text = ''.join(bulkfile.readall())
      pos = TextPosition(text)
    while not pos.finished():
      pos.skipspace()
      if pos.checkskip(','):
        pos.skipspace()
      self.parseentry(pos)

  def parseentry(self, pos):
    "Parse a single entry"
    for entry in BibEntry.instances:
      if entry.detect(pos):
        newentry = Cloner.clone(entry)
        newentry.parse(pos)
        if not newentry.isvisible():
          return
        if self.showall or newentry.isreferenced():
          self.entries.append(newentry)
          self.added += 1
        else:
          Trace.debug('Ignored entry ' + unicode(newentry))
          self.ignored += 1
        return
    # Skip the whole line since it's a comment outside an entry
    pos.globincluding('\n').strip()

  def __unicode__(self):
    "String representation"
    string = self.filename + ': ' + unicode(self.added) + ' entries added, '
    string += unicode(self.ignored) + ' entries ignored'
    return string

class BibEntry(Container):
  "An entry in a BibTeX file"

  instances = []

  def detect(self, pos):
    "Throw an error."
    Trace.error('Tried to detect() in ' + unicode(self))

  def parse(self, pos):
    "Throw an error."
    Trace.error('Tried to parse() in ' + unicode(self))

  def isvisible(self):
    "Return if the entry should be visible. Throws an error."
    Trace.error('Function isvisible() not implemented for ' + unicode(self))

  def isreferenced(self):
    "Return if the entry is referenced. Throws an error."
    Trace.error('Function isreferenced() not implemented for ' + unicode(self))

  def __unicode__(self):
    "Return a string representation"
    return 'BibTeX entry ' + self.__class__.__name__

class CommentEntry(BibEntry):
  "A simple comment."

  def detect(self, pos):
    "Detect the special entry"
    return pos.checkfor('%')

  def parse(self, pos):
    "Parse all consecutive comment lines."
    while pos.checkfor('%'):
      pos.globincluding('\n')

  def isvisible(self):
    "A comment entry is never visible."
    return False

  def __unicode__(self):
    "Return a string representation"
    return 'Comment'

class SpecialEntry(BibEntry):
  "A special entry"

  types = ['@preamble', '@comment']

  def __init__(self):
    self.contents = []
    self.output = EmptyOutput()

  def detect(self, pos):
    "Detect the special entry"
    for type in self.types:
      if pos.checkforlower(type):
        return True
    return False

  def parse(self, pos):
    "Parse and ignore."
    self.type = 'special'
    pos.globincluding('{')
    pos.pushending('}')
    while not pos.finished():
      if pos.checkfor('{'):
        self.parse(pos)
      else:
        pos.skipcurrent()
    pos.popending()

  def isvisible(self):
    "A special entry is never visible."
    return False

  def __unicode__(self):
    "Return a string representation"
    return self.type

class StringEntry(SpecialEntry):
  "A string definition. The definition can later be used in other entries."

  parser = BibTagParser()
  start = '@string'
  key = None

  def detect(self, pos):
    "Detect the string definition."
    return pos.checkforlower(self.start)

  def parse(self, pos):
    "Parse a single tag, which will define a string."
    self.type = self.start
    if not self.checkstart(pos):
      return
    pos.skipspace()
    if not pos.checkskip('{'):
      Trace.error('Missing opening { in ' + unicode(self))
      pos.globincluding('\n')
      return
    pos.pushending('}')
    (self.key, value) = self.parser.getkeyvalue(pos)
    BibTag.stringdefs[self.key] = value
    pos.popending('}')

  def checkstart(self, pos):
    "Check that the entry starts with @string."
    if not pos.checkskip('@'):
      Trace.error('Missing @ from elyxer.string definition')
      return False
    name = '@' + pos.globalpha()
    if not name.lower() == self.start.lower():
      Trace.error('Invalid start @' + name +', missing ' + self.start + ' from elyxer.' + unicode(self))
      pos.globincluding('\n')
      return False
    return True

  def __unicode__(self):
    "Return a printable representation."
    result = 'string definition'
    if self.key:
      result += ' for ' + self.key
    return result


# More instances will be added later
BibEntry.instances += [CommentEntry(), SpecialEntry(), StringEntry()]

