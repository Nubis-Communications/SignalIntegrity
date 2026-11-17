# SignalIntegrity desktop app (Electron)

A desktop window for SignalIntegrity built with [Electron](https://www.electronjs.org). Like the
Tauri app in [`Tauri/`](../Tauri/README.md), it starts the SignalIntegrity Python engine as a
sidecar process and shows its web GUI. The UI, the server and the `.si` files are the same.
Only the shell differs: Electron ships its own Chromium instead of using the system WebView.

| GUI | Start with | Notes |
|---|---|---|
| tk (original, full featured) | `SignalIntegrity` | unchanged |
| Web | `SignalIntegrityServer --browser` | any browser |
| Tauri | `npm run tauri dev` in `Tauri/` | system WebView, small installer |
| Electron (this PR) | `npm start` in `Electron/` | bundled Chromium, same rendering on every OS |

## Architecture

```mermaid
flowchart LR
    subgraph Electron["Electron shell (Electron/main.js)"]
        Main["main process"] -->|"spawn python -m SignalIntegrity.Server"| Proc
        Main --> BW["BrowserWindow (sandboxed renderer)"]
    end
    subgraph Py["Python sidecar (SignalIntegrity.Server)"]
        Proc[SignalIntegrityServer] --> HTTP["HttpServer 127.0.0.1:random"]
        HTTP --> Api --> PS["GuiCore.ProjectSession"]
        PS --> H["SignalIntegrityAppHeadless (unchanged)"]
        H --> Lib["SignalIntegrity.Lib (unchanged)"]
    end
    Proc -- "ready line on stdout: port + token" --> Main
    BW -- "loads http://127.0.0.1:port/#token=..." --> HTTP
    BW -- "fetch /api/* (Bearer token)" --> HTTP
```

Start-up sequence, the same as the Tauri shell:

1. The window opens on the bundled loading page (`loading/`).
2. `main.js` looks for Python: `$SIGNALINTEGRITY_PYTHON`, then the checkout's `.venv`, then
   `python`, `python3` and (on Windows) `py -3`. It runs
   `python -m SignalIntegrity.Server --exit-with-stdin [project.si]` with no console window.
3. The server binds a random port on `127.0.0.1`, makes a random token and prints one JSON
   ready line. The shell accepts only an `http://127.0.0.1` URL.
4. The window loads `http://127.0.0.1:<port>/#token=<token>`. From then on the UI talks only
   to the token-protected JSON API (see
   [`SignalIntegrity/Server/README.md`](../SignalIntegrity/Server/README.md)).
5. On quit the shell closes the sidecar's stdin and kills it. Because the shell holds that
   pipe, the sidecar also stops by itself if Electron is killed or crashes.

If no interpreter works, the loading page lists every one it tried and why it failed.

When run from a checkout, `main.js` puts the repository root (`Electron/..`, or
`$SIGNALINTEGRITY_ROOT`) on `PYTHONPATH` and starts the server there, so it runs your
working tree. A packaged app has no checkout and uses whatever `SignalIntegrity` the chosen
interpreter imports (`pip install SignalIntegrity`, or set `SIGNALINTEGRITY_PYTHON`).

The project to open comes from the command line (`electron . path/to/file.si`, or
`SignalIntegrity.exe file.si` when packaged; `.si` files are associated by the installer) or,
on macOS, from the `open-file` event.

## Security

The page is a normal web page served by the local server, so the shell gives it no extra
power. There is no preload script and no IPC.

| Measure | Where |
|---|---|
| `contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`, `webSecurity: true` | `BrowserWindow` options |
| Navigation and redirects are refused unless they go to the loading page or the server's own origin | `will-navigate`, `will-redirect` |
| No pop-up windows; external `http(s)` links open in the default browser | `setWindowOpenHandler` |
| No `<webview>` tags | `will-attach-webview` |
| All permission requests (camera, notifications, ...) denied | `setPermissionRequestHandler`, `setPermissionCheckHandler` |
| The loading page has its own CSP (`default-src 'none'; script-src 'self'`) | `loading/index.html` |
| Token in the URL fragment, Host/Origin checks, CSP on the UI | the server (unchanged) |
| A fresh token every start; `SIGNALINTEGRITY_SERVER_TOKEN` is removed from the sidecar's environment | `startCandidate` |

Help opens in the system browser through the server's `help` API, so the window never needs
to show anything else.

`npm audit` reports advisories (glob ReDoS in `minimatch`/`picomatch` and similar) in
electron-builder's dependency tree. They are build-time tools only and are not in the
packaged app, which contains just `main.js`, `loading/` and `icons/` on top of Electron.

## Running and building

Prerequisites: Node.js 18+ and a Python with SignalIntegrity's requirements (the checkout's
`.venv` is used automatically).

```bash
cd Electron
npm install          # electron and electron-builder (dev dependencies)
npm start            # run the app on this checkout
npm start -- ../SignalIntegrity/App/Examples/RLC.si
npm run smoke        # headless check, see below
npm run dist         # installers in Electron/dist (NSIS on Windows, AppImage/deb on Linux, dmg on macOS)
npx electron-builder --dir   # unpacked app only, faster
```

In VS Code, use the Run and Debug configuration `SignalIntegrity: Desktop (Electron)`.

Behind a TLS-inspecting proxy, Node's built-in CA list may reject the Electron download
(`fetch failed`, `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`). Set `NODE_USE_SYSTEM_CA=1` for the
install so Node trusts the operating system's certificate store. Don't disable TLS checks.

### Smoke test

`electron . --smoke-test [project.si]` (`npm run smoke`) runs the real shell with a hidden
window. It waits for the toolbar, the menus and, if a project is given, the drawn schematic.
It then checks that the page can't see Node (`require` and `process` are undefined) and that
navigating to another origin is blocked. It prints one JSON line and exits with 0 or 1:

```json
{"ok":true,"nodeInPage":"undefined/undefined","navigationBlocked":true,"title":"SignalIntegrity - RLC.si","toolbarButtons":21,"menus":8,"drawn":46,"origin":"http://127.0.0.1:60231"}
```

Start-up failures print `{"ok":false,"error":"..."}` and exit 1, so the same command works
in CI.

## Icon

`icons/icon.png` (1024 px) and `icons/icon.ico` are rendered by `Tauri/MakeIcons.py`:
`python Tauri/MakeIcons.py Electron/icons electron` (needs Pillow and numpy). The Electron
icon is the same eye diagram on a midnight-navy tile with an electric-blue trace, so it is
easy to tell apart from the Tauri (violet) and Qt (teal) icons.

## Files

- `main.js`: the main process (Python search, sidecar, window, security, smoke test).
- `loading/`: page shown while the engine starts, and `showStartupError`.
- `icons/`: app icons.
- `package.json`: scripts and the electron-builder configuration (`build`).

## Validation

Tested on Windows 11 with Electron 45.3.3, electron-builder 26.18.0 and Python 3.14:

- `npm run smoke` with no project and with `RLC.si`: `ok:true`, 21 toolbar buttons, 8 menus,
  46 schematic elements, no Node in the page, navigation blocked.
- No usable Python (`SIGNALINTEGRITY_PYTHON` pointing nowhere, empty `PATH`): the error lists
  all four candidates; exit code 1.
- Normal launch with `RLC.si`: window title `SignalIntegrity - RLC.si`; closing the window
  stops the sidecar.
- Electron force-killed: the sidecar exits by itself (`--exit-with-stdin`).
- `npx electron-builder --dir --win`: the packaged `SignalIntegrity.exe` passes the smoke test
  with `RLC.si`.
- The Python test suites (GuiCore, Server) are unchanged by this PR and still pass.
