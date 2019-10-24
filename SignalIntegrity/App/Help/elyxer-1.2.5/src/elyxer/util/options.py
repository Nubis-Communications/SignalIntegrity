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
# Alex 20090313
# eLyXer runtime options

import os.path
import sys
from elyxer.conf.config import *
from elyxer.util.trace import *
from elyxer.util.clparse import *


class Options(object):
  "A set of runtime options"

  instance = None

  location = None
  nocopy = False
  copyright = False
  debug = False
  quiet = False
  version = False
  hardversion = False
  versiondate = False
  html = False
  help = False
  showlines = True
  unicode = False
  iso885915 = False
  css = []
  title = None
  directory = None
  destdirectory = None
  toc = False
  toctarget = ''
  tocfor = None
  forceformat = None
  lyxformat = False
  target = None
  splitpart = None
  memory = True
  lowmem = False
  nobib = False
  converter = 'imagemagick'
  raw = False
  jsmath = None
  mathjax = None
  nofooter = False
  simplemath = False
  template = None
  noconvert = False
  notoclabels = False
  letterfoot = True
  numberfoot = False
  symbolfoot = False
  hoverfoot = True
  marginfoot = False
  endfoot = False
  supfoot = True
  alignfoot = False
  footnotes = None
  imageformat = None
  copyimages = False
  googlecharts = False
  embedcss = []

  branches = dict()

  def parseoptions(self, args):
    "Parse command line options"
    Options.location = args[0]
    del args[0]
    parser = CommandLineParser(Options)
    result = parser.parseoptions(args)
    if result:
      Trace.error(result)
      self.usage()
    self.processoptions()

  def processoptions(self):
    "Process all options parsed."
    if Options.help:
      self.usage()
    if Options.version:
      self.showversion()
    if Options.hardversion:
      self.showhardversion()
    if Options.versiondate:
      self.showversiondate()
    if Options.lyxformat:
      self.showlyxformat()
    if Options.splitpart:
      try:
        Options.splitpart = int(Options.splitpart)
        if Options.splitpart <= 0:
          Trace.error('--splitpart requires a number bigger than zero')
          self.usage()
      except:
        Trace.error('--splitpart needs a numeric argument, not ' + Options.splitpart)
        self.usage()
    if Options.lowmem or Options.toc or Options.tocfor:
      Options.memory = False
    self.parsefootnotes()
    if Options.forceformat and not Options.imageformat:
      Options.imageformat = Options.forceformat
    if Options.imageformat == 'copy':
      Options.copyimages = True
    if Options.css == []:
      Options.css = ['http://elyxer.nongnu.org/lyx.css']
    if Options.html:
      Options.simplemath = True
    if Options.toc and not Options.tocfor:
      Trace.error('Option --toc is deprecated; use --tocfor "page" instead')
      Options.tocfor = Options.toctarget
    if Options.nocopy:
      Trace.error('Option --nocopy is deprecated; it is no longer needed')
    if Options.jsmath:
      Trace.error('Option --jsmath is deprecated; use --mathjax instead')
    # set in Trace if necessary
    for param in dir(Trace):
      if param.endswith('mode'):
        setattr(Trace, param, getattr(self, param[:-4]))

  def usage(self):
    "Show correct usage"
    Trace.error('Usage: ' + os.path.basename(Options.location) + ' [options] [filein] [fileout]')
    Trace.error('Convert LyX input file "filein" to HTML file "fileout".')
    Trace.error('If filein (or fileout) is not given use standard input (or output).')
    Trace.error('Main program of the eLyXer package (http://elyxer.nongnu.org/).')
    self.showoptions()

  def parsefootnotes(self):
    "Parse footnotes options."
    if not Options.footnotes:
      return
    Options.marginfoot = False
    Options.letterfoot = False
    Options.hoverfoot = False
    options = Options.footnotes.split(',')
    for option in options:
      footoption = option + 'foot'
      if hasattr(Options, footoption):
        setattr(Options, footoption, True)
      else:
        Trace.error('Unknown footnotes option: ' + option)
    if not Options.endfoot and not Options.marginfoot and not Options.hoverfoot:
      Options.hoverfoot = True
    if not Options.numberfoot and not Options.symbolfoot:
      Options.letterfoot = True

  def showoptions(self):
    "Show all possible options"
    Trace.error('  Common options:')
    Trace.error('    --help:                 show this online help')
    Trace.error('    --quiet:                disables all runtime messages')
    Trace.error('')
    Trace.error('  Advanced options:')
    Trace.error('    --debug:                enable debugging messages (for developers)')
    Trace.error('    --version:              show version number and release date')
    Trace.error('    --lyxformat:            return the highest LyX version supported')
    Trace.error('  Options for HTML output:')
    Trace.error('    --title "title":        set the generated page title')
    Trace.error('    --css "file.css":       use a custom CSS file')
    Trace.error('    --embedcss "file.css":  embed styles from a CSS file into the output')
    Trace.error('    --html:                 output HTML 4.0 instead of the default XHTML')
    Trace.error('    --unicode:              full Unicode output')
    Trace.error('    --iso885915:            output a document with ISO-8859-15 encoding')
    Trace.error('    --nofooter:             remove the footer "generated by eLyXer"')
    Trace.error('    --simplemath:           do not generate fancy math constructions')
    Trace.error('  Options for image output:')
    Trace.error('    --directory "img_dir":  look for images in the specified directory')
    Trace.error('    --destdirectory "dest": put converted images into this directory')
    Trace.error('    --imageformat ".ext":   image output format, or "copy" to copy images')
    Trace.error('    --noconvert:            do not convert images, use in original locations')
    Trace.error('    --converter "inkscape": use an alternative program to convert images')
    Trace.error('  Options for footnote display:')
    Trace.error('    --numberfoot:           mark footnotes with numbers instead of letters')
    Trace.error('    --symbolfoot:           mark footnotes with symbols (*, **...)')
    Trace.error('    --hoverfoot:            show footnotes as hovering text (default)')
    Trace.error('    --marginfoot:           show footnotes on the page margin')
    Trace.error('    --endfoot:              show footnotes at the end of the page')
    Trace.error('    --supfoot:              use superscript for footnote markers (default)')
    Trace.error('    --alignfoot:            use aligned text for footnote markers')
    Trace.error('    --footnotes "options":  specify several comma-separated footnotes options')
    Trace.error('      Available options are: "number", "symbol", "hover", "margin", "end",')
    Trace.error('        "sup", "align"')
    Trace.error('  Advanced output options:')
    Trace.error('    --splitpart "depth":    split the resulting webpage at the given depth')
    Trace.error('    --tocfor "page":        generate a TOC that points to the given page')
    Trace.error('    --target "frame":       make all links point to the given frame')
    Trace.error('    --notoclabels:          omit the part labels in the TOC, such as Chapter')
    Trace.error('    --lowmem:               do the conversion on the fly (conserve memory)')
    Trace.error('    --raw:                  generate HTML without header or footer.')
    Trace.error('    --mathjax remote:       use MathJax remotely to display equations')
    Trace.error('    --mathjax "URL":        use MathJax from the given URL to display equations')
    Trace.error('    --googlecharts:         use Google Charts to generate formula images')
    Trace.error('    --template "file":      use a template, put everything in <!--$content-->')
    Trace.error('    --copyright:            add a copyright notice at the bottom')
    Trace.error('  Deprecated options:')
    Trace.error('    --toc:                  (deprecated) create a table of contents')
    Trace.error('    --toctarget "page":     (deprecated) generate a TOC for the given page')
    Trace.error('    --nocopy:               (deprecated) maintained for backwards compatibility')
    Trace.error('    --jsmath "URL":         use jsMath from the given URL to display equations')
    sys.exit()

  def showversion(self):
    "Return the current eLyXer version string"
    string = 'eLyXer version ' + GeneralConfig.version['number']
    string += ' (' + GeneralConfig.version['date'] + ')'
    Trace.error(string)
    sys.exit()

  def showhardversion(self):
    "Return just the version string"
    Trace.message(GeneralConfig.version['number'])
    sys.exit()

  def showversiondate(self):
    "Return just the version dte"
    Trace.message(GeneralConfig.version['date'])
    sys.exit()

  def showlyxformat(self):
    "Return just the lyxformat parameter"
    Trace.message(GeneralConfig.version['lyxformat'])
    sys.exit()

class BranchOptions(object):
  "A set of options for a branch"

  def __init__(self, name):
    self.name = name
    self.options = {'color':'#ffffff'}

  def set(self, key, value):
    "Set a branch option"
    if not key.startswith(ContainerConfig.string['startcommand']):
      Trace.error('Invalid branch option ' + key)
      return
    key = key.replace(ContainerConfig.string['startcommand'], '')
    self.options[key] = value

  def isselected(self):
    "Return if the branch is selected"
    if not 'selected' in self.options:
      return False
    return self.options['selected'] == '1'

  def __unicode__(self):
    "String representation"
    return 'options for ' + self.name + ': ' + unicode(self.options)

