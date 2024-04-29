"""
Dispatcher.py
"""
# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
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

class Dispatcher(object):
    def __init__(self):
        pass
    def SystemDescription(self,sd):
        lines=[]
        lines.append(str(len(sd)))
        for device in sd:
            lines.append(device.Name)
            lines.append(str(len(device)))
            for port in device:
                lines.append(port.A)
                lines.append(port.B)
                lines.append(port.M)
        for device in sd:
            sp=device.SParameters
            lines.append(str(len(sp)))
            for r in range(len(sp)):
                for c in range(len(sp)):
                    if isinstance(sp[r][c],str):
                        lines.append('0')
                        lines.append('0')
                    else:
                        lines.append(str(sp[r][c].real))
                        lines.append(str(sp[r][c].imag))
        lines = [line+'\n' for line in lines]
        return lines
    def SParameters(self,spc):
        lines=[]
        lines.append(str(len(spc)))
        for name,sp in spc:
            lines.append(name)
            lines.append(str(len(sp)))
            lines.append(str(sp.m_P))
            for n in range(len(sp)):
                for r in range(sp.m_P):
                    for c in range(sp.m_P):
                        lines.append(str(sp[n][r][c].real))
                        lines.append(str(sp[n][r][c].imag))
        lines = [line+'\n' for line in lines]
        return lines
        
            
