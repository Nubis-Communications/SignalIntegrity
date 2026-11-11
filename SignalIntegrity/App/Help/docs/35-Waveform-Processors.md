# Waveform Processors {#sec:Waveform-Processors}

A waveform processor is a simulation device that transforms measured circuit
# Waveform Processors {#sec:Waveform-Processors}

A waveform processor is a simulation device that transforms measured circuit
waveforms and uses the transformed waveforms as sources on subsequent processing
iterations. It is an application-level device, not a standalone component in
`SignalIntegrity.Lib`.

## Add a Processor

Choose **Waveform Processor** from the Add Part picker for a new processor with
one input and one output. Use **Waveform Processor Python Script** to choose a
`.py` file and create a processor whose ports and variables are declared in that
script's interface block. In either case, the script text is embedded in the
project; the project does not depend on the selected script file remaining at
its original path.

The processor symbol places input pins down its left side and output pins down
its right side. Port counts are at least one. Changing counts preserves the
device's position and orientation.

## Script Editor

Open the device properties and choose **Edit Script**, or right-click a writable
processor in the schematic and choose **Edit Script**. The editor's **File** menu
has two commands:

- **Import…** replaces the editor contents with a Python file. This only changes
  the script text in the current properties dialog.
- **Save As…** writes the current editor contents to a `.py` file. The processor
  continues to store the script in the project; Save As does not link the device
  to the exported file.

The **Debug** menu can execute the script with example input waveforms or run it
automatically as it is edited. When the editor is opened from device properties,
changes are committed to the schematic when **OK** is pressed and discarded when
**Cancel** is pressed.

## Script Interface

The simulator supplies sampled input waveforms in pin order as
`input_waveform_1`, `input_waveform_2`, and so on. The generated probe labels,
such as `WFP1_in1`, are also available as local variables. Device variables are
available by name; `int` and `float` values are passed as numbers, while `string`,
`enum`, and `file` values are passed as strings. A value beginning with `=` is
resolved from the schematic variables. `iteration` is the zero-based index of
the waveform pass that has just completed; a device variable named
`iteration` overrides it.

Assign every processor output using `output_waveform_1`, `output_waveform_2`,
and so on. Values should be `Waveform` objects or compatible results from
waveform operations. For example, a two-input, two-output processor might use:

```python
output_waveform_1 = (input_waveform_1 - input_waveform_2) * gain
output_waveform_2 = input_waveform_1 * gain
```

The same script is evaluated for each dependent output waveform on each
iteration. Keep transforms free of side effects, and assign all declared outputs
on every run.

Scripts run with Python `exec` and are not sandboxed. The active project folder
is added to Python's import path, so a script can import a trusted helper module
stored beside the project. Only run scripts you trust.

## Interface Metadata

The comment-delimited metadata block describes the processor interface. Each
line inside the block must remain a Python comment, so the script can be executed
normally:

```python
# <waveform-processor-interface>
# {
#   "version": 1,
#   "ports": {"inputs": 2, "outputs": 1},
#   "variables": [
#     {
#       "name": "gain",
#       "description": "Linear voltage gain",
#       "type": "float",
#       "default": 0.9,
#       "units": "V/V",
#       "visible": true,
#       "read_only": false,
#       "in_cache": true
#     }
#   ]
# }
# </waveform-processor-interface>
# Python script follows the metadata block.
output_waveform_1 = input_waveform_1 * gain
```

The block must occur once and declare `version` 1, positive integer input and
output counts, and a `variables` list. Every variable requires `name`, `type`,
and `default`. Names must be unique Python identifiers. Supported types are
`int`, `float`, `string`, `enum`, and `file`. Optional fields are `description`,
`units`, `visible`, `read_only`, and `in_cache`. The default becomes the initial
value when a processor is created from the script.

## Import Variables

In the processor's **Variables** dialog, choose **Import from Script** to apply
the interface block in the current script. The application validates the full
block before changing anything, then updates the input and output port counts,
the device picture, and the variable definitions together. Invalid or missing
metadata leaves the device unchanged and reports an error.

When importing into an existing processor, definitions are refreshed by name.
The current value is preserved when a variable has the same name and type; new
variables receive their declared defaults. Variables no longer declared by the
script are removed only after confirmation. The port and variable changes are
part of the device-properties working copy: **OK** commits them to the schematic,
while **Cancel** discards them.

The **Waveform Processor Python Script** picker uses this same metadata parser
when creating a device from a `.py` file. A missing or invalid block prevents
creation, rather than creating a partially configured processor.

## Results And Linearization

When `show` is true, the processor's generated outputs appear in the simulation's
`other waveform labels` and `other waveforms` results, named `REF_out1`,
`REF_out2`, and so on. They are also available in the Simulator waveform plot.
They remain separate from circuit output probes and do not change transfer
matrices.

For transfer matrices and statistical-noise calculations, variable-port
processors are linearized as a unity-gain path from input 1 to output 1. Later
inputs and outputs are ignored in that view; the iterative waveform solver
still uses the full processor and all its ports.

Each processor stores its Python code in the project's `script` property.
`inputports` and `outputports` define the script interface.