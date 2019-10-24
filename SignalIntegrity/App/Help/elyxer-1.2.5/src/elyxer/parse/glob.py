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
# Alex 20110111
# eLyXer globbing of an underlying string.

from elyxer.util.trace import Trace


class Globable(object):
  """A bit of text which can be globbed (lumped together in bits).
  Methods current(), skipcurrent(), checkfor() and isout() have to be
  implemented by subclasses."""

  leavepending = False

  def __init__(self):
    self.endinglist = EndingList()

  def checkbytemark(self):
    "Check for a Unicode byte mark and skip it."
    if self.finished():
      return
    if ord(self.current()) == 0xfeff:
      self.skipcurrent()

  def isout(self):
    "Find out if we are out of the position yet."
    Trace.error('Unimplemented isout()')
    return True

  def current(self):
    "Return the current character."
    Trace.error('Unimplemented current()')
    return ''

  def checkfor(self, string):
    "Check for the given string in the current position."
    Trace.error('Unimplemented checkfor()')
    return False

  def finished(self):
    "Find out if the current text has finished."
    if self.isout():
      if not self.leavepending:
        self.endinglist.checkpending()
      return True
    return self.endinglist.checkin(self)

  def skipcurrent(self):
    "Return the current character and skip it."
    Trace.error('Unimplemented skipcurrent()')
    return ''

  def glob(self, currentcheck):
    "Glob a bit of text that satisfies a check on the current char."
    glob = ''
    while not self.finished() and currentcheck():
      glob += self.skipcurrent()
    return glob

  def globalpha(self):
    "Glob a bit of alpha text"
    return self.glob(lambda: self.current().isalpha())

  def globnumber(self):
    "Glob a row of digits."
    return self.glob(lambda: self.current().isdigit())

  def isidentifier(self):
    "Return if the current character is alphanumeric or _."
    if self.current().isalnum() or self.current() == '_':
      return True
    return False

  def globidentifier(self):
    "Glob alphanumeric and _ symbols."
    return self.glob(self.isidentifier)

  def isvalue(self):
    "Return if the current character is a value character:"
    "not a bracket or a space."
    if self.current().isspace():
      return False
    if self.current() in '{}()':
      return False
    return True

  def globvalue(self):
    "Glob a value: any symbols but brackets."
    return self.glob(self.isvalue)

  def skipspace(self):
    "Skip all whitespace at current position."
    return self.glob(lambda: self.current().isspace())

  def globincluding(self, magicchar):
    "Glob a bit of text up to (including) the magic char."
    glob = self.glob(lambda: self.current() != magicchar) + magicchar
    self.skip(magicchar)
    return glob

  def globexcluding(self, excluded):
    "Glob a bit of text up until (excluding) any excluded character."
    return self.glob(lambda: self.current() not in excluded)

  def pushending(self, ending, optional = False):
    "Push a new ending to the bottom"
    self.endinglist.add(ending, optional)

  def popending(self, expected = None):
    "Pop the ending found at the current position"
    if self.isout() and self.leavepending:
      return expected
    ending = self.endinglist.pop(self)
    if expected and expected != ending:
      Trace.error('Expected ending ' + expected + ', got ' + ending)
    self.skip(ending)
    return ending

  def nextending(self):
    "Return the next ending in the queue."
    nextending = self.endinglist.findending(self)
    if not nextending:
      return None
    return nextending.ending

class EndingList(object):
  "A list of position endings"

  def __init__(self):
    self.endings = []

  def add(self, ending, optional = False):
    "Add a new ending to the list"
    self.endings.append(PositionEnding(ending, optional))

  def pickpending(self, pos):
    "Pick any pending endings from a parse position."
    self.endings += pos.endinglist.endings

  def checkin(self, pos):
    "Search for an ending"
    if self.findending(pos):
      return True
    return False

  def pop(self, pos):
    "Remove the ending at the current position"
    if pos.isout():
      Trace.error('No ending out of bounds')
      return ''
    ending = self.findending(pos)
    if not ending:
      Trace.error('No ending at ' + pos.current())
      return ''
    for each in reversed(self.endings):
      self.endings.remove(each)
      if each == ending:
        return each.ending
      elif not each.optional:
        Trace.error('Removed non-optional ending ' + each)
    Trace.error('No endings left')
    return ''

  def findending(self, pos):
    "Find the ending at the current position"
    if len(self.endings) == 0:
      return None
    for index, ending in enumerate(reversed(self.endings)):
      if ending.checkin(pos):
        return ending
      if not ending.optional:
        return None
    return None

  def checkpending(self):
    "Check if there are any pending endings"
    if len(self.endings) != 0:
      Trace.error('Pending ' + unicode(self) + ' left open')

  def __unicode__(self):
    "Printable representation"
    string = 'endings ['
    for ending in self.endings:
      string += unicode(ending) + ','
    if len(self.endings) > 0:
      string = string[:-1]
    return string + ']'

class PositionEnding(object):
  "An ending for a parsing position"

  def __init__(self, ending, optional):
    self.ending = ending
    self.optional = optional

  def checkin(self, pos):
    "Check for the ending"
    return pos.checkfor(self.ending)

  def __unicode__(self):
    "Printable representation"
    string = 'Ending ' + self.ending
    if self.optional:
      string += ' (optional)'
    return string

