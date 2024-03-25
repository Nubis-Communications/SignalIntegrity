"""
ClockRecovery.py
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

from SignalIntegrity.Lib.TimeDomain.Waveform import TimeDescriptor,Waveform
from SignalIntegrity.Lib.TimeDomain.Filters import WaveformTrimmer

import numpy as np
from copy import deepcopy
from scipy import interpolate

class ClockRecoveredWaveform(Waveform):
    """Resamples an input waveform using clock recovery
        """
    def __init__(self,input_waveform,baudrate,trim_left_right=20):
        """Generates a resampled waveform using clock recovery  
        It is formed by hashing the bitmap definition with whatever else is hashed.
        @param input_waveform instance of class Waveform, waveform to resample 
        @param baudrate float, symbol rate of the waveform.
        @param trim_left_right int, defaults to 20, number of points to trim from the two samples per
        UI waveform that determines the time error for the clock recovery.  This must be enough points so that when
        interpolating, the timing error does not try to interpolate beyond the boundaries of the input waveform.
        """
        Fs=baudrate*2. # we want a waveform that contains two samples per unit interval
        UpsampleFactor=Fs/input_waveform.td.Fs

        # The waveform is adapted to the new sample rate.  This puts it on the same sample frame as the original waveform, such that there
        # is the assumption that there is a point at exactly time zero, and that is the center of the unit interval.
        # the amount of points to remove is trimmed from the left to make the very first sample at the center of a unit interval.
        adapted_waveform=input_waveform.Adapt(TimeDescriptor(input_waveform.td.H,input_waveform.td.K*UpsampleFactor,Fs))

        samples=np.array(adapted_waveform.Values())

        Nf=int(2**8)
        No=0
        Nw=Nf//4
        Na=5

        """
        This function performs timing recovery for input PAM4 signal at 2sps
        S. Lees timing recovery algorithm
        A new non data aided. S. Lee, A new non data aided feedforward symbol timing estimator using two samples per symbol IEEE Commun Lett. 6 (5), 205 207, (2002)

        example

        Nf = 2^13
        No = 0
        Nw = Nf/4
        Na = 5

        """
        x = deepcopy(samples)
        x = x / (np.sqrt(np.mean(np.abs(x) ** 2)))  # Normalization
        Nb = int(np.floor((len(x) - No) / (Nf - No)))  # Number of block

        # Blockwise spectra

        Xk = np.zeros(shape=(Nf, Nb), dtype=complex)

        for nn in range(Nb):
            xk = x[nn * (Nf - No) : nn * (Nf - No) + Nf]
            Xk[:, nn] = np.fft.fft(xk) / np.sqrt(Nf)

        # Cross correlation

        Xl = Xk[int(Nf / 4 - Nw / 2) : int(Nf / 4 - Nw / 2) + Nw, :]
        Xu = Xk[
            int(Nf / 4 - Nw / 2)
            + int(Nf / 2) : int(Nf / 4 - Nw / 2)
            + int(Nf / 2)
            + Nw,
            :,
        ]
        Xu1 = np.imag(Xl * np.conj(Xu))
        Xu2 = np.sin(
            2
            * np.pi
            * np.arange(int(Nf / 4 - Nw / 2), int(Nf / 4 - Nw / 2) + Nw, 1)
            / Nf
        )

        for nn in range(Nb):
            Xu1[:, nn] = Xu2 * Xu1[:, nn]

        Xu1 = 1j * Xu1

        xc = np.sum(np.real(Xl * np.conj(Xu)) + Xu1, 0)
        xc = np.concatenate(
            (
                np.ones(int(np.floor(Na / 2))) * xc[0],
                xc,
                np.ones(int(np.floor(Na / 2))) * xc[-1],
            )
        )
        xc = np.convolve(xc, np.ones(Na) / Na, mode="valid")

        # Determinant

        dt = np.unwrap(np.angle(xc))
        te = dt / np.pi

        # Generating timing grid

        xg = np.arange(int(Nf / 2 + 1), Nb * (Nf - No) + int(Nf / 2 + 1), Nf - No)
        f = interpolate.interp1d(xg, te, "cubic")
        xg_1 = np.arange(xg[0], xg[-1] + 1, 1)
        te = f(xg_1)
        xg_inter = xg_1 + te

        f1 = interpolate.interp1d(xg_inter, samples[xg[0] : xg[-1] + 1], "cubic")
        samples = f1(xg_1[trim_left_right:-trim_left_right])

        # Originally, this was the timing corrected waveform.  The problem with it is that it is the input waveform downsampled to two samples per UI
        # For now, I comment this out and try to reconstitute the input waveform that is timing corrected.
#         Waveform.__init__(self,TimeDescriptor(adapted_waveform.td.H+(xg_1[1])/adapted_waveform.td.Fs,samples.shape[0],adapted_waveform.td.Fs),samples.tolist())

        # calculate the time error waveform on the two samples per UI timing grid
        te_waveform=Waveform(TimeDescriptor(adapted_waveform.td.H+(Nf//2+1)/adapted_waveform.td.Fs,te.shape[0],adapted_waveform.td.Fs),
                             (te/adapted_waveform.td.Fs).tolist())

        # trim some points to try to keep the time error in range
        te_waveform*=WaveformTrimmer(trim_left_right,trim_left_right)

        # upsample the time error to the sample rate of the input waveform
        te_waveform=te_waveform.Adapt(TimeDescriptor(te_waveform.td.H,te_waveform.td.K*input_waveform.td.Fs/te_waveform.td.Fs,input_waveform.td.Fs))

        # interpolate the input waveform, removing the timing error
        f1 = interpolate.interp1d(input_waveform.Times(),input_waveform.Values(), "cubic")
        retimed_waveform_values=f1([t-e for t,e in zip(te_waveform.Times(),te_waveform.Values())])
        retimed_waveform=Waveform(te_waveform.TimeDescriptor(),retimed_waveform_values.tolist())

        # The interpolation will have failed if trim_left_right is insufficient.
        Waveform.__init__(self,retimed_waveform.TimeDescriptor(),retimed_waveform.Values())

#         retimed_waveform.WriteToFile('retimed.txt')
#         import matplotlib.pyplot as plt
#         plt.plot(te_waveform.Times('ns'),[v/1e-12 for v in te_waveform.Values()])
#         plt.xlabel('time (ns)')
#         plt.ylabel('time error (ps)')
#         plt.grid()
#         plt.show()
