# SignalIntegrity Server (web GUI back end)

`SignalIntegrity.Server` is a small HTTP/JSON server, using only the Python standard library.
It serves the SignalIntegrity web GUI (`ui/`) and an API built on
[`GuiCore.ProjectSession`](../GuiCore/README.md). The Tauri desktop app ([`Tauri/`](../../Tauri/README.md))
uses it, and you can also use it from any browser.

It only **adds** code: the tk GUI, `SignalIntegrityAppHeadless`, `SignalIntegrity.Lib` and
the `.si` format are unchanged, and it adds no new install requirements.

## Running

```bash
SignalIntegrityServer [project.si] [--port N] [--browser] [--verbose]
python -m SignalIntegrity.Server [project.si] --browser
```

On startup it prints one JSON line to stdout. The Tauri shell reads this line to find the
server:

```json
{"signalintegrity_server": {"port": 53122, "token": "...", "url": "http://127.0.0.1:53122/#token=..."}}
```

`--browser` opens that URL in the default browser. The UI reads the token from the URL
fragment, keeps it in `sessionStorage`, and removes it from the address bar.

## Security model

The API can open, save and calculate any project, and project equations run Python. Treat it
like a local editor process:

| Protection | How it's done |
|---|---|
| Local only | Listens on `127.0.0.1`, never on all interfaces. |
| Authentication | Every `/api/*` call needs `Authorization: Bearer <token>`. The token is a random `secrets.token_urlsafe(32)` per process, compared in constant time. It can be set with the `SIGNALINTEGRITY_SERVER_TOKEN` environment variable, never on the command line. |
| DNS rebinding / CSRF | The `Host` header must be `127.0.0.1:<port>` or `localhost:<port>`. A present `Origin` header must match. The body must be `application/json` (so a cross-site form can't send it without a CORS preflight, which fails). |
| Static files | Served only from `ui/`, with an extension allow-list and a real-path containment check (no path traversal). |
| Browser hardening | Strict `Content-Security-Policy` (`default-src 'self'`, no inline script), `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `Cache-Control: no-store`. The UI uses `textContent` and DOM APIs only, never `innerHTML`. |
| Resource limits | 1 MiB request body limit, 30 s socket timeout, `Connection: close`. |
| File browsing | `listDirectory` lists only folders and `.si` files (or, when asked, `.json`/`.vsix` theme files; other extensions are rejected). It is authenticated like every other method. |

Do not put the server behind a reverse proxy or bind it to another interface.

## API

`POST /api/<method>` with a JSON object body. The response is `{"result": ...}`, or
`{"error": "..."}` with status 400 (bad request), 401, 403, 404 (unknown method/job),
409 (a calculation is running), 413, 415 or 500.

| Method | Params | Result |
|---|---|---|
| `version` | – | `{version}` |
| `open` | `filename` | render (see GuiCore) |
| `new` | `filename` | creates and saves an empty project; render |
| `save` | `filename?` | `{filename}` |
| `render` | – | render |
| `deviceAt` | `x`, `y` | `{index}` |
| `select` | `index` (int or null) | render |
| `deviceProperties` | `index` | property list (with `visible`, `keywordVisible`, `validEntries`) |
| `setDeviceProperty` | `index`, `keyword`, `value` (string) | property list |
| `setPropertyVisibility` | `index`, `keyword`, `visible?`, `keywordVisible?` (bool) | property list |
| `moveDevice` | `index`, `dx`, `dy` (grid units) | render |
| `rotateDevice` | `index` | render |
| `variables` / `setVariable` / `setVariableVisible` | – / `name`, `value` / `name`, `visible` | variable list |
| `calculationProperties` / `setCalculationProperties` | – / `values` (object) | properties |
| `netlist` | – | `{netlist}` |
| `viewActions` | `index` | the device's View actions: `file`, `openproject`, `waveform` |
| `view` | `index`, `action` | `{kind:'project',drawing}` after descending into a sub-project, or `{kind:'result',result}` |
| `ascend` | – | render of the parent project |
| `calculate` | `kind`: `simulate`, `sparameters`, `virtualprobe`, `deembed` | job |
| `job` | `id` | job (`{id,kind,state,progress,error,result?}`); `result` is a result summary |
| `cancel` | `id` | job |
| `plotData` | `resultId`, `view` (`time`/`content`/`density`), `indices?`, `xmin?`, `xmax?`, `points?` | `{series:[{index,name,dc,x,y,total}],autoscale}` for that x range, min/max-decimated to `points` |
| `listDirectory` | `path?`, `extensions?` (any of `.si`, `.json`, `.vsix`; default `.si`) | `{path,parent,entries:[{name,path,directory}]}` |
| `partCatalog` | – | the parts stencil: `[{index,partname,description,categories,preview:{items,bbox}}]` (computed once per server) |
| `addPart` | `part` (catalog index), `x`, `y` (schematic pixels) | render with `added` (the new device index, selected) |
| `deleteDevice` | `index` | render |
| `themes` | – | built-in and installed VS Code themes `[{id,label,uiTheme,extension}]` |
| `theme` | – | the saved theme `{id,name,palette,colorMap}` |
| `setTheme` | `id` (built-in id, theme id, `.json` path or `.vsix` path), `name?` | `{id,name,palette,colorMap}`; also saves it for both GUIs |
| `themesInPackage` | `path` (`.vsix` or extension folder) | the themes it contains |
| `addWire` | `points` (`[[x,y],...]` schematic pixels, snapped to the grid) | render (with `wires`) |
| `selectWire` / `deleteWire` | `index` | render |
| `menus` | – | `{menus:[{title,items}],toolbar,toolbarLabels,icons}` from `GuiCore.Menus`/`GuiCore.Icons` (`icons` are SVG strings by command id) |
| `recentProjects` / `clearRecentProjects` | – | recent project paths, newest first; `open`, `new` and `save` with a `filename` add to it |

To add a method or a UI command, see [RECIPES.md](RECIPES.md).

A result summary is `{resultId,type,title,waveforms:[{index,name,dc,points,start,sampleRate}],sparameters:[...],eyes:[{name,image}]}`.
Waveform samples are not sent with the summary. The UI requests `plotData` for the visible x range
at screen resolution, so multi-million-point waveforms stay responsive and are complete at
any zoom. The server keeps the last 8 results.

Calculations run as one background job at a time, because the engine keeps a process-global
project. Poll `job` until `state` is `done` or `failed`. While a job is running, project calls
return 409; `job`, `cancel`, `plotData`, `listDirectory`, `version`, the theme methods, `menus` and
the recent-project methods never wait
for the
calculation.

## Files

| File | Role |
|---|---|
| `SignalIntegrityServer.py` | Command-line entry point (`main`) and the ready line. |
| `HttpServer.py` | `SignalIntegrityServer` (a `ThreadingHTTPServer`) and the request handler (security checks, static files, JSON). |
| `Api.py` | `Api` method dispatcher, parameter validation and calculation jobs. |
| `ui/index.html`, `ui/app.css` | Page layout and styles. |
| `ui/app.js` | Application logic: API client, schematic view (pan/zoom/select/drag), parts stencil (HTML5 drag-and-drop of `text/x-si-part`, click-to-place, Delete), theme menu (applies the palette to CSS variables, the schematic color map and plot traces), device context menu and hierarchy navigation, property/variable tables with Show/Keyword checkboxes, file dialog, progress, and the simulator results dialog. |
| `ui/schematic.js` | Turns GuiCore primitives into SVG (tk-style arrowheads, arcs and text anchors), recoloring the tk part colors through the theme's color map. Also draws the label-free stencil thumbnails. |
| `ui/favicon.png` | App icon used as the favicon and toolbar logo. |
| `ui/plot.js` | Dependency-free interactive SVG plot reproducing matplotlib's navigation in the tk dialogs: pan mode by default (left-drag pans, right-drag zooms x and y independently about the pointer, hold `x`/`y` to constrain), zoom-box mode (left zooms in, right zooms out, a flat box zooms one axis), Home/Back/Forward history, and autoscale. |

The web UI has no third-party JavaScript and needs no build step.

## Tests

`Test/TestSignalIntegrity/TestServer` (registered in `TestAll.py`). It covers parameter
validation, the job lifecycle, rejecting calls while busy, authentication, host/origin
checks, content-type checks, path traversal and an end-to-end S-parameter calculation over
HTTP.
