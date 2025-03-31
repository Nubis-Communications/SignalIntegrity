"""
Reference.py
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

def Reference():
    """Reference

    This part is used either to identify the reference in a typical s-parameter measurement or simulation to convert two + and - referenced ports
    to a single port, or in reverse, when taking a typical s-parameter measurement or simulation result and exposing the reference.

    Port 1 is the single-ended input

    Ports 2 and 3 are the positive and negative single-ended outputs, respectively.

    Examples:
    If I have a four-port DUT where two of the ports are the so-called ground reference for a port, such as in HFSS, it is simulated in HFSS
    something like this:

        +-----+    +-----+    +-----+
        |   + +----+     +----+ +   |
    1 >-+  R  |    | DUT |    |  R  +-< 2
        |   - +----+     +----+ -   |
        +-----+    +-----+    +-----+

    Then, if we place the two-port DUT simulated and place this into a circuit simulation, the reference nodes for each port are exposed by
    placing this device in reverse:

        +-----+    +-----+    +-----+
    1 >-+ +   |    |     |    |   + +-< 3
        |  R  +----+ DUT +----+  R  |
    2 >-+ -   |    |     |    |   - +-< 4
        +-----+    +-----+    +-----+

    where port 2 is the reference for port 1 (i.e. port 1 should be measured differentially with respect to port 2) and
    port 4 is the reference for port 3.

    @return the s-parameter matrix of a reference
    """
    return [[1./3.,2./3.,-2./3.],
            [2./3.,1./3.,2./3.],
            [-2./3.,2./3.,1./3.]]
