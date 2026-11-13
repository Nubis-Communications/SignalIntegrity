# Recipes for the alternative GUIs

These notes are for anyone (person or coding agent) extending the PySide6 GUI
(`SignalIntegrity/QtApp`) or the web/Tauri GUI (`SignalIntegrity/Server` + `Tauri/`).
They describe where each kind of change goes so a feature lands in a few predictable
places instead of spreading through both GUIs. GUI-specific steps are in
[QtApp/RECIPES.md](../QtApp/RECIPES.md) and [Server/RECIPES.md](../Server/RECIPES.md). Each GUI is
on its own branch (`feature/pyside6-gui`, `feature/tauri-gui`), so one of those two links points
at the other branch; this file and the rest of GuiCore are the same on both.

## Rules that keep churn low

1. **Never change existing code for a GUI feature.** `SignalIntegrity.Lib`, `SignalIntegrity.App`,
   `SignalIntegrityAppHeadless` and the `.si` format stay untouched so scripts, the tk app and
   regression tests behave exactly as before. If the engine lacks something, wrap it in GuiCore.
2. **Logic goes in GuiCore, once.** Anything that is not drawing widgets (project edits, hit
   testing in schematic units, result shaping, settings, menus, icons, themes) belongs in
   `GuiCore`, where both GUIs and the tests share it. A GUI should only translate events into
   `ProjectSession` calls and render what comes back.
3. **GuiCore is byte-identical in both branches.** Edit it in one worktree, copy the changed
   files to the other, and compare hashes before committing:
   ```powershell
   $q='c:\work\GitHub\SignalIntegrity-qt'; $t='c:\work\GitHub\SignalIntegrity-tauri'
   Get-ChildItem "$q\SignalIntegrity\GuiCore\*.*","$q\Test\TestSignalIntegrity\TestGuiCore\*.py" | ForEach-Object {
     $rel=$_.FullName.Substring($q.Length); if ((Get-FileHash $_).Hash -ne (Get-FileHash ($t+$rel)).Hash) { "DIFF $rel" } }
   ```
4. **Data, not code, for shared UI structure.** Menus, toolbar order, captions, shortcuts and
   icons are tables in `Menus.py` and `Icons.py`. Both GUIs build from them, and tests fail if a
   GUI lacks a handler for an id. Add a row instead of writing a menu item twice.
5. **Return plain data.** `ProjectSession` methods take and return ints, floats, strings, lists
   and dicts (JSON-serializable) so the HTTP API can pass them through unchanged.
6. **Mirror the tk app.** Use tk's names, menu layout, snapping, reference designators and
   consolidation rules, and reuse its classes (`Wire`, `SegmentList`, `PartPicture`...) rather
   than re-deriving behaviour. Users switch between GUIs on the same files.
7. **Coordinates:** GuiCore talks to GUIs in schematic *pixels* (`grid` pixels per grid unit,
   origin already applied). Convert with `Session._GridCoordinate`; never let grid units leak
   into a GUI. Hit-test tolerances that should feel constant on screen are passed in pixels by
   the GUI (see `WireAt(x,y,tolerance)`).
8. **Settings live in `Settings.SettingsDirectory()`** and tests point
   `SIGNALINTEGRITY_GUI_SETTINGS` at a temporary folder. Never let a test write the user's
   theme or recent projects.
9. **Read-only levels.** Every editing method starts with `self._Writable()`; GUIs disable the
   matching commands through their enable rules rather than checking again.
10. **Test where the logic is.** Session/Menus/Icons/Settings behaviour is tested in
    `TestGuiCore`; GUI tests only check wiring (events reach the session, enables update).
    New `.py` files under `Test/` need the exact 16-line license header
    (`TestHeadersTest::testFiles`), and new test classes are imported in the package `__init__.py`.

## Shared recipes

### Add a menu/toolbar command (both GUIs)
1. `Menus.py`: add `Command('myId','My Label...','Ctrl+M')` to the right menu (tk's menu if it
   has one). Use `only='qt'`/`'web'` only for things one platform cannot do.
2. For the toolbar, add the id to `TOOLBAR` and a short caption to `TOOLBAR_LABELS`.
3. `Icons.py`: add an entry to `ICONS` (or `ALIASES` to reuse one). Icons are 32x32 SVG bodies;
   prefix gradient ids with `ID-` so they stay unique when inlined. Check the contact sheet on a
   light and a dark background (see `testToolbarIcons`).
4. Implement the handler in each GUI (one line each, see the GUI recipes).
5. `TestGuiCore.TestMenusTest`, `TestQtApp.testMenusLikeTk` and
   `TestServer.testWebHandlesEveryCommand` fail until both GUIs handle the id.

### Add a project operation
1. `Session.py`: add a method that validates arguments (`SessionError` with a user-readable
   message), calls `_Writable()` when it edits, works on `self.app.Drawing.schematic` or
   `SignalIntegrity.App.Project`, and returns plain data (usually nothing; GUIs call `Render()`).
2. Test it in `TestGuiCore` without any GUI, including the read-only and bad-argument cases.
3. Expose it: Qt calls it directly; the web GUI needs an `Api` method (Server recipe).

### Add a setting shared by both GUIs
Add functions next to the recent-projects ones in `Settings.py` that read and write a JSON file in
`SettingsDirectory()`, tolerate a missing or corrupt file, and never raise on write errors.

### Add a theme-driven colour
Add the key to `Themes.Palette` (pick it from VS Code workbench colours with a fallback from the
built-in theme), then use it in `QtApp/Theme.StyleSheet` and in `CSS_VARS` in `Server/ui/app.js`.
