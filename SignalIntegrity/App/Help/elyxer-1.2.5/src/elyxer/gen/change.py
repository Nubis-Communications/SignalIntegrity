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
# Alex 20100829
# Change tracking

from elyxer.util.trace import Trace
from elyxer.util.docparams import *
from elyxer.gen.container import *


class ChangeInserted(Container):
  "A change which consists of an insertion."

  def __init__(self):
    self.parser = TextParser(self)
    if DocumentParameters.outputchanges:
      self.output = TaggedOutput().settag('span class="inserted"')
    else:
      self.output = ContentsOutput()

class ChangeDeleted(TaggedText):
  "A change which consists of a deletion."

  def __init__(self):
    self.parser = TextParser(self)
    if DocumentParameters.outputchanges:
      self.output = TaggedOutput().settag('span class="deleted"')
    else:
      self.output = EmptyOutput()

