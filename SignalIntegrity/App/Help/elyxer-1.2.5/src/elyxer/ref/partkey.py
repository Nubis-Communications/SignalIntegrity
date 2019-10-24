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
# Alex 20100705
# eLyXer: key that identifies a given document part (chapter, section...).

from elyxer.util.trace import Trace
from elyxer.util.options import *
from elyxer.util.translate import *
from elyxer.util.numbering import *
from elyxer.util.docparams import *
from elyxer.ref.label import *
from elyxer.gen.inset import *
from elyxer.out.template import *


class PartKey(object):
  "A key to identify a given document part (chapter, section...)."

  partkey = None
  tocentry = None
  anchortext = None
  number = None
  filename = None
  titlecontents = None
  header = False

  def __init__(self):
    self.level = 0

  def createindex(self, partkey):
    "Create a part key for an index page."
    self.partkey = partkey
    self.tocentry = partkey
    self.filename = partkey
    return self

  def createfloat(self, float):
    "Create a part key for a float."
    self.number = NumberGenerator.chaptered.generate(float.type)
    self.partkey = Translator.translate('float-' + float.type) + self.number
    if Options.notoclabels:
      self.tocentry = self.number
    else:
      self.tocentry = self.partkey
    self.readtitle(float)
    return self

  def createsubfloat(self, number):
    "Create the part key for a subfloat."
    self.partkey = '(' + number + ')'
    self.number = number
    return self

  def createformula(self, number):
    "Create the part key for a formula."
    self.number = number
    self.partkey = 'formula-' + number
    self.tocentry = '(' + number + ')'
    return self

  def createheader(self, headorfooter):
    "Create the part key for a header or footer."
    self.partkey = headorfooter
    self.tocentry = None
    self.header = True
    return self

  def createanchor(self, partkey):
    "Create an anchor for the page."
    self.partkey = partkey
    self.tocentry = partkey
    self.header = True
    return self

  def createmain(self):
    "Create the part key for the main page."
    self.partkey = ''
    self.tocentry = DocumentTitle().getvalue()
    return self

  def addtoclabel(self, container):
    "Create the label for the TOC, and add it to the container."
    labeltext = ''
    if self.anchortext:
      labeltext = self.anchortext
      container.contents.insert(0, Separator(u' '))
    label = Label().create(labeltext, self.partkey, type='toc')
    container.contents.insert(0, label)

  def readtitle(self, container):
    "Read the title of the TOC entry."
    shorttitles = container.searchall(ShortTitle)
    if len(shorttitles) > 0:
      self.titlecontents = []
      for shorttitle in shorttitles:
        self.titlecontents += shorttitle.contents
      return
    extractor = ContainerExtractor(TOCConfig.extracttitle)
    captions = container.searchall(Caption)
    if len(captions) == 1:
      self.titlecontents = extractor.extract(captions[0])
      return
    self.titlecontents = extractor.extract(container)

  def __unicode__(self):
    "Return a printable representation."
    return 'Part key for ' + self.partkey

class LayoutPartKey(PartKey):
  "The part key for a layout."

  generator = NumberGenerator()

  def create(self, layout):
    "Set the layout for which we are creating the part key."
    self.processtype(layout.type)
    self.readtitle(layout)
    return self

  def processtype(self, type):
    "Process the layout type."
    self.level = self.generator.getlevel(type)
    self.number = self.generator.generate(type)
    anchortype = self.getanchortype(type)
    self.partkey = 'toc-' + anchortype + '-' + self.number
    self.tocentry = self.gettocentry(type)
    self.filename = self.getfilename(type)
    if self.generator.isnumbered(type):
      if not self.tocentry:
        self.tocentry = ''
      else:
        self.tocentry += ' '
      self.tocentry += self.number
      self.anchortext = self.getanchortext(type)

  def getanchortype(self, type):
    "Get the type for the anchor."
    parttype = self.generator.getparttype(type)
    if self.generator.isunordered(type):
      parttype += '-'
    return parttype

  def gettocentry(self, type):
    "Get the entry for the TOC: Chapter, Section..."
    if Options.notoclabels:
      return ''
    return Translator.translate(self.generator.getparttype(type))

  def addtotocentry(self, text):
    "Add some text to the tocentry; create if None."
    if not self.tocentry:
      self.tocentry = ''
    self.tocentry += text

  def getanchortext(self, type):
    "Get the text for the anchor given to a layout type."
    if self.generator.isunique(type):
      return self.tocentry + '.'
    return self.number

  def getfilename(self, type):
    "Get the filename to be used if splitpart is active."
    if self.level == Options.splitpart and self.generator.isnumbered(type):
      return self.number
    if self.level <= Options.splitpart:
      return self.partkey.replace('toc-', '')
    return None

  def needspartkey(self, layout):
    "Find out if a layout needs a part key."
    if self.generator.isunique(layout.type):
      return True
    return self.generator.isinordered(layout.type)

  def __unicode__(self):
    "Get a printable representation."
    return 'Part key for layout ' + self.tocentry

class PartKeyGenerator(object):
  "Number a layout with the relevant attributes."

  partkeyed = []
  layoutpartkey = LayoutPartKey()

  def forlayout(cls, layout):
    "Get the part key for a layout."
    if layout.hasemptyoutput():
      return None
    if not cls.layoutpartkey.needspartkey(layout):
      return None
    Label.lastlayout = layout
    cls.partkeyed.append(layout)
    return LayoutPartKey().create(layout)

  def forindex(cls, index):
    "Get the part key for an index or nomenclature."
    if index.hasemptyoutput():
      return None
    cls.partkeyed.append(index)
    return PartKey().createindex(index.name)

  forlayout = classmethod(forlayout)
  forindex = classmethod(forindex)

