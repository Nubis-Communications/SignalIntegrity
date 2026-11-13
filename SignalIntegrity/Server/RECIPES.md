# Web/Tauri GUI recipes

Shared rules and recipes are in [GuiCore/RECIPES.md](../GuiCore/RECIPES.md); read the
"Rules that keep churn low" first. This file covers `SignalIntegrity/Server` (HTTP API and
the web UI in `ui/`) and the Tauri shell in `Tauri/`.

## Where things are

| You want to change... | Edit |
|---|---|
| An API method | `Api.py`: add the name to `METHODS` (and to `UNLOCKED` if it never touches the project), then `_name(self,params)` |
| What a menu or toolbar command does | `COMMANDS` in `ui/app.js`: `{ run, when }` per `Menus.py` id |
| When a command is enabled | its `when(c)` rule; `c` comes from `commandContext()` |
| A dynamic submenu (recent projects, theme) | `SUBMENUS` in `ui/app.js`: an async function returning items |
| Mouse/keyboard behaviour on the schematic | the `svg` listeners in `ui/app.js` |
| Drawing primitives as SVG | `ui/schematic.js` |
| Plot interaction | `ui/plot.js` (a `Plot` class with matplotlib semantics) |
| Colours | CSS variables in `ui/app.css`, filled from the palette by `CSS_VARS` in `app.js` |
| Security (host/origin/token/CSP) | `HttpServer.py`; don't weaken it (see README "Security model") |
| Desktop shell, sidecar start-up, window options | `Tauri/src-tauri/src/main.rs`, `tauri.conf.json` |

## Data flow

```
DOM event -> runCommand(id) or handler -> api('method', params) -> Api._method -> ProjectSession
          <- render dict <- setDrawing(drawing) -> renderPrimitives + refreshCommands()
```
Editing methods in `Api.py` return `self.session.Render()` so the UI updates with one call:
`await setDrawing(await api('x', {...}))`. `setDrawing` calls `updateEnables()`, which refreshes
toolbar states; menus compute enables when they open, so there is nothing else to update.

## Recipes

### Add a command
1. Do the shared steps (`Menus.py`, `Icons.py`). The menu bar, toolbar, captions, icons and
   shortcuts appear automatically (`api('menus')` -> `buildMenus`).
2. Add `myId: { run: myThing, when: c => c.writable && c.device }` to `COMMANDS`
   (`always: true` for commands that work without a project, `idle: true` for ones allowed while
   a calculation runs, `checked: () => ...` for toggles).
3. If it needs the server, add the API method (below).
4. `TestServer.testWebHandlesEveryCommand` fails until the id is in `COMMANDS`.

### Add an API method
1. `Api.py`: append to `METHODS`; implement `_method(self,params)` using
   `self._Get(params,'name',type,optional)` for every parameter (it rejects wrong types,
   including bools passed as ints); raise `ApiError` for bad input; let `SessionError` propagate
   (the dispatcher turns it into a 400).
2. Return JSON-serializable data; for edits return `self.session.Render()`.
3. Add a test in `TestServer.TestServerApiTest` (valid call, bad parameters).
4. Document it in the API table in `README.md`.

### Add a schematic interaction mode (like Add Wire)
Keep its state in `state`, handle it first in the `pointerdown`/`pointermove`/`dblclick`/
`contextmenu` listeners and return early, draw feedback as an element with a fixed id appended
to `#viewport` (re-added in `setDrawing`, which re-renders the viewport), make it a checkable
command, and turn it off in `cancel()` and in `updateEnables()` when editing isn't allowed.

### Add a dialog
Add a `<dialog>` to `index.html` and drive it from `app.js` with `textContent`/DOM APIs only.
Never use `innerHTML` (the CSP and security model rely on it). SVG icons are inserted as
`<img src="data:image/svg+xml,...">`, which the CSP allows.

### Change the desktop shell
`main.rs` starts `python -m SignalIntegrity.Server`, reads its ready line, and navigates the
window to the local URL. Prefer changing behaviour in the web UI so the browser version
(`SignalIntegrityServer --browser`) gets it too. Rebuild with
`cargo build --manifest-path Tauri/src-tauri/Cargo.toml`.

## Testing
- `Test/TestSignalIntegrity/TestServer/TestServer.py` tests `Api` directly and over HTTP; both
  classes point `SIGNALINTEGRITY_GUI_SETTINGS` at a temporary folder.
- Syntax-check the UI: `node --check SignalIntegrity/Server/ui/app.js`.
- Browser check: start the server with a fixed token, e.g.
  `$env:PYTHONSAFEPATH='1'; $env:SIGNALINTEGRITY_SERVER_TOKEN='...'; .venv\Scripts\python -m SignalIntegrity.Server --port 8766 project.si`
  (`PYTHONSAFEPATH` stops a different checkout in the current directory from shadowing the
  package), open `http://127.0.0.1:8766/?r=<n>#token=...` (a new query string forces a reload),
  and drive it with Playwright. Map schematic pixels to the screen with
  `document.getElementById('viewport').getScreenCTM()`.
