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
# eLyXer labels

from elyxer.util.trace import Trace
from elyxer.parse.parser import *
from elyxer.out.output import *
from elyxer.gen.container import *
from elyxer.gen.styles import *
from elyxer.ref.link import *
from elyxer.proc.postprocess import *


class Label(Link):
  "A label to be referenced"

  names = dict()
  lastlayout = None

  def __init__(self):
    Link.__init__(self)
    self.lastnumbered = None

  def process(self):
    "Process a label container."
    key = self.getparameter('name')
    self.create(' ', key)
    self.lastnumbered = Label.lastlayout

  def create(self, text, key, type = 'Label'):
    "Create the label for a given key."
    self.key = key
    self.complete(text, anchor = key, type = type)
    Label.names[key] = self
    if key in Reference.references:
      for reference in Reference.references[key]:
        reference.destination = self
    return self

  def findpartkey(self):
    "Get the part key for the latest numbered container seen."
    numbered = self.numbered(self)
    if numbered and numbered.partkey:
      return numbered.partkey
    return ''

  def numbered(self, container):
    "Get the numbered container for the label."
    if container.partkey:
      return container
    if not container.parent:
      if self.lastnumbered:
        return self.lastnumbered
      return None
    return self.numbered(container.parent)

  def __unicode__(self):
    "Return a printable representation."
    if not hasattr(self, 'key'):
      return 'Unnamed label'
    return 'Label ' + self.key

class Reference(Link):
  "A reference to a label."

  references = dict()
  key = 'none'

  def process(self):
    "Read the reference and set the arrow."
    self.key = self.getparameter('reference')
    if self.key in Label.names:
      self.direction = u'↑'
      label = Label.names[self.key]
    else:
      self.direction = u'↓'
      label = Label().complete(' ', self.key, 'preref')
    self.destination = label
    self.formatcontents()
    if not self.key in Reference.references:
      Reference.references[self.key] = []
    Reference.references[self.key].append(self)

  def formatcontents(self):
    "Format the reference contents."
    formatkey = self.getparameter('LatexCommand')
    if not formatkey:
      formatkey = 'ref'
    self.formatted = u'↕'
    if formatkey in StyleConfig.referenceformats:
      self.formatted = StyleConfig.referenceformats[formatkey]
    else:
      Trace.error('Unknown reference format ' + formatkey)
    self.replace(u'↕', self.direction)
    self.replace('#', '1')
    self.replace('on-page', Translator.translate('on-page'))
    partkey = self.destination.findpartkey()
    # only if partkey and partkey.number are not null, send partkey.number
    self.replace('@', partkey and partkey.number)
    self.replace(u'¶', partkey and partkey.tocentry)
    if not '$' in self.formatted or not partkey or not partkey.titlecontents:
      # there is a $ left, but it should go away on preprocessing
      self.contents = [Constant(self.formatted)]
      return
    pieces = self.formatted.split('$')
    self.contents = [Constant(pieces[0])]
    for piece in pieces[1:]:
      self.contents += partkey.titlecontents
      self.contents.append(Constant(piece))

  def replace(self, key, value):
    "Replace a key in the format template with a value."
    if not key in self.formatted:
      return
    if not value:
      value = ''
    self.formatted = self.formatted.replace(key, value)

  def __unicode__(self):
    "Return a printable representation."
    return 'Reference ' + self.key

