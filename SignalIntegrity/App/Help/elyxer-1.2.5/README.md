eLyXer -- convert LyX source files to HTML output.

Introduction
============
eLyXer converts a LyX source file to a HTML page. Full documentation in HTML
format can be found at docs/index.html, or on the web:
  http://www.nongnu.org/elyxer/

Installation
============
Quick installation guide (for the impatient):
* download the latest version from http://www.nongnu.org/elyxer/,
* decompress the .zip or .tar.gz
* and install it using the provided script install.py as root:
    # ./install.py
  or on Windows:
    > python install.py

To install eLyXer first download a compressed version from
  http://www.nongnu.org/elyxer/
You will also need a recent (> 2.4) version of Python on your target machine.

For decompression: open a terminal window in the directory that contains the
downloaded file and just write at the command line prompt:
  $ tar -xzf elyxer-[version].tar.gz
Or for the .zip version:
  $ unzip elyxer-[version].zip
where [version] should be something like 0.44; the full name might be something
like elyxer-0.44.tar.gz.

On Windows or Mac OS X you can unzip the file using the graphical tool of your
choice. In any case, a directory called elyxer-[version] should appear, where
the installer script install.py can be found (along with this README).

The recommended installation procedure is to just run this script. On Linux
type as root:
  # ./install.py
and similarly for Mac OS X, while for Windows open a console and type:
  > python install.py
Note the you don't need to write the prompt, # or >; the console will print it
for you. Double-clicking on install.py should also work if your Python
installation is minimally sane. It will tell you as a result to which directory
eLyXer has been installed as a binary, which is be the typical result; in this
case eLyXer should be run as follows:
  $ elyxer.py [input file] [output file]
or, on Windows:
  > elyxer.py [input file] [output file]
You can test that it works with the --help option:
  $ elyxer.py --help
or, on Windows:
  > elyxer.py --help
Usage and options should then be shown.

LyX Integration
===============

To integrate eLyXer with LyX you just have to reconfigure LyX, selecting
Tools -> Reconfigure from within LyX. For rather old versions of LyX (< 1.6.2)
you may have to copy elyxer.py into the LyX directory, and reconfigure it.
Later versions will recognize eLyXer automatically, either if you install it
using distutils or as a binary.

Usage
=====
eLyXer can be invoked from the command line as:
  $ elyxer.py [source file] [destination file]

If the source file is omitted then STDIN is used; likewise, if no destination
file is specified eLyXer will output to STDOUT. This allows its use in pipes
and other flexible configurations.

Examples:
  $ elyxer.py file.lyx file.html
converts file.lyx to file.html. Debug messages are shown.
  $ cat file.lyx | elyxer.py > file.html
converts file.lyx to file.html, as before. This time debug messages are not
shown.
  $ elyxer.py file.lyx | grep "<blockquote>" | wc
counts all blockquote paragraphs.
  $ elyxer.py file.lyx | wget --no-check-certificate --spider -nv -F -i -
checks all external links in a document recursively. (Local links will appear
as unresolved, but they can be ignored.)

Documentation
=============
Documentation about eLyXer, including a user guide and a developer guide, can
be found in the docs directory. The project is hosted at Savannah.nongnu.org.  
Be sure to visit the project home page at:
  http://www.nongnu.org/elyxer/

License
=======
eLyXer is Copyright (C) 2009-2011 Alex Fernández.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


math2html (a subset of eLyXer) Copyright (C) 2009-2011 Alex Fernández

Released under the terms of the `2-Clause BSD license'_, in short:
Copying and distribution of this file, with or without modification,
are permitted in any medium without royalty provided the copyright
notice and this notice are preserved.
This file is offered as-is, without any warranty.
.. _2-Clause BSD license: http://www.spdx.org/licenses/BSD-2-Clause

Enjoy!

