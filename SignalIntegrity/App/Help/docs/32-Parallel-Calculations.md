# Parallel Calculations {#sec:Parallel-Calculations}

Many of the calculations performed by ***SignalIntegrityApp*** &ndash; [S-parameter Generation](07-S-Parameter-Generation.md#sec:S-parameter-Generation), [Simulation](08-Simulation.md#sec:Simulation), [Deembedding](09-Deembedding.md#sec:Deembedding), and [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing) &ndash; can optionally be spread across multiple processor cores to speed up computation. This section explains how that works and how to turn it on.

By default, parallel calculations are turned off, and all calculations run serially on a single core.

## Theory of Operation {#sub:Parallel-Calculations-Theory}

Nearly all of the heavy numeric work in *SignalIntegrity* is performed one frequency point at a time. The solution at each frequency &ndash; whether it is an s-parameter matrix, a set of transfer matrices, or a deembedded device &ndash; depends only on the circuit description and that single frequency. The result at one frequency does not depend on the result at any other frequency.

Because the per-frequency solves are **independent** of one another, they are an ideal candidate for parallelization: the list of frequencies can be divided among several worker processes, each solving its share at the same time, and the individual results reassembled, in order, into the final answer. All four calculation types listed above route their per-frequency solves through the same parallel solver, so they all benefit identically.

Parallel execution, however, is not free. Before the workers can begin, a pool of worker processes must be started, and the problem must be shipped to them &ndash; this requires making a copy of the system description and every per-frequency matrix and transmitting it to each process. For the vast majority of real problems, the per-frequency solve is cheap relative to this setup cost, so running serially is actually **faster**. Parallel execution only pays off for large, expensive problems &ndash; for example, those with many frequency points and/or large, tightly-coupled circuits.

For this reason, enabling parallelization is best thought of as granting *permission* rather than issuing a *command*. Even when parallelization is allowed, a built-in cost model estimates the serial cost of each solve and only distributes the work across cores when it predicts that doing so will actually be worthwhile. Small problems continue to run serially even with the feature enabled.

When the calculation does run in parallel, it uses a number of worker processes appropriate to the machine (typically the number of available processor cores). The final results are identical, to within numerical precision, to those produced by a serial calculation; only the wall-clock time changes.

## Enabling Parallel Calculations {#sub:Enabling-Parallel-Calculations}

Parallelization is gated by **two** settings, and it is permitted only when **both** of them are enabled:

1. The global [Calculation.AllowParallelization](29-Preferences.md#sub:Calculation.AllowParallelization) preference, and

2. The per-project [Allow Parallelization](15-Main-Schematic-Dialog.md#sub:Allow-Parallelization) calculation property.

### The Preference {#sub:Parallel-Calculations-Preference}

The [Calculation.AllowParallelization](29-Preferences.md#sub:Calculation.AllowParallelization) preference is a global, application-wide switch found in the [Preferences](29-Preferences.md#sec:Preferences). It defaults to False. Because it is experimental, it is off by default.

The preference acts as a hard override: when it is False, no calculation will ever run in parallel, regardless of any project setting. When it is True, the feature becomes available and the [Allow Parallelization](15-Main-Schematic-Dialog.md#sub:Allow-Parallelization) property becomes visible in the [Calculation Properties](15-Main-Schematic-Dialog.md#Control-Help:Calculation-Properties) dialog.

### The Calculation Property {#sub:Parallel-Calculations-Property}

The [Allow Parallelization](15-Main-Schematic-Dialog.md#sub:Allow-Parallelization) calculation property is stored with each project (in its project file) and controls whether *that particular project* is permitted to calculate in parallel. It, too, defaults to False.

The property is shown in the [Calculation Properties](15-Main-Schematic-Dialog.md#Control-Help:Calculation-Properties) dialog whenever the [Calculation.AllowParallelization](29-Preferences.md#sub:Calculation.AllowParallelization) preference is True, or whenever the project already has the property set to True (so that a project saved with parallelization enabled always exposes the control, even if the preference has since been turned off).

In summary, a calculation is allowed to run in parallel only when the preference **and** the project property are both True; even then, the cost model makes the final, per-solve decision.

## Parallelization Is Not Passed Into Sub-blocks {#sub:Parallel-Calculations-Sub-blocks}

The [Allow Parallelization](15-Main-Schematic-Dialog.md#sub:Allow-Parallelization) calculation property is deliberately **not** propagated into sub-blocks (hierarchical blocks or referenced sub-projects).

When a project contains a sub-block, the parent normally pushes its calculation properties (such as the end frequency, number of frequency points, and reference impedance) down into the sub-block so that the sub-block is solved consistently with the parent. The parallelization setting is a deliberate exception to this rule: the parent's [Allow Parallelization](15-Main-Schematic-Dialog.md#sub:Allow-Parallelization) value is never allowed to override the value a sub-block carries in its own project.

In other words, every block &ndash; the top-level project and each sub-block &ndash; honors *its own* [Allow Parallelization](15-Main-Schematic-Dialog.md#sub:Allow-Parallelization) property for *its own* solve. Enabling parallelization on a top-level project does not cause its sub-blocks to run in parallel, and vice versa. If you want a sub-block's solve to be parallelized, enable the property in that sub-block's project; if you want to be sure a sub-block never parallelizes, leave the property off in that sub-block's project. Keep in mind that, because the global [Calculation.AllowParallelization](29-Preferences.md#sub:Calculation.AllowParallelization) preference is a hard override, turning the preference off disables parallelization everywhere &ndash; in every project and every sub-block.
