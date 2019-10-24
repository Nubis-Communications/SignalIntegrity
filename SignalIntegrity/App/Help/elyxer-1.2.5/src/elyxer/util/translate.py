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
# Alex 20100112
# eLyXer translations and translation generation

import gettext
from elyxer.util.trace import Trace
from elyxer.util.docparams import *
from elyxer.conf.config import *


class Translator(object):
  "Reads the configuration file and tries to find a translation."
  "Otherwise falls back to the messages in the config file."

  instance = None

  def translate(cls, key):
    "Get the translated message for a key."
    return cls.instance.getmessage(key)

  translate = classmethod(translate)

  def __init__(self):
    self.translation = None
    self.first = True

  def findtranslation(self):
    "Find the translation for the document language."
    self.langcodes = None
    if not DocumentParameters.language:
      Trace.error('No language in document')
      return
    if not DocumentParameters.language in TranslationConfig.languages:
      Trace.error('Unknown language ' + DocumentParameters.language)
      return
    if TranslationConfig.languages[DocumentParameters.language] == 'en':
      return
    langcodes = [TranslationConfig.languages[DocumentParameters.language]]
    try:
      self.translation = gettext.translation('elyxer', None, langcodes)
    except IOError:
      Trace.error('No translation for ' + unicode(langcodes))

  def getmessage(self, key):
    "Get the translated message for the given key."
    if self.first:
      self.findtranslation()
      self.first = False
    message = self.getuntranslated(key)
    if not self.translation:
      return message
    try:
      message = self.translation.ugettext(message)
    except IOError:
      pass
    return message

  def getuntranslated(self, key):
    "Get the untranslated message."
    if not key in TranslationConfig.constants:
      Trace.error('Cannot translate ' + key)
      return key
    return TranslationConfig.constants[key]

Translator.instance = Translator()

