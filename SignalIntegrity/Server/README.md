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
| File browsing | `listDirectory` lists only folders and `.si` files. It is authenticated like every other method. |

Do not put the server behind a reverse proxy or bind it to another interface.

## API

`POST /api/<method>` with a JSON object body. The response is `{"result": ...}`, or
`{"error": "..."}` with status 400 (bad request), 401, 403, 404 (unknown method/job),
409 (a calculation is running), 413, 415 or 500.

| Method | Params | Result |
|---|---|---|
| `version` | – | `{version}` |
| `open` | `filename` | render (see GuiCore) |
| `save` | `filename?` | `{filename}` |
| `render` | – | render |
| `deviceAt` | `x`, `y` | `{index}` |
| `select` | `index` (int or null) | render |
| `deviceProperties` | `index` | property list |
| `setDeviceProperty` | `index`, `keyword`, `value` (string) | property list |
| `moveDevice` | `index`, `dx`, `dy` (grid units) | render |
| `rotateDevice` | `index` | render |
| `variables` / `setVariable` | – / `name`, `value` | variable list |
| `calculationProperties` / `setCalculationProperties` | – / `values` (object) | properties |
| `netlist` | – | `{netlist}` |
| `calculate` | `kind`: `simulate`, `sparameters`, `virtualprobe`, `deembed` | job |
| `job` | `id` | job (`{id,kind,state,progress,error,result?}`) |
| `cancel` | `id` | job |
| `listDirectory` | `path?` | `{path,parent,entries:[{name,path,directory}]}` |

Calculations run as one background job at a time, because the engine keeps a process-global
project. Poll `job` until `state` is `done` or `failed`. While a job is running, only `job`,
`cancel`, `listDirectory` and `version` are accepted.

## Files

| File | Role |
|---|---|
| `SignalIntegrityServer.py` | Command-line entry point (`main`) and the ready line. |
| `HttpServer.py` | `SignalIntegrityServer` (a `ThreadingHTTPServer`) and the request handler (security checks, static files, JSON). |
| `Api.py` | `Api` method dispatcher, parameter validation and calculation jobs. |
| `ui/index.html`, `ui/app.css` | Page layout and styles. |
| `ui/app.js` | Application logic: API client, schematic view (pan/zoom/select/drag), tables, file dialog, progress, results. |
| `ui/schematic.js` | Turns GuiCore primitives into SVG (tk-style arrowheads, arcs and text anchors). |
| `ui/plot.js` | Dependency-free SVG line plots with engineering-unit axes. |

The web UI has no third-party JavaScript and needs no build step.

## Tests

`Test/TestSignalIntegrity/TestServer` (registered in `TestAll.py`). It covers parameter
validation, the job lifecycle, rejecting calls while busy, authentication, host/origin
checks, content-type checks, path traversal and an end-to-end S-parameter calculation over
HTTP.
