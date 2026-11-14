"""
conftest.py

Makes the suite safe to run in parallel with pytest-xdist (pytest -n auto --dist loadscope).
Has no effect on serial runs.
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
import os
import shutil
import tempfile

_workerId = os.environ.get('PYTEST_XDIST_WORKER')
_workerDir = None

if _workerId is not None:
    # Each xdist worker is a full process, so keep numpy/BLAS and SignalIntegrity's own process
    # pool single-threaded to avoid oversubscribing the CPU. Must run before numpy is imported.
    for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                  'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'SIGNALINTEGRITY_NUM_WORKERS'):
        os.environ.setdefault(_name, '1')

    # Many tests change preferences and call Preferences.SaveToFile(), which rewrites the shared
    # per-user preferences file that every other worker reads. Give each worker a private copy.
    from SignalIntegrity.App.Preferences import Preferences
    _sharedPreferences = Preferences.ResolveFileName()
    _workerDir = tempfile.mkdtemp(prefix='si_pytest_' + _workerId + '_')
    _workerPreferences = os.path.join(_workerDir, 'preferences.xml')
    if os.path.isfile(_sharedPreferences):
        shutil.copy2(_sharedPreferences, _workerPreferences)
    os.environ[Preferences.envVar] = _workerPreferences

def pytest_configure(config):
    config.addinivalue_line('markers', 'gui: Tk GUI test from the TestGui package')

def pytest_collection_modifyitems(config, items):
    # TestAll.py re-exports the TestGui classes, so mark them by their defining module. CI runs
    # them serially (-m gui -p no:xdist); Tk start-up fails intermittently in xdist workers on Windows.
    for item in items:
        cls = getattr(item, 'cls', None)
        if cls is not None and cls.__module__.split('.')[0] == 'TestGui':
            item.add_marker('gui')

def pytest_unconfigure(config):
    if _workerDir is not None:
        shutil.rmtree(_workerDir, ignore_errors=True)
