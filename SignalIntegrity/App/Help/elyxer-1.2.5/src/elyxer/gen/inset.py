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
# Alex 20090506
# LyX insets

from elyxer.util.trace import Trace
from elyxer.parse.parser import *
from elyxer.parse.headerparse import *
from elyxer.out.output import *
from elyxer.io.bulk import *
from elyxer.gen.container import *
from elyxer.gen.styles import *
from elyxer.gen.layout import *


class InsetText(Container):
  "An inset of text in a lyx file"

  def __init__(self):
    self.parser = BoundedParser()
    self.output = ContentsOutput()

class Inset(Container):
  "A generic inset in a LyX document"

  def __init__(self):
    self.contents = list()
    self.parser = InsetParser()
    self.output = TaggedOutput().setbreaklines(True)

  def process(self):
    self.type = self.header[1]
    self.output.tag = 'span class="' + self.type + '"'

  def __unicode__(self):
    return 'Inset of type ' + self.type

class NewlineInset(Newline):
  "A newline or line break in an inset"

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

class NewPageInset(NewPage):
  "A new page command."

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

class Branch(Container):
  "A branch within a LyX document"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="branch"', True)

  def process(self):
    "Disable inactive branches"
    self.branch = self.header[2]
    if not self.isactive():
      Trace.debug('Branch ' + self.branch + ' not active')
      self.output = EmptyOutput()

  def isactive(self):
    "Check if the branch is active"
    if not self.branch in Options.branches:
      Trace.error('Invalid branch ' + self.branch)
      return True
    branch = Options.branches[self.branch]
    return branch.isselected()

class ShortTitle(Container):
  "A short title to display (always hidden)"

  def __init__(self):
    self.parser = InsetParser()
    self.output = EmptyOutput()

class FlexInset(Container):
  "A flexible inset, generic version."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span', False)

  def process(self):
    "Set the correct flex tag."
    self.type = self.header[2]
    if self.type in TagConfig.flex:
      self.output.settag(TagConfig.flex[self.type], False)
    else:
      self.output.settag('span class="' + self.type + '"', False)

class InfoInset(Container):
  "A LyX Info inset"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="Info"', False)

  def process(self):
    "Set the shortcut as text"
    self.type = self.getparameter('type')
    self.contents = [Constant(self.getparameter('arg'))]

class BoxInset(Container):
  "A box inset"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('div', True)

  def process(self):
    "Set the correct tag"
    self.type = self.header[2]
    self.output.settag('div class="' + self.type + '"', True)
    ContainerSize().readparameters(self).addstyle(self)

class PhantomText(Container):
  "A line of invisible text (white over white)."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span class="phantom"', False)

class LineInset(LyXLine):
  "A LaTeX ruler, but parsed as an inset."

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

class Caption(Container):
  "A caption for a figure or a table"

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('div class="caption"', True)
    
  def create(self, message):
    "Create a caption with a given message."
    self.contents = [Constant(message)]
    return self

class ScriptInset(Container):
  "Sub- or super-script in an inset."

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput().settag('span', False)

  def process(self):
    "Set the correct script tag."
    self.type = self.header[2]
    if not self.type in TagConfig.script:
      Trace.error('Unknown script type ' + self.type)
      return
    self.output.settag(TagConfig.script[self.type], False)

