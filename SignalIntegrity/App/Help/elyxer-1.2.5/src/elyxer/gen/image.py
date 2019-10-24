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
# Alex 20090308
# eLyXer image treatment

import struct
import sys
import os
import shutil
from elyxer.util.trace import Trace
from elyxer.util.translate import *
from elyxer.gen.container import *
from elyxer.gen.size import *
from elyxer.io.path import *


class Image(Container):
  "An embedded image"

  defaultformat = ImageConfig.formats['default']
  size = None
  copy = None

  def __init__(self):
    self.parser = InsetParser()
    self.output = TaggedOutput()
    self.type = 'embedded'

  def process(self):
    "Place the url, convert the image if necessary."
    self.origin = InputPath(self.getparameter('filename'))
    self.destination = self.getdestination(self.origin)
    self.size = ContainerSize().readparameters(self)
    if self.origin.exists():
      ImageConverter.instance.convert(self)
    else:
      Trace.error('Image ' + unicode(self.origin) + ' not found')
    self.setsize()
    self.settag()

  def getdestination(self, origin):
    "Convert origin path to destination path."
    "Changes extension of destination to output image format."
    destination = OutputPath(origin)
    if Options.noconvert:
      return destination
    self.convertformat(destination)
    destination.removebackdirs()
    return destination

  def convertformat(self, destination):
    "Convert the format of the destination image."
    if Options.copyimages:
      return
    imageformat = '.jpg'
    forcedest = Image.defaultformat
    if Options.imageformat:
      imageformat = Options.imageformat
      forcedest = Options.imageformat
    if not destination.hasext(imageformat):
      destination.changeext(forcedest)

  def setsize(self):
    "Set the size attributes width and height."
    width, height = ImageFile(self.destination).getdimensions()
    self.size.checkimage(width, height)

  def scalevalue(self, value):
    "Scale the value according to the image scale and return it as unicode."
    scaled = value * int(self.size.scale) / 100
    return unicode(int(scaled)) + 'px'

  def settag(self):
    "Set the output tag for the image."
    tag = 'img class="' + self.type + '"'
    if self.origin.exists():
      url = self.destination.url
    else:
      url = self.origin.url
    alt = Translator.translate('figure') + ' ' + url
    tag += ' src="' + url + '" alt="' + alt + '"'
    emptytag = True
    if self.destination.hasext('.svg'):
      self.contents = [Constant(alt)]
      tag = 'object class="' + self.type + '" data="' + url + '"'
      emptytag = False
    self.output.settag(tag, True, empty=emptytag)
    self.size.addstyle(self)

class ImageConverter(object):
  "A converter from elyxer.one image file to another."

  vectorformats = ImageConfig.formats['vector']
  cropboxformats = ImageConfig.cropboxformats

  active = True
  instance = None

  def convert(self, image):
    "Convert an image to PNG"
    if not ImageConverter.active or Options.noconvert:
      return
    if image.origin.path == image.destination.path:
      return
    if image.destination.exists():
      if image.origin.getmtime() <= image.destination.getmtime():
        # file has not changed; do not convert
        return
    image.destination.createdirs()
    if Options.copyimages:
      Trace.debug('Copying ' + image.origin.path + ' to ' + image.destination.path)
      shutil.copy2(image.origin.path, image.destination.path)
      return
    converter, command = self.buildcommand(image)
    try:
      Trace.debug(converter + ' command: "' + command + '"')
      result = os.system(command.encode(sys.getfilesystemencoding()))
      if result != 0:
        Trace.error(converter + ' not installed; images will not be processed')
        ImageConverter.active = False
        return
      Trace.message('Converted ' + unicode(image.origin) + ' to ' +
          unicode(image.destination))
    except OSError, exception:
      Trace.error('Error while converting image ' + unicode(image.origin)
          + ': ' + unicode(exception))

  def buildcommand(self, image):
    "Build the command to convert the image."
    if Options.converter in ImageConfig.converters:
      command = ImageConfig.converters[Options.converter]
    else:
      command = Options.converter;
    params = self.getparams(image)
    for param in params:
      command = command.replace('$' + param, unicode(params[param]))
    # remove unwanted options
    while '[' in command and ']' in command:
      command = self.removeparam(command)
    return Options.converter, command

  def removeparam(self, command):
    "Remove an unwanted param."
    if command.index('[') > command.index(']'):
      Trace.error('Converter command should be [...$...]: ' + command)
      exit()
    before = command[:command.index('[')]
    after = command[command.index(']') + 1:]
    between = command[command.index('[') + 1:command.index(']')]
    if '$' in between:
      return before + after
    return before + between + after

  def getparams(self, image):
    "Get the parameters for ImageMagick conversion"
    params = dict()
    params['input'] = image.origin
    params['output'] = image.destination
    if image.origin.hasexts(self.vectorformats):
      scale = 100
      if image.size.scale:
        scale = image.size.scale
        # descale
        image.size.scale = None
      params['scale'] = scale
    if image.origin.getext() in self.cropboxformats:
      params['format'] = self.cropboxformats[image.origin.getext()]
    return params

ImageConverter.instance = ImageConverter()

class ImageFile(object):
  "A file corresponding to an image (JPG or PNG)"

  dimensions = dict()

  def __init__(self, path):
    "Create the file based on its path"
    self.path = path

  def getdimensions(self):
    "Get the dimensions of a JPG or PNG image"
    if not self.path.exists():
      return None, None
    if unicode(self.path) in ImageFile.dimensions:
      return ImageFile.dimensions[unicode(self.path)]
    dimensions = (None, None)
    if self.path.hasext('.png'):
      dimensions = self.getpngdimensions()
    elif self.path.hasext('.jpg'):
      dimensions = self.getjpgdimensions()
    elif self.path.hasext('.svg'):
      dimensions = self.getsvgdimensions()
    ImageFile.dimensions[unicode(self.path)] = dimensions
    return dimensions

  def getpngdimensions(self):
    "Get the dimensions of a PNG image"
    pngfile = self.path.open()
    pngfile.seek(16)
    width = self.readlong(pngfile)
    height = self.readlong(pngfile)
    pngfile.close()
    return (width, height)

  def getjpgdimensions(self):
    "Get the dimensions of a JPEG image"
    jpgfile = self.path.open()
    start = self.readword(jpgfile)
    if start != int('ffd8', 16):
      Trace.error(unicode(self.path) + ' not a JPEG file')
      return (None, None)
    self.skipheaders(jpgfile, ['ffc0', 'ffc2'])
    self.seek(jpgfile, 3)
    height = self.readword(jpgfile)
    width = self.readword(jpgfile)
    jpgfile.close()
    return (width, height)

  def getsvgdimensions(self):
    "Get the dimensions of a SVG image."
    return (None, None)

  def skipheaders(self, file, hexvalues):
    "Skip JPEG headers until one of the parameter headers is found"
    headervalues = [int(value, 16) for value in hexvalues]
    header = self.readword(file)
    safetycounter = 0
    while header not in headervalues and safetycounter < 30:
      length = self.readword(file)
      if length == 0:
        Trace.error('End of file ' + file.name)
        return
      self.seek(file, length - 2)
      header = self.readword(file)
      safetycounter += 1

  def readlong(self, file):
    "Read a long (32-bit) value from elyxer.file"
    return self.readformat(file, '>L', 4)

  def readword(self, file):
    "Read a 16-bit value from elyxer.file"
    return self.readformat(file, '>H', 2)

  def readformat(self, file, format, bytes):
    "Read any format from elyxer.file"
    read = file.read(bytes)
    if read == '' or len(read) < bytes:
      Trace.error('EOF reached')
      return 0
    tuple = struct.unpack(format, read)
    return tuple[0]

  def seek(self, file, bytes):
    "Seek forward, just by reading the given number of bytes"
    file.read(bytes)

