# Scripting SignalIntegrity {#sec:Scripting-SignalIntegrity}

Everything that ***SignalIntegrityApp*** calculates can also be calculated from a Python script, without the graphical user interface. This is called running *SignalIntegrity* headless. A typical use is to draw and debug a schematic interactively, save it as a project, and then calculate it from a script: sweeping its variables, running it as part of an automated flow, or collecting its results for further processing.

Headless calculation is provided by the class `SignalIntegrityAppHeadless`. It opens the same project files as ***SignalIntegrityApp***, applies arguments to the project's [Schematic Variables](15-Main-Schematic-Dialog.md#Control-Help:Schematic-Variables) and [Calculation Properties](15-Main-Schematic-Dialog.md#Control-Help:Calculation-Properties), performs the calculation, and returns a [result dictionary](34-Scripting-SignalIntegrity.md#sub:Scripting-Results) containing the waveforms, s-parameters, and other results that the graphical application would display.

## Getting Started {#sub:Scripting-Getting-Started}

The following script opens the RC example project that is installed with *SignalIntegrity*, simulates it, and writes the output waveform named Vout to a file:

```python
import os
import SignalIntegrity.App
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless

project = os.path.join(os.path.dirname(SignalIntegrity.App.__file__), 'Examples', 'RC.si')
output = os.path.abspath('Vout.txt')  # before opening the project, which changes the working directory

app = SignalIntegrityAppHeadless()
if not app.OpenProjectFile(project):
    raise RuntimeError('could not open ' + project)

result = app.Simulate()
if not result:
    raise RuntimeError('the simulation failed')

vout = result.OutputWaveform('Vout')
print(vout.td.H, vout.td.K, vout.td.Fs)  # time of the first point, number of points, sample rate
vout.WriteToFile(output)
```

The steps are always the same:

1. Create a `SignalIntegrityAppHeadless`.

2. Open a project with [OpenProjectFile](34-Scripting-SignalIntegrity.md#sub:Scripting-Opening-a-Project), optionally passing [Arguments](34-Scripting-SignalIntegrity.md#sub:Scripting-Arguments).

3. Perform the calculation that the project is drawn for (see [Calculating](34-Scripting-SignalIntegrity.md#sub:Scripting-Calculating)).

4. Check that the result is not empty and use its contents (see [Results](34-Scripting-SignalIntegrity.md#sub:Scripting-Results)).

The objects in the results (waveforms, s-parameters, transfer matrices, and so on) are classes of the *SignalIntegrity* library, which is normally imported as:

```python
import SignalIntegrity.Lib as si
```

## The Headless Application {#sub:Scripting-Headless-Application}

`SignalIntegrityAppHeadless()` takes no arguments. Creating one reads the [Preferences](29-Preferences.md#sec:Preferences) (see [Preferences and Caching](34-Scripting-SignalIntegrity.md#sub:Scripting-Preferences)).

The open project is held globally in `SignalIntegrity.App.Project`, so only one project is open at a time. Opening a project, in this or another `SignalIntegrityAppHeadless`, replaces the project that was open. To calculate other projects from within a script while keeping the current one, use the [Project Functions](34-Scripting-SignalIntegrity.md#sub:Scripting-Project-Functions), which save and restore the current project.

The methods of `SignalIntegrityAppHeadless` are:

| Method | Description |
|:---|:---|
| `OpenProjectFile(filename, args={}, writable=False)` | opens a project, applying the arguments. See [Opening a Project](34-Scripting-SignalIntegrity.md#sub:Scripting-Opening-a-Project). |
| `SetVariables(args, reportMissing=False)` | applies arguments to the open project. See [Arguments](34-Scripting-SignalIntegrity.md#sub:Scripting-Arguments). |
| `Simulate(callback=None, TransferMatricesOnly=False, EyeDiagrams=False)` | performs a [Simulation](08-Simulation.md#sec:Simulation). |
| `TransferParameters(callback=None)` | calculates only the transfer matrices of a simulation or virtual probe project. |
| `VirtualProbe(callback=None, TransferMatricesOnly=False, EyeDiagrams=False)` | performs [Virtual Probing](10-Virtual-Probing.md#sec:Virtual-Probing). |
| `CalculateSParameters(callback=None, calculate_impedance_profiles=False)` | performs [S-Parameter Generation](07-S-Parameter-Generation.md#sec:S-parameter-Generation). |
| `Deembed(callback=None)` | performs [Deembedding](09-Deembedding.md#sec:Deembedding). |
| `CalculateErrorTerms(callback=None)` | calculates the calibration error terms of a [Network Analyzer Measurements](12-Network-Analyzer-Measurements.md#sec:Network-Analyzer-Measurements) calibration project. |
| `SimulateNetworkAnalyzerModel(callback=None, SParameters=False)` | simulates a network analyzer model project. |
| `Device(ref)` | returns the part with the reference designator ref, or None. See [Changing Parts](34-Scripting-SignalIntegrity.md#sub:Scripting-Changing-Parts). |
| `NetListText()` | returns the [Netlist](24-Netlist.md#sec:Netlist) of the schematic as a list of strings. |
| `SaveProject()`, `SaveProjectToFile(filename)` | save the project, only when it was opened writable. |
| `ReadOnly()` | returns whether the project was opened read-only. |
| `Archive(...)`, `ExtractArchive(...)`, `FreshenArchive()`, `UnExtractArchive()` | archive functions. See [Archives and Regression](34-Scripting-SignalIntegrity.md#sub:Scripting-Archives-and-Regression). |
| `GenerateRegression(...)`, `RunRegression(...)` | regression functions. See [Archives and Regression](34-Scripting-SignalIntegrity.md#sub:Scripting-Archives-and-Regression). |

## Opening a Project {#sub:Scripting-Opening-a-Project}

```python
ok = app.OpenProjectFile(filename, args={}, writable=False)
```

- filename – the project file name. The extension .si is assumed.

- args – (optional) a dictionary of [Arguments](34-Scripting-SignalIntegrity.md#sub:Scripting-Arguments) applied to the project after it is read.

- writable – (optional, defaults to False) whether the project can be saved. A project opened read-only (the default) is never written; SaveProject and SaveProjectToFile do nothing.

OpenProjectFile returns True if the project was opened and False otherwise (for example, if the file does not exist).

Opening a project changes the current working directory to the directory containing the project. This is how files referenced by the project with relative paths are found. As a consequence:

- relative file names used by the script after the project is opened are relative to the project's directory, so a script that writes results should determine the absolute paths of its output files before opening the project, and

- the script must not change the working directory between opening a project and calculating it, or the files the project references with relative paths will not be found and the calculation will fail.

## Arguments {#sub:Scripting-Arguments}

Arguments are a dictionary of names and values. Each name is matched against the project in the following order:

1. If the name is a [Schematic Variable](15-Main-Schematic-Dialog.md#Control-Help:Schematic-Variables), the variable's value is set to the value supplied.

2. Otherwise, if the name is a calculation property (see below), the property is set to the value supplied.

3. Otherwise, the argument is ignored and, when the arguments are applied by OpenProjectFile, the message variable *name* not in project is printed.

Arguments are how a project is parameterized for scripting. Any part property in the schematic whose value is = followed by a variable name takes its value from that variable (see [Parameterize Schematic](15-Main-Schematic-Dialog.md#Control-Help:Parameterize-Project)), so passing that variable as an argument changes the part. These are the same arguments that a parent project passes to a project used as a part, such as a project used as the file of a [Voltage Source](23-Built-in-Devices-Parts.md#device:Voltage-Source).

Values can be given as numbers or as strings. A float variable given as a string must be written without units (for example '1e-9', not '1 ns').

The calculation properties that can be set as arguments are:

| Name | Description |
|:---|:---|
| EndFrequency | the end frequency (Hz) |
| FrequencyPoints | the number of frequency points |
| UserSampleRate | the sample rate of the output waveforms (S/s) |
| ReferenceImpedance | the reference impedance of s-parameter calculations (ohms) |
| UnderlyingType | the frequency list type, Linear or Logarithmic |
| LogarithmicStartFrequency, LogarithmicEndFrequency, LogarithmicPointsPerDecade | the logarithmic frequency list, when UnderlyingType is Logarithmic |
| TimeBeforeZeroMode, TimeBeforeZeroSpecified | the time before zero of simulated waveforms |
| AllowParallelization | whether the calculation may be performed in parallel (see [Parallel Calculations](32-Parallel-Calculations.md#sec:Parallel-Calculations)) |
| LimitImpulseResponseLength, MaximumImpulseResponseLength | the limit on the impulse response length |

The remaining calculation properties (BaseSampleRate, BaseSamplePeriod, UserSamplePeriod, TimePoints, FrequencyResolution, and ImpulseResponseLength) are always recalculated from these after the arguments are applied, so there is no point in passing them. See [Calculation Properties](15-Main-Schematic-Dialog.md#Control-Help:Calculation-Properties) for the meaning of each property.

For example, to simulate a project with the schematic variable amplitude set to 2 and an end frequency of 10 GHz:

```python
app = SignalIntegrityAppHeadless()
app.OpenProjectFile('MyProject.si', {'amplitude': 2.0, 'EndFrequency': 10e9})
result = app.Simulate()
```

Arguments can also be applied to a project that is already open:

```python
app.SetVariables({'amplitude': 3.0}, reportMissing=True)
app.Drawing.DrawSchematic()
result = app.Simulate()
```

SetVariables only prints the message for unknown names when reportMissing is True.

### Equations {#sub:Scripting-Equations}

If the project has [Equations](26-Equations.md#sec:Equations), they are run when the schematic is drawn, which happens automatically before the first calculation. The equations use the variables as set by the arguments and set any output variables. If the equations fail, every calculation returns an empty result.

After changing variables or parts of a project that has already been calculated, call app.Drawing.DrawSchematic() before calculating again so that the equations are run with the new values. Alternatively, open the project again with the new arguments, which always starts from the project as saved.

### Changing Parts {#sub:Scripting-Changing-Parts}

Parts can also be changed directly. Device returns the part with the given reference designator, and its properties are accessed by keyword (the keywords are listed for each part in [Built-in Devices (Parts)](23-Built-in-Devices-Parts.md#sec:Built-in-Devices)):

```python
resistor = app.Device('R1')
print(resistor['r'].GetValue())       # the value, in the property's units
resistor['r'].SetValueFromString('100')
result = app.Simulate()
```

SetValueFromString accepts the value as it would be typed in the [Edit Properties](15-Main-Schematic-Dialog.md#Control-Help:Edit-Properties) dialog, including = followed by a variable name. The change is to the open project only; it is saved only if the project was opened writable and is saved.

## Calculating {#sub:Scripting-Calculating}

A project is drawn for a particular kind of calculation, determined by the parts it contains, in the same way that ***SignalIntegrityApp*** enables only certain calculations for a schematic. After app.Drawing.DrawSchematic() has been called (each calculation calls it if it has not been), the following flags of app.Drawing indicate which calculations are possible:

| Flag | Calculation |
|:---|:---|
| canSimulate | Simulate |
| canGenerateTransferMatrices | TransferParameters |
| canVirtualProbe | VirtualProbe |
| canCalculateSParameters | CalculateSParameters |
| canDeembed | Deembed |
| canCalculateErrorTerms | CalculateErrorTerms |
| canSimulateNetworkAnalyzerModel | SimulateNetworkAnalyzerModel, and CalculateSParameters |

Calling a calculation that the project is not drawn for returns an empty result, except that Simulate on a network analyzer model project performs SimulateNetworkAnalyzerModel and returns its result.

The calculations and their arguments are:

- `Simulate(callback=None, TransferMatricesOnly=False, EyeDiagrams=False)` – simulates the project. If TransferMatricesOnly is True, only the transfer matrices are calculated, and the result contains no waveforms. If EyeDiagrams is True, the eye diagrams of the eye probes and eye waveforms whose eye diagrams are turned on are also calculated.

- `TransferParameters(callback=None)` – calculates only the transfer matrices of a simulation or virtual probe project.

- `VirtualProbe(callback=None, TransferMatricesOnly=False, EyeDiagrams=False)` – performs virtual probing. TransferMatricesOnly is as for Simulate. If EyeDiagrams is True, the eye diagrams of the eye probes whose eye diagrams are turned on are also calculated.

- `CalculateSParameters(callback=None, calculate_impedance_profiles=False)` – calculates the s-parameters of the project. If calculate_impedance_profiles is True, the impedance profile of each port is also calculated. For a network analyzer model project, this calculates the s-parameters that the modeled network analyzer would measure.

- `Deembed(callback=None)` – calculates the s-parameters of each unknown device.

- `CalculateErrorTerms(callback=None)` – calculates the calibration error terms.

- `SimulateNetworkAnalyzerModel(callback=None, SParameters=False)` – simulates the network analyzer model, producing the waveforms at the network analyzer's receivers, or, if SParameters is True, the s-parameters that the modeled network analyzer would measure.

### Callbacks {#sub:Scripting-Callbacks}

Every calculation takes an optional callback function, which is called periodically during the calculation to report progress and to give the opportunity to abort. It is called with the progress in percent as its first argument and, in some cases, a message as its second argument (for example, the name of a sub-project or eye diagram being calculated), so it should be written to accept an optional second argument. It must return True for the calculation to continue; returning False aborts the calculation, which then returns an empty result.

```python
def progress(percent, message=None):
    if message is not None:
        print(message)
    print('%5.1f%%' % percent, end='\r')
    return True

result = app.Simulate(callback=progress)
```

## Results {#sub:Scripting-Results}

Each calculation returns a result dictionary (an instance of `SignalIntegrity.App.Result.Result`, which is a Python dict). If the calculation could not be performed, the dictionary is empty, so a result is tested with:

```python
result = app.Simulate()
if not result:
    print('the simulation failed')
```

A calculation fails if the project is not drawn for it, if its equations fail, if a part cannot be calculated (for example, because a file it references cannot be read, or a [Scripted Source](23-Built-in-Devices-Parts.md#device:Voltage-Scripted-Source) script raises an error), or if it is aborted by the callback. Unlike ***SignalIntegrityApp***, the headless application does not report why a calculation failed; opening the project in ***SignalIntegrityApp*** and performing the same calculation shows the error.

Every non-empty result contains:

| Key | Contents |
|:---|:---|
| type | the type of result: simulation, virtual probe, s-parameters, de-embed, error terms, or network analyzer |
| variables | a dictionary of the [Schematic Variables](15-Main-Schematic-Dialog.md#Control-Help:Schematic-Variables) by name, with their values after the calculation, including output variables set by the [Equations](26-Equations.md#sec:Equations). It is empty if the project has no variables. |

The other contents depend on the type of result, as described below.

The result dictionary also provides the following methods:

| Method | Returns |
|:---|:---|
| `OutputWaveform(name)` | the output waveform named name (`si.td.wf.Waveform`) |
| `FrequencyResponse(from_name, to_name)` | the frequency response from the source named from_name to the output named to_name (`si.fd.FrequencyResponse`) |
| `EyeDiagram(name)` | the eye diagram named name |
| `Legacy()` | the results as a tuple, in the form returned by older versions of *SignalIntegrity*. This is deprecated. |

### Simulation and Virtual Probe Results {#sub:Scripting-Simulation-Results}

Simulate returns a result of type simulation, and VirtualProbe returns a result of type virtual probe; TransferParameters returns the type of the project it calculates. These results contain:

| Key | Contents |
|:---|:---|
| source names | list of the names of the sources: the reference designators of the sources and generators in a simulation, or of the voltage measure probes in a virtual probe project |
| output waveform labels | list of the names of the output waveforms (see below) |
| transfer matrices | the transfer matrices (`si.fd.TransferMatrices`), relating each source to each output probe |
| output waveforms | list of the output waveforms (`si.td.wf.Waveform`), in the order of output waveform labels. Not present when only the transfer matrices are calculated. |
| noise | (simulation only) the [Statistical Noise Results](34-Scripting-SignalIntegrity.md#sub:Scripting-Noise-Results). Not present when only the transfer matrices are calculated. |
| eye diagram labels | (only when eye diagrams are calculated) list of the names of the eye diagrams |
| eye diagrams | (only when eye diagrams are calculated) list of the [eye diagrams](34-Scripting-SignalIntegrity.md#sub:Scripting-Eye-Diagram-Results), in the order of eye diagram labels |

The output waveform labels are the reference designators of the output probes, in the order of the outputs of the transfer matrices, followed by the names of any [Waveform](23-Built-in-Devices-Parts.md#device:Waveform) parts, followed by the reference designators of any sources whose show property is true. The waveforms of sources that are shown are the waveforms the sources produce. Only the output probes have rows in the transfer matrices, so the transfer matrices may have fewer outputs than there are output waveform labels.

The output waveforms are produced as they are displayed in the [Simulator Dialog](14-Simulator-Dialog.md#sec:Simulator-Dialog): the gain, offset, delay, and AC coupling of each output probe are applied, and the waveforms of the output probes are at the UserSampleRate of the [Calculation Properties](15-Main-Schematic-Dialog.md#Control-Help:Calculation-Properties).

For example, the RC example of [Getting Started](34-Scripting-SignalIntegrity.md#sub:Scripting-Getting-Started) has one source and two output probes:

```python
result = app.Simulate()
print(result['source names'])              # ['VG1']
print(result['output waveform labels'])    # ['Vin', 'Vout']
fr = result.FrequencyResponse('VG1', 'Vout')
print(fr.Frequencies()[1], fr.Values('dB')[1])
```

### S-parameter Results {#sub:Scripting-SParameter-Results}

CalculateSParameters returns a result of type s-parameters, containing:

| Key | Contents |
|:---|:---|
| s-parameters | the s-parameters (`si.sp.SParameters`) |
| file names | the file name that ***SignalIntegrityApp*** would save the s-parameters to: the project name with the extension .s*P*p, where *P* is the number of ports |
| impedance profiles | (only when calculate_impedance_profiles is True) list of the impedance profile of each port (`si.ip.ImpedanceProfileWaveform`); element *p* is for port *p*+1 |

The s-parameters are not written to a file by the calculation. To write them:

```python
result = app.CalculateSParameters()
result['s-parameters'].WriteToFile(result['file names'])
```

### De-embedding Results {#sub:Scripting-Deembedding-Results}

Deembed returns a result of type de-embed, containing:

| Key | Contents |
|:---|:---|
| unknown names | list of the reference designators of the unknown devices |
| s-parameters | list of the de-embedded s-parameters (`si.sp.SParameters`) of each unknown device, in the order of unknown names. This is a list even when there is one unknown device. |
| file names | list of the file names that ***SignalIntegrityApp*** would save the s-parameters of each unknown device to, in the order of unknown names: the project name, an underscore, and the unknown device's reference designator, with the extension .s*P*p |

### Error Terms Results {#sub:Scripting-Error-Terms-Results}

CalculateErrorTerms returns a result of type error terms, containing:

| Key | Contents |
|:---|:---|
| error terms | the calibration (`si.m.cal.Calibration`) |
| file names | the file name that ***SignalIntegrityApp*** would save the calibration to: the project name with the extension .cal |

### Network Analyzer Results {#sub:Scripting-Network-Analyzer-Results}

SimulateNetworkAnalyzerModel returns a result of type network analyzer. When SParameters is False, it contains the source names, output waveform labels, transfer matrices, and output waveforms, as for a [simulation](34-Scripting-SignalIntegrity.md#sub:Scripting-Simulation-Results), with the output waveform labels naming each receiver waveform and the driven port. When SParameters is True, it contains:

| Key | Contents |
|:---|:---|
| s-parameters | the s-parameters that the modeled network analyzer would measure (`si.sp.SParameters`) |

CalculateSParameters on a network analyzer model project returns these s-parameters as a result of type s-parameters.

### Statistical Noise Results {#sub:Scripting-Noise-Results}

The noise entry of a simulation result contains the results of the [Statistical Noise Analysis](31-Statistical-Noise-Dialog.md#sub:Statistical-Noise-Analysis). It is an empty dictionary when the project has no enabled statistical noise sources. Otherwise, it is a dictionary containing:

| Key | Contents |
|:---|:---|
| output_names | list of the names of the outputs included in the noise analysis |
| noise_display_output_names | list of the names of the outputs whose *include in noise* property is set; these are the outputs shown in the [Statistical Noise Dialog](31-Statistical-Noise-Dialog.md#sec:Statistical-Noise-Dialog) |
| input_names | list of the names of the statistical noise sources |
| output_types, input_types | dictionaries giving, for each output and each noise source, whether it is a voltage or a current |
| transfer_matrices | the transfer matrices from the noise sources to the outputs (`si.fd.TransferMatrices`) |
| input_noise_spectral_density | dictionary, by noise source name, of the noise produced by each noise source |
| output_noise_spectral_density | dictionary, by output name, of the total noise at each output |
| signal_noise_spectral_density | dictionary, by output name, of the signal at each output |
| signal_to_noise_ratio | dictionary, by output name, of a dictionary containing SNR and SalzSNR (dB) |
| contributions | dictionary, by output name, of a dictionary, by noise source name, of the noise contributed by each noise source to each output |
| input_noise_spectral_density_list, output_noise_spectral_density_list, signal_noise_spectral_density_list | the spectra of the corresponding dictionaries, as lists in the order of input_names or output_names |

Each entry of the spectral density dictionaries is a dictionary containing:

| Key | Contents |
|:---|:---|
| spectrum | the spectral density (`si.fd.SpectralDensity`) |
| type | voltage or current |
| rms | the total rms value (V or A) |
| dBm | the total power (dBm) |
| rms/sqrt(Hz), rms/sqrt(GHz), dBm/Hz, dBm/GHz | (output_noise_spectral_density only) the average noise density |
| SNR, SalzSNR | (contributions only) the signal-to-noise ratio (dB) at the output if this noise source were the only noise |

These are the values shown in the [Statistical Noise Measurements](31-Statistical-Noise-Dialog.md#sub:Statistical-Noise-Measurements). For example:

```python
noise = result['noise']
for output in noise['noise_display_output_names']:
    print(output, noise['output_noise_spectral_density'][output]['rms'],
          noise['signal_to_noise_ratio'][output]['SNR'])
```

The noise analysis is performed by headless simulations regardless of the [Features.StatisticalNoise](29-Preferences.md#sec:Preferences) preference.

### Eye Diagram Results {#sub:Scripting-Eye-Diagram-Results}

When Simulate or VirtualProbe is called with EyeDiagrams=True, each eye diagram in the result provides:

| Method | Returns |
|:---|:---|
| `Measurements()` | a dictionary of the eye diagram measurements, as shown in the [Eye Diagram Measurements Dialog](18-Eye-Diagram-Measurements-Dialog.md#sec:Eye-Diagram-Measurements-Dialog), or None if measurements are not enabled in the [Eye Diagram Properties](21-Eye-Diagram-Properties-Dialog.md#sec:Eye-Diagram-Properties-Dialog) of the eye probe |
| `Image()` | the eye diagram image (a PIL Image), which can be saved with its save method |
| `BitMap()` | the raw eye diagram bitmap (a numpy array) |

The measurements dictionary contains entries such as Eye, Level, Linearity, RLM, Noise, SNR, Bathtub, and Probabilities, depending on the measurements enabled in the [Eye Diagram Properties](21-Eye-Diagram-Properties-Dialog.md#sec:Eye-Diagram-Properties-Dialog) of the eye probe. For example:

```python
outputDirectory = os.path.abspath('Eyes')  # before opening the project
os.makedirs(outputDirectory, exist_ok=True)

app = SignalIntegrityAppHeadless()
app.OpenProjectFile('MyEyeProject.si')
result = app.Simulate(EyeDiagrams=True)
for name in result['eye diagram labels']:
    eye = result.EyeDiagram(name)
    eye.Image().save(os.path.join(outputDirectory, name + '.png'))
    measurements = eye.Measurements()
    if measurements is not None:
        print(name, list(measurements.keys()))
```

## Working With Results {#sub:Scripting-Working-With-Results}

The results are objects of the *SignalIntegrity* library. Some commonly used members are:

| Object | Members |
|:---|:---|
| `si.td.wf.Waveform` | `Times()` and `Values()` – lists of the times and values; `td.H`, `td.K`, `td.Fs` – the time of the first point, the number of points, and the sample rate; `WriteToFile(filename)` and `ReadFromFile(filename)` |
| `si.sp.SParameters` | `m_P` – the number of ports; `f()` – the frequencies; `s[n][r][c]` – the s-parameter from port *c*+1 to port *r*+1 at frequency index *n*; `FrequencyResponse(r, c)` – the frequency response from port *c* to port *r*; `WriteToFile(filename)` |
| `si.fd.TransferMatrices` | `FrequencyResponse(o, s)` – the frequency response from source *s* to output *o* (both numbered from 1); `SParameters()` – the transfer matrices as s-parameters |
| `si.fd.FrequencyResponse` | `Frequencies()` and `Values(unit)` – the frequencies and the values, where unit may be omitted or be 'dB', 'mag', or 'deg'; `ImpulseResponse()` |
| `si.fd.SpectralDensity` | `Frequencies()` and `Values()` |
| `si.m.cal.Calibration` | `WriteToFile(filename)` |

## Project Functions {#sub:Scripting-Project-Functions}

The following functions in `SignalIntegrity.App.SignalIntegrityAppHeadless` calculate a project and return a single result from it. They are what ***SignalIntegrityApp*** uses to calculate projects that are used as parts, and they are convenient in scripts that combine the results of several projects. Each saves the currently open project (and the current working directory) before opening the project, and restores them afterward, so they can be called while another project is open.

| Function | Returns |
|:---|:---|
| `ProjectWaveform(filename, wfname, callback, **args)` | the output waveform named wfname of a simulation or virtual probe project |
| `ProjectSParameters(filename, callback, **args)` | the s-parameters of an s-parameter generation or network analyzer model project, or the s-parameters of the first unknown device of a de-embedding project |
| `ProjectNoise(filename, noise_name, callback, lanes=1., **args)` | the output noise spectral density of the output named noise_name, multiplied by $\sqrt{\mathrm{lanes}}$ |
| `ProjectCalibration(filename, callback, **args)` | the calibration of a calibration project |

The arguments are passed as keyword arguments, and the callback may be None. Each function returns None if the project cannot be calculated. For example:

```python
from SignalIntegrity.App.SignalIntegrityAppHeadless import ProjectWaveform

vout = ProjectWaveform('MyProject.si', 'Vout', None, amplitude=2.0, EndFrequency=10e9)
if vout is None:
    print('the project could not be calculated')
```

## Sweeping Variables {#sub:Scripting-Sweeps}

A common use of scripting is to calculate a project for a range of values of its variables. Opening the project for each set of values ensures that each calculation starts from the project as saved:

```python
from SignalIntegrity.App.SignalIntegrityAppHeadless import SignalIntegrityAppHeadless

for resistance in [25., 50., 100.]:
    app = SignalIntegrityAppHeadless()
    if not app.OpenProjectFile('MyProject.si', {'R': resistance}):
        raise RuntimeError('could not open the project')
    result = app.Simulate()
    if not result:
        print('R =', resistance, 'failed')
        continue
    vout = result.OutputWaveform('Vout')
    print('R =', resistance, 'peak =', max(vout.Values()))
```

## Archives and Regression {#sub:Scripting-Archives-and-Regression}

The archive functions of the [Main Schematic Dialog](15-Main-Schematic-Dialog.md#sec:Main-Schematic-Dialog) are available for the open project:

| Method | Description |
|:---|:---|
| `Archive(overrideExistance=True, archiveNonRelativeFiles=None)` | creates an archive of the project, as [Archive Project](15-Main-Schematic-Dialog.md#Control-Help:Archive) does. If overrideExistance is False and the archive exists, it is not overwritten. archiveNonRelativeFiles overrides the [ProjectFiles.ArchiveNonRelativeFiles](29-Preferences.md#sub:ArchiveNonRelativeFiles) preference when it is not None. Returns True if the archive was created. |
| `ExtractArchive(filename, args={})` | extracts the archive filename, as [Extract Archived Project](15-Main-Schematic-Dialog.md#Control-Help:Extract-Archive) does, and opens the extracted project with the arguments. Returns True if the project was opened. |
| `FreshenArchive()` | as [Freshen Archived Project](15-Main-Schematic-Dialog.md#Control-Help:Freshen-Archive). Returns True on success. |
| `UnExtractArchive()` | as [Unextract Archived Project](15-Main-Schematic-Dialog.md#Control-Help:Unextract-Archive). Returns True on success. |

Regression archives record the results of a project and the projects it uses, so that later versions of the project, or of *SignalIntegrity*, can be checked against them:

| Method | Description |
|:---|:---|
| `GenerateRegression(regressionArchiveFile=None, archiveNonRelativeFiles=None, args=None, artifacts=None, callback=None)` | generates a regression archive for the open project, named, if regressionArchiveFile is not supplied, after the project with \_regression.siz appended. Returns the name of the regression archive. |
| `RunRegression(regressionArchiveFile=None, archiveNonRelativeFiles=None, args=None, artifacts=None, callback=None, openDiffTool=None)` | checks the open project against its regression archive. Returns a list of results, one for each file checked; each is true if the file matched, and has the members filename, ok, message (describing the difference), and written. If openDiffTool is True (by default, as set by the Regression.OpenDiffToolOnFailure preference), the differing files are opened in meld, if it is installed. |

## Preferences and Caching {#sub:Scripting-Preferences}

Headless calculations use the [Preferences](29-Preferences.md#sec:Preferences) of the user running the script, in the same file that ***SignalIntegrityApp*** uses. Each SignalIntegrityAppHeadless reads the preferences when it is created, and so do the [Project Functions](34-Scripting-SignalIntegrity.md#sub:Scripting-Project-Functions), so changes made in memory to SignalIntegrity.App.Preferences do not last. To calculate with different preferences, such as on a build server, set the environment variable SIGNALINTEGRITY_PREFERENCES to the name of a preferences file before *SignalIntegrity* is used:

```python
import os
os.environ['SIGNALINTEGRITY_PREFERENCES'] = '/path/to/preferences.xml'
```

If the file does not exist, it is created (from the preferences of an older installation, if one is found, or otherwise with the default preferences).

Preferences that commonly matter to scripts are:

- Cache.CacheResults – whether calculation results are cached. When it is enabled, cache files are written in the project's directory, and calculating a project again uses the cached results when nothing that affects them has changed.

- Calculation.AllowParallelization – whether calculations may be performed in parallel (see [Parallel Calculations](32-Parallel-Calculations.md#sec:Parallel-Calculations)).

- ProjectFiles.Encryption.Password – the password used to read encrypted projects (see [Encryption](30-Encryption.md#sec:Encryption)).

## Command Line {#sub:Scripting-Command-Line}

***SignalIntegrityApp*** can also be started from the command line with arguments for the project, in which case the project opens in the graphical application with the arguments applied:

    SignalIntegrity [project.si] [-r | --readonly | -w | --writable] [-e | --external] [--pwd password] [name value ...]

- project.si – the project to open.

- -r, --readonly and -w, --writable – open the project read-only or writable, overriding the project and the preferences (see [Read-Only Schematics](15-Main-Schematic-Dialog.md#sub:Read-Only-Schematics)).

- -e, --external – the application was started by another application that waits for it to close. The window cannot be minimized, and the project is not added to the list of recently opened projects.

- --pwd password – the password used to read encrypted projects, overriding the ProjectFiles.Encryption.Password preference.

- name value ... – pairs of names and values, applied as [Arguments](34-Scripting-SignalIntegrity.md#sub:Scripting-Arguments) to the project when it is opened. The values are passed as strings.

For example, to open a project with the variable amplitude set to 2 and an end frequency of 10 GHz:

    SignalIntegrity MyProject.si amplitude 2 EndFrequency 10e9
