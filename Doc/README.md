# SignalIntegrity Software Documentation

## Usage
SignalIntegrity comes with a library called _SignalIntegrity.Lib_.  From within your scripts, you type:

    import SignalIntegrity.Lib as si

Then, all of the elements from within SignalIntegrity are accessible using si as the prefix.  For example, the single frequency s-parameters of a current amplifier are found by calling the function:

    si.dev.CurrentAmplifier()

All of the namespaces for these packages are listed at [Packages](http://nubis-communications.github.io/SignalIntegrity/Doc/xhtml/namespaces.xhtml).

All of the classes available to you are located at [Class List](http://nubis-communications.github.io/SignalIntegrity/Doc/xhtml/annotated.xhtml) along with the [Class Hierarchy](http://nubis-communications.github.io/SignalIntegrity/Doc/xhtml/inherits.xhtml).

The table of codes corresponding to each namespace is:

code | namespace | Description
:--- | :--- | :---
si | SignalIntegrity.Lib | Top of SignalIntegrity.Lib Package
si.czt | SignalIntegrity.Lib.ChirpZTransform | Chirp z transform
si.cvt | SignalIntegrity.Lib.Conversions | Conversion Formulas
si.dev | SignalIntegrity.Lib.Devices | Single Frequency Devices
si.eye | SignalIntegrity.Lib.Eye | Eye Diagram Generation and Processing
si.fit | SignalIntegrity.Lib.Fit | Fitting Algorithms
si.fd | SignalIntegrity.Lib.FrequencyDomain | Frequency Domain
si.helper | SignalIntegrity.Lib.Helper | Helper functions and classes
si.ip | SignalIntegrity.Lib.ImpedanceProfile | Impedance profile
si.m | SignalIntegrity.Lib.Measurement | Measurment
si.m.cal | SignalIntegrity.Lib.Measurement.Calibration | Calibration algorithms
si.m.calkit | SignalIntegrity.Lib.Measurement.CalKit | Calibration kits
si.m.tdr | SignalIntegrity.Lib.Measurement.TDR | Time-domain reflectometry
si.p | SignalIntegrity.Lib.Parsers | Netlist parsers
si.p.dev | SignalIntegrity.Lib.Parsers.Devices | Netlist parser devices
si.prbs | SignalIntegrity.Lib.Prbs | Pseudo-random polynomials and waveforms
si.rat | SignalIntegrity.Lib.Rat | The RAT function
si.sp | SignalIntegrity.Lib.SParameters | S-parameters
si.sp.dev | SignalIntegrity.Lib.SParameters.Devices | S-parameter devices
si.spl | SignalIntegrity.Lib.Splines | Spline functions
si.sub | SignalIntegrity.Lib.SubCircuits | Netlist Subcircuits
si.sy | SignalIntegrity.Lib.Symbolic | Symbolic Solutions
si.sd | SignalIntegrity.Lib.SystemDescriptions | System descriptions
si.test | SignalIntegrity.Lib.Test | Test helpers
si.td | SignalIntegrity.Lib.TimeDomain | Time-domain
si.td.f | SignalIntegrity.Lib.TimeDomain.Filters | Filters
si.td.wf | SignalIntegrity.Lib.TimeDomain.Waveform | Waveforms
si.wl | SignalIntegrity.Lib.Wavelets | Wavelets


## Building the Package Documentation
The package documentation is generated using a tool called [Doxygen](http://www.doxygen.nl/).
Unfortunately, Doxygen is a tool made for C++ and Java and is not perfect for Python.  I chose it originally because it is capable of creating [LaTeX](https://www.latex-project.org/) documentation that was originally intended with my book - that idea was abandoned.  But still, it produces a very good documentation system.

When properly set up, it is invoked from the [Doc](https://github.com/Nubis-Communications/SignalIntegrity/tree/master/Doc) directory using:

    doxygen SignalIntegrityWindows


or:


    doxygen SignalIntegrityLinux


depending on which platform you're on.

This uses the configuration provided in the [SignalIntegrityWindows](https://github.com/Nubis-Communications/SignalIntegrity/tree/master/Doc/SignalIntegrityWindows) or [SignalIntegrityLinux](https://github.com/Nubis-Communications/SignalIntegrity/tree/master/Doc/SignalIntegrityLinux) configuration file and creates a directory called xhtml with the web documentation.  Both need to use a hack of [doxypy.py](https://github.com/Nubis-Communications/SignalIntegrity/tree/master/Doc/doxypy.py) that strips the triple quoted header required at the top of each Python file prior to processing.  This filter is specified in the [SignalIntegrityLinux](https://github.com/Nubis-Communications/SignalIntegrity/tree/master/Doc/SignalIntegrityLinux) as:

    # The INPUT_FILTER tag can be used to specify a program that doxygen should
    # invoke to filter for each input file. Doxygen will invoke the filter program
    # by executing (via popen()) the command:
    #
    # <filter> <input-file>
    #
    # where <filter> is the value of the INPUT_FILTER tag, and <input-file> is the
    # name of an input file. Doxygen will then use the output that the filter
    # program writes to standard output. If FILTER_PATTERNS is specified, this tag
    # will be ignored.
    #
    # Note that the filter must not add or remove lines; it is applied before the
    # code is scanned, but not when the output code is generated. If lines are added
    # or removed, the anchors will not be placed correctly.
    #
    # Note that for custom extensions or not directly supported extensions you also
    # need to set EXTENSION_MAPPING for the extension otherwise the files are not
    # properly processed by doxygen.
    
    INPUT_FILTER           = ./doxypy.py

Usually, Doxygen can find the hacked doxypy.py in the /SignalIntegrity/Doc/ directory - if it can't you might need to specify the path to this file directly.

In [SignalIntegrityWindows](https://github.com/Nubis-Communications/SignalIntegrity/tree/master/Doc/SignalIntegrityWindows) this needs to be specified as:

    INPUT_FILTER           = doxypy.bat

Which uses the local [doxypy.bat](https://github.com/Nubis-Communications/SignalIntegrity/tree/master/Doc/doxypy.bat), which simply calls the input filter file.

In order to render any equations in the documentation, you must have [GhostScript](https://www.ghostscript.com/download/gsdnld.html) installed.

Currently package documentation is modified only the branch gh-pages.  In other words, you should have another repository checked out on the gh-pages branch, generate this documentation, copy it to the gh-pages repository directory and check it in on gh-pages.
