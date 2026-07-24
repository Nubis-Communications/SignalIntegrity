# Errors and Exceptions {#sec:Errors-and-Exceptions}

When problems crop up during calculation, ***SignalIntegrityApp*** throws an exception and a message box is shown with the exception and the message the exception generates. As such, the exception type defines the main category of the exception and the message pertains to various flavors of that exception type.

The ***SignalIntegrity*** exceptions are:

- [SystemDescription](27-Errors-and-Exceptions.md#sub:System-Description-Error) - pertains to a general problem with the netlist used for calculation.

- [Numeric](27-Errors-and-Exceptions.md#sub:Numeric) - pertains to a general numerical error during calculation.

- [SParameterFile](27-Errors-and-Exceptions.md#sub:SParameterFile) - pertains to a problem with reading an s-parameter file.

- [WaveformFile](27-Errors-and-Exceptions.md#sub:WaveformFile) - pertains to a problem with reading a [Waveform](28-Waveform.md#sec:Waveform) file.

- [Waveform](27-Errors-and-Exceptions.md#sub:Waveform) - pertains to a problem with calculating with a [Waveform](28-Waveform.md#sec:Waveform).

- [DeviceParser](27-Errors-and-Exceptions.md#sub:DeviceParser) - pertains to a problem parsing a device description in the netlist.

- [Simulator](27-Errors-and-Exceptions.md#sub:Simulator) - pertains to a problem specific to the Simulator application and calculation.

- [VirtualProbe](27-Errors-and-Exceptions.md#sub:VirtualProbe) - pertains to a problem specific to the Virtual Probe application and calculation.

- [PostProcessing](27-Errors-and-Exceptions.md#sub:PostProcessing) - pertains to a problem with [Post-Processing](25-Post-Processing.md#sec:Post-Processing).

## SParameterFile {#sub:SParameterFile}

An s-parameter file was specified for reading and it could not be read

**incorrect extension in s-parameter file name**

All s-parameter files must have an extension ’.s\[x\]p’ where x is the number of ports. This is the only way to precisely determine the number of ports in an s-parameter file, so the files must have an extension like this.

**filename not found**

The s-parameter file could not be found.

## WaveformFile {#sub:WaveformFile}

A [Waveform](28-Waveform.md#sec:Waveform) file was specified for reading and it could not be read

**filename not found**

The waveform file could not be found.

## Waveform {#sub:Waveform}

An error occurred involving a waveform

**cannot generate frequency content**

An error occurred in the generation of frequency content of a waveform. This usually occurs when the frequencies are not evenly spaced and the DFT cannot be used.

**PRBS risetime too high for waveform generation**

The generation of serial data waveforms uses a raised cosine for setting the risetime. This requires the risetime to be such that it forms a raised cosine on the edges that does not extend beyond one-half of the unit interval. This means a risetime greater than 56% of the unit interval.

**cannot add waveform to type ...**

An attempt is made to add a waveform to an unsupported type. Supported types are Waveform, float, int, and complex.

**cannot subtract type ... from waveform**

An attempt is made to subtract an unsupported type from a waveform. Supported types are Waveform, float, int, and complex.

**cannot multiply waveform by type ...**

An attempt is made to multiply a waveform by an unsupported type. Supported types are Waveform, float, int, and complex.

**cannot divide waveform by type ...**

An attempt is made to divide a waveform by an unsupported type. Supported types are Waveform, float, int, and complex.

**waveform file to large to process**

An attempt is made to process a waveform that is larger than the preference specified in [Calculation.MaximumWaveformPoints](29-Preferences.md#sub:Calculation.MaximumWaveformPoints).

## SystemDescription {#sub:System-Description-Error}

During calculation, the netlist is parsed to set up the calculation. In this process, various things can go wrong because of incorrect specification of the netlist:

**Unconnected Device Ports**

One or more device ports in the schematic is not connected. With the exception of the system device used in deembedding applications, all device ports must be connected to one or more other device ports.

Generally, by looking at your schematic, you can see this, because unconnected device ports will have a red x on device pins. That being said, simply connecting a wire to the device port makes the red x disappear (because it is connected to the vertex of a wire) and the wire itself might not be connected to anything.

You can troubleshoot connection problems exactly by looking at the netlist. The netlist will list each device with a name and number of ports and will list all connections between device ports.

**Duplicate Device Name**

One or more devices in your schematic has the same device name. Usually, as you add devices to the schematic, you do not worry about the reference designations and the application adds unique reference designators as parts are added. These reference designators can be edited, however, by the user and the user can enter reference designations that are the same accidentally. To troubleshoot this problem, you can look both at the schematic, specifically the part properties for the devices, and at the netlist which will have device declarations with the same device name.

**No Device Named**

A connection or other type of declaration specifies a device name that is nonexistent. This type of error ought to be impossible to create from the application and is more typical of hand generated netlists. Nevertheless, this error message indicates that the netlist contains a reference to a device name (listed in the error) that is not specified elsewhere in the netlist. An error like this is really an internal error, but you can see the cause of an error like this by examining the netlist.

**Cannot Connect Device Ports**

This is the same error as No Device Named, except that it was explicitly called in an attempt to connect non-existent device ports. It also handles non-existent ports of the device if they cannot be found.

## Simulator {#sub:Simulator}

**No Outputs**

There are no output probes in the circuit. This type of error ought to be difficult to create from the application because the application checks for the existence of at least one output probe prior to enabling the simulation calculation, but it does not check whether the output probe is actually connected to anything. It is useful to leave some output probes unconnected and floating in the schematic to avoid calculation (for example, it might have been used for troubleshooting), but at least one of the output probes must be connected to the circuit.

By looking at your schematic, you can see this, because unconnected output probes will have a red x on their connection pins. That being said, simply connecting a wire to the output probe makes the red x disappear (because it is connected to the vertex of a wire) and the wire itself might not be connected to anything.

**No Sources**

There are no sources in the circuit. This type of error ought to be impossible to create from the application because the application checks for the existence of at least one source prior to enabling the simulation calculation, but it does not check whether the output probe is actually connected to anything. If it is not connected, it ought to generate an Unconnected Device Ports error.

By looking at your schematic, you can see this, because unconnected sources will have a red x on their connection pins. That being said, simply connecting a wire to the pins of a source makes the red x’s disappear (because it is connected to the vertex of a wire) and the wire itself might not be connected to anything.

**Numerical Error**

This is the same error as Cannot Invert I-W or I-Wxx while calculating the simulator transfer parameters. It indicates pathological problems in the system described. In many cases this can be resolved using the [Calculation.TrySVD](29-Preferences.md#sub:Calculation.TrySVD) preference in the [Preferences](29-Preferences.md#sec:Preferences).

## VirtualProbe {#sub:VirtualProbe}

**No Measures**

There are no measure probes in the circuit. This type of error ought to be difficult to create from the application because the application checks for the existence of at least one measure probe prior to enabling the simulation calculation, but it does not check whether the measure probe is actually connected to anything.

By looking at your schematic, you can see this, because unconnected measure probes will have a red x on their connection pins. That being said, simply connecting a wire to the measure probe makes the red x disappear (because it is connected to the vertex of a wire) and the wire itself might not be connected to anything.

**No Outputs**

There are no output probes in the circuit. This type of error ought to be difficult to create from the application because the application checks for the existence of at least one output probe prior to enabling the simulation calculation, but it does not check whether the output probe is actually connected to anything. It is useful to leave some output probes unconnected and floating in the schematic to avoid calculation (for example, it might have been used for troubleshooting), but at least one of the output probes must be connected to the circuit.

By looking at your schematic, you can see this, because unconnected output probes will have a red x on their connection pins. That being said, simply connecting a wire to the output probe makes the red x disappear (because it is connected to the vertex of a wire) and the wire itself might not be connected to anything.

**No Sources**

There are no sources in the circuit. In the context of [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing), sources mean stims as a stim looks like a source in the depths of the calculation. The application checks for the existence of at least one [Stim](23-Built-in-Devices-Parts.md#device:Stim) defined by a [Netlist](24-Netlist.md#sec:Netlist) line defining a [stim](24-Netlist.md#sub:stim) prior to enabling the [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing) calculation, but it does not check whether the stim is actually connected to anything.

By looking at your schematic, you can examine unconnected stims, because they will have a red x on their connection pins. That being said, simply connecting a wire to the pins of a stim makes the red x’s disappear (because it is connected to the vertex of a wire) and the wire itself might not be connected to anything.

Stims also require that the end of the arrow is connected directly to a device port. This is because unlike waves which are present along a wire, stims represent waves that emanate from a device port. Unfortunately, the schematic editor allows you to make this mistake.

Also, stims must be connected to only one device port. While the schematic editor allows device ports to be connected directly together, when a stim is connected to a device port, the device port must be separated from others in the schematic by a small piece of wire.

**Numerical Error**

This is the same error as Cannot Invert I-W or I-Wxx while calculating the virtual probe transfer parameters. It indicates pathological problems in the system described.

**Incorrect Matrix Alignment**

This cryptic error is an all encompassing error to indicate that something is wrong with the number of stims or measures in your system. In virtual probing, the number of independent stims (stims without the non-arrow side connected) must be less than or equal to the number of measure probes in the system. This error probably indicates that this is not the case (I say probably because there are other sources of this error especially when hand created netlists are entered into the system).

## Numeric {#sub:Numeric}

**Cannot Invert I-W or I-Wxx**

Understanding this error involves understanding the theory in the accompanying book. Suffice it to say that the problem is ill-determined in the sense that the system characteristics matrix is not invertible. This occurs under many pathological cases, some of which can be worked around and others cannot (i.e. there is simply no solution to the problem).

An example of a pathological case that cannot be worked around are attempts to de-embed elements in systems where elements are present that do not pass anything (at a given frequency).

Examples of pathological cases that can be worked around are circuit nodes whose absolute voltage or current cannot be determined due to the construction of the circuit. Sometimes, these can be worked around through the insertion of large resistors to ground or tiny series resistors. A detailed examination of the circuit would be necessary.

Also, in many cases this can be resolved using the [Calculation.TrySVD](29-Preferences.md#sub:Calculation.TrySVD) preference in the [Preferences](29-Preferences.md#sec:Preferences).

## DeviceParser {#sub:DeviceParser}

This error class is for errors parsing [Netlist](24-Netlist.md#sec:Netlist) lines with the [device](24-Netlist.md#sub:device) keyword.

**Mandatory Keywords Not Supplied**

This error message states that mandatory keywords and values were not supplied to the device parser for a particular [device](24-Netlist.md#sub:device) line in the [Netlist](24-Netlist.md#sec:Netlist), defining one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices). This would be an internal error to the application because you cannot really control this.

The keyword error looks like: \[’keyword1’,’keyword2’,…\] for ’deviceName’ where ’keyword1’ and ’keyword2’ are representative of keywords that must be defined for the device and ’deviceName’ is representative of the name of the device.

If a keyword is ”, then the device takes an argument without a keyword (the keyword is inherent - see [device](24-Netlist.md#sub:device)).

For example, an error message that says that the keywords not supplied are: \[”\] for file, this means that the file name (which is not specified with a keyword) was not supplied.

When entering netlists by hand, it is easy to forget a mandatory keyword, but in ***SignalIntegrityApp***, this is difficult since the application creates the netlist entry from the instantiated part in the schematic.

**Arguments Must Come in Keyword Pairs**

This error message states that the netlist [device](24-Netlist.md#sub:device) line in the [Netlist](24-Netlist.md#sec:Netlist), defining one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices) was formed incorrectly and that it was expecting the arguments to come in keyword/value pairs. This would be an internal error to the application because you cannot really control this.

**Device Could Not Be Instantiated**

This error message states that the netlist [device](24-Netlist.md#sub:device) line in the [Netlist](24-Netlist.md#sec:Netlist), defining one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices) was formed incorrectly and the result of trying to create a device with the given name and arguments failed. This would be an internal error to the application because you cannot really control this.

**Device Not Found**

This error message states that the netlist [device](24-Netlist.md#sub:device) line in the [Netlist](24-Netlist.md#sec:Netlist), defining one of the [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices) was formed incorrectly and that the device name specified is unknown. This would be an internal error to the application because you cannot really control this.

## PostProcessing {#sub:PostProcessing}

**not understood**

A [Post-Processing](25-Post-Processing.md#sec:Post-Processing) command (a [Netlist](24-Netlist.md#sec:Netlist) line preceded by the keyword [post](24-Netlist.md#sub:post)) is not understood or cannot be parsed.

