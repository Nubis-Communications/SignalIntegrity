"""
 Termination polynomials for calibration standards.
"""

# Copyright (c) 2018 Teledyne LeCroy, Inc.
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

from SignalIntegrity.Lib.SParameters.SParameters import SParameters
from SignalIntegrity.Lib.Devices.TerminationC import TerminationC
from SignalIntegrity.Lib.Devices.TerminationL import TerminationL

class TerminationPolynomial(object):
    """Base class for terminations for calibration standards"""
    def __init__(self,a0=0.0,a1=0.0,a2=0.0,a3=0.0):
        """Constructor
        @param a0 (optional) float polynomial term for f^0 (defaults to 0.0).
        @param a1 (optional) float polynomial term for f^1 (defaults to 0.0).
        @param a2 (optional) float polynomial term for f^2 (defaults to 0.0).
        @param a3 (optional) float polynomial term for f^3 (defaults to 0.0).
        """
        self.a0=a0
        self.a1=a1
        self.a2=a2
        self.a3=a3
    def Polynomial(self,f):
        """Evaluates polynomial.
        @param f float frequency
        @return float polynomial evaluated at frequency f
        """
        return ((self.a3*f+self.a2)*f+self.a1)*f+self.a0
 
class TerminationCPolynomial(SParameters,TerminationPolynomial):
    """Class for capacitive terminations for open calibration standards"""
    def __init__(self,f,C0=0.0,C1=0.0,C2=0.0,C3=0.0,Z0=50.):
        """Constructor
        @param f list of frequencies for the s-parameters
        @param C0 (optional) float polynomial term for f^0 (defaults to 0.0).
        @param C1 (optional) float polynomial term for f^1 (defaults to 0.0).
        @param C2 (optional) float polynomial term for f^2 (defaults to 0.0).
        @param C3 (optional) float polynomial term for f^3 (defaults to 0.0).
        @param Z0 (optional) real or complex reference impedance Z0 (defaults to 50 Ohms).
        """
        TerminationPolynomial.__init__(self,C0,C1,C2,C3)
        SParameters.__init__(self,f,None,Z0)
    def PolynomialC(self,n):
        """Evaluate capacitance polynomial.
        @param n integer index of frequency
        @return float polynomial evaluated at frequency f[n]
        """
        f=self.m_f[n]
        return self.Polynomial(f)
    def __getitem__(self,n):
        """Overrides [n]
        @param n integer index of s-parameter frequency to evaluate
        @return list of list s-parameter matrix for frequency at index n
        """
        return TerminationC(self.PolynomialC(n),self.m_f[n],self.m_Z0)
    
class TerminationLPolynomial(SParameters,TerminationPolynomial):
    """Class for inductive terminations for short calibration standards"""
    def __init__(self,f,L0=0.0,L1=0.0,L2=0.0,L3=0.0,Z0=50.):
        """Constructor
        @param f list of frequencies for the s-parameters
        @param L0 (optional) float polynomial term for f^0 (defaults to 0.0).
        @param L1 (optional) float polynomial term for f^1 (defaults to 0.0).
        @param L2 (optional) float polynomial term for f^2 (defaults to 0.0).
        @param L3 (optional) float polynomial term for f^3 (defaults to 0.0).
        @param Z0 (optional) real or complex reference impedance Z0 (defaults to 50 Ohms).
        """
        TerminationPolynomial.__init__(self,L0,L1,L2,L3)
        SParameters.__init__(self,f,None,Z0)
    def PolynomialL(self,n):
        """Evaluate inductance polynomial.
        @param n integer index of frequency
        @return float polynomial evaluated at frequency f
        """
        f=self.m_f[n]
        return self.Polynomial(f)
    def __getitem__(self,n):
        """Overrides [n]
        @param n integer index of s-parameter frequency to evaluate
        @return list of list s-parameter matrix for frequency at index n
        """
        return TerminationL(self.PolynomialL(n),self.m_f[n],self.m_Z0)
