"""
 Transfer Matrices
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

from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import FrequencyList
from numpy import zeros

class TransferMatrices(list):
    """Class that is used for processing waveforms in simulation."""
    def __init__(self,f,d):
        """Constructor
        @param f instance of class FrequencyList
        @param d list of list of list matrices
        @remark
        The list of list of list matrices in d are such that each element in the list
        represents a list of list matrix for a given frequency.  The list of list matrix
        for a frequency is the frequency response that converts inputs (columns) to outputs
        (rows).  If d is an N+1 element list of RxC matrices, then for n in 0..N, d[n][r][c]
        represents the frequency response for a filter used to convert input C into output
        r.

        Generally, you don't deal with the structure of d as it is produced completely by the
        two classes SimulatorNumericParser and VirtualProbeNumericParser, and an element of d
        for a frequency is produced by the two classes SimulatorNumeric and VirtualProbeNumeric.
        """
        self.f=FrequencyList(f)
        list.__init__(self,d)
        self.Inputs=len(d[0][0])
        self.Outputs=len(d[0])
    def SParameters(self):
        """SParameters
        @return list of list of lists representing the transfer matrices as s-parameters.
        @note that transfer matrices are actually very much like s-parameters because they
        provide the complex frequency-domain relationship between an input and output at the
        given frequencies.  The only actual difference is that an s-parameter matrix must be
        square while transfer parameter matrices can be rectangular.

        s-parameters make it convenient for writing and viewing transfer matrices, so this
        format is provided.  The transfer matrices converted to s-parameters will have a square
        matrix whose row and column length is the maximum of the row and column length of a
        transfer matrix.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.SParameters.SParameters import SParameters
        # pragma: include
        if self.Inputs == self.Outputs:
            return SParameters(self.f,self)
        else:
            squareMatrices=[]
            P=max(self.Inputs,self.Outputs)
            for transferMatrix in self:
                squareMatrix=zeros((P,P),complex).tolist()
                for r in range(len(transferMatrix)):
                    for c in range(len(transferMatrix[0])):
                        squareMatrix[r][c]=transferMatrix[r][c]
                squareMatrices.append(squareMatrix)
            return SParameters(self.f,squareMatrices)
    def FrequencyResponse(self,o,i):
        """frequency response of one filter
        @param o integer index of output
        @param i integer index of input
        @return instance of class FrequencyResponse corresponding to the frequency response of
        a filter used to convert input i to output o.
        """
        # pragma: silent exclude
        from SignalIntegrity.Lib.FrequencyDomain.FrequencyResponse import FrequencyResponse
        # pragma: include
        return FrequencyResponse(self.f,[Matrix[o-1][i-1]
            for Matrix in self])
    def FrequencyResponses(self):
        """frequency responses of filters
        @return list of list of instances of class FrequencyResponse
        @remark
        The return is a list of list like a matrix where each element in the matrix M is
        such that M[o][i] is the frequency response of a filter that would convert the
        input i to an output o.
        @see FrequencyResponse()
        """
        return [[self.FrequencyResponse(o+1,s+1)
            for s in range(self.Inputs)] for o in range(self.Outputs)]
    def ImpulseResponses(self,td=None):
        """impulse responses of filters
        @return list of list of instances of class ImpulseResponse
        @remark
        The return is a list of list like a matrix where each element in the matrix M is
        such that M[o][i] is the impulse response of a filter that would convert the
        input i to an output o.
        """
        fr = self.FrequencyResponses()
        if td is None or isinstance(td,float) or isinstance(td,int):
            td = [td for m in range(len(fr[0]))]
        return [[fro[m].ImpulseResponse(td[m]) for m in range(len(fro))]
            for fro in fr]
