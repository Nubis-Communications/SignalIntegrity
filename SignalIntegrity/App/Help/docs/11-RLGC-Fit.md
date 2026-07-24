# RLGC Fit {#sec:RLGC-Fit}

This calculates the s-parameters of a [COM Transmission Line](23-Built-in-Devices-Parts.md#device:Transmission-Line-COM) device fitted to the s-parameters of the schematic.

When invoked, the system will:

- Calculate the s-parameters of the schematic (see [S-Parameter Generation](07-S-Parameter-Generation.md#sec:S-parameter-Generation)).

- Fit the [COM Transmission Line](23-Built-in-Devices-Parts.md#device:Transmission-Line-COM) device to the s-parameters.

- Open the [S-parameter Viewer](13-S-parameter-Viewer.md#sec:S-parameter-Viewer) showing the s-parameters of the resulting device.

- Place the [COM Transmission Line](23-Built-in-Devices-Parts.md#device:Transmission-Line-COM) device on the clipboard.

With the fitted device on the clipboard, pressing the right mouse button anywhere on the schematic will place the new device.

The fit is performed iteratively using the Levenberg-Marquardt algorithm. The fit progress is shown in the status message area, which shows the iteration number and the mean-squared error. Convergence is determined automatically.

Devices that fit automatically can be placed in the schematic using the [RLGC Fit](23-Built-in-Devices-Parts.md#device:RLGC-Fit) device.

