"""
BenchmarkParallelCalculations.py
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

# Benchmark and correctness verification for parallel TransferMatrices.
#
# This script solves the same simulation twice - once forced to run serially and
# once in parallel - and:
#   1. verifies that the two results are identical (correctness), and
#   2. reports the wall-clock time and speedup (performance).
#
# Run directly, e.g.:
#     python BenchmarkParallelCalculations.py
#     python BenchmarkParallelCalculations.py --points 2000 --workers 8

import argparse
import time

import SignalIntegrity.Lib as si
import SignalIntegrity.Lib.Parsers.ParallelCalculations as ptm


def BuildNetlist(sections=1):
    """A two-port simulation netlist.
    @param sections int number of cascaded telegrapher sections.  Increasing
    this makes each per-frequency solve more expensive (a larger system to
    invert), which models heavier real-world channels and exposes the point at
    which parallel execution becomes worthwhile.
    """
    Td = 1.23e-9 / sections; Zc = 55; C = Td / Zc; L = Td * Zc
    Rse = 0.001; df = .001; R = .1
    lines = ['voltagesource Vs 1', 'voltagesource Vn 2', 'device Rt 2 R 65',
             'device Rr 1 R 60', 'connect Vs 1 Vn 1', 'connect Vn 2 Rt 1',
             'connect Rt 2 T0 1']
    for s in range(sections):
        lines.append('device T' + str(s) + ' 2 telegrapher r ' + str(R) +
                     ' rse ' + str(Rse) + ' l ' + str(L) + ' c ' + str(C) +
                     ' df ' + str(df))
        if s > 0:
            lines.append('connect T' + str(s - 1) + ' 2 T' + str(s) + ' 1')
    last = sections - 1
    lines += ['connect T' + str(last) + ' 2 Rr 1',
              'output T0 1', 'output T' + str(last) + ' 2']
    return lines


def BuildSystemSParametersNetlist(sections=1):
    """A two-port system s-parameter netlist (cascaded telegrapher sections).
    @param sections int number of cascaded telegrapher sections; higher makes
    each per-frequency solve more expensive.
    """
    Td = 1.23e-9 / sections; Zc = 55; C = Td / Zc; L = Td * Zc
    Rse = 0.001; df = .001; R = .1
    lines = []
    for s in range(sections):
        lines.append('device T' + str(s) + ' 2 telegrapher r ' + str(R) +
                     ' rse ' + str(Rse) + ' l ' + str(L) + ' c ' + str(C) +
                     ' df ' + str(df))
        if s > 0:
            lines.append('connect T' + str(s - 1) + ' 2 T' + str(s) + ' 1')
    last = sections - 1
    lines += ['port 1 T0 1', 'port 2 T' + str(last) + ' 2']
    return lines


def FrequencyList(points):
    """Builds an evenly spaced frequency list with the requested number of points."""
    Fs = 40e9; Ts = 1. / Fs
    return si.td.wf.TimeDescriptor(0, 2 * points, Fs).FrequencyList()


def Solve(netlist, f):
    """Solves the transfer matrices and returns the raw list of matrices."""
    parser = si.p.SimulatorNumericParser(f).AddLines(netlist)
    return parser.TransferMatrices()


def SolveSystemSParameters(netlist, f):
    """Solves the system s-parameters and returns the raw list of matrices."""
    parser = si.p.SystemSParametersNumericParser(f).AddLines(netlist)
    return parser.SParameters().m_d


def MaxDifference(tmA, tmB):
    """Largest absolute difference between two transfer-matrix results."""
    worst = 0.0
    for n in range(len(tmA)):
        mA = tmA[n]; mB = tmB[n]
        for r in range(len(mA)):
            for c in range(len(mA[0])):
                worst = max(worst, abs(mA[r][c] - mB[r][c]))
    return worst


def main():
    argParser = argparse.ArgumentParser(description=__doc__)
    argParser.add_argument('--points', type=int, default=1000,
                           help='number of frequency points')
    argParser.add_argument('--workers', type=int, default=None,
                           help='number of worker processes (default: auto)')
    argParser.add_argument('--sections', type=int, default=1,
                           help='cascaded telegrapher sections; higher makes '
                                'each per-frequency solve more expensive')
    argParser.add_argument('--kind', choices=['simulator', 'systemsparameters'],
                           default='simulator',
                           help='which per-frequency solve to benchmark')
    args = argParser.parse_args()

    if args.kind == 'systemsparameters':
        netlist = BuildSystemSParametersNetlist(args.sections)
        solve = SolveSystemSParameters
    else:
        netlist = BuildNetlist(args.sections)
        solve = Solve
    f = FrequencyList(args.points)
    print('kind: %s, frequencies: %d, sections: %d' %
          (args.kind, len(f), args.sections))

    # --- serial run (force single worker) ---------------------------------
    ptm.DefaultNumberOfWorkers = 1
    t0 = time.perf_counter()
    serial = solve(netlist, f)
    serialTime = time.perf_counter() - t0
    print('serial:   %8.3f s' % serialTime)

    # --- parallel run -----------------------------------------------------
    ptm.DefaultNumberOfWorkers = args.workers
    ptm.MinimumFrequenciesForParallel = 1
    t0 = time.perf_counter()
    parallel = solve(netlist, f)
    parallelTime = time.perf_counter() - t0
    print('parallel: %8.3f s' % parallelTime)

    # --- verify + report --------------------------------------------------
    diff = MaxDifference(serial, parallel)
    print('max abs difference: %g' % diff)
    if diff > 1e-12:
        print('FAIL: parallel result differs from serial result')
    else:
        print('PASS: results identical')
    if parallelTime > 0:
        print('speedup: %.2fx' % (serialTime / parallelTime))


if __name__ == '__main__':
    main()
