"""
SignalIntegrityQt.py - PySide6 user interface for SignalIntegrity
"""
# Copyright (c) 2026 Nubis Communications, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>
import sys

def main(argv=None):
    argv=sys.argv if argv is None else argv
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        sys.stderr.write('PySide6 is required: pip install SignalIntegrity[qt]\n')
        return 1
    from SignalIntegrity.QtApp.MainWindow import MainWindow
    app=QApplication.instance() or QApplication(argv)
    app.setApplicationName('SignalIntegrity (Qt)')
    window=MainWindow()
    window.show()
    if len(argv)>1:
        window.OpenProject(argv[1])
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
