"""
Amplifier.py
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

import numpy as np


def dbm_to_vpeak(dbm, r=50.0):
    """
    Convert dBm into sinusoidal peak voltage.
    """
    p_watts = 10 ** ((dbm - 30.0) / 10.0)
    vrms = np.sqrt(p_watts * r)
    return np.sqrt(2.0) * vrms


def amplifier_iip2_iip3_slew(
    x,
    fs,
    gain_db,
    iip2_dbm,
    iip3_dbm,
    bandwidth_hz,
    slew_rate_v_per_s,
):
    """
    Behavioral amplifier model.

    Parameters
    ----------
    x : ndarray
        Input voltage samples.
    fs : float
        Sample rate (Hz).
    gain_db : float
        Small-signal gain (dB).
    iip2_dbm : float
        IIP2 (dBm, 50 ohm).
    iip3_dbm : float
        IIP3 (dBm, 50 ohm).
    bandwidth_hz : float
        Small-signal bandwidth (Hz).
    slew_rate_v_per_s : float
        Slew rate (V/s).

    Returns
    -------
    y : ndarray
        Output voltage samples.
    """

    x = np.asarray(x, dtype=float)

    # Voltage gain
    a1 = 10.0 ** (gain_db / 20.0)

    # Convert intercept points to peak-voltage equivalents
    viip2 = dbm_to_vpeak(iip2_dbm)
    viip3 = dbm_to_vpeak(iip3_dbm)

    # Polynomial coefficients. The third-order term is opposite in sign to the
    # linear term so the amplifier compresses (gain drops at large signals),
    # which is the physical behavior that IIP3 characterizes.
    a2 = a1 / viip2
    a3 = -(4.0 * a1) / (3.0 * viip3**2)

    # Input limits at the polynomial's extrema (roots of a1 + 2*a2*x + 3*a3*x^2).
    # Clamping the input here hard-clips the output at the polynomial peaks
    # instead of letting the cubic fold back beyond them.
    x_lo, x_hi = np.sort(np.roots([3.0 * a3, 2.0 * a2, a1]).real)

    Ts = 1.0 / fs
    # Stable one-pole coefficient (exact exponential/ZOH discretization).
    # Unconditionally stable for any bandwidth/sample-rate, unlike forward Euler.
    alpha = np.exp(-2.0 * np.pi * bandwidth_hz * Ts)
    # Maximum change per sample imposed by the slew-rate limit
    max_delta = slew_rate_v_per_s * Ts

    y = np.zeros_like(x)
    y_prev = 0.0

    for n in range(len(x)):
        # Nonlinear static stage
        xc = min(max(x[n], x_lo), x_hi)
        z = a1 * xc + a2 * xc**2 + a3 * xc**3

        # Desired output of the (stable) one-pole low-pass this step
        y_target = alpha * y_prev + (1.0 - alpha) * z

        # Slew-rate limit: cap the change per step (|dy/dt| <= slew_rate)
        delta = np.clip(
            y_target - y_prev,
            -max_delta,
            max_delta,
        )

        # Integrate
        y_prev = y_prev + delta
        y[n] = y_prev

    return y