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
# Alex 20090218
# eLyXer links

from elyxer.util.trace import Trace
from elyxer.util.translate import *
from elyxer.parse.parser import *
from elyxer.out.output import *
from elyxer.gen.container import *
from elyxer.gen.styles import *


class Link(Container):
  "A link to another part of the document"

  anchor = None
  url = None
  type = None
  page = None
  target = None
  destination = None
  title = None

  def __init__(self):
    "Initialize the link, add target if configured."
    self.contents = []
    self.parser = InsetParser()
    self.output = LinkOutput()
    if Options.target:
      self.target = Options.target

  def complete(self, text, anchor = None, url = None, type = None, title = None):
    "Complete the link."
    self.contents = [Constant(text)]
    if anchor:
      self.anchor = anchor
    if url:
      self.url = url
    if type:
      self.type = type
    if title:
      self.title = title
    return self

  def computedestination(self):
    "Use the destination link to fill in the destination URL."
    if not self.destination:
      return
    self.url = ''
    if self.destination.anchor:
      self.url = '#' + self.destination.anchor
    if self.destination.page:
      self.url = self.destination.page + self.url

  def setmutualdestination(self, destination):
    "Set another link as destination, and set its destination to this one."
    self.destination = destination
    destination.destination = self

  def __unicode__(self):
    "Return a printable representation."
    result = 'Link'
    if self.anchor:
      result += ' #' + self.anchor
    if self.url:
      result += ' to ' + self.url
    return result

class URL(Link):
  "A clickable URL"

  def process(self):
    "Read URL from elyxer.parameters"
    target = self.escape(self.getparameter('target'))
    self.url = target
    type = self.getparameter('type')
    if type:
      self.url = self.escape(type) + target
    name = self.getparameter('name')
    if not name:
      name = target
    self.contents = [Constant(name)]

class FlexURL(URL):
  "A flexible URL"

  def process(self):
    "Read URL from elyxer.contents"
    self.url = self.extracttext()

class LinkOutput(ContainerOutput):
  "A link pointing to some destination"
  "Or an anchor (destination)"

  def gethtml(self, link):
    "Get the HTML code for the link"
    type = link.__class__.__name__
    if link.type:
      type = link.type
    tag = 'a class="' + type + '"'
    if link.anchor:
      tag += ' name="' + link.anchor + '"'
    if link.destination:
      link.computedestination()
    if link.url:
      tag += ' href="' + link.url + '"'
    if link.target:
      tag += ' target="' + link.target + '"'
    if link.title:
      tag += ' title="' + link.title + '"'
    return TaggedOutput().settag(tag).gethtml(link)

