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
# Alex 20090203
# eLyXer html outputters

from elyxer.util.trace import Trace


class ContainerOutput(object):
  "The generic HTML output for a container."

  def gethtml(self, container):
    "Show an error."
    Trace.error('gethtml() not implemented for ' + unicode(self))

  def isempty(self):
    "Decide if the output is empty: by default, not empty."
    return False

class EmptyOutput(ContainerOutput):

  def gethtml(self, container):
    "Return empty HTML code."
    return []

  def isempty(self):
    "This output is particularly empty."
    return True

class FixedOutput(ContainerOutput):
  "Fixed output"

  def gethtml(self, container):
    "Return constant HTML code"
    return container.html

class ContentsOutput(ContainerOutput):
  "Outputs the contents converted to HTML"

  def gethtml(self, container):
    "Return the HTML code"
    html = []
    if container.contents == None:
      return html
    for element in container.contents:
      if not hasattr(element, 'gethtml'):
        Trace.error('No html in ' + element.__class__.__name__ + ': ' + unicode(element))
        return html
      html += element.gethtml()
    return html

class TaggedOutput(ContentsOutput):
  "Outputs an HTML tag surrounding the contents."

  tag = None
  breaklines = False
  empty = False

  def settag(self, tag, breaklines=False, empty=False):
    "Set the value for the tag and other attributes."
    self.tag = tag
    if breaklines:
      self.breaklines = breaklines
    if empty:
      self.empty = empty
    return self

  def setbreaklines(self, breaklines):
    "Set the value for breaklines."
    self.breaklines = breaklines
    return self

  def gethtml(self, container):
    "Return the HTML code."
    if self.empty:
      return [self.selfclosing(container)]
    html = [self.open(container)]
    html += ContentsOutput.gethtml(self, container)
    html.append(self.close(container))
    return html

  def open(self, container):
    "Get opening line."
    if not self.checktag():
      return ''
    open = '<' + self.tag + '>'
    if self.breaklines:
      return open + '\n'
    return open

  def close(self, container):
    "Get closing line."
    if not self.checktag():
      return ''
    close = '</' + self.tag.split()[0] + '>'
    if self.breaklines:
      return '\n' + close + '\n'
    return close

  def selfclosing(self, container):
    "Get self-closing line."
    if not self.checktag():
      return ''
    selfclosing = '<' + self.tag + '/>'
    if self.breaklines:
      return selfclosing + '\n'
    return selfclosing

  def checktag(self):
    "Check that the tag is valid."
    if not self.tag:
      Trace.error('No tag in ' + unicode(container))
      return False
    if self.tag == '':
      return False
    return True

class FilteredOutput(ContentsOutput):
  "Returns the output in the contents, but filtered:"
  "some strings are replaced by others."

  def __init__(self):
    "Initialize the filters."
    self.filters = []

  def addfilter(self, original, replacement):
    "Add a new filter: replace the original by the replacement."
    self.filters.append((original, replacement))

  def gethtml(self, container):
    "Return the HTML code"
    result = []
    html = ContentsOutput.gethtml(self, container)
    for line in html:
      result.append(self.filter(line))
    return result

  def filter(self, line):
    "Filter a single line with all available filters."
    for original, replacement in self.filters:
      if original in line:
        line = line.replace(original, replacement)
    return line

class StringOutput(ContainerOutput):
  "Returns a bare string as output"

  def gethtml(self, container):
    "Return a bare string"
    return [container.string]

