"""
Equalizer.py
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
import copy
import numpy as np

from SignalIntegrity.Lib.Exception import SignalIntegrityExceptionFitter
from SignalIntegrity.Lib.Fit.LevMar import LevMar
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform


class BlindEqualizer(LevMar):
    """Blind symbol-spaced FFE/DFE equalizer solved with Levenberg-Marquardt."""

    def __init__(
        self,
        waveform,
        num_levels,
        baud_rate,
        ideal_samples_per_ui,
        num_ffe_taps,
        num_dfe_taps,
        num_precursor_taps,
        spectral_density=None,
        callback=None,
    ):
        if not isinstance(waveform, Waveform):
            raise SignalIntegrityExceptionFitter('waveform must be an instance of Waveform')
        if num_levels < 2:
            raise SignalIntegrityExceptionFitter('num_levels must be >= 2')
        if baud_rate <= 0.0:
            raise SignalIntegrityExceptionFitter('baud_rate must be > 0')
        if int(ideal_samples_per_ui) != ideal_samples_per_ui or ideal_samples_per_ui <= 0:
            raise SignalIntegrityExceptionFitter('ideal_samples_per_ui must be a positive integer')
        if num_ffe_taps <= 0:
            raise SignalIntegrityExceptionFitter('num_ffe_taps must be > 0')
        if num_dfe_taps < 0:
            raise SignalIntegrityExceptionFitter('num_dfe_taps must be >= 0')
        if num_precursor_taps < 0 or num_precursor_taps >= num_ffe_taps:
            raise SignalIntegrityExceptionFitter('num_precursor_taps must satisfy 0 <= precursor < num_ffe_taps')

        self.input_waveform = Waveform(waveform)
        self.num_levels = int(num_levels)
        self.baud_rate = float(baud_rate)
        self.ideal_samples_per_ui = int(ideal_samples_per_ui)
        self.num_ffe_taps = int(num_ffe_taps)
        self.num_dfe_taps = int(num_dfe_taps)
        self.num_precursor_taps = int(num_precursor_taps)
        self.spectral_density = spectral_density

        self.ui = 1.0 / self.baud_rate
        self.goal_sample_rate = self.baud_rate * self.ideal_samples_per_ui
        self.levels = np.linspace(-1.0, 1.0, self.num_levels)

        self._base_h = self.input_waveform.td.H
        self._num_symbols = int(math.floor(self.input_waveform.td.Duration() * self.baud_rate))
        self._num_symbols = max(self._num_symbols, self.num_dfe_taps + 2)
        self._goal_num_points = self._num_symbols * self.ideal_samples_per_ui

        self._resampled_cache = {}
        self._cursor_index = self.num_precursor_taps
        self._noise_frequency_grid = None
        self._noise_frequencies = None
        self._noise_density_squared = None
        if self.spectral_density is not None:
            self._initialize_noise_residual()

        LevMar.__init__(self, callback)
        # Numerical derivative step must work for both tap values and phase (seconds).
        self.m_epsilon = 1e-4 / self.goal_sample_rate

        tau0 = self._scan_initial_phase()
        a0 = np.zeros((self.num_ffe_taps + self.num_dfe_taps + 1, 1), dtype=float)
        a0[self._cursor_index][0] = 1.0
        a0[-1][0] = tau0

        initial_residuals, _, _, _ = self._evaluate(a0)
        y0 = np.zeros_like(initial_residuals)
        LevMar.Initialize(self, a0, y0)

    def _wrap_phase(self, tau):
        return float(tau) % self.ui

    def _residual_length(self):
        conv_len = self._goal_num_points + self.num_ffe_taps - 1
        symbol_count = 1 + (conv_len - 1 - self._cursor_index) // self.ideal_samples_per_ui
        return symbol_count + (1 if self.spectral_density is not None else 0)

    def _initialize_noise_residual(self):
        # Build a fixed grid from DC to baud Nyquist for spectral-density integration.
        f_nyquist = 0.5 * self.baud_rate
        grid_intervals = max(4, self._num_symbols)
        self._noise_frequency_grid = EvenlySpacedFrequencyList(f_nyquist, grid_intervals)
        sd_resampled = self.spectral_density.Resample(self._noise_frequency_grid)
        self._noise_frequencies = np.asarray(self._noise_frequency_grid.Frequencies(), dtype=float)
        rho = np.asarray(sd_resampled.Values('V/sqrt(Hz)'), dtype=float)
        self._noise_density_squared = np.square(rho)

    def _compute_noise_residual(self, ffe):
        if self._noise_frequencies is None or self._noise_density_squared is None:
            return 0.0
        tap_index = np.arange(len(ffe), dtype=float)
        phase = (-2j * np.pi / self.goal_sample_rate) * np.outer(self._noise_frequencies, tap_index)
        h_f = np.exp(phase).dot(ffe)
        integrand = np.square(np.abs(h_f)) * self._noise_density_squared
        noise_power = float(np.trapz(integrand, self._noise_frequencies))
        noise_rms = math.sqrt(max(noise_power, 0.0))
        return noise_rms / math.sqrt(max(self._num_symbols, 1))

    def _resample_with_phase(self, tau):
        tau = self._wrap_phase(tau)
        if tau in self._resampled_cache:
            return self._resampled_cache[tau]
        td = TimeDescriptor(
            HorOffset=self._base_h + tau,
            NumPts=self._goal_num_points,
            SampleRate=self.goal_sample_rate,
        )
        wf = self.input_waveform.Adapt(td)
        values = np.asarray(wf.Values(), dtype=float)
        self._resampled_cache[tau] = values
        return values

    def _slice_levels(self, values):
        values = np.asarray(values, dtype=float)
        distance = np.abs(values.reshape(-1, 1) - self.levels.reshape(1, -1))
        return self.levels[np.argmin(distance, axis=1)]

    def _evaluate(self, a, forced_decisions=None):
        ffe = np.asarray(a[: self.num_ffe_taps, 0], dtype=float)
        dfe = np.asarray(a[self.num_ffe_taps : self.num_ffe_taps + self.num_dfe_taps, 0], dtype=float)
        tau = self._wrap_phase(a[-1][0].real)

        resampled = self._resample_with_phase(tau)
        ffe_output = np.convolve(resampled, ffe, mode='full')
        symbol_stream = ffe_output[self._cursor_index :: self.ideal_samples_per_ui]
        if len(symbol_stream) >= self._num_symbols:
            symbol_stream = symbol_stream[: self._num_symbols]
        else:
            symbol_stream = np.pad(symbol_stream, (0, self._num_symbols - len(symbol_stream)), mode='constant')

        equalized = np.zeros(len(symbol_stream), dtype=float)
        decisions = np.zeros(len(symbol_stream), dtype=float)

        if forced_decisions is not None:
            forced = np.asarray(forced_decisions, dtype=float)
            if len(forced) != len(symbol_stream):
                raise SignalIntegrityExceptionFitter('forced decision length mismatch')

        for n in range(len(symbol_stream)):
            feedback = 0.0
            for k in range(self.num_dfe_taps):
                idx = n - k - 1
                if idx >= 0:
                    src = forced[idx] if forced_decisions is not None else decisions[idx]
                    feedback += dfe[k] * src
            eq = symbol_stream[n] - feedback
            equalized[n] = eq
            decisions[n] = forced[n] if forced_decisions is not None else self._slice_levels([eq])[0]

        residuals = equalized - decisions
        if self.spectral_density is not None:
            residuals = np.append(residuals, self._compute_noise_residual(ffe))
        return residuals.reshape(-1, 1), equalized, decisions, tau

    def _scan_initial_phase(self):
        best_tau = 0.0
        best_rms = float('inf')
        for phase_index in range(self.ideal_samples_per_ui):
            tau = phase_index / self.goal_sample_rate
            resampled = self._resample_with_phase(tau)
            symbols = resampled[0:: self.ideal_samples_per_ui]
            symbols = symbols[: self._num_symbols]
            if len(symbols) == 0:
                continue
            decisions = self._slice_levels(symbols)
            err = symbols - decisions
            rms = float(np.sqrt(np.mean(np.square(err))))
            if rms < best_rms:
                best_rms = rms
                best_tau = tau
        return best_tau

    def fF(self, a):
        residuals, _, _, _ = self._evaluate(a)
        return residuals

    def fPartialFPartiala(self, a, m, Fa=None):
        # Freeze hard decisions at the current point to keep finite-difference Jacobian stable.
        base_residuals, _, base_decisions, _ = self._evaluate(a)
        if Fa is None:
            Fa = base_residuals

        a_plus = copy.copy(a)
        a_plus[m][0] = a_plus[m][0] + self.m_epsilon
        perturbed_residuals, _, _, _ = self._evaluate(a_plus, forced_decisions=base_decisions)
        return (perturbed_residuals - Fa) / self.m_epsilon

    def AdjustVariablesAfterIteration(self, a):
        for row in range(len(a)):
            a[row][0] = float(a[row][0].real)
        a[-1][0] = self._wrap_phase(a[-1][0])
        return a

    def Results(self):
        a = self.m_a
        residuals, equalized, _, tau = self._evaluate(a)
        ffe = np.asarray(a[: self.num_ffe_taps, 0], dtype=float)
        dfe = np.asarray(a[self.num_ffe_taps : self.num_ffe_taps + self.num_dfe_taps, 0], dtype=float)

        td = TimeDescriptor(HorOffset=0.0, NumPts=len(equalized), SampleRate=self.baud_rate)
        equalized_wf = Waveform(td, equalized.tolist())
        return equalized_wf, ffe, dfe, tau, residuals

    def Solve(self):
        LevMar.Solve(self)
        equalized_wf, ffe, dfe, tau, _ = self.Results()
        return equalized_wf, ffe, dfe, tau
