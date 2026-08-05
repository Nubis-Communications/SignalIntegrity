# Netlist {#sec:Netlist}

Netlists are the internal text based format of the schematic. There is a one-to-one correspondence between the netlist and the schematic from a device and connectivity standpoint.

each line in the netlist starts with one of the following keywords:

- [device](24-Netlist.md#sub:device)- specifies one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices) in the schematic.

- [connect](24-Netlist.md#sub:connect)- specifies one or more device pin connections.

- [port](24-Netlist.md#sub:port)- specifies a [Port](23-Built-in-Devices-Parts.md#device:Port) and it’s connection to a device pin. (used only for [S-Parameter Generation](07-S-Parameter-Generation.md#sec:S-parameter-Generation) and [Deembedding](09-Deembedding.md#sec:Deembedding) applications).

- [meas](24-Netlist.md#sub:meas)- specifies a [Voltage Measure Probe](23-Built-in-Devices-Parts.md#device:Measure-Probe) and it’s connection to a device pin. (used only for [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing) applications).

- [output](24-Netlist.md#sub:output)- specifies an [Voltage Output Probe](23-Built-in-Devices-Parts.md#device:Output-Probe) and it’s connection to a device pin. (used only for [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing) and [Simulation](08-Simulation.md#sec:Simulation) applications).

- [stim](24-Netlist.md#sub:stim)- specifies a [Stim](23-Built-in-Devices-Parts.md#device:Stim) and it’s associated device pin. (used only for [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing) applications).

- [stimdef](24-Netlist.md#sub:stimdef)- specifies the relationship between defining and dependent stims (see [Stim](23-Built-in-Devices-Parts.md#device:Stim)). (used only for [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing) applications).

- [unknown](24-Netlist.md#sub:unknown)- specifies an [Unknown](23-Built-in-Devices-Parts.md#device:Unknown) device (used only for [Deembedding](09-Deembedding.md#sec:Deembedding) applications).

- [system](24-Netlist.md#sub:system)- specifies a [System](23-Built-in-Devices-Parts.md#device:System) device (used only for [Deembedding](09-Deembedding.md#sec:Deembedding) applications).

- [post](24-Netlist.md#sub:post)- specifies [Post-Processing](25-Post-Processing.md#sec:Post-Processing) of a resulting s-parameter file (used only for [Deembedding](09-Deembedding.md#sec:Deembedding) and [S-Parameter Generation](07-S-Parameter-Generation.md#sec:S-parameter-Generation) applications).

## device {#sub:device}

A netlist line beginning with the keyword *device* defines one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices) in the schematic.

The syntax is at least the keyword *device* followed by the reference designator followed by the number of ports followed by a keyword defining one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices).

Following this is often optional keyword pairs specifying the arguments for the device.

Sometimes the first argument is specified without a keyword (the keyword is implied). Usually this is for devices with only one argument, like a [Resistor](23-Built-in-Devices-Parts.md#device:Resistor) whose only argument is the resistance.

If a device line of a netlist is specified incorrectly, you will get one of the [Errors and Exceptions](27-Errors-and-Exceptions.md#sec:Errors-and-Exceptions) or the type: [DeviceParser](27-Errors-and-Exceptions.md#sub:DeviceParser).

## connect {#sub:connect}

A netlist line beginning with the keyword *connect* specifies one or more device pin connections.

The syntax is the keyword *device* followed pairs of reference designators and pin numbers.

The reference designators refer to one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices) specified in a [device](24-Netlist.md#sub:device) command elsewhere in the netlist.

The pin numbers refer to a pin of the device.

## port {#sub:port}

A netlist line beginning with the keyword *port* specifies a [Port](23-Built-in-Devices-Parts.md#device:Port) and it’s connection to a device pin.

This should appear only in [S-Parameter Generation](07-S-Parameter-Generation.md#sec:S-parameter-Generation) and [Deembedding](09-Deembedding.md#sec:Deembedding) applications and there must be at least one statement like this.

The syntax is the keyword *port* followed by triplets containing a port number followed by the reference designator and pin number of the device pin that the port is connected to.

The reference designators refer to one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices) specified in a [device](24-Netlist.md#sub:device) command elsewhere in the netlist.

The pin numbers refer to a pin of the device.

If in your schematic, a [Port](23-Built-in-Devices-Parts.md#device:Port) is connected to a net with multiple device pins connected, the line in the netlist will specify a connection to an arbitrarily chosen one of the device pins (with the connection to the other device pins held in [connect](24-Netlist.md#sub:connect) netlist lines.)

## meas {#sub:meas}

A netlist line beginning with the keyword *meas* specifies a [Voltage Measure Probe](23-Built-in-Devices-Parts.md#device:Measure-Probe) and it’s connection to a device pin.

This should only appear in [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing) applications and there must be at least one statement like this.

The syntax is the keyword *meas* followed by a reference designator and pin number.

The reference designators refer to one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices) specified in a [device](24-Netlist.md#sub:device) command elsewhere in the netlist.

The pin numbers refer to a pin of the device.

If in your schematic, a [Voltage Measure Probe](23-Built-in-Devices-Parts.md#device:Measure-Probe) is connected to a net with multiple device pins connected, the line in the netlist will specify a connection to an arbitrarily chosen one of the device pins (with the connection to the other device pins held in [connect](24-Netlist.md#sub:connect) netlist lines.)

Note that the reference designator (i.e. the name) and the filename of the [Waveform](28-Waveform.md#sec:Waveform) associated with the [Voltage Measure Probe](23-Built-in-Devices-Parts.md#device:Measure-Probe) do not appear in the netlist as it is unimportant for the calculations. Instead, the application keeps track of this information during netlist generation for use in managing the calculation.

## output {#sub:output}

A netlist line beginning with the keyword *output* specifies a [Voltage Output Probe](23-Built-in-Devices-Parts.md#device:Output-Probe) and it’s connection to a device pin.

This should only appear in [Simulation](08-Simulation.md#sec:Simulation) or [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing) applications and there must be at least one statement like this in the netlist.

The syntax is the keyword *output* followed by a reference designator and pin number.

The reference designators refer to one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices) specified in a [device](24-Netlist.md#sub:device) command elsewhere in the netlist.

The pin numbers refer to a pin of the device.

If in your schematic, a [Voltage Output Probe](23-Built-in-Devices-Parts.md#device:Output-Probe) is connected to a net with multiple device pins connected, the line in the netlist will specify a connection to an arbitrarily chosen one of the device pins (with the connection to the other device pins held in [connect](24-Netlist.md#sub:connect) netlist lines.)

Note that the reference designator (i.e. the name) associated with the [Voltage Output Probe](23-Built-in-Devices-Parts.md#device:Output-Probe) do not appear in the netlist as it is unimportant for the calculations. Instead, the application keeps track of this information during netlist generation for use in managing the calculation.

## stim {#sub:stim}

A netlist line beginning with the keyword *stim* specifies a [Stim](23-Built-in-Devices-Parts.md#device:Stim) and it’s connection to a device pin.

This should only appear in [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing) applications, and there must be at least one statement like this in the netlist.

The syntax is the keyword *stim* followed by the name of the stim followed by a reference designator and pin number.

The reference designators refer to one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices) specified in a [device](24-Netlist.md#sub:device) command elsewhere in the netlist.

The pin numbers refer to a pin of the device from which the stimulus emanates.

The name of the stim is always a lowercase m followed by a number, where the number is unique and is generated automatically during netlist generation. The name and number have nothing to do with the reference designator for the stim which is unimportant.

## stimdef {#sub:stimdef}

A netlist line beginning with the keyword *stimdef* specifies the relationship between defining and dependent stims in the schematic (see [Stim](23-Built-in-Devices-Parts.md#device:Stim)).

This should only appear in [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing) applications.

A *stimdef* statement will only appear if there is a defining stim in the schematic.

The syntax is the keyword *stimdef* followed by a python list-based matrix definition where the form:

$$\left[\left[d_{11},d_{12},\ldots,d_{1C}\right],\left[d_{21},d_{22},\ldots,d_{2C}\right],\ldots,\left[d_{R1},d_{R2},\ldots,d_{RC}\right]\right]$$

which is equivalent to a $R\times C$ matrix $\mathbf{D}$:

$$\left(\begin{array}{cccc}
d_{11} & d_{12} & \ldots & d_{1C}\\
d_{21} & d_{22} & \ldots & d_{2C}\\
\vdots & \vdots & \ddots & \vdots\\
d_{R1} & d_{R2} & \ldots & d_{RC}
\end{array}\right)$$

The matrix is such that for a $C$ element vector of dependent stims $\mathbf{m}$ (with the elements $\left(\begin{array}{c}
m_{1}\\
m_{2}\\
\vdots\\
m_{C}
\end{array}\right)$), as listed in the netlist for the dependent stims and an $R$ element vector of defining stims $\mathbf{d}$ (see [stim](24-Netlist.md#sub:stim) for the netlist statement for the stim and [Stim](23-Built-in-Devices-Parts.md#device:Stim) for a description of dependent and defining stims), that the stimdef defines $\mathbf{D}$ such that:

$$\mathbf{d}=\mathbf{D}\cdot\mathbf{m}$$

When no stimdef statement appears, there are $C$ unknowns (and there must be at least $C$ [Voltage Measure Probe](23-Built-in-Devices-Parts.md#device:Measure-Probe)s specified with lines that begin with [meas](24-Netlist.md#sub:meas) in the netlist). If a stimdef statement appears, there are $R$ unknowns (and there must be at least $R$ [Voltage Measure Probe](23-Built-in-Devices-Parts.md#device:Measure-Probe)s specified with lines that begin with [meas](24-Netlist.md#sub:meas) in the netlist).

## unknown {#sub:unknown}

A netlist line beginning with the keyword *unknown* defines an [Unknown](23-Built-in-Devices-Parts.md#device:Unknown) in the schematic.

This should appear only for [Deembedding](09-Deembedding.md#sec:Deembedding) applications and there must be one such statement in the netlist.

The syntax is the keyword *unknown* followed by the reference designator followed by the number of ports.

## system {#sub:system}

A netlist line beginning with the keyword *system* defines an [System](23-Built-in-Devices-Parts.md#device:System) in the schematic.

This should appear only for [Deembedding](09-Deembedding.md#sec:Deembedding) applications and there must be one such statement in the netlist.

The syntax is the keyword *system* followed by the reference designator followed by the number of ports followed by the keyword *file* followed by the name of the file containing s-parameters that define the [System](23-Built-in-Devices-Parts.md#device:System).

## post {#sub:post}

A netlist line beginning with the keyword post defines [Post-Processing](25-Post-Processing.md#sec:Post-Processing) of a resulting s-parameter file.

This should appear only for [Deembedding](09-Deembedding.md#sec:Deembedding) and [S-Parameter Generation](07-S-Parameter-Generation.md#sec:S-parameter-Generation) applications.

valid post processing lines are:

- post preserve DC - causes causality enforcement to preserve the DC response behavior.

- post enforce causality - is the same as issuing [Enforce Causality](13-S-parameter-Viewer.md#Control-Help:Enforce-Causality) on the final result.

- post enforce passivity - is the same as issuing [Enforce Passivity](13-S-parameter-Viewer.md#Control-Help:Enforce-Passivity) on the final result.

- post enforce both – is the same as issuing [Enforce Both Passivity and Reciprocity](13-S-parameter-Viewer.md#Control-Help:Enforce-Both-Passivity-and-Reciprocity) on the final result.

- post enforce reciprocity - is the same as issuing [Enforce Reciprocity](13-S-parameter-Viewer.md#Control-Help:Enforce-Reciprocity) on the final result.

- post enforce all – is the same as issuing [Enforce All](13-S-parameter-Viewer.md#Control-Help:Enforce-All) on the final result.

- post limit <negative> <positive> - limits the impulse response lengths of the final result to be between the negative and positive time values specified.

- post reference impedance <value> - sets the resulting s-parameter calculation reference impedance according to the value specified.

- post offset <negative> <positive> - removes the DC offset from the impulse responses of the final result by subtracting the mean of the impulse response samples that fall outside the negative and positive time limits specified. Either or both limits may be given as none, and if no limits are supplied the entire impulse response is used.

- post port reorder <order> - reorders the ports of the final result according to the comma-separated list of one-based port numbers specified (for example, post port reorder 1,3,2,4).

- post scale rho <scale> - scales the time-domain reflection coefficients (rho) of the final result by the scale specified.  Each diagonal (reflect) s-parameter element is converted to its time-domain reflection coefficient (the integral of its impulse response), scaled, and the diagonal element is regenerated from the scaled reflection coefficient.



- post taper <from> <to> - tapers the frequency response of the final result, keeping it flat up to the from frequency and rolling it off to zero with a raised cosine between the from and to frequencies. If the to frequency is omitted, the last frequency is used.

- post wavelet denoise <threshold> - denoises the final result by keeping only the wavelet transform coefficients of each impulse response whose absolute value exceeds the threshold specified.

- post ! <text> - adds the specified text as a comment line in the header of the resulting s-parameter file.



