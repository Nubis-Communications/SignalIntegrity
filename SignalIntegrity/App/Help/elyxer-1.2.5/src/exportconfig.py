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
# Alex 20090504
# eLyXer configuration manipulation

import sys
import datetime
from elyxer.util.trace import Trace
from elyxer.util.clparse import *
from elyxer.conf.fileconfig import *
from elyxer.conf.importconfig import *


class Config(object):
  "A configuration file"

  cfg = 'conf/base.cfg'
  py = 'elyxer/conf/config.py'
  po = 'conf/elyxer.pot'
  addcfg = None
  importcfg = None
  importcsv = None
  importunimath = None
  help = False

  def run(self, args):
    "Parse command line options and run export to cfg or to py"
    parser = CommandLineParser(Config)
    error = parser.parseoptions(args)
    if error:
      Trace.error(error)
      self.usage()
    elif Config.help:
      self.usage()
    option = self.parseoption(args)
    if not option:
      Trace.error('Choose cfg, py or po')
      self.usage()
    if option == 'cfg':
      self.exportcfg()
      return
    elif option == 'py':
      self.exportpy()
      return
    elif option == 'po':
      self.exportpo()
    else:
      Trace.error('Unknown option ' + option)
      self.usage()

  def usage(self):
    "Show tool usage"
    Trace.error('Usage: exportconfig.py [options] [cfg|py|po]')
    Trace.error('  cfg: export to text configuration file')
    Trace.error('  py: export to python file')
    Trace.error('  po: export elyxer.pot internationalization file')
    Trace.error('  options:')
    Trace.error('    --cfg base.cfg: choose base config file')
    Trace.error('    --addcfg add.cfg: load additional config file')
    Trace.error('    --py config.py: choose Python config file')
    Trace.error('    --importcfg unicodesymbols: import LyX unicode symbols file')
    Trace.error('    --importcsv unicodecsv: import a file of "\command,unicode" pairs')
    Trace.error('    --importunimath unimath.txt: import a file in unimath format')
    Trace.error('      (See http://milde.users.sourceforge.net/LUCR/Math/)')
    exit()

  def read(self):
    "Read from configuration file"
    reader = ConfigReader(Config.cfg).parse()
    if Config.addcfg:
      addreader = ConfigReader(Config.addcfg).parse()
      self.mix(reader, addreader)
    if Config.importcfg:
      addreader = ImportCommands(Config.importcfg).parse()
      self.mix(reader, addreader)
    if Config.importcsv:
      addreader = ImportCsv(Config.importcsv).parse()
      self.mix(reader, addreader)
    if Config.importunimath:
      addreader = ImportUnimath(Config.importunimath).parse()
      self.mix(reader, addreader)
    reader.objects['GeneralConfig.version']['date'] = datetime.date.today().isoformat()
    return reader

  def exportcfg(self):
    "Export configuration to a cfg file"
    linewriter = LineWriter(Config.cfg)
    writer = ConfigWriter(linewriter)
    configs = [globals()[x] for x in dir(elyxer.conf.config) if x.endswith('Config')]
    writer.writeall(configs)

  def exportpy(self):
    "Export configuration as a Python file"
    reader = self.read()
    linewriter = LineWriter(Config.py)
    translator = ConfigToPython(linewriter)
    translator.write(reader.objects)

  def exportpo(self):
    "Export configuration as a gettext .po file."
    reader = self.read()
    writer = LineWriter(Config.po)
    export = TranslationExport(writer)
    export.export(reader.objects['TranslationConfig.constants'])

  def parseoption(self, args):
    "Parse the next option"
    if len(args) == 0:
      return None
    option = args[0]
    del args[0]
    return option

  def mix(self, reader, addreader):
    "Mix two configuration files"
    Trace.message('--- new content follows ---')
    for name, object in addreader.objects.iteritems():
      Trace.message('')
      Trace.message('[' + name + ']')
      equiv = reader.objects[name]
      for key, value in object.iteritems():
        if not key in equiv:
          equiv[key] = value
          Trace.message(key + ':' + unicode(value))

class TranslationExport(object):
  "Export the translation to a file."

  def __init__(self, writer):
    self.writer = writer

  def export(self, constants):
    "Export the translation constants as a .po file."
    self.writer.writeline('# eLyXer internationalization file.')
    self.writer.writeline('# Created on ' + datetime.date.today().isoformat())
    self.writer.writeline(u'# Contact: Alex Fernandez <elyxer@gmail.com>')
    self.writer.writeline(u'# http://elyxer.nongnu.org/')
    self.writer.writeline('# This file is distributed under the same license as the eLyXer package.')
    self.writer.writeline('# (C) 2010 Alex Fernandez <elyxer@gmail.com>.')
    self.writer.writeline('#')
    self.writer.writeline('')
    for key, message in constants.iteritems():
      self.writer.writeline('')
      self.writer.writeline('#: ' + key)
      self.writer.writeline('msgid  "' + message + '"')
      self.writer.writeline('msgstr "' + message + '"')
    self.writer.close()

config = Config()
del sys.argv[0]
config.run(sys.argv)

