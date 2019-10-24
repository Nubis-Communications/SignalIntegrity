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
# Alex 20100201
# LyX literate programming with the newfangle module.

from elyxer.util.trace import Trace
from elyxer.util.numbering import *
from elyxer.gen.container import *
from elyxer.gen.layout import *
from elyxer.gen.inset import *
from elyxer.gen.float import *
from elyxer.ref.label import *


class NewfangledChunk(Layout):
  "A chunk of literate programming."

  names = dict()
  firsttime = True

  def process(self):
    "Process the literate chunk."
    self.output.tag = 'div class="chunk"'
    self.type = 'chunk'
    text = self.extracttext()
    parts = text.split(',')
    if len(parts) < 1:
      Trace.error('Not enough parameters in ' + text)
      return
    self.name = parts[0]
    self.number = self.order()
    self.createlinks()
    self.contents = [self.left, self.declaration(), self.right]
    ChunkProcessor.lastchunk = self

  def order(self):
    "Create the order number for the chunk."
    return NumberGenerator.generator.generate('chunk')

  def createlinks(self):
    "Create back and forward links."
    self.leftlink = Link().complete(self.number, 'chunk:' + self.number, type='chunk')
    self.left = TaggedText().complete([self.leftlink], 'span class="chunkleft"', False)
    self.right = TaggedText().constant('', 'span class="chunkright"', False)
    if not self.name in NewfangledChunk.names:
      NewfangledChunk.names[self.name] = []
    else:
      last = NewfangledChunk.names[self.name][-1]
      forwardlink = Link().complete(self.number + u'→', 'chunkback:' + last.number, type='chunk')
      backlink = Link().complete(u'←' + last.number + u' ', 'chunkforward:' + self.number, type='chunk')
      forwardlink.setmutualdestination(backlink)
      last.right.contents.append(forwardlink)
      self.right.contents.append(backlink)
    NewfangledChunk.names[self.name].append(self)
    self.origin = self.createorigin()
    if self.name in NewfangledChunkRef.references:
      for ref in NewfangledChunkRef.references[self.name]:
        self.linkorigin(ref.origin)

  def createorigin(self):
    "Create a link that points to the chunks' origin."
    link = Link()
    self.linkorigin(link)
    return link

  def linkorigin(self, link):
    "Create a link to the origin."
    start = NewfangledChunk.names[self.name][0]
    link.complete(start.number, type='chunk')
    link.destination = start.leftlink
    link.computedestination()

  def declaration(self):
    "Get the chunk declaration."
    contents = []
    text = u'⟨' + self.name + '[' + unicode(len(NewfangledChunk.names[self.name])) + '] '
    contents.append(Constant(text))
    contents.append(self.origin)
    text = ''
    if NewfangledChunk.firsttime:
      Listing.processor = ChunkProcessor()
      NewfangledChunk.firsttime = False
    text += u'⟩'
    if len(NewfangledChunk.names[self.name]) > 1:
      text += '+'
    text += u'≡'
    contents.append(Constant(text))
    return TaggedText().complete(contents, 'span class="chunkdecl"', True)

class ChunkProcessor(object):
  "A processor for listings that belong to chunks."

  lastchunk = None
  counters = dict()
  endcommand = '}'
  chunkref = 'chunkref'

  def preprocess(self, listing):
    "Preprocess a listing: set the starting counter."
    if not ChunkProcessor.lastchunk:
      return
    name = ChunkProcessor.lastchunk.name
    if not name in ChunkProcessor.counters:
      ChunkProcessor.counters[name] = 0
    listing.counter = ChunkProcessor.counters[name]
    for command, container, index in self.commandsinlisting(listing):
      chunkref = self.getchunkref(command)
      if chunkref:
        self.insertchunkref(chunkref, container, index)

  def commandsinlisting(self, listing):
    "Find all newfangle commands in a listing."
    for container in listing.contents:
      for index in range(len(container.contents) - 2):
        if self.findinelement(container, index):
          third = container.contents[index + 2].string
          end = third.index(NewfangleConfig.constants['endmark'])
          command = third[:end]
          lenstart = len(NewfangleConfig.constants['startmark'])
          container.contents[index].string = container.contents[index].string[:-lenstart]
          del container.contents[index + 1]
          container.contents[index + 1].string = third[end + len(NewfangleConfig.constants['endmark']):]
          yield command, container, index

  def findinelement(self, container, index):
    "Find a newfangle command in an element."
    for i in range(2):
      if not isinstance(container.contents[index + i], StringContainer):
        return False
    first = container.contents[index].string
    second = container.contents[index + 1].string
    third = container.contents[index + 2].string
    if not first.endswith(NewfangleConfig.constants['startmark']):
      return False
    if second != NewfangleConfig.constants['startcommand']:
      return False
    if not NewfangleConfig.constants['endmark'] in third:
      return False
    return True

  def getchunkref(self, command):
    "Get the contents of a chunkref command, if present."
    if not command.startswith(NewfangleConfig.constants['chunkref']):
      return None
    if not NewfangleConfig.constants['endcommand'] in command:
      return None
    start = len(NewfangleConfig.constants['chunkref'])
    end = command.index(NewfangleConfig.constants['endcommand'])
    return command[start:end]

  def insertchunkref(self, ref, container, index):
    "Insert a chunkref after the given index at the given container."
    chunkref = NewfangledChunkRef().complete(ref)
    container.contents.insert(index + 1, chunkref)

  def postprocess(self, listing):
    "Postprocess a listing: store the ending counter for next chunk."
    if not ChunkProcessor.lastchunk:
      return
    ChunkProcessor.counters[ChunkProcessor.lastchunk.name] = listing.counter

class NewfangledChunkRef(Inset):
  "A reference to a chunk."

  references = dict()

  def process(self):
    "Show the reference."
    self.output.tag = 'span class="chunkref"'
    self.ref = self.extracttext()
    self.addbits()

  def complete(self, ref):
    "Complete the reference to the given string."
    self.output = ContentsOutput()
    self.ref = ref
    self.contents = [Constant(self.ref)]
    self.addbits()
    return self

  def addbits(self):
    "Add the bits to the reference."
    if not self.ref in NewfangledChunkRef.references:
      NewfangledChunkRef.references[self.ref] = []
    NewfangledChunkRef.references[self.ref].append(self)
    if self.ref in NewfangledChunk.names:
      start = NewfangledChunk.names[self.ref][0]
      self.origin = start.createorigin()
    else:
      self.origin = Link()
    self.contents.insert(0, Constant(u'⟨'))
    self.contents.append(Constant(' '))
    self.contents.append(self.origin)
    self.contents.append(Constant(u'⟩'))

  def __unicode__(self):
    "Return a printable representation."
    return 'Reference to chunk ' + self.ref

