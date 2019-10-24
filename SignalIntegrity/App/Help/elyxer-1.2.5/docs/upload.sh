#!/bin/bash

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

# Alex 20090315: upload generated documentation to Savannah CVS

# download current docs
mkdir cvs
cd cvs
#rm -Rf elyxer
#cvs -z3 -d:ext:alexfernandez@cvs.savannah.nongnu.org:/web/elyxer co elyxer
cvs  -z3 -d:ext:alexfernandez@cvs.savannah.nongnu.org:/web/elyxer update elyxer
# overwrite with current docs
cp ../*.html elyxer/
cp ../*.png elyxer/
cp ../*.css elyxer/
# remove MathJaX and jsMath (comment if they are updated)
#rm -Rf elyxer/MathJax
#rm -Rf elyxer/jsMath
# commit
cd elyxer
cvs commit -m "Automatic upload"

