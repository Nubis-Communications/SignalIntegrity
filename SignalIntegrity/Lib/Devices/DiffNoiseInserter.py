"""
DiffNoiseInserter.py
"""

# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# Copyright (c) 2021-2025 Nubis Communications, Inc.
# Copyright (c) 2026 Ciena, Inc.
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

def DiffNoiseInserter():
    """DiffNoiseInserter
    Differential noise inserter.
    @return the s-parameter matrix of a differential noise inserter.
    @remark
    Six-port device with ports:
    - 1, 2 : left differential pair
    - 3, 4 : right differential pair
    - 5, 6 : differential noise ports (noise source connects between 5 and 6)

    The device passes the differential signal from ports 1-2 through to
    ports 3-4 and simultaneously injects the differential noise from
    ports 5-6 into the output.

    It is formed by placing two voltage mixed-mode converters back-to-back,
    connecting the common-mode ports together.  The statistical noise source
    is then connected between the differential ports, having the final effect
    of adding the noise to the differential signal.

             +--------+                 +--------+
      1 >----+ +    D +---< 5     6 >---+ D    + +----< 3
             |        |                 |        |
             |    V   |                 |    V   |
             |        |                 |        |
      2 >----+ -    C +-----------------+ C    - +----< 4
             +--------+                 +--------+
    """
    return [[ 0. ,  0. ,  0.5,  0.5,  0.5,  0. ],
            [ 0. ,  0. ,  0.5,  0.5, -0.5,  0. ],
            [ 0.5,  0.5,  0. ,  0. ,  0. ,  0.5],
            [ 0.5,  0.5,  0. ,  0. ,  0. , -0.5],
            [ 1. , -1. ,  0. ,  0. ,  0. ,  0. ],
            [ 0. ,  0. ,  1. , -1. ,  0. ,  0. ]]