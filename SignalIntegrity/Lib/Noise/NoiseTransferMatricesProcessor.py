"""
NoiseTransferMatricesProcessor.py
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

from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionSimulator
from SignalIntegrity.Lib.CallBacker import CallBacker

class NoiseTransferMatricesProcessor(CallBacker):
    """Processes transfer matrices for noise spectral densities.
    Given transfer matrices and a list of input spectral densities, produces
    output spectral densities by multiplying each input by its corresponding
    frequency response magnitude and combining contributions via root-sum-square
    (assuming uncorrelated noise sources).

    @see TransferMatrices
    @see SpectralDensity
    """
    def __init__(self, transferMatrices, callback=None):
        """Constructor
        @param transferMatrices instance of class TransferMatrices.
        @param callback (optional) reference to function that takes float percentage
        used for periodically calling to show progress and allow aborting.
        @see CallBacker
        """
        self.TransferMatrices = transferMatrices
        CallBacker.__init__(self, callback)

    def ProcessNoise(self, sdl):
        """Processes input noise spectral densities through transfer matrices.
        @param sdl list of SpectralDensity instances, one per input source.
        @return list of SpectralDensity instances, one per output.
        @remark
        For each output o, the output spectral density is computed as:
            SD_out[o](f) = sqrt( sum_i ( |H[o][i](f)| * SD_in[i](f) )^2 )
        This assumes uncorrelated noise sources so contributions add in
        root-sum-square fashion.
        """
        fr = self.TransferMatrices.FrequencyResponses()
        if fr is None:
            return None
        self.Contributions = [[None for _ in range(self.TransferMatrices.Inputs)]
                              for _ in range(self.TransferMatrices.Outputs)]
        self.Result = []
        for o in range(self.TransferMatrices.Outputs):
            outputSD = None
            for i in range(self.TransferMatrices.Inputs):
                contribution = sdl[i] * fr[o][i]
                self.Contributions[o][i] = contribution
                if outputSD is None:
                    outputSD = contribution
                else:
                    outputSD = outputSD + contribution
                if self.HasACallBack():
                    progress = (float(o) / self.TransferMatrices.Outputs +
                                float(i) / (self.TransferMatrices.Outputs *
                                             self.TransferMatrices.Inputs)) * 100.0
                    if not self.CallBack(progress):
                        raise SignalIntegrityExceptionSimulator('calculation aborted')
            self.Result.append(outputSD)
        return self.Result
