# Post-Processing {#sec:Post-Processing}

Post-processing commands are commands to be executed after a [Deembedding](09-Deembedding.md#sec:Deembedding) or [S-Parameter Generation](07-S-Parameter-Generation.md#sec:S-parameter-Generation) calculation completes.

These commands are entered as text in the order that they are to be executed in a dialog opened by the [Post-Processing](15-Main-Schematic-Dialog.md#Control-Help:Post-Processing). command.

All of the post-processing commands are appended to the [Netlist](24-Netlist.md#sec:Netlist) generated for calculation and can be seen when you issue [Export Netlist](15-Main-Schematic-Dialog.md#Control-Help:Export-Netlist), with the caveat that commands are entered directly in the post-processing dialog, but have the keyword [post](24-Netlist.md#sub:post) added when putting the commands in the netlist.

Because they are in the netlist, one is able to make scripted solutions with post-processing, and the cache coherency of the calculated result is maintained (i.e. changes to the netlist change the validity of cached results).

Valid post-processing commands are:

- preserve DC - this causes causality enforcement to preserve the DC response behavior.

- enforce causality - is the same as issuing [Enforce Causality](13-S-parameter-Viewer.md#Control-Help:Enforce-Causality) on the final result.

- enforce passivity - is the same as issuing [Enforce Passivity](13-S-parameter-Viewer.md#Control-Help:Enforce-Passivity) on the final result.

- enforce both passivity and causality – is the same as issuing [Enforce Both Passivity and Reciprocity](13-S-parameter-Viewer.md#Control-Help:Enforce-Both-Passivity-and-Reciprocity) on the final result.

- enforce reciprocity - is the same as issuing [Enforce Reciprocity](13-S-parameter-Viewer.md#Control-Help:Enforce-Reciprocity) on the final result.

- enforce all – is the same as issuing [Enforce All](13-S-parameter-Viewer.md#Control-Help:Enforce-All) on the final result.

- limit \<negative\> \<positive\> - limits the impulse response lengths of the final result to be between the negative and positive time values specified.

- reference impedance \<value\> – sets the resulting s-parameter calculation reference impedance according to the value specified.

If the post-processing commands are not recognized or cannot be parsed, the [PostProcessing](27-Errors-and-Exceptions.md#sub:PostProcessing) exception is raised

