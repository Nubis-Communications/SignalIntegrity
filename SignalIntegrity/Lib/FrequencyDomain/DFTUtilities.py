"""
 DFTUtilities.py
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

import math
import cmath
import random

import numpy as np

class DFTUtilities(object):
    """A set of DFT utilities for dealing with the DFT for handling frequency
    and time-domain information properly.

    @remark
    All methods are static. They operate on either:
    - a full conjugate-symmetric DFT vector of length K, or
    - a single-sided spectrum of length N+1 where N = K // 2.

    The @a Keven flag indicates the parity of the time-record length K:
    - Keven = True  : K = 2*N
    - Keven = False : K = 2*N + 1

    Reference: Pupalaikis, Peter J., S-parameters for Signal Integrity,
    Cambridge University Press, p. 371.
    """

    # ---- basic counts / axes -------------------------------------------------

    @staticmethod
    def N(K):
        """Number of frequency points minus one.
        @param K integer time-record length.
        @return integer N = floor(K/2), the index of the highest frequency bin
        in a single-sided spectrum.
        """
        return K // 2

    @staticmethod
    def K(N, Keven=True):
        """Time-record length from the frequency bin count.
        @param N integer number of frequency bins minus one.
        @param Keven (optional) bool, True (default) if K is even (K=2N),
        False if K is odd (K=2N+1).
        @return integer K = 2*N if Keven else 2*N + 1.
        @see N
        """
        return 2 * N + (0 if Keven else 1)

    @staticmethod
    def Keven(K):
        """Parity test for a time-record length K.
        @param K integer (or integer-valued) time-record length.
        @return bool, True if K is even, False if odd.
        @remark K is cast to int first so that callers passing numpy
        integer/float scalars (e.g. from a TimeDescriptor) get a correct
        integer parity test rather than an accidental float modulus.
        @see N
        @see K
        """
        return int(K) % 2 == 0

    @staticmethod
    def EndFrequency(K, Fs):
        """Highest frequency of a single-sided spectrum.
        @param K integer time-record length.
        @param Fs float sample rate (Hz).
        @return float Fe = (N/K) * Fs, where N = K//2.
        @note Equals Fs/2 only when K is even.
        @see SampleRate
        """
        return (K // 2) * Fs / K

    @staticmethod
    def SampleRate(K, Fe):
        """Sample rate from the end frequency.
        @param K integer time-record length.
        @param Fe float end frequency (Hz).
        @return float Fs = (K/N) * Fe, where N = K//2.
        @note Inverse of EndFrequency().
        @see EndFrequency
        """
        return K * Fe / (K // 2)

    @staticmethod
    def DeltaFrequency(K, Fs):
        """Frequency bin spacing.
        @param K integer time-record length.
        @param Fs float sample rate (Hz).
        @return float df = Fs / K.
        """
        return Fs / K

    @staticmethod
    def Frequency(n, K, Fs):
        """Frequency of the n-th DFT bin.
        @param n integer bin index (0..K-1).
        @param K integer time-record length.
        @param Fs float sample rate (Hz).
        @return float frequency in Hz, f = n * Fs / K.
        """
        return n * Fs / K

    # ---- DFT length conversions ---------------------------------------------

    @staticmethod
    def Full_to_Half(X):
        """Single-sided spectrum from a full conjugate-symmetric DFT.
        @param X list of complex values, the full DFT of length K (even or odd).
        @return list of complex values, the first N+1 = K//2 + 1 entries.
        @remark
        A Keven flag is unnecessary because N = K // 2 yields the correct
        half length for both parities:
        - K = 2N   (Keven=True)  -> half length N+1
        - K = 2N+1 (Keven=False) -> half length N+1
        @see Half_to_Full
        """
        N = len(X) // 2
        return list(X[:N + 1])

    @staticmethod
    def Half_to_Full(X,Keven=True):
        Xarr=np.asarray(X)
        N = len(Xarr) - 1
        K = DFTUtilities.K(N, Keven)
        F = np.zeros(K,dtype=complex)
        F[:N+1]=Xarr
        if Keven:
            F[N+1:K]=np.conjugate(Xarr[N-1:0:-1])
        else:
            F[N+1:K]=np.conjugate(Xarr[N:0:-1])
        return F.tolist()

    # ---- DFT <-> amplitude --------------------------------------------------

    @staticmethod
    def X_to_A(X, Keven = True):
        """Single-sided amplitude A[n] from single-sided DFT X[n].
        @param X list of complex single-sided DFT values, length N+1.
        @param Keven bool, True if the underlying K is even (K=2N),
        False if odd (K=2N+1).
        @return list of float amplitudes A[n] = |X[n]| / K * factor, where
        factor is 1 for the DC bin (n=0) and (when Keven) the Nyquist bin
        (n=N), and 2 otherwise.
        @see AtoX
        """
        N = len(X) - 1
        K = 2 * N if Keven else 2 * N + 1
        factor=np.full(N+1,2.)
        factor[0]=1.
        if Keven: factor[N]=1.
        return (np.abs(np.asarray(X))/K*factor).tolist()

    # ---- amplitude -> DFT ---------------------------------------------------

    @staticmethod
    def A_to_X(A, Keven = True, random_phase=True):
        """Single-sided DFT X[n] from amplitude A[n].
        @param A list of float per-bin amplitudes, length N+1.
        @param Keven bool, True if the underlying K is even (K=2N),
        False if odd (K=2N+1).
        @param random_phase (optional) bool, True (default) to assign each
        interior bin an independent phase uniformly distributed in
        [-pi, pi); False to use zero phase (returns real magnitudes).
        @return list of complex DFT values of length N+1 with
        |X[n]| = A[n] * K / factor, where factor is 1 for the DC bin (n=0)
        and (when Keven) the Nyquist bin (n=N), and 2 otherwise.
        @note The DC bin (n=0) and, when Keven, the Nyquist bin (n=N) are
        kept real so that Hermitian extension yields a real-valued
        time-domain signal.
        @note Inverse of X_to_A().
        @see X_to_A
        """
        N = len(A) - 1
        K = 2 * N if Keven else 2 * N + 1
        X = []
        for n in range(N + 1):
            factor = 1. if (n == 0 or (n == N and Keven)) else 2.
            mag = A[n] * K / factor
            if random_phase and not (n == 0 or (n == N and Keven)):
                phase = random.uniform(-math.pi, math.pi)
            else:
                phase = 0.0
            X.append(mag * cmath.exp(1j * phase))
        return X

    # ---- amplitude -> rms ---------------------------------------------------

    @staticmethod
    def A_to_rms(A, Keven = True):
        """RMS values from single-sided amplitudes.
        @param A list of float amplitudes A[n], length N+1.
        @param Keven bool, True if the underlying K is even.
        @return list of float rms values, rms[n] = A[n] for DC and (when
        Keven) Nyquist bins, else A[n] / sqrt(2).
        @see rms_to_A
        """
        N = len(A) - 1
        divisor=np.full(N+1,math.sqrt(2.))
        divisor[0]=1.
        if Keven: divisor[N]=1.
        return (np.asarray(A)/divisor).tolist()

    @staticmethod
    def rms_to_A(rms, Keven = True):
        """Single-sided amplitudes from RMS values.
        @param rms list of float per-bin rms values, length N+1.
        @param Keven bool, True if the underlying K is even.
        @return list of float amplitudes, A[n] = rms[n] for DC and (when
        Keven) Nyquist bins, else rms[n] * sqrt(2).
        @note Inverse of A_to_rms().
        @see A_to_rms
        """
        N = len(rms) - 1
        factor=np.full(N+1,math.sqrt(2.))
        factor[0]=1.
        if Keven: factor[N]=1.
        return (np.asarray(rms)*factor).tolist()

    # ---- dBm ----------------------------------------------------------------

    @staticmethod
    def rms_to_dBm(rms):
        """Convert per-bin RMS values to dBm (referenced to 50 ohm, 1 mW).
        @param rms list of float per-bin rms values (Vrms).
        @return list of float dBm values, computed as
        20*log10(rms) - 10*log10(R*P), with R = 50 ohm and P = 1 mW.
        @note Values below 1e-15 Vrms clamp to -3000 dBm to avoid log of zero.
        """
        LogRP10 = 10. * math.log10(50.0 * 1e-3)
        r=np.asarray(rms,dtype=float)
        result=np.full(len(r),-3000.)
        mask=r>=1e-15
        result[mask]=20.*np.log10(r[mask])-LogRP10
        return result.tolist()

    # ---- spectral density ---------------------------------------------------

    @staticmethod
    def rms_to_rho(rms, delta_f, Keven = True):
        """Spectral density (Vrms/sqrt(Hz)) from per-bin RMS values.
        @param rms list of float per-bin rms values, length N+1.
        @param delta_f float bin spacing (Hz).
        @param Keven bool, True if the underlying K is even.
        @return list of float spectral densities rho[n]; an extra factor of
        sqrt(2) is applied at the DC bin (and, when Keven, the Nyquist bin)
        to account for their one-sided contribution.
        @see rho_to_rms
        """
        N = len(rms) - 1
        sqrt_df = math.sqrt(delta_f)
        factor=np.ones(N+1)
        factor[0]=math.sqrt(2.)
        factor[N]=math.sqrt(2.)
        return (np.asarray(rms)*factor/sqrt_df).tolist()

    @staticmethod
    def rho_to_rms(rho, delta_f, Keven = True):
        """Per-bin RMS values from spectral density.
        @param rho list of float spectral densities (Vrms/sqrt(Hz)), length N+1.
        @param delta_f float bin spacing (Hz).
        @param Keven bool, True if the underlying K is even.
        @return list of float per-bin rms values; an extra 1/sqrt(2) is
        applied at the DC bin (and, when Keven, the Nyquist bin), undoing
        the boost applied by rms_to_rho.
        @note Inverse of rms_to_rho().
        @see rms_to_rho
        """
        N = len(rho) - 1
        sqrt_df = math.sqrt(delta_f)
        factor=np.ones(N+1)
        factor[0]=math.sqrt(2.)
        factor[N]=math.sqrt(2.)
        return (np.asarray(rho)/factor*sqrt_df).tolist()

    # ---- totals -------------------------------------------------------------

    @staticmethod
    def TotalSpectralContentRMS(rms):
        """Total RMS across a single-sided spectrum.
        @param rms list of float per-bin rms values.
        @return float total rms = sqrt(sum(rms[n]^2)).
        """
        return math.sqrt(np.sum(np.square(np.asarray(rms,dtype=float))))

    @staticmethod
    def TotalSpectralContentdBm(dBm):
        """Total power (dBm) across a single-sided spectrum.
        @param dBm list of float per-bin dBm values.
        @return float total power in dBm, obtained by summing the linear
        powers and converting back to dBm.
        """
        LogRP10 = 10. * math.log10(50.0 * 1e-3)
        return 10. * math.log10(
            np.sum(10. ** ((np.asarray(dBm,dtype=float) + LogRP10) / 10.))) - LogRP10

    # --- spectral density conversions --------------------------------------

    @staticmethod
    def ConvertSpectralDensity(value, from_units, to_units, bw=None, reference='voltage'):
        """Convert a spectral quantity between unit representations.

        Supported voltage units (reference='voltage'):
            - 'dBm/Hz'      power spectral density (50 ohm, 1 mW reference)
            - 'V/sqrt(Hz)'  amplitude spectral density
            - 'V^2/GHz'     voltage power spectral density per GHz
            - 'Vrms'        integrated rms voltage over bandwidth @a bw
                            (assumes a flat/white spectrum across @a bw)

        Supported current units (reference='current'):
            - 'dBm/Hz'      power spectral density (50 ohm, 1 mW reference)
            - 'A/sqrt(Hz)'  amplitude spectral density
            - 'A^2/GHz'     current power spectral density per GHz
            - 'Arms'        integrated rms current over bandwidth @a bw
                            (assumes a flat/white spectrum across @a bw)

        @param value      float value to convert.
        @param from_units source unit (voltage or current set per @a reference).
        @param to_units   destination unit (voltage or current set per @a reference).
        @param bw         float bandwidth in Hz; required only when the rms
                          ('Vrms'/'Arms') unit appears as input or output.
        @param reference  'voltage' (default) or 'current'. Selects the unit
                          set and the power law used for the dBm leg. For a
                          voltage source P = asd^2 / R (R divides); for a
                          current source P = asd^2 * R (R multiplies).
        @return           converted value in @a to_units.
        @throws ValueError on unknown units, or missing @a bw when needed.
        @note
        Only the dBm leg differs between voltage and current references; the
        sqrt(Hz), ^2/GHz, and rms legs are structurally identical because they
        do not involve the reference impedance.
        """
        R = 50.
        P = 1e-3
        if reference == 'current':
            asd_units = 'A/sqrt(Hz)'
            sq_units = 'A^2/GHz'
            rms_units = 'Arms'
        else:
            asd_units = 'V/sqrt(Hz)'
            sq_units = 'V^2/GHz'
            rms_units = 'Vrms'
        valid = ('dBm/Hz', asd_units, sq_units, rms_units)
        if from_units not in valid:
            raise ValueError(f'Unknown spectral density unit: {from_units}')
        if to_units not in valid:
            raise ValueError(f'Unknown spectral density unit: {to_units}')
        if from_units == to_units:
            return value
        if (from_units == rms_units or to_units == rms_units) and bw is None:
            raise ValueError(f"'bw' is required when converting to/from '{rms_units}'")

        # Step 1: normalize input to amplitude spectral density (asd_units)
        if from_units == asd_units:
            asd = value
        elif from_units == 'dBm/Hz':
            # P = asd^2 / R (voltage) or P = asd^2 * R (current)
            if reference == 'current':
                asd = math.sqrt(P * 10. ** (value / 10.) / R)
            else:
                asd = math.sqrt(R * P * 10. ** (value / 10.))
        elif from_units == sq_units:
            asd = 0. if value <= 0. else math.sqrt(value / 1e9)
        else:  # rms_units
            asd = value / math.sqrt(bw)

        # Step 2: convert amplitude spectral density to requested output
        if to_units == asd_units:
            return asd
        if to_units == sq_units:
            return asd * asd * 1e9
        if to_units == 'dBm/Hz':
            if asd <= 0.:
                return -3000.
            if reference == 'current':
                return 10. * math.log10(asd * asd * R / P)
            return 10. * math.log10(asd * asd / R / P)
        return asd * math.sqrt(bw)  # rms_units