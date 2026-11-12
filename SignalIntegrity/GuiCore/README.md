# GuiCore

`SignalIntegrity.GuiCore` is a small, toolkit-neutral layer used by the alternative user
interfaces (the PySide6 GUI in `SignalIntegrity/QtApp` and the Tauri GUI in
`SignalIntegrity/Server` + `Tauri/`). The tk application in `SignalIntegrity/App` does not
use it and is unchanged.

GuiCore only **adds** code. It does not change `SignalIntegrity.Lib`, `SignalIntegrity.App`,
or the `.si` project format. Scripts that use `SignalIntegrityAppHeadless`, `si.p.*` parsers,
`ProjectSParameters` and similar keep working exactly as before.

## Modules

| Module | Purpose |
|---|---|
| `RecordingCanvas.py` | Implements the six `tk.Canvas` calls the schematic code uses (`create_line`, `create_polygon`, `create_rectangle`, `create_oval`, `create_arc`, `create_text`) and records them as JSON-serializable dicts. |
| `Session.py` | `ProjectSession` is a façade over `SignalIntegrityAppHeadless`: it opens and saves projects, renders, selects and moves devices, edits properties and variables, sets calculation properties, shows the netlist, and runs calculations. It returns plain Python data. |

## How rendering works

```mermaid
flowchart LR
    SI[".si project (XML)"] --> H[SignalIntegrityAppHeadless]
    H --> D["DrawingHeadless.DrawSchematic(canvas)"]
    D -->|"PartPicture / Wire / PartPin draw calls"| RC[RecordingCanvas]
    RC --> P["primitives (JSON)"]
    P --> Qt["QGraphicsScene (PySide6)"]
    P --> SVG["SVG (Tauri web UI)"]
```

The part pictures in `PartPicture.py` (about 2,900 lines of procedural drawing code) are reused
as-is. `DrawingHeadless` already accepts any object with the `tk.Canvas` drawing API (the TikZ
exporter works the same way), so each new GUI only needs to turn about 6 primitive types into
its own toolkit.

### Primitive format

| type | fields |
|---|---|
| `line` | `points` [x0,y0,x1,y1,...], `color`, `width`, optional `arrow` (`first`/`last`/`both`), `arrowshape` [d1,d2,d3], `dash` |
| `polygon` | `points`, `outline`, `fill` |
| `rectangle`, `oval` | `bbox` [x0,y0,x1,y1], `outline`, `fill` |
| `arc` | `bbox`, `start`, `extent` (degrees, counter-clockwise, like tk), `outline` |
| `text` | `x`, `y`, `text`, `anchor` (tk anchor: `n`, `sw`, `center`, ...), `color` |

Coordinates are in the same pixel units the tk application uses (`grid` pixels per grid unit).

## ProjectSession API

| Method | Returns |
|---|---|
| `Open(filename)` | render dict (below); raises `SessionError` on failure |
| `Save(filename=None)` | the saved path (`.si` is appended if missing) |
| `Render()` | `{filename,title,grid,items,bbox,devices,capabilities,equationsValid}` |
| `DeviceAt(x,y)` / `Select(index)` | device index under a pixel point / select one device |
| `DeviceProperties(index)` / `SetDeviceProperty(index,keyword,value)` | list of `{keyword,name,description,type,unit,value,visible,readOnly}` |
| `MoveDevice(index,dx,dy)` / `RotateDevice(index)` | move by whole grid units / rotate 90° |
| `Variables()` / `SetVariable(name,value)` | list of `{name,value,type,units,description,readOnly}` |
| `CalculationProperties()` / `SetCalculationProperties(dict)` | `EndFrequency`, `FrequencyPoints`, `UserSampleRate`, `ReferenceImpedance` |
| `NetList()` | netlist text |
| `Calculate(kind, callback=None)` | `kind` is one of `simulate`, `sparameters`, `virtualprobe`, `deembed`; returns `{type, waveforms:[{name,x,y,xunit,yunit}], sparameters:[{name,ports,frequencies,traces:[{name,to,from,dB,deg}]}]}` |

Every calculation runs through the same `SignalIntegrityAppHeadless` methods (`Simulate`,
`CalculateSParameters`, `VirtualProbe`, `Deembed`) that scripts and the regression tests use,
so results are numerically identical to the tk GUI. `TestGuiCore.testSimulateMatchesHeadless`
checks this to 12 decimal places.

If the progress callback returns `False`, the calculation is cancelled and `Calculate` raises
`SessionError`.

## Limits

- `ProjectSession` uses the process-global `SignalIntegrity.App.Project`, the same as the
  headless app. Use one session per process (or per worker process).
- Opening a project changes the working directory to the project's folder, matching the
  existing headless behaviour. Pass absolute paths.

## Tests

`Test/TestSignalIntegrity/TestGuiCore` (included in `TestAll.py`).
