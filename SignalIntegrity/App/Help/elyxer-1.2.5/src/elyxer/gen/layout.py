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
# Alex 20090411
# LyX layout and derived classes

from elyxer.util.trace import Trace
from elyxer.parse.parser import *
from elyxer.out.output import *
from elyxer.gen.container import *
from elyxer.gen.styles import *
from elyxer.gen.header import *
from elyxer.proc.postprocess import *
from elyxer.ref.label import *
from elyxer.ref.partkey import *
from elyxer.ref.link import *


class Layout(Container):
  "A layout (block of text) inside a lyx file"

  type = 'none'

  def __init__(self):
    "Initialize the layout."
    self.contents = []
    self.parser = BoundedParser()
    self.output = TaggedOutput().setbreaklines(True)

  def process(self):
    "Get the type and numerate if necessary."
    self.type = self.header[1]
    if self.type in TagConfig.layouts:
      self.output.tag = TagConfig.layouts[self.type] + ' class="' + self.type + '"'
    elif self.type.replace('*', '') in TagConfig.layouts:
      self.output.tag = TagConfig.layouts[self.type.replace('*', '')]
      self.output.tag += ' class="' +  self.type.replace('*', '-') + '"'
    else:
      self.output.tag = 'div class="' + self.type + '"'
    self.numerate()

  def numerate(self):
    "Numerate if necessary."
    partkey = PartKeyGenerator.forlayout(self)
    if partkey:
      self.partkey = partkey
      self.output.tag = self.output.tag.replace('?', unicode(partkey.level))

  def __unicode__(self):
    "Return a printable representation."
    if self.partkey:
      return 'Layout ' + self.type + ' #' + unicode(self.partkey.partkey)
    return 'Layout of type ' + self.type

class StandardLayout(Layout):
  "A standard layout -- can be a true div or nothing at all"

  indentation = False

  def process(self):
    self.type = 'standard'
    self.output = ContentsOutput()

  def complete(self, contents):
    "Set the contents and return it."
    self.process()
    self.contents = contents
    return self

class Title(Layout):
  "The title of the whole document"

  def process(self):
    self.type = 'title'
    self.output.tag = 'h1 class="title"'
    title = self.extracttext()
    DocumentTitle.title = title
    Trace.message('Title: ' + title)

class Author(Layout):
  "The document author"

  def process(self):
    self.type = 'author'
    self.output.tag = 'h2 class="author"'
    author = self.extracttext()
    Trace.debug('Author: ' + author)
    DocumentAuthor.appendauthor(author)

class Abstract(Layout):
  "A paper abstract"

  done = False

  def process(self):
    self.type = 'abstract'
    self.output.tag = 'div class="abstract"'
    if Abstract.done:
      return
    message = Translator.translate('abstract')
    tagged = TaggedText().constant(message, 'p class="abstract-message"', True)
    self.contents.insert(0, tagged)
    Abstract.done = True

class FirstWorder(Layout):
  "A layout where the first word is extracted"

  def extractfirstword(self):
    "Extract the first word as a list"
    return self.extractfromcontents(self.contents)

  def extractfromcontents(self, contents):
    "Extract the first word in contents."
    firstcontents = []
    while len(contents) > 0:
      if self.isfirstword(contents[0]):
        firstcontents.append(contents[0])
        del contents[0]
        return firstcontents
      if self.spaceincontainer(contents[0]):
        extracted = self.extractfromcontainer(contents[0])
        firstcontents.append(extracted)
        return firstcontents
      firstcontents.append(contents[0])
      del contents[0]
    return firstcontents

  def extractfromcontainer(self, container):
    "Extract the first word from a container cloning it including its output."
    if isinstance(container, StringContainer):
      return self.extractfromstring(container)
    result = Cloner.clone(container)
    result.output = container.output
    result.contents = self.extractfromcontents(container.contents)
    return result

  def extractfromstring(self, container):
    "Extract the first word from elyxer.a string container."
    if not ' ' in container.string:
      Trace.error('No space in string ' + container.string)
      return container
    split = container.string.split(' ', 1)
    container.string = split[1]
    return Constant(split[0])

  def spaceincontainer(self, container):
    "Find out if the container contains a space somewhere."
    return ' ' in container.extracttext()

  def isfirstword(self, container):
    "Find out if the container is valid as a first word."
    if not isinstance(container, FirstWord):
      return False
    return not container.isempty()

class FirstWord(Container):
  "A container which is in itself a first word, unless it's empty."
  "Should be inherited by other containers, e.g. ERT."

  def isempty(self):
    "Find out if the first word is empty."
    Trace.error('Unimplemented isempty()')
    return True

class Description(FirstWorder):
  "A description layout"

  def process(self):
    "Set the first word to bold"
    self.type = 'Description'
    self.output.tag = 'div class="Description"'
    firstword = self.extractfirstword()
    if not firstword:
      return
    tag = 'span class="Description-entry"'
    self.contents.insert(0, TaggedText().complete(firstword, tag))
    self.contents.insert(1, Constant(u' '))

class List(FirstWorder):
  "A list layout"

  def process(self):
    "Set the first word to bold"
    self.type = 'List'
    self.output.tag = 'div class="List"'
    firstword = self.extractfirstword()
    if not firstword:
      return
    first = TaggedText().complete(firstword, 'span class="List-entry"')
    second = TaggedText().complete(self.contents, 'span class="List-contents"')
    self.contents = [first, second]

class PlainLayout(Layout):
  "A plain layout"

  def process(self):
    "Output just as contents."
    self.output = ContentsOutput()
    self.type = 'Plain'

  def makevisible(self):
    "Make the layout visible, output as tagged text."
    self.output = TaggedOutput().settag('div class="PlainVisible"', True)

class LyXCode(Layout):
  "A bit of LyX-Code."

  def process(self):
    "Output as pre."
    self.output.tag = 'pre class="LyX-Code"'
    for newline in self.searchall(Newline):
      index = newline.parent.contents.index(newline)
      newline.parent.contents[index] = Constant('\n')

class PostLayout(object):
  "Numerate an indexed layout"

  processedclass = Layout

  def postprocess(self, last, layout, next):
    "Group layouts and/or number them."
    if layout.type in TagConfig.group['layouts']:
      return self.group(last, layout)
    if layout.partkey:
      self.number(layout)
    return layout

  def group(self, last, layout):
    "Group two layouts if they are the same type."
    if not self.isgroupable(layout) or not self.isgroupable(last) or last.type != layout.type:
      return layout
    layout.contents = last.contents + [Constant('<br/>\n')] + layout.contents
    last.contents = []
    last.output = EmptyOutput()
    return layout

  def isgroupable(self, container):
    "Check that the container can be grouped."
    if not isinstance(container, Layout):
      return False
    for element in container.contents:
      if not element.__class__.__name__ in LayoutConfig.groupable['allowed']:
        return False
    return True

  def number(self, layout):
    "Generate a number and place it before the text"
    layout.partkey.addtoclabel(layout)

class PostStandard(object):
  "Convert any standard spans in root to divs"

  processedclass = StandardLayout

  def postprocess(self, last, standard, next):
    "Switch to div, and clear if empty."
    type = 'Standard'
    if self.isempty(standard):
      standard.output = EmptyOutput()
      return standard
    if DocumentParameters.indentstandard:
      if isinstance(last, StandardLayout):
        type = 'Indented'
      else:
        type = 'Unindented'
    standard.output = TaggedOutput().settag('div class="' + type + '"', True)
    return standard

  def isempty(self, standard):
    "Find out if the standard layout is empty."
    for element in standard.contents:
      if not element.output.isempty():
        return False
    return True

class PostPlainLayout(PostLayout):
  "Numerate a plain layout"

  processedclass = PlainLayout

  def postprocess(self, last, plain, next):
    "Group plain layouts."
    if not self.istext(last) or not self.istext(plain):
      return plain
    plain.makevisible()
    return self.group(last, plain)

  def istext(self, container):
    "Find out if the container is only text."
    if not isinstance(container, PlainLayout):
      return False
    extractor = ContainerExtractor(TOCConfig.extractplain)
    text = extractor.extract(container)
    return (len(text) > 0)

class PostLyXCode(object):
  "Coalesce contiguous LyX-Code layouts."

  processedclass = LyXCode

  def postprocess(self, last, lyxcode, next):
    "Coalesce if last was also LyXCode"
    if not isinstance(last, LyXCode):
      return lyxcode
    if hasattr(last, 'first'):
      lyxcode.first = last.first
    else:
      lyxcode.first = last
    toappend = lyxcode.first.contents
    toappend.append(Constant('\n'))
    toappend += lyxcode.contents
    lyxcode.output = EmptyOutput()
    return lyxcode

Postprocessor.stages += [
    PostLayout, PostStandard, PostLyXCode, PostPlainLayout
    ]

