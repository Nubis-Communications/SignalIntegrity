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
# Alex 20090311
# LyX styles in containers

from elyxer.util.trace import Trace
from elyxer.util.numbering import *
from elyxer.parse.parser import *
from elyxer.out.output import *
from elyxer.gen.container import *
from elyxer.gen.size import *


class QuoteContainer(Container):
  "A container for a pretty quote"

  def __init__(self):
    self.parser = BoundedParser()
    self.output = FixedOutput()

  def process(self):
    "Process contents"
    self.type = self.header[2]
    if not self.type in StyleConfig.quotes:
      Trace.error('Quote type ' + self.type + ' not found')
      self.html = ['"']
      return
    self.html = [StyleConfig.quotes[self.type]]

class LyXLine(Container):
  "A Lyx line"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = FixedOutput()

  def process(self):
    self.html = ['<hr class="line" />']

class EmphaticText(TaggedText):
  "Text with emphatic mode"

  def process(self):
    self.output.tag = 'i'

class ShapedText(TaggedText):
  "Text shaped (italic, slanted)"

  def process(self):
    self.type = self.header[1]
    if not self.type in TagConfig.shaped:
      Trace.error('Unrecognized shape ' + self.header[1])
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.shaped[self.type]

class VersalitasText(TaggedText):
  "Text in versalitas"

  def process(self):
    self.output.tag = 'span class="versalitas"'

class ColorText(TaggedText):
  "Colored text"

  def process(self):
    self.color = self.header[1]
    self.output.tag = 'span class="' + self.color + '"'

class SizeText(TaggedText):
  "Sized text"

  def process(self):
    self.size = self.header[1]
    self.output.tag = 'span class="' + self.size + '"'

class BoldText(TaggedText):
  "Bold text"

  def process(self):
    self.output.tag = 'b'

class TextFamily(TaggedText):
  "A bit of text from elyxer.a different family"

  def process(self):
    "Parse the type of family"
    self.type = self.header[1]
    if not self.type in TagConfig.family:
      Trace.error('Unrecognized family ' + type)
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.family[self.type]

class Hfill(TaggedText):
  "Horizontall fill"

  def process(self):
    self.output.tag = 'span class="hfill"'

class BarredText(TaggedText):
  "Text with a bar somewhere"

  def process(self):
    "Parse the type of bar"
    self.type = self.header[1]
    if not self.type in TagConfig.barred:
      Trace.error('Unknown bar type ' + self.type)
      self.output.tag = 'span'
      return
    self.output.tag = TagConfig.barred[self.type]

class LangLine(TaggedText):
  "A line with language information"

  def process(self):
    "Only generate a span with lang info when the language is recognized."
    lang = self.header[1]
    if not lang in TranslationConfig.languages:
      self.output = ContentsOutput()
      return
    isolang = TranslationConfig.languages[lang]
    self.output = TaggedOutput().settag('span lang="' + isolang + '"', False)

class InsetLength(BlackBox):
  "A length measure inside an inset."

  def process(self):
    self.length = self.header[1]

class Space(Container):
  "A space of several types"

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()
  
  def process(self):
    self.type = self.header[2]
    if self.type not in StyleConfig.hspaces:
      Trace.error('Unknown space type ' + self.type)
      self.html = [' ']
      return
    self.html = [StyleConfig.hspaces[self.type]]
    length = self.getlength()
    if not length:
      return
    self.output = TaggedOutput().settag('span class="hspace"', False)
    ContainerSize().set(length).addstyle(self)

  def getlength(self):
    "Get the space length from elyxer.the contents or parameters."
    if len(self.contents) == 0 or not isinstance(self.contents[0], InsetLength):
      return None
    return self.contents[0].length

class VerticalSpace(Container):
  "An inset that contains a vertical space."

  def __init__(self):
    self.parser = InsetParser()
    self.output = FixedOutput()

  def process(self):
    "Set the correct tag"
    self.type = self.header[2]
    if self.type not in StyleConfig.vspaces:
      self.output = TaggedOutput().settag('div class="vspace" style="height: ' + self.type + ';"', True)
      return
    self.html = [StyleConfig.vspaces[self.type]]

class Align(Container):
  "Bit of aligned text"

  def __init__(self):
    self.parser = ExcludingParser()
    self.output = TaggedOutput().setbreaklines(True)

  def process(self):
    self.output.tag = 'div class="' + self.header[1] + '"'

class Newline(Container):
  "A newline"

  def __init__(self):
    self.parser = LoneCommand()
    self.output = FixedOutput()

  def process(self):
    "Process contents"
    self.html = ['<br/>\n']

class NewPage(Newline):
  "A new page"

  def process(self):
    "Process contents"
    self.html = ['<p><br/>\n</p>\n']

class Separator(Container):
  "A separator string which is not extracted by extracttext()."

  def __init__(self, constant):
    self.output = FixedOutput()
    self.contents = []
    self.html = [constant]

class StrikeOut(TaggedText):
  "Striken out text."

  def process(self):
    "Set the output tag to strike."
    self.output.tag = 'strike'

class StartAppendix(BlackBox):
  "Mark to start an appendix here."
  "From this point on, all chapters become appendices."

  def process(self):
    "Activate the special numbering scheme for appendices, using letters."
    NumberGenerator.generator.startappendix()

