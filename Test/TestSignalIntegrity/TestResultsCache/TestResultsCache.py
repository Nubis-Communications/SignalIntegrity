"""
TestResultsCache.py
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
import os
import pickle
import shutil
import tempfile

from SignalIntegrity.Lib.ResultsCache import ResultsCache

class _CacheProbe(ResultsCache):
    """minimal ResultsCache used to exercise the cache versioning behavior"""
    check_times = False
    keep_extra_file_for_archive = False
    def __init__(self, filename):
        ResultsCache.__init__(self, 'Probe', filename)
    def HashValue(self, stuffToHash=''):
        return ResultsCache.HashValue(self, 'probe')

class TestResultsCache(unittest.TestCase):
    def setUp(self):
        self.tempDir = tempfile.mkdtemp()
        self.base = os.path.join(self.tempDir, 'proj')
    def tearDown(self):
        shutil.rmtree(self.tempDir, ignore_errors=True)
    def testCurrentCacheRoundTrips(self):
        """A cache written and read by the current code must round-trip."""
        writer = _CacheProbe(self.base)
        self.assertFalse(writer.CheckCache(), 'no cache should exist yet')
        writer.payload = [1, 2, 3]
        writer.CacheResult(['payload'])
        reader = _CacheProbe(self.base)
        self.assertTrue(reader.CheckCache(), 'current cache should load')
        self.assertEqual(reader.payload, [1, 2, 3])
    def testUnstampedOldCacheIgnored(self):
        """An old cache file with no version stamp must be ignored, not loaded."""
        writer = _CacheProbe(self.base)
        self.assertFalse(writer.CheckCache())
        writer.payload = [1, 2, 3]
        writer.CacheResult(['payload'])
        fileName = writer._FileName()
        # re-write the file in the legacy format: hash then dict, with no
        # leading version stamp.
        with open(fileName, 'rb') as f:
            pickle.load(f)                     # discard the version stamp
            legacyHash = pickle.load(f)
            legacyDict = pickle.load(f)
        with open(fileName, 'wb') as f:
            pickle.dump(legacyHash, f, 2)
            pickle.dump(legacyDict, f, 2)
        reader = _CacheProbe(self.base)
        self.assertFalse(reader.CheckCache(),
                         'an unstamped legacy cache must be treated as a miss')
    def testWrongVersionCacheIgnored(self):
        """A cache file stamped with a different version must be ignored."""
        writer = _CacheProbe(self.base)
        self.assertFalse(writer.CheckCache())
        writer.payload = [1, 2, 3]
        writer.CacheResult(['payload'])
        fileName = writer._FileName()
        with open(fileName, 'rb') as f:
            pickle.load(f)
            goodHash = pickle.load(f)
            goodDict = pickle.load(f)
        with open(fileName, 'wb') as f:
            pickle.dump(ResultsCache.cacheStructureVersion + 1000, f, 2)
            pickle.dump(goodHash, f, 2)
            pickle.dump(goodDict, f, 2)
        reader = _CacheProbe(self.base)
        self.assertFalse(reader.CheckCache(),
                         'a cache with a mismatched version must be treated as a miss')

if __name__ == '__main__':
    unittest.main()
