# PySI Software Documentation

## Usage
PySI comes with a top-level Python package called _SignalIntegrity_.  From within your scripts, you type:

    import SignalIntegrity as si

Then, all of the elements from within SignalIntegrity are accessible using si as the prefix.  For example, the single frequency s-parameters of a current amplifier are found by call ing the function:

    si.d.CurrentAmplifier()

All of the namespaces for these packages are listed at [Packages](http://teledynelecroy.github.io/PySI/Doc/xhtml/namespaces.xhtml).

All of the classes available to you are located at [Class List](http://teledynelecroy.github.io/PySI/Doc/xhtml/annotated.xhtml) along with the [Class Hierarchy](http://teledynelecroy.github.io/PySI/Doc/xhtml/inherits.xhtml).

The table of codes corresponding to each namespace is:

code | namespace | Description
:--- | :--- | :---
si | SignalIntegrity | Top of SignalIntegrity Package
si.czt | SignalIntegrity.ChirpZTransform | Chirp z transform
si.cvt | SignalIntegrity.Conversions | Conversion Formulas
si.d | SignalIntegrity.Devices | Single Frequency Devices
si.fit | SignalIntegrity.Fit | Fitting Algorithms
si.fd | SignalIntegrity.FrequencyDomain | Frequency Domain
si.helper | SignalIntegrity.Helper | Helper functions and classes
si.ip | SignalIntegrity.ImpedanceProfile | Impedance profile
si.m | SignalIntegrity.Measurement | Measurment
si.m.cal | SignalIntegrity.Measurement.Calibration | Calibration algorithms
si.m.calkit | SignalIntegrity.Measurement.CalKit | Calibration kits
si.m.tdr | SignalIntegrity.Measurement.TDR | Time-domain reflectometry
si.p | SignalIntegrity.Parsers | Netlist parsers
si.p.dev | SignalIntegrity.Parsers.Devices | Netlist parser devices
si.rat | SignalIntegrity.Rat | The RAT function
si.sp | SignalIntegrity.SParameters | S-parameters
si.sp.dev | SignalIntegrity.SParameters.Devices | S-parameter devices
si.spl | SignalIntegrity.Splines | Spline functions
si.sub | SignalIntegrity.SubCircuits | Netlist Subcircuits
si.sy | SignalIntegrity.Symbolic | Symbolic Solutions
si.sd | SignalIntegrity.SystemDescriptions | System descriptions
si.test | SignalIntegrity.Test | Test helpers
si.td | SignalIntegrity.TimeDomain | Time-domain
si.td.f | SignalIntegrity.TimeDomain.Filters | Filters
si.td.wf | SignalIntegrity.TimeDomain.Waveform | Waveforms
si.wl | SignalIntegrity.Wavelets | Wavelets


