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
# Alex 20101027
# eLyXer BibTeX tag parsing

from elyxer.util.trace import Trace
from elyxer.util.clone import *
from elyxer.conf.config import *
from elyxer.parse.position import *
from elyxer.gen.container import *
from elyxer.maths.formula import *
from elyxer.maths.command import *
from elyxer.tex.texcode import *


class BibTagParser(object):
  "A parser for BibTeX tags."

  nameseparators = ['{', '=', '"', '#']

  def __init__(self):
    self.key = None
    tags = BibStylesConfig.defaulttags
    self.tags = dict((x, BibTag().constant(tags[x])) for x in tags)

  def parse(self, pos):
    "Parse the entry between {}."
    self.type = pos.globexcluding(self.nameseparators).strip()
    if not pos.checkskip('{'):
      pos.error('Entry should start with {')
      return
    pos.pushending('}')
    self.parsetags(pos)
    pos.popending('}')
    pos.skipspace()

  def parsetags(self, pos):
    "Parse all tags in the entry."
    pos.skipspace()
    while not pos.finished():
      if pos.checkskip('{'):
        pos.error('Unmatched {')
        return
      pos.pushending(',', True)
      self.parsetag(pos)
      if pos.checkfor(','):
        pos.popending(',')
  
  def parsetag(self, pos):
    "Parse a single tag."
    (key, value) = self.getkeyvalue(pos)
    if not key:
      return
    if not value:
      self.key = key
      return
    name = key.lower()
    self.tags[name] = value
    if hasattr(self, 'dissect' + name):
      dissector = getattr(self, 'dissect' + name)
      dissector(value.extracttext())
    if not pos.finished():
      remainder = pos.globexcluding(',')
      pos.error('Ignored ' + remainder + ' before comma')

  def getkeyvalue(self, pos):
    "Parse a string of the form key=value."
    piece = pos.globexcluding(self.nameseparators).strip()
    if pos.finished():
      return (piece, None)
    if not pos.checkskip('='):
      pos.error('Undesired character in tag name ' + piece)
      pos.skipcurrent()
      return (piece, None)
    key = piece.lower()
    pos.skipspace()
    value = self.parsevalue(pos)
    return (key, value)

  def parsevalue(self, pos):
    "Parse the value for a tag."
    tag = BibTag()
    pos.skipspace()
    if pos.checkfor(','):
      pos.error('Unexpected ,')
      return tag.error()
    tag.parse(pos)
    return tag

  def dissectauthor(self, authortag):
    "Dissect the author tag into pieces."
    authorsplit = authortag.split(' and ')
    if len(authorsplit) == 0:
      return
    authorlist = []
    for authorname in authorsplit:
      author = BibAuthor().parse(authorname)
      authorlist.append(author)
    initials = ''
    authors = ''
    if len(authorlist) == 1:
      initials = authorlist[0].surname[0:3]
      authors = unicode(authorlist[0])
    else:
      for author in authorlist:
        initials += author.surname[0:1]
        authors += unicode(author) + ', '
      authors = authors[:-2]
    self.tags['surname'] = BibTag().constant(authorlist[0].surname)
    self.tags['Sur'] = BibTag().constant(initials)
    self.tags['authors'] = BibTag().constant(authors)

  def dissectyear(self, yeartag):
    "Dissect the year tag into pieces, looking for 4 digits in a row."
    pos = TextPosition(yeartag)
    while not pos.finished():
      if pos.current().isdigit():
        number = pos.globnumber()
        if len(number) == 4:
          self.tags['YY'] = BibTag().constant(number[2:])
          return
      else:
        pos.skipcurrent()

  def dissectfile(self, filetag):
    "Extract the filename from elyxer.the file tag as ':filename:FORMAT'."
    if not filetag.startswith(':'):
      return
    bits = filetag.split(':')
    if len(bits) != 3:
      return
    self.tags['filename'] = BibTag().constant(bits[1])
    self.tags['format'] = BibTag().constant(bits[2])

  def gettag(self, key):
    "Get the tag for a given key."
    if not key in self.tags:
      return None
    return self.tags[key]

  def gettagtext(self, key):
    "Get the tag for a key as raw text."
    return self.gettag(key).extracttext()

class BibTag(Container):
  "A tag in a BibTeX file."

  valueseparators = ['{', '"', '#', '}']
  stringdefs = dict()

  def __init__(self):
    self.contents = []
    self.output = ContentsOutput()

  def constant(self, text):
    "Initialize for a single constant."
    self.contents = [Constant(text)]
    return self

  def error(self):
    "To use when parsing resulted in an error."
    return self.constant('')

  def parse(self, pos):
    "Parse brackets or quotes at the first level."
    while not pos.finished():
      self.parsetext(pos)
      if pos.finished():
        return
      elif pos.checkfor('{'):
        self.parsebracket(pos)
      elif pos.checkfor('"'):
        self.parsequoted(pos)
      elif pos.checkfor('#'):
        self.parsehash(pos)
      else:
        pos.error('Unexpected character ' + pos.current())
        pos.skipcurrent()

  def parsetext(self, pos):
    "Parse a bit of text, try to substitute strings with string defs."
    text = pos.globexcluding(self.valueseparators)
    key = text.strip()
    if key == '':
      return
    if key in self.stringdefs:
      self.add(self.stringdefs[key])
      return
    self.add(Constant(key))

  def add(self, piece):
    "Add a new piece to the tag."
    self.contents.append(piece)

  def parsetex(self, pos):
    "Parse some TeX code."
    tex = TeXCode()
    tex.parse(pos)
    self.add(tex)

  def parsebracket(self, pos):
    "Parse a {} bracket"
    if not pos.checkskip('{'):
      pos.error('Missing opening { in bracket')
      return
    pos.pushending('}')
    self.parsetex(pos)
    pos.popending('}')

  def parsequoted(self, pos):
    "Parse a piece of quoted text"
    if not pos.checkskip('"'):
      pos.error('Missing opening " in quote')
      return
    pos.pushending('"')
    self.parsetex(pos)
    pos.popending('"')
    pos.skipspace()

  def parsehash(self, pos):
    "Parse a hash mark #."
    if not pos.checkskip('#'):
      pos.error('Missing # in hash')
      return

  def __unicode__(self):
    "Return a printable representation."
    return 'BibTag: ' + self.extracttext()

class BibAuthor(object):
  "A BibTeX individual author."

  def __init__(self):
    self.surname = ''
    self.firstnames = []

  def parse(self, tag):
    "Parse an individual author tag."
    if ',' in tag:
      self.parsecomma(tag)
    else:
      self.parsewithoutcomma(tag)
    return self

  def parsecomma(self, tag):
    "Parse an author with a comma: Python, M."
    bits = tag.split(',')
    if len(bits) > 2:
      Trace.error('Too many commas in ' + tag)
    self.surname = bits[0].strip()
    self.parsefirstnames(bits[1].strip())

  def parsewithoutcomma(self, tag):
    "Parse an author without a comma: M. Python."
    bits = tag.rsplit(None, 1)
    if len(bits) == 0:
      Trace.error('Empty author')
      ppp()
      return
    self.surname = bits[-1].strip()
    if len(bits) == 1:
      return
    self.parsefirstnames(bits[0].strip())

  def parsefirstnames(self, firstnames):
    "Parse the first name."
    for firstname in firstnames.split():
      self.firstnames.append(firstname)

  def getinitial(self):
    "Get the main initial for the author."
    if len(self.surname) == 0:
      return ''
    return self.surname[0].toupper()

  def __unicode__(self):
    "Return a printable representation."
    result = ''
    for firstname in self.firstnames:
      result += firstname + ' '
    return result + self.surname

