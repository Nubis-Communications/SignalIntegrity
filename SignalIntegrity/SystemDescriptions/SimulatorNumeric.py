"""
 Performs Simulations Numerically
"""
# Teledyne LeCroy Inc. ("COMPANY") CONFIDENTIAL
# Unpublished Copyright (c) 2015-2016 Peter J. Pupalaikis and Teledyne LeCroy,
# All Rights Reserved.
#
# Explicit license in accompanying README.txt file.  If you don't have that file
# or do not agree to the terms in that file, then you are not licensed to use
# this material whatsoever.

from numpy import matrix

from SignalIntegrity.SystemDescriptions.Simulator import Simulator


class SimulatorNumeric(Simulator):
    """class for performing numeric simulations
    @note For the purposes of this class, the numerical simulation work
    has been performed by returning the transfer matrix.  Transfer matrices
    built over many frequencies are then utilized in the actual waveform
    processing for the simulation."""
    def __init__(self,sd=None):
        """Constructor
        @param sd (optional) instance of class SystemDescription
        """
        Simulator.__init__(self,sd)
    def TransferMatrix(self):
        """TransferMatrix
        @return list of list transfer matrix that for O output waveforms
        and I input waveforms is OxI and be considered as multiplied by
        a vector of input waveforms to produce a vector of output waveforms.

        The transfer matrix provided is for a single frequency."""
        self.Check()
        VE_o=matrix(self.VoltageExtractionMatrix(self.m_ol))
        SIPrime=matrix(self.SIPrime())
        sm=matrix(self.SourceToStimsPrimeMatrix())
        Result=(VE_o*SIPrime*sm).tolist()
        return Result