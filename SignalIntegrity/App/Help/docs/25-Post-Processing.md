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

- limit <negative> <positive> - limits the impulse response lengths of the final result to be between the negative and positive time values specified.

- reference impedance <value> – sets the resulting s-parameter calculation reference impedance according to the value specified.

- offset <negative> <positive> - removes the DC offset from the impulse responses of the final result by subtracting the mean of the impulse response samples that fall outside the negative and positive time limits specified. Either or both limits may be given as none, and if no limits are supplied the entire impulse response is used.

- port reorder <order> - reorders the ports of the final result according to the comma-separated list of one-based port numbers specified (for example, port reorder 1,3,2,4).

- taper <from> <to> - tapers the frequency response of the final result, keeping it flat up to the from frequency and rolling it off to zero with a raised cosine between the from and to frequencies. If the to frequency is omitted, the last frequency is used.

- wavelet denoise <threshold> - denoises the final result by keeping only the wavelet transform coefficients of each impulse response whose absolute value exceeds the threshold specified.

- ! <text> - adds the specified text as a comment line in the header of the resulting s-parameter file.

If the post-processing commands are not recognized or cannot be parsed, the [PostProcessing](27-Errors-and-Exceptions.md#sub:PostProcessing) exception is raised

