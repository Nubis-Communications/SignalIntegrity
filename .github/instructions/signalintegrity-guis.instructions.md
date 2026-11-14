---
applyTo: "SignalIntegrity/GuiCore/**,SignalIntegrity/QtApp/**,SignalIntegrity/Server/**,Tauri/**,Test/TestSignalIntegrity/TestGuiCore/**,Test/TestSignalIntegrity/TestQtApp/**,Test/TestSignalIntegrity/TestServer/**"
---
# Alternative SignalIntegrity GUIs

Follow `SignalIntegrity/GuiCore/RECIPES.md` (rules and shared recipes) and the GUI's own
`RECIPES.md` (`SignalIntegrity/QtApp/` or `SignalIntegrity/Server/`). In short:

- Do not modify `SignalIntegrity/Lib`, `SignalIntegrity/App` or the `.si` format for GUI work.
- Put non-widget logic in `SignalIntegrity/GuiCore` and keep that folder identical in the Qt and
  Tauri branches; copy changed files to the other worktree and compare hashes.
- Menus, toolbar, shortcuts and icons are data in `GuiCore/Menus.py` and `GuiCore/Icons.py`;
  each GUI adds one handler per command id. Tests fail if a GUI misses one.
- `ProjectSession` takes and returns plain JSON-serializable data in schematic pixels.
- Tests set `SIGNALINTEGRITY_GUI_SETTINGS` to a temporary folder; new files under `Test/` need
  the standard 16-line license header.
