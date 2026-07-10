"""
TestEqualizer.py
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

import unittest

import numpy as np
import SignalIntegrity.Lib as si
from SignalIntegrity.Lib.Equalization.Equalizer import BlindEqualizer
from SignalIntegrity.Lib.FrequencyDomain.FrequencyList import EvenlySpacedFrequencyList
from SignalIntegrity.Lib.FrequencyDomain.SpectralDensity import SpectralDensity
from SignalIntegrity.Lib.TimeDomain.Waveform.TimeDescriptor import TimeDescriptor
from SignalIntegrity.Lib.TimeDomain.Waveform.Waveform import Waveform


class TestEqualizerTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)

    @staticmethod
    def _build_waveform(levels, baud_rate, samples_per_ui, channel=None):
        values = np.repeat(np.asarray(levels, dtype=float), samples_per_ui)
        if channel is not None:
            values = np.convolve(values, np.asarray(channel, dtype=float), mode='same')
        td = TimeDescriptor(0.0, len(values), baud_rate * samples_per_ui)
        return Waveform(td, values.tolist())

    def testInputValidation(self):
        wf = self._build_waveform([-1.0, 1.0, -1.0, 1.0], 1.0e9, 4)

        with self.assertRaises(si.SignalIntegrityException):
            BlindEqualizer(None, 2, 1.0e9, 4, 3, 2, 1)
        with self.assertRaises(si.SignalIntegrityException):
            BlindEqualizer(wf, 1, 1.0e9, 4, 3, 2, 1)
        with self.assertRaises(si.SignalIntegrityException):
            BlindEqualizer(wf, 2, 0.0, 4, 3, 2, 1)
        with self.assertRaises(si.SignalIntegrityException):
            BlindEqualizer(wf, 2, 1.0e9, 4.5, 3, 2, 1)
        with self.assertRaises(si.SignalIntegrityException):
            BlindEqualizer(wf, 2, 1.0e9, 4, 0, 2, 1)
        with self.assertRaises(si.SignalIntegrityException):
            BlindEqualizer(wf, 2, 1.0e9, 4, 3, -1, 1)
        with self.assertRaises(si.SignalIntegrityException):
            BlindEqualizer(wf, 2, 1.0e9, 4, 3, 2, -1)
        with self.assertRaises(si.SignalIntegrityException):
            BlindEqualizer(wf, 2, 1.0e9, 4, 3, 2, 3)

    def testEvaluateAndJacobianPaths(self):
        symbols = [-1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0] * 8
        wf = self._build_waveform(symbols, 1.0e9, 8, channel=[0.1, 0.8, 0.1])

        eq = BlindEqualizer(
            waveform=wf,
            num_levels=2,
            baud_rate=1.0e9,
            ideal_samples_per_ui=8,
            num_ffe_taps=3,
            num_dfe_taps=2,
            num_precursor_taps=1,
        )

        residuals, equalized, decisions, tau = eq._evaluate(eq.m_a)
        self.assertEqual(residuals.shape[0], eq._num_symbols)
        self.assertEqual(residuals.shape[1], 1)
        self.assertEqual(len(equalized), eq._num_symbols)
        self.assertEqual(len(decisions), eq._num_symbols)
        self.assertTrue(all(d in (-1.0, 1.0) for d in decisions))

        cached_1 = eq._resample_with_phase(tau)
        cached_2 = eq._resample_with_phase(tau)
        self.assertIs(cached_1, cached_2)

        dfa = eq.fPartialFPartiala(eq.m_a, 0, residuals)
        self.assertEqual(dfa.shape, residuals.shape)

        with self.assertRaises(si.SignalIntegrityException):
            eq._evaluate(eq.m_a, forced_decisions=[0.0])

    def testSolveAndResults(self):
        symbols = [-1.0, 1.0, -1.0, 1.0] * 32
        wf = self._build_waveform(symbols, 1.0e9, 4)

        eq = BlindEqualizer(
            waveform=wf,
            num_levels=2,
            baud_rate=1.0e9,
            ideal_samples_per_ui=4,
            num_ffe_taps=1,
            num_dfe_taps=0,
            num_precursor_taps=0,
        )

        raw = np.array([[1.0], [-0.75 * eq.ui]], dtype=float)
        adjusted = eq.AdjustVariablesAfterIteration(raw)
        self.assertTrue(np.isfinite(adjusted[0][0]))
        self.assertTrue(np.isfinite(adjusted[1][0]))
        self.assertGreaterEqual(adjusted[-1][0], 0.0)
        self.assertLess(adjusted[-1][0], eq.ui)

        # Keep runtime bounded for unit testing.
        eq.ccm.Initialize(maxIterations=15, tolerance=1e-12, lambdaTimeConstant=3, mseTimeConstant=3)

        equalized_wf, ffe, dfe, tau = eq.Solve()
        self.assertIsInstance(equalized_wf, Waveform)
        self.assertAlmostEqual(equalized_wf.td.Fs, eq.goal_sample_rate)
        self.assertEqual(len(ffe), 1)
        self.assertEqual(len(dfe), 0)
        self.assertGreaterEqual(tau, 0.0)
        self.assertLess(tau, eq.ui)

        result_wf, result_ffe, result_dfe, result_tau, residuals = eq.Results()
        self.assertIsInstance(result_wf, Waveform)
        self.assertAlmostEqual(result_wf.td.Fs, eq.goal_sample_rate)
        self.assertEqual(len(result_ffe), 1)
        self.assertEqual(len(result_dfe), 0)
        self.assertEqual(residuals.shape[1], 1)
        self.assertGreaterEqual(result_tau, 0.0)
        self.assertLess(result_tau, eq.ui)

    def testCoverageBranches(self):
        symbols = [-1.0, 1.0, -1.0, 1.0] * 8
        wf = self._build_waveform(symbols, 1.0e9, 4)

        eq = BlindEqualizer(
            waveform=wf,
            num_levels=2,
            baud_rate=1.0e9,
            ideal_samples_per_ui=4,
            num_ffe_taps=2,
            num_dfe_taps=1,
            num_precursor_taps=0,
        )

        # Exercise helper used by sizing logic.
        self.assertGreater(eq._residual_length(), 0)

        # Exercise fPartialFPartiala path that computes Fa internally.
        dfa = eq.fPartialFPartiala(eq.m_a, 0)
        self.assertEqual(dfa.shape[1], 1)

        # Force the empty-symbol defensive branch inside the phase scan.
        saved_num_symbols = eq._num_symbols
        try:
            eq._num_symbols = 0
            tau = eq._scan_initial_phase()
        finally:
            eq._num_symbols = saved_num_symbols
        self.assertGreaterEqual(tau, 0.0)
        self.assertLess(tau, eq.ui)

    def testSpectralDensityNoiseResidual(self):
        symbols = [-1.0, 1.0, -1.0, 1.0] * 12
        wf = self._build_waveform(symbols, 1.0e9, 4, channel=[0.15, 0.7, 0.15])

        # Use a coarse source grid so the equalizer path must resample to its own Nyquist grid.
        src_fd = EvenlySpacedFrequencyList(2.0e9, 8)
        sd = SpectralDensity.WhiteNoise(src_fd, 'V/sqrt(Hz)', 1e-9)

        eq = BlindEqualizer(
            waveform=wf,
            num_levels=2,
            baud_rate=1.0e9,
            ideal_samples_per_ui=4,
            num_ffe_taps=3,
            num_dfe_taps=1,
            num_precursor_taps=1,
            spectral_density=sd,
        )

        self.assertIsNotNone(eq._noise_frequency_grid)
        self.assertIsNotNone(eq._noise_frequencies)
        self.assertIsNotNone(eq._noise_density_squared)

        residuals, _, _, _ = eq._evaluate(eq.m_a)
        self.assertEqual(residuals.shape[0], eq._num_symbols + 1)
        self.assertEqual(residuals.shape[1], 1)
        self.assertGreaterEqual(float(residuals[-1][0]), 0.0)

    def testNoiseResidualGuardWithoutSpectralDensity(self):
        symbols = [-1.0, 1.0, -1.0, 1.0] * 6
        wf = self._build_waveform(symbols, 1.0e9, 4)

        eq = BlindEqualizer(
            waveform=wf,
            num_levels=2,
            baud_rate=1.0e9,
            ideal_samples_per_ui=4,
            num_ffe_taps=2,
            num_dfe_taps=0,
            num_precursor_taps=0,
        )

        self.assertEqual(eq._compute_noise_residual(np.array([1.0, 0.0])), 0.0)


if __name__ == '__main__':
    unittest.main()
