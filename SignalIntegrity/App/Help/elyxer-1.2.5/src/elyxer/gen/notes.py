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
# Alex 20101119
# LyX notes: notes, footnotes and margin notes.

from elyxer.util.trace import Trace
from elyxer.util.numbering import *
from elyxer.parse.parser import *
from elyxer.out.output import *
from elyxer.gen.container import *
from elyxer.ref.link import *


class SideNote(Container):
  "A side note that appears at the right."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput()

  def process(self):
    "Enclose everything in a marginal span."
    self.output.settag('span class="Marginal"', True)

class FootnoteMarker(Container):
  "A marker for a footnote."

  def __init__(self):
    "Set the correct span class."
    self.contents = []
    span = 'span class="SupFootMarker"'
    if Options.alignfoot:
      span = 'span class="AlignFootMarker"'
    self.output = TaggedOutput().settag(span, False)
    mode = 'A'
    if Options.numberfoot:
      mode = '1'
    if Options.symbolfoot:
      mode = '*'
    NumberGenerator.generator.getcounter('Footnote').setmode(mode)

  def create(self):
    "Create the marker for a footnote."
    self.order = NumberGenerator.generator.generate('Footnote')
    if Options.endfoot:
      self.link = Link().complete(self.getmark(), 'footmarker-' + self.order)
    self.createcontents()
    return self

  def createanchor(self, marker):
    "Create the anchor for a footnote. Adds a link for end footnotes."
    self.order = marker.order
    if Options.endfoot:
      self.link = Link().complete(self.getmark(), 'footnote-' + self.order)
      self.link.setmutualdestination(marker.link)
    self.createcontents()
    return self

  def createlabel(self, marker):
    "Create the label for a footnote. Used in hoverfoot and marginfoot."
    self.order = marker.order
    self.contents = [Constant(self.getmark())]
    space = Constant(u' ')
    self.contents = [space] + self.contents + [space]
    return self

  def createcontents(self):
    "Create the contents of the marker."
    if Options.endfoot:
      self.contents = [self.link]
    else:
      self.contents = [Constant(self.getmark())]
    space = Constant(u' ')
    self.contents = [space] + self.contents + [space]

  def getmark(self):
    "Get the mark to be displayed in the marker based on the order."
    if Options.symbolfoot:
      return self.order
    else:
      return '[' + self.order + ']'

class Footnote(Container):
  "A footnote to the main text."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="FootOuter"', False)

  def process(self):
    "Add a counter for the footnote."
    "Can be numeric or a letter depending on runtime options."
    marker = FootnoteMarker().create()
    anchor = FootnoteMarker().createanchor(marker)
    label = FootnoteMarker().createlabel(marker)
    notecontents = list(self.contents)
    self.contents = [marker]
    if Options.hoverfoot:
      self.contents.append(self.createnote([label] + notecontents, 'span class="HoverFoot"'))
    if Options.marginfoot:
      self.contents.append(self.createnote([label] + notecontents, 'span class="MarginFoot"'))
    if Options.endfoot:
      EndFootnotes.footnotes.append(self.createnote([anchor] + notecontents, 'div class="EndFoot"'))

  def createnote(self, contents, tag):
    "Create a note with the given contents and HTML tag."
    return TaggedText().complete(contents, tag, False)

class EndFootnotes(Container):
  "The collection of footnotes at the document end."

  footnotes = []

  def __init__(self):
    "Generate all footnotes and a proper header for them all."
    self.output = ContentsOutput()
    header = TaggedText().constant(Translator.translate('footnotes'), 'h1 class="index"')
    self.contents = [header] + self.footnotes

class Note(Container):
  "A LyX note of several types"

  def __init__(self):
    self.parser = InsetParser()
    self.output = EmptyOutput()

  def process(self):
    "Hide note and comment, dim greyed out"
    self.type = self.header[2]
    if TagConfig.notes[self.type] == '':
      return
    self.output = TaggedOutput().settag(TagConfig.notes[self.type], True)

