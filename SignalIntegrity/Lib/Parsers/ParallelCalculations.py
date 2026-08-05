"""
ParallelCalculations.py
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

# Parallel computation of per-frequency solutions.
#
# The transfer-matrix solutions performed by SimulatorNumericParser and
# VirtualProbeNumericParser, and the system s-parameter solution performed by
# SystemSParametersNumericParser, loop over every frequency and solve an
# independent problem at each one.  Because the per-frequency solves are
# independent, they can be distributed across multiple processor cores.  This
# module provides that machinery in a form that is safe on Windows (which uses
# the 'spawn' start method and therefore requires module-level, picklable worker
# callables).
#
# The worker interface is *batch ready*: a worker receives a chunk (list) of
# frequency payloads so that frequency batching can be tuned later simply by
# changing the chunk size, with no change to the worker signature.  With the
# default chunk size of 1 the behavior matches a straightforward
# one-task-per-frequency mapping.

import os
import copy
import time

#: Number of worker processes to use *when parallel execution has been allowed*.
#:
#: Parallel per-frequency execution is **gated** by the ``allowParallel``
#: argument to :func:`Solve` (which itself originates from the
#: ``AllowParallelization`` calculation property, defaulting to False).  This
#: attribute does NOT turn parallelism on; it only chooses how many workers are
#: used once it is allowed.  The gate is separate because, for the vast majority
#: of real problems, the per-frequency solve is cheap relative to the cost of
#: standing up a process pool and shipping the problem (deepcopy + pickle of the
#: system description and every per-frequency matrix) to the workers.  In those
#: cases the process/IPC overhead dominates and the "parallel" path is actually
#: slower than serial -- sometimes by 2x or more.  Measured example: a
#: 1000-point TDR calibration that solves in 110s serially takes 219s when
#: forced parallel, because the tiny solves are swamped by the repeated pool
#: startup and data transfer.  Even when parallel is allowed, the cost model
#: below still decides per-solve whether it actually pays off.
#:
#: Values: ``None`` means "choose automatically" from os.cpu_count(); an int > 1
#: uses that many workers; 1 (or anything <= 1) forces serial even when allowed.
#: The environment variable SIGNALINTEGRITY_NUM_WORKERS overrides this at run
#: time (an integer count, or 0/"auto" for os.cpu_count()).
DefaultNumberOfWorkers = None

#: Environment variable that overrides DefaultNumberOfWorkers at run time so
#: parallelism can be enabled without editing code.  Accepts an integer worker
#: count, or "auto"/"0" for os.cpu_count().  Unset means "use
#: DefaultNumberOfWorkers".
NumberOfWorkersEnvVar = 'SIGNALINTEGRITY_NUM_WORKERS'

#: Minimum number of frequencies before parallel execution is attempted.  Below
#: this the process startup / data transfer overhead is not worth it and the
#: serial path is used.
MinimumFrequenciesForParallel = 8

#: Estimated serial solve time (in seconds) below which parallel execution is
#: never attempted.  The per-frequency solve is timed once and extrapolated; if
#: the whole calculation is predicted to take less than this, the process
#: startup / pickling overhead would dominate and the serial path is used
#: instead.  This is only a coarse floor; the finer decision is made by the
#: cost model below (see EstimatedPoolStartupSeconds).
MinimumEstimatedSerialSeconds = 2.0

#: Estimated fixed cost (in seconds) of standing up a worker process pool.  On
#: Windows (the 'spawn' start method) each worker is a fresh interpreter that
#: re-imports SignalIntegrity and unpickles the base problem, which measures at
#: roughly 2 seconds for a pool of several workers.  Parallel execution only
#: pays off when the time it *saves* clearly exceeds this fixed cost, so the
#: driver compares the two before spawning anything.  This guards against the
#: pathological case of many moderate solves (for example a calibration run)
#: each spinning up and tearing down a pool whose startup dwarfs the tiny gain.
EstimatedPoolStartupSeconds = 2.0

#: Safety factor applied to the predicted parallel savings.  The estimated time
#: saved by going parallel must exceed EstimatedPoolStartupSeconds by at least
#: this factor before a pool is created.  A value > 1 keeps borderline problems
#: serial, where the estimate is least reliable and a wrong guess is most costly.
ParallelStartupSafetyFactor = 2.0

#: Number of frequencies handled per worker task.  1 reproduces
#: one-task-per-frequency behavior.  Larger values amortize process startup,
#: pickling and per-solver setup costs.  A value of ``None`` means "choose
#: automatically" based on the number of frequencies and workers.
DefaultChunkSize = None

#: Environment variables that control the number of threads used by the various
#: BLAS / linear-algebra back-ends that numpy may sit on top of.  Each worker
#: process performs its own linear-algebra solves, and those back-ends *already*
#: try to use every core.  If that is left unchecked then N worker processes
#: each spawn N BLAS threads, oversubscribing the machine by a factor of N and
#: making the parallel run dramatically slower than the serial one.  To get a
#: real speedup, each worker is restricted to a single BLAS thread so that the
#: parallelism comes purely from the process pool.
_ThreadLimitEnvVars = (
    'OMP_NUM_THREADS',
    'OPENBLAS_NUM_THREADS',
    'MKL_NUM_THREADS',
    'NUMEXPR_NUM_THREADS',
    'VECLIB_MAXIMUM_THREADS',
)

#: Number of BLAS threads each worker process is allowed to use.  1 avoids
#: oversubscription (see _ThreadLimitEnvVars).  Increase only if you deliberately
#: run fewer worker processes than cores and want each to use the remainder.
ThreadsPerWorker = 1

class _WorkerThreadLimit(object):
    """Context manager that restricts the BLAS thread count seen by worker
    processes spawned while it is active.

    Worker processes created with the (default on Windows) 'spawn' start method
    inherit a *copy* of the parent's environment and import numpy fresh, reading
    these variables when their BLAS back-end initializes.  Setting the variables
    here therefore limits the children without disturbing the parent's own,
    already-initialized numpy.  The parent's environment is restored on exit.
    """
    def __init__(self, threadsPerWorker):
        self._value = str(max(1, int(threadsPerWorker)))
        self._saved = {}
    def __enter__(self):
        for name in _ThreadLimitEnvVars:
            self._saved[name] = os.environ.get(name)
            os.environ[name] = self._value
        return self
    def __exit__(self, *excInfo):
        for name, previous in self._saved.items():
            if previous is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = previous
        return False

class _SuppressMainReimport(object):
    """Context manager that stops spawned worker processes from re-importing the
    parent's ``__main__`` module.

    With the 'spawn' start method (the default on Windows) every worker is a
    brand-new interpreter that, as part of its bootstrap, re-imports the parent's
    ``__main__`` module (see ``multiprocessing.spawn.get_preparation_data``).  The
    workers created here need *nothing* from ``__main__``: the worker callable
    (:func:`_SolveChunk`) and every payload object (the system description, the
    per-frequency matrices, numpy arrays) live in ordinary importable
    SignalIntegrity/library modules.  So that re-import is pure overhead -- and,
    critically, its cost is unbounded and depends entirely on *what launched the
    process*:

    * Run a single ``.si`` file or one test module directly and ``__main__`` is
      tiny, so each worker starts almost instantly.
    * Run the same solve as part of a larger driver -- a test runner performing
      unittest discovery, PyDev/Eclipse, pytest, or a top-level script that does
      ``from Test... import *`` for a whole suite -- and ``__main__`` is *that*
      driver.  Re-importing it in a worker drags in the entire suite's imports
      (dozens of test modules, the matplotlib GUI backend, ...) before the worker
      can do any work.  That happens for *every* worker, in *every* pool, for
      *every* solve, which is exactly the pathological slowdown observed when
      these parallel solves run inside a big test run instead of on their own.

    ``multiprocessing`` decides how to reconstruct ``__main__`` in the child from
    two attributes of the parent's ``__main__`` module: ``__spec__`` (import it by
    module name) and ``__file__`` (execute it by path).  Clearing both for the
    duration of pool creation makes the preparation data carry no main-init
    directive at all, so the workers skip the re-import completely.  The parent's
    own ``__main__`` is restored on exit, so this is invisible to the caller.
    """
    _SENTINEL = object()
    def __init__(self):
        self._main = None
        self._savedSpec = self._SENTINEL
        self._savedFile = self._SENTINEL
    def __enter__(self):
        import sys
        self._main = sys.modules.get('__main__')
        if self._main is not None:
            self._savedSpec = getattr(self._main, '__spec__', self._SENTINEL)
            self._savedFile = getattr(self._main, '__file__', self._SENTINEL)
            # __spec__ = None suppresses the "import by module name" path;
            # removing __file__ suppresses the "execute by path" path.  With both
            # gone, get_preparation_data emits no main-init directive.
            try:
                self._main.__spec__ = None
            except Exception:
                pass
            if self._savedFile is not self._SENTINEL:
                try:
                    del self._main.__file__
                except Exception:
                    pass
        return self
    def __exit__(self, *excInfo):
        if self._main is not None:
            if self._savedSpec is not self._SENTINEL:
                try:
                    self._main.__spec__ = self._savedSpec
                except Exception:
                    pass
            if self._savedFile is not self._SENTINEL:
                try:
                    self._main.__file__ = self._savedFile
                except Exception:
                    pass
        return False

# ---------------------------------------------------------------------------
# Worker side (runs in the child processes)
# ---------------------------------------------------------------------------

#: Per-process worker state, cached across tasks and reused between solves.
#:
#: Because the process pool is now *persistent* (created once and reused for
#: every per-frequency solve -- see _GetPersistentExecutor), a worker cannot be
#: handed the base problem once via a pool ``initializer``: successive solves use
#: different system descriptions.  Instead every task carries the base problem
#: tagged with a monotonically increasing ``generation`` id.  A worker rebuilds
#: its solver only when it first sees a new generation, so within one solve the
#: (structurally cached) solver is still built once per worker and reused for all
#: of that solve's frequencies -- exactly as before -- but the expensive process
#: spawn and interpreter/import startup is paid only once for the whole run.
_WorkerState = {}

def _SolveChunk(payload):
    """Solves the per-frequency result for a chunk of frequencies.
    @param payload tuple ``(generation, kind, sd, names, Z0, solvetype, chunk)``
    where ``chunk`` is a list of ``(n, matrices, system)`` tuples (n is the
    frequency index, matrices is a list of per-device s-parameter matrices
    aligned with names, and system is the per-frequency system s-parameter matrix
    used by the 'deembedder' kind -- None for the other kinds) and the remaining
    fields describe the base problem for this solve.
    @return list of (n, result) tuples.
    @remark The base problem (kind, sd, names, Z0, solvetype) is identical for
    every chunk of a given solve, so it is cached per worker keyed on the
    generation id and the solver is rebuilt only when the generation changes.
    This keeps the per-frequency work identical to the original one-solver-per-
    worker behavior while allowing the pool itself to be reused across solves.
    """
    (generation, kind, sd, names, Z0, solvetype, chunk) = payload
    if _WorkerState.get('generation') != generation:
        _WorkerState['generation'] = generation
        _WorkerState['kind'] = kind
        _WorkerState['sd'] = sd
        _WorkerState['names'] = names
        _WorkerState['Z0'] = Z0
        _WorkerState['solvetype'] = solvetype
        # The solver (when applicable) shares the same Device objects that
        # AssignSParameters mutates, and its structural caches are valid across
        # all frequencies of this solve, so a single solver is reused for every
        # frequency until the next solve (a new generation) arrives.
        _WorkerState['solver'] = _MakeSolver(kind, sd)
    sd = _WorkerState['sd']
    names = _WorkerState['names']
    Z0 = _WorkerState['Z0']
    kind = _WorkerState['kind']
    solver = _WorkerState['solver']
    solvetype = _WorkerState['solvetype']
    results = []
    for (n, matrices, system) in chunk:
        results.append((n, _SolveOneFrequency(kind, sd, names, matrices, Z0,
                                              solver, solvetype, system)))
    return results

def _WarmUpWorker(_ignored):
    """Trivial task submitted only to force a worker process to be spawned and to
    finish importing this module.  Returns the worker pid for debugging."""
    return os.getpid()

def _InitializeWorker(loggingConfiguration=None):
    """Pool initializer, run once inside each worker process as it starts.

    Moves the worker out of whatever directory it inherited from the parent at
    spawn time.  Workers perform no file I/O of their own -- every input arrives
    pickled in the task payload (see _SolveChunk) -- but a process's current
    working directory is an open handle on that directory, and on Windows an open
    handle prevents the directory from being renamed, moved or deleted.  Because
    the pool is persistent, a worker spawned while the parent happened to be
    inside a project directory would otherwise keep that directory locked for the
    rest of the run: deleting it (for example un-extracting a project archive, or
    simply cleaning up a working directory) would fail with
    'the process cannot access the file because it is being used by another
    process'.  Chdir'ing to the temp directory releases that hold.

    @param loggingConfiguration dict (optional) the logging configuration for this
    worker, produced by LogConfiguration.WorkerConfiguration() in the parent.
    @remark the logging configuration must be passed in explicitly because workers
    are spawned (not forked) on Windows and therefore inherit nothing from the
    parent process.  Doing this makes worker logging behave the same on Windows
    and on Linux.
    """
    import tempfile
    try:
        os.chdir(tempfile.gettempdir())
    except Exception:
        # A worker that cannot chdir is still perfectly able to do its work, so
        # this must never be allowed to break the pool.
        pass
    try:
        from SignalIntegrity.Lib.Log import LogConfiguration
        LogConfiguration.ConfigureWorker(loggingConfiguration)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Driver side (runs in the main process)
# ---------------------------------------------------------------------------

class _Aborted(Exception):
    """Internal sentinel used to signal a callback-requested abort so that it
    can be distinguished from genuine multiprocessing failures."""
    pass

#: The persistent, process-wide worker pool and the number of workers it was
#: created with.  The pool is created lazily on the first parallel solve and then
#: reused for every subsequent solve, so the ~2 second cost of spawning worker
#: interpreters and importing numpy/SignalIntegrity into each is paid *once* for
#: the whole run instead of once per solve.  This is the dominant cost when many
#: independent solves run back to back (for example a calibration sweep or a test
#: suite that solves dozens of small schematics); rebuilding a fresh pool for
#: each of those solves made "parallel" execution slower than serial even though
#: the individual solves genuinely parallelize.
_PersistentExecutor = None
_PersistentExecutorWorkers = None

#: Monotonic id identifying the current solve's base problem to the workers.
#: Incremented for every parallel solve; a worker rebuilds its cached solver when
#: it sees a generation it has not seen before (see _SolveChunk).
_SolveGeneration = 0

def _GetPersistentExecutor(workers, mainGuard):
    """Returns a process pool with ``workers`` workers, creating (and warming) it
    on first use and reusing it thereafter.
    @param workers int number of worker processes required.
    @param mainGuard context manager active while any *new* workers are spawned
    (restricts BLAS threads and suppresses the __main__ re-import in children).
    @return a ProcessPoolExecutor, or None if one could not be created.
    @remark If a pool with a different worker count already exists it is shut
    down and replaced.  New workers are spawned eagerly (warmed up) while
    ``mainGuard`` is active so the spawn-time environment (thread limits, no
    __main__ re-import) is guaranteed to apply to them.
    """
    global _PersistentExecutor, _PersistentExecutorWorkers
    from concurrent.futures import ProcessPoolExecutor
    if (_PersistentExecutor is not None and
            _PersistentExecutorWorkers != workers):
        try:
            _PersistentExecutor.shutdown(wait=True)
        except Exception:
            pass
        _PersistentExecutor = None
        _PersistentExecutorWorkers = None
    created = False
    if _PersistentExecutor is None:
        try:
            from SignalIntegrity.Lib.Log import LogConfiguration
            loggingConfiguration=LogConfiguration.WorkerConfiguration()
        except Exception:
            loggingConfiguration=None
        try:
            _PersistentExecutor = ProcessPoolExecutor(max_workers=workers,
                                                      initializer=_InitializeWorker,
                                                      initargs=(loggingConfiguration,))
        except TypeError:
            # ProcessPoolExecutor gained the 'initializer' argument in Python 3.7.
            # Without it the workers simply keep the cwd they were spawned in.
            _PersistentExecutor = ProcessPoolExecutor(max_workers=workers)
        _PersistentExecutorWorkers = workers
        created = True
    if created:
        # Force every worker to spawn now, while mainGuard is active, so the
        # child interpreters inherit the restricted BLAS thread count and skip
        # re-importing __main__.  Without this warm-up the workers would instead
        # spawn lazily during the first real submit loop -- outside the guard and
        # timed as part of that solve.
        with mainGuard:
            try:
                list(_PersistentExecutor.map(_WarmUpWorker, range(workers)))
            except Exception:
                pass
    return _PersistentExecutor

def ShutdownPersistentExecutor():
    """Shuts down the persistent worker pool, if any.  Safe to call at any time;
    a later parallel solve simply creates a fresh pool.  Provided mainly for
    tests and for callers that want to release the worker processes explicitly.
    """
    global _PersistentExecutor, _PersistentExecutorWorkers
    if _PersistentExecutor is not None:
        try:
            _PersistentExecutor.shutdown(wait=True)
        except Exception:
            pass
        _PersistentExecutor = None
        _PersistentExecutorWorkers = None

def _ResolveNumberOfWorkers(numWorkers, numFrequencies):
    """Determines the effective number of worker processes to use.

    Resolution order:
      1. an explicit ``numWorkers`` argument (from the caller),
      2. the ``SIGNALINTEGRITY_NUM_WORKERS`` environment variable,
      3. the module attribute ``DefaultNumberOfWorkers`` (serial by default).
    ``None`` at any level means "choose automatically" from os.cpu_count().  A
    resolved value <= 1 forces serial execution.
    """
    if numWorkers is None:
        numWorkers = _WorkersFromEnv()
    if numWorkers is None:
        numWorkers = DefaultNumberOfWorkers
    if numWorkers is None:
        numWorkers = os.cpu_count() or 1
    return max(1, min(numWorkers, numFrequencies))

def _WorkersFromEnv():
    """Reads the worker count from the environment, or returns None if unset.
    Accepts an integer, or "auto"/"0"/"" for automatic (os.cpu_count())."""
    raw = os.environ.get(NumberOfWorkersEnvVar)
    if raw is None:
        return None
    raw = raw.strip().lower()
    if raw in ('', 'auto', '0'):
        return os.cpu_count() or 1
    try:
        return int(raw)
    except ValueError:
        return None

def _ResolveChunkSize(chunkSize, numFrequencies, numWorkers):
    """Determines the effective chunk size."""
    if chunkSize is None:
        chunkSize = DefaultChunkSize
    if chunkSize is None:
        # Aim for several chunks per worker for reasonable load balancing while
        # still amortizing per-task overhead.
        chunkSize = max(1, numFrequencies // (numWorkers * 4))
    return max(1, chunkSize)

def _BuildChunks(spc, numFrequencies, chunkSize, startIndex=0, systemMatrices=None):
    """Builds the list of per-frequency payload chunks.
    @param startIndex (optional) first frequency index to include (frequencies
    before it, for example a timing probe, are skipped).
    @param systemMatrices (optional) list of per-frequency system s-parameter
    matrices used by the 'deembedder' kind; None (the default) supplies None as
    the per-frequency system for every frequency.
    @return list of chunks, each a list of (n, [spc[d][1][n] for d], system_n)
    tuples.
    """
    numDevices = len(spc)
    chunks = []
    n = startIndex
    while n < numFrequencies:
        chunk = []
        for nn in range(n, min(n + chunkSize, numFrequencies)):
            matrices = [spc[d][1][nn] for d in range(numDevices)]
            system = systemMatrices[nn] if systemMatrices is not None else None
            chunk.append((nn, matrices, system))
        chunks.append(chunk)
        n += chunkSize
    return chunks

def _MakeSolver(kind, sd):
    """Creates the reusable per-process solver for kinds that support reuse."""
    if kind == 'simulator':
        from SignalIntegrity.Lib.SystemDescriptions import SimulatorNumeric
        return SimulatorNumeric(sd)
    if kind == 'systemsparameters':
        from SignalIntegrity.Lib.SystemDescriptions import SystemSParametersNumeric
        return SystemSParametersNumeric(sd)
    if kind == 'deembedder':
        from SignalIntegrity.Lib.SystemDescriptions.DeembedderNumeric import DeembedderNumeric
        return DeembedderNumeric(sd)
    return None

def _SolveOneFrequency(kind, sd, names, matrices, Z0, solver, solvetype=None,
                       system=None):
    """Assigns the per-device s-parameters for one frequency and solves it.
    @param system (optional) the per-frequency system s-parameter matrix used by
    the 'deembedder' kind (the s-parameters of the known overall system).
    """
    for d in range(len(names)):
        if names[d] is not None:
            sd.AssignSParameters(names[d], matrices[d])
    if kind == 'simulator':
        return solver.TransferMatrix(Z0=Z0)
    if kind == 'systemsparameters':
        return solver.SParameters(solvetype=solvetype)
    if kind == 'deembedder':
        # The deembedder solver reads its assigned per-device s-parameters from
        # sd each call, so the (structurally cache-free) solver is safely reused
        # across frequencies.  It returns the unknown device s-parameters (a
        # single matrix for one unknown, or a list of matrices for several).
        return solver.CalculateUnknown(system)
    from SignalIntegrity.Lib.SystemDescriptions import VirtualProbeNumeric
    return VirtualProbeNumeric(sd).TransferMatrix()

def _SolveSerial(kind, sd, spc, numFrequencies, Z0, callback, abortException,
                 result=None, startIndex=0, solver=None, solvetype=None,
                 systemMatrices=None):
    """Serial fallback that reproduces the original per-frequency loop.
    @param result (optional) pre-allocated result list; already-computed entries
    (for example a timing probe) are preserved and not recomputed.
    @param startIndex (optional) first frequency index to compute.
    @param solver (optional) reusable solver to continue with.
    @param solvetype (optional) solve method string, used by 'systemsparameters'.
    @param systemMatrices (optional) list of per-frequency system s-parameter
    matrices, used by 'deembedder'.
    """
    names = [spc[d][0] for d in range(len(spc))]
    if solver is None:
        solver = _MakeSolver(kind, sd)
    if result is None:
        result = [None] * numFrequencies
    for n in range(startIndex, numFrequencies):
        matrices = [spc[d][1][n] for d in range(len(spc))]
        system = systemMatrices[n] if systemMatrices is not None else None
        result[n] = _SolveOneFrequency(kind, sd, names, matrices, Z0, solver,
                                       solvetype, system)
        if callback is not None:
            progress = (n + 1) / numFrequencies * 100.0
            if not callback(progress):
                raise abortException
    return result

def Solve(kind, sd, spc, numFrequencies, Z0,
          callback=None, abortException=None,
          numWorkers=None, chunkSize=None, solvetype=None,
          allowParallel=False, systemMatrices=None):
    """Computes the per-frequency result, in parallel when beneficial.
    @param kind string, one of 'simulator', 'virtualprobe', 'systemsparameters'
    or 'deembedder'.
    @param sd instance of the (already checked) system description.
    @param spc list of (deviceName, sParametersOverFrequency) tuples.
    @param numFrequencies integer number of frequencies.
    @param Z0 float reference impedance for the calculation.
    @param callback (optional) callable taking a float progress percentage and
    returning False to abort.
    @param abortException (optional) exception instance to raise when the
    callback requests an abort.
    @param numWorkers (optional) number of worker processes; None chooses
    automatically, 1 forces serial.
    @param chunkSize (optional) number of frequencies per worker task; None
    chooses automatically.
    @param solvetype (optional) solve method string, used by 'systemsparameters'.
    @param allowParallel (optional) master gate for parallel execution.  When
    False (the default) the calculation always runs serially and no worker pool
    is ever created.  When True, parallel execution is *permitted* but still
    subject to the size/cost model below, which decides per-solve whether it
    actually pays off.  This value originates from the AllowParallelization
    calculation property.
    @param systemMatrices (optional) list of per-frequency system s-parameter
    matrices used by the 'deembedder' kind (the s-parameters of the known overall
    system, one matrix per frequency, or None).  Ignored by the other kinds.
    @return list of per-frequency results ordered by frequency index.  For the
    'deembedder' kind each entry is the unknown device s-parameters at that
    frequency (a single matrix for one unknown, or a list of matrices for
    several), which the caller reorganizes per unknown device.
    @remark Falls back to serial execution when not allowed, for small problems,
    when a single worker is requested, or if parallel execution cannot be started
    (for example if the problem cannot be pickled).
    """
    # Master gate: unless parallel execution has been explicitly allowed, run
    # the original serial loop and never stand up a worker pool.
    if not allowParallel:
        return _SolveSerial(kind, sd, spc, numFrequencies, Z0,
                            callback, abortException, solvetype=solvetype,
                            systemMatrices=systemMatrices)

    # Re-entrancy guard against the Windows 'spawn' fork-bomb.  Each worker is a
    # fresh interpreter that re-imports __main__ (the caller's script).  If that
    # script fails to guard its top-level work with `if __name__ == '__main__':`,
    # every worker re-runs the whole script, which lands back here and would try
    # to spawn yet another pool -- an exponential explosion of processes that
    # repeats the calculation.  Detect that we are inside a spawned child (it has
    # a parent process) and force serial there so a nested pool can never be
    # created.  Note: this only stops the library from compounding the problem;
    # the caller's script must still use the `if __name__ == '__main__':` guard
    # (or multiprocessing.freeze_support()) to avoid re-running its own top-level
    # code in each worker.
    try:
        import multiprocessing
        if multiprocessing.parent_process() is not None:
            return _SolveSerial(kind, sd, spc, numFrequencies, Z0,
                                callback, abortException, solvetype=solvetype,
                                systemMatrices=systemMatrices)
    except (ImportError, AttributeError):
        # parent_process() exists on Python 3.8+; if unavailable, skip the guard.
        pass

    effectiveWorkers = _ResolveNumberOfWorkers(numWorkers, numFrequencies)

    if (effectiveWorkers <= 1 or
            numFrequencies < MinimumFrequenciesForParallel):
        return _SolveSerial(kind, sd, spc, numFrequencies, Z0,
                            callback, abortException, solvetype=solvetype,
                            systemMatrices=systemMatrices)

    names = [spc[d][0] for d in range(len(spc))]

    # Probe: time a single frequency solve serially and extrapolate.  If the
    # whole calculation is cheap, the multiprocessing overhead would dominate,
    # so stay serial.  The probe result is kept and reused, so no work is lost.
    solver = _MakeSolver(kind, sd)
    result = [None] * numFrequencies
    probeMatrices = [spc[d][1][0] for d in range(len(spc))]
    probeSystem = systemMatrices[0] if systemMatrices is not None else None
    # Warm up before timing.  The very first solve pays one-time costs that are
    # not representative of the steady-state per-frequency cost: building the
    # solver's structural caches, importing the numeric solver modules, and
    # initializing numpy's linear-algebra back-end.  Timing that cold solve and
    # extrapolating it across every frequency can overestimate the serial cost
    # by an order of magnitude, which intermittently tricks the cost model into
    # standing up a process pool for a problem that actually solves in a
    # fraction of a second serially -- and the spawn/deepcopy/pickle overhead of
    # that pool then makes the "parallel" run dramatically slower than serial.
    # A single untimed warm-up solve moves those one-time costs out of the
    # measurement so the probe reflects the real per-frequency cost.  The result
    # is deterministic, so the timed solve below reproduces result[0] exactly and
    # no work is wasted beyond one extra solve of a single frequency.
    if not os.environ.get('SI_PARALLEL_NOWARMUP'):
        _SolveOneFrequency(kind, sd, names, probeMatrices, Z0, solver, solvetype,
                           probeSystem)
    t0 = time.perf_counter()
    result[0] = _SolveOneFrequency(kind, sd, names, probeMatrices, Z0, solver,
                                   solvetype, probeSystem)
    probeSeconds = time.perf_counter() - t0
    if os.environ.get('SI_PARALLEL_DEBUG'):
        import sys as _sys
        _est = probeSeconds * numFrequencies
        _sys.stderr.write(
            f'[PTM] kind={kind} nf={numFrequencies} workers={effectiveWorkers} '
            f'probe={probeSeconds*1e3:.2f}ms est_serial={_est:.3f}s\n')
        _sys.stderr.flush()
    if callback is not None:
        if not callback(1.0 / numFrequencies * 100.0):
            raise abortException
    # Decide whether going parallel actually pays off.  Extrapolate the whole
    # serial cost from the single probe, then compare against the fixed pool
    # startup cost.  Parallel execution roughly turns a serial time S into
    # (startup + S/workers), so the time it *saves* is S*(1 - 1/workers).  Only
    # spawn a pool when that saving comfortably exceeds the startup cost; below
    # a coarse absolute floor, never bother.  The probe result is kept and
    # reused either way, so no work is lost.
    #
    # When a persistent worker pool with the required worker count already
    # exists (created by an earlier solve), the ~2 second spawn/import startup
    # cost has already been paid and reusing it is nearly free, so the startup
    # term drops out of the decision and even modestly sized solves are worth
    # dispatching to the pool.
    poolAlreadyWarm = (_PersistentExecutor is not None and
                       _PersistentExecutorWorkers == effectiveWorkers)
    effectivePoolStartup = 0.0 if poolAlreadyWarm else EstimatedPoolStartupSeconds
    estimatedSerialSeconds = probeSeconds * numFrequencies
    estimatedSavings = estimatedSerialSeconds * (1.0 - 1.0 / effectiveWorkers)
    if (estimatedSerialSeconds < MinimumEstimatedSerialSeconds or
            estimatedSavings <
            effectivePoolStartup * ParallelStartupSafetyFactor):
        return _SolveSerial(kind, sd, spc, numFrequencies, Z0,
                            callback, abortException,
                            result=result, startIndex=1, solver=solver,
                            solvetype=solvetype, systemMatrices=systemMatrices)

    effectiveChunkSize = _ResolveChunkSize(chunkSize, numFrequencies,
                                           effectiveWorkers)
    chunks = _BuildChunks(spc, numFrequencies, effectiveChunkSize, startIndex=1,
                          systemMatrices=systemMatrices)

    if os.environ.get('SI_PARALLEL_DEBUG'):
        import sys as _sys
        _sys.stderr.write(f'[PTM] --> GOING PARALLEL nf={numFrequencies} '
                          f'workers={effectiveWorkers} chunks={len(chunks)}\n')
        _sys.stderr.flush()

    try:
        from concurrent.futures import as_completed
        # A picklable, mutable copy of the base description is handed to the
        # workers; the caller's sd is left untouched.
        _pt0 = time.perf_counter()
        baseSd = copy.deepcopy(sd)
        _pt_deepcopy = time.perf_counter()
        if os.environ.get('SI_PARALLEL_DEBUG'):
            try:
                import pickle as _pk
                _sdbytes = len(_pk.dumps(baseSd))
                _chunkbytes = len(_pk.dumps(chunks))
            except Exception:
                _sdbytes = _chunkbytes = -1
            import sys as _sys
            _sys.stderr.write(f'[PTM]   deepcopy(sd)={(_pt_deepcopy-_pt0)*1e3:.1f}ms '
                              f'sd_pickle={_sdbytes/1024:.1f}KB '
                              f'chunks_pickle={_chunkbytes/1024:.1f}KB\n')
            _sys.stderr.flush()
        # Restrict each worker to a single BLAS thread so that N workers do not
        # each spawn N linear-algebra threads (which would oversubscribe the
        # machine and make the parallel run slower than serial).  The workers
        # are spawned while this restriction is in effect and inherit it; the
        # parent's own numpy is unaffected.  The _SuppressMainReimport guard
        # additionally prevents each spawned worker from re-importing the
        # parent's __main__ module (which, under a test runner or suite driver,
        # can be enormous and would otherwise dominate every worker's startup).
        import contextlib as _ctxlib
        _mainGuard = (_SuppressMainReimport()
                      if not os.environ.get('SI_PARALLEL_NOSUPPRESSMAIN')
                      else _ctxlib.nullcontext())
        # Reuse a persistent pool across solves.  The expensive part -- spawning
        # worker interpreters and importing numpy/SignalIntegrity into each --
        # happens only the first time (inside _GetPersistentExecutor, warmed up
        # under the thread-limit/main-suppress guards); subsequent solves reuse
        # the already-running workers, so what used to be a ~2 second per-solve
        # pool spin-up collapses to just the (cheap) task submission below.
        with _WorkerThreadLimit(ThreadsPerWorker):
            executor = _GetPersistentExecutor(effectiveWorkers, _mainGuard)
            _pt_exec = time.perf_counter()
            # Tag this solve's tasks with a fresh generation so workers know to
            # (re)build their cached solver for this base problem exactly once.
            global _SolveGeneration
            _SolveGeneration += 1
            generation = _SolveGeneration
            futures = [executor.submit(_SolveChunk,
                                       (generation, kind, baseSd, names, Z0,
                                        solvetype, chunk))
                       for chunk in chunks]
            _pt_submit = time.perf_counter()
            _first_result_done = [False]
            _pt_first = _pt_submit
            # Results can complete out of order, but the callback must be
            # driven in strict frequency order so that its progress values
            # and abort point are identical to the serial path (some tests
            # and progress bars rely on this exact contract).  Completed
            # results are buffered and a pointer advances over the
            # contiguous run of finished frequencies, invoking the callback
            # for each in order.  The probe already reported frequency 0, so
            # in-order reporting resumes at frequency 1.
            nextToReport = 1
            for future in as_completed(futures):
                for (n, tm) in future.result():
                    result[n] = tm
                if not _first_result_done[0]:
                    _first_result_done[0] = True
                    _pt_first = time.perf_counter()
                if callback is not None:
                    while (nextToReport < numFrequencies and
                           result[nextToReport] is not None):
                        progress = (nextToReport + 1) / numFrequencies * 100.0
                        if not callback(progress):
                            for f in futures:
                                f.cancel()
                            raise _Aborted
                        nextToReport += 1
        if os.environ.get('SI_PARALLEL_DEBUG'):
            import sys as _sys
            _sys.stderr.write(f'[PTM]   exec_create={(_pt_exec-_pt_deepcopy)*1e3:.1f}ms '
                              f'submit_loop={(_pt_submit-_pt_exec)*1e3:.1f}ms '
                              f'to_first_result={(_pt_first-_pt_submit):.3f}s '
                              f'total_compute={(time.perf_counter()-_pt_submit):.3f}s '
                              f'PARALLEL_TOTAL={(time.perf_counter()-_pt0):.3f}s\n')
            _sys.stderr.flush()
        return result
    except _Aborted:
        # The caller asked to abort.  Discard the (possibly still busy) pool so
        # its leftover tasks cannot bleed into a later solve; a fresh pool is
        # created on demand next time.
        ShutdownPersistentExecutor()
        if abortException is not None:
            raise abortException
        raise
    except Exception as _e:
        if os.environ.get('SI_PARALLEL_DEBUG'):
            import sys as _sys, traceback as _tb
            _sys.stderr.write(f'[PTM] !!! PARALLEL FAILED -> serial fallback: '
                              f'{type(_e).__name__}: {_e}\n')
            _tb.print_exc()
            _sys.stderr.flush()
        # A multiprocessing/pickling problem should never prevent a result, so
        # fall back to serial execution, reusing the probe result already
        # computed for frequency 0.  The pool may have been left broken (for
        # example a BrokenProcessPool), so discard it; the serial fallback below
        # does not need it and a later solve will build a fresh one.
        ShutdownPersistentExecutor()
        return _SolveSerial(kind, sd, spc, numFrequencies, Z0,
                            callback, abortException,
                            result=result, startIndex=1, solver=solver,
                            solvetype=solvetype, systemMatrices=systemMatrices)
