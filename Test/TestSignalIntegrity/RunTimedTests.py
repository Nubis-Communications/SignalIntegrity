"""
RunTimedTests.py

Run the SignalIntegrity unit tests while timing each one, recording the results to a
CSV file, and optionally running only the subset of tests that previously ran faster
than a given time threshold.

Examples:
    # Run every test, timing each, and (over)write the timings CSV:
    python RunTimedTests.py --record

    # Run only tests whose last recorded time was under 1.5 seconds:
    python RunTimedTests.py --faster-than 1.5

    # Same, but refresh the CSV timings for the tests that actually ran:
    python RunTimedTests.py --faster-than 1.5 --update

    # Print the 20 slowest recorded tests and exit:
    python RunTimedTests.py --list-slowest 20
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
import argparse
import csv
import datetime
import os
import sys
import time
import unittest

# Importing TestAll pulls in every test module (via its 'from TestX import *' lines)
# without running unittest.main(), which only fires under TestAll's __main__ guard.
import TestAll

# The timings CSV lives next to the tests regardless of the current working directory
# (individual tests os.chdir into their own directory during setUp).
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CSV = os.path.join(THIS_DIR, 'test_timings.csv')

CSV_FIELDS = ['test_id', 'duration_seconds', 'outcome', 'timestamp']


def TestKey(test):
    """Stable, unique key for a test case.

    The test classes override id() to return a shortened method name for reference
    filenames, so it is not unique across classes; build the key from the real
    module, class and method names instead.
    """
    cls = type(test)
    return '%s.%s.%s' % (cls.__module__, cls.__qualname__, test._testMethodName)


class TimingTestResult(unittest.TextTestResult):
    """A TextTestResult that records the wall-clock duration and outcome of each test."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timings = {}
        self._outcomes = {}
        self._start = None

    def startTest(self, test):
        self._start = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test):
        elapsed = time.perf_counter() - self._start
        super().stopTest(test)
        key = TestKey(test)
        self.timings[key] = elapsed
        # Default to 'pass'; the add* hooks below overwrite this for the current test.
        self._outcomes.setdefault(key, 'pass')

    def addSuccess(self, test):
        super().addSuccess(test)
        self._outcomes[TestKey(test)] = 'pass'

    def addError(self, test, err):
        super().addError(test, err)
        self._outcomes[TestKey(test)] = 'error'

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._outcomes[TestKey(test)] = 'fail'

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._outcomes[TestKey(test)] = 'skip'

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._outcomes[TestKey(test)] = 'expected_failure'

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._outcomes[TestKey(test)] = 'unexpected_success'


def IterateTests(suite):
    """Yield the individual test cases contained in a (possibly nested) suite."""
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from IterateTests(item)
        else:
            yield item


def LoadAllTests():
    return unittest.defaultTestLoader.loadTestsFromModule(TestAll)


def LoadRecordedTimes(csvPath):
    """Return {test_id: duration_seconds} from the CSV, or {} if it does not exist."""
    times = {}
    if not os.path.exists(csvPath):
        return times
    with open(csvPath, 'r', newline='') as f:
        for row in csv.DictReader(f):
            try:
                times[row['test_id']] = float(row['duration_seconds'])
            except (KeyError, ValueError):
                continue
    return times


def WriteRecordedTimes(csvPath, times, outcomes):
    timestamp = datetime.datetime.now().isoformat(timespec='seconds')
    with open(csvPath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for key in sorted(times):
            writer.writerow({
                'test_id': key,
                'duration_seconds': '%.6f' % times[key],
                'outcome': outcomes.get(key, ''),
                'timestamp': timestamp,
            })


def MergeTimes(csvPath, newTimes, newOutcomes):
    """Update only the entries that were just measured, preserving all others."""
    merged = LoadRecordedTimes(csvPath)
    mergedOutcomes = {}
    if os.path.exists(csvPath):
        with open(csvPath, 'r', newline='') as f:
            for row in csv.DictReader(f):
                mergedOutcomes[row['test_id']] = row.get('outcome', '')
    merged.update(newTimes)
    mergedOutcomes.update(newOutcomes)
    WriteRecordedTimes(csvPath, merged, mergedOutcomes)


def BuildFilteredSuite(fullSuite, recordedTimes, threshold):
    """Include a test if its recorded time is < threshold, or if it has no record."""
    suite = unittest.TestSuite()
    included = skipped = new = 0
    for test in IterateTests(fullSuite):
        key = TestKey(test)
        if key not in recordedTimes:
            suite.addTest(test)
            included += 1
            new += 1
        elif recordedTimes[key] < threshold:
            suite.addTest(test)
            included += 1
        else:
            skipped += 1
    return suite, included, skipped, new


def ListSlowest(csvPath, count):
    times = LoadRecordedTimes(csvPath)
    if not times:
        print('No recorded timings found at %s' % csvPath)
        return
    for key, duration in sorted(times.items(), key=lambda kv: kv[1], reverse=True)[:count]:
        print('%9.3f s  %s' % (duration, key))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--record', action='store_true',
                       help='Run every test, timing each, and (over)write the timings CSV.')
    group.add_argument('--faster-than', type=float, metavar='SECONDS', dest='faster_than',
                       help='Run only tests whose last recorded time was under SECONDS. '
                            'Tests with no recorded time are always included.')
    group.add_argument('--list-slowest', type=int, metavar='N', dest='list_slowest',
                       help='Print the N slowest recorded tests and exit.')
    parser.add_argument('--update', action='store_true',
                        help='With --faster-than, refresh the CSV timings for the tests that ran.')
    parser.add_argument('--csv', default=DEFAULT_CSV,
                        help='Path to the timings CSV (default: %(default)s).')
    parser.add_argument('-v', '--verbosity', type=int, default=2,
                        help='unittest verbosity (default: 2).')
    args = parser.parse_args(argv)

    if args.list_slowest is not None:
        ListSlowest(args.csv, args.list_slowest)
        return 0

    fullSuite = LoadAllTests()

    if args.faster_than is not None:
        recordedTimes = LoadRecordedTimes(args.csv)
        suite, included, skipped, new = BuildFilteredSuite(fullSuite, recordedTimes,
                                                           args.faster_than)
        print('Filter < %g s: running %d tests, skipping %d (of which %d are new/unrecorded '
              'and were included).' % (args.faster_than, included, skipped, new))
    else:
        # Default behaviour (with or without an explicit --record) is a full timed run.
        suite = fullSuite
        included = sum(1 for _ in IterateTests(fullSuite))
        print('Running all %d tests (timed).' % included)

    runner = unittest.TextTestRunner(verbosity=args.verbosity, resultclass=TimingTestResult)
    result = runner.run(suite)

    recordFull = args.faster_than is None
    if recordFull:
        WriteRecordedTimes(args.csv, result.timings, result._outcomes)
        print('Wrote %d timings to %s' % (len(result.timings), args.csv))
    elif args.update:
        MergeTimes(args.csv, result.timings, result._outcomes)
        print('Updated %d timings in %s' % (len(result.timings), args.csv))

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
