# Qt GUI recipes

Shared rules and recipes are in [GuiCore/RECIPES.md](../GuiCore/RECIPES.md); read the
"Rules that keep churn low" first. This file covers what is specific to `SignalIntegrity/QtApp`.

## Where things are

| You want to change... | Edit |
|---|---|
| What a menu or toolbar command does | `MainWindow._Handlers()` (one entry per `Menus.py` id) |
| When a command is enabled | `MainWindow.UpdateEnables()` |
| A dynamic submenu (recent projects, theme, panels) | `MainWindow._SubmenuBuilders()` and its `Build...Menu` method |
| Mouse/keyboard behaviour on the schematic | `SchematicView` (emits signals; never calls the session) |
| Reaction to a schematic event | the `MainWindow.On...` slot connected in `__init__` |
| Panes (stencil, variables, properties, calculation) | `MainWindow._BuildDocks()`, `PartsDock.py`; moving, tear-off windows and the saved layout are in `Docking.py` |
| Selection gestures (rubber band, Ctrl/Shift+click, group drag, middle-drag pan) | `SchematicView.mousePressEvent/MoveEvent/ReleaseEvent`, which emit `regionSelected`, `deviceToggled`, `selectionDragged` |
| How text and property labels are drawn | `AddPrimitives` in `SchematicView.py` (tk anchors; items with `role: 'property'` get a backing) |
| Colours, fonts, widget styling | `Theme.StyleSheet()`; plot axes in `Theme.StyleAxes()` |
| Plot windows | `SimulatorWindow.py` |

## Data flow

```
SchematicView signal -> MainWindow.On...() -> ProjectSession.X() -> MainWindow.Redraw()/Refresh...()
```
`Redraw()` re-renders from `session.Render()` and calls `UpdateEnables()`, so a handler that
edits the project normally needs only `self.session.X(...)` followed by `self.Redraw()`
(plus `RefreshProperties()` when the selection changed). Do not cache project state in the
window; read it from the last render (`self.drawing`) or the session.

## Recipes

### Add a command
1. Do the shared steps (`Menus.py`, `Icons.py`).
2. Add `'myId':self.OnMyThing` to `_Handlers()` and write `OnMyThing`.
3. Add its enable rule to `UpdateEnables()` via `self.actions['myId'].setEnabled(...)`.
4. Single-key shortcuts (no Ctrl/Alt) are scoped to the schematic automatically so they don't
   fire while typing in a table.

### Add a schematic interaction mode (like Add Wire)
1. In `SchematicView`, add state plus `StartX()/StopX()`; handle it at the top of
   `mousePressEvent`/`mouseMoveEvent`/`mouseDoubleClickEvent` and return early; emit a signal
   with schematic pixel coordinates when the gesture completes. Mouse tracking is already on.
2. Draw transient feedback as a scene item you remove/recreate (see `_UpdateWirePreview`);
   `SetDrawing` clears the scene, so recreate it there.
3. Make it a checkable command and turn it off in `OnCancel()` (Esc) and when the project
   becomes read-only (`UpdateEnables`). Stop other modes when starting one.

### Add a pane
Create the widget, wrap it in a `Docking.Pane` (it offers the `QDockWidget` calls the window
uses: `setWidget`, `widget`, `toggleViewAction`, `raise_`), add it with
`self.docks.AddPane('myId',pane,'left'|'right'|'bottom')` in `_BuildDocks()` before
`docks.Finish(...)`, and add it to `BuildPanelsMenu()` so View > Panels can show it again.
The pane id is stored in the saved layout; a saved layout that doesn't place every pane exactly
once is ignored, so adding a pane never breaks an existing layout file.

### Change what a selection operation does
Multiple selection lives in `GuiCore.Session` (`SelectRegion`, `ToggleDevice`, `MoveSelection`,
`DeleteSelection`, `CopySelection`, `CutSelection`, `DuplicateSelection`, and `Paste` of a group),
so both GUIs change together. `MainWindow.MultipleSelection()` decides whether a command acts on
the whole selection or on the single selected part or wire.

### Add a plot view
Extend `SimulatorWindow`; get data from `ResultData` (GuiCore) rather than the raw waveforms, so
the web GUI can reuse the same series and autoscale rules.

## Testing
- `Test/TestSignalIntegrity/TestQtApp/TestQtApp.py` runs offscreen (`QT_QPA_PLATFORM=offscreen`).
  Call `IsolateSettings(self)` in `setUp`.
- Drive real events where it matters: `QTest.mouseClick(view.viewport(), ..., view.mapFromScene(QPointF(x,y)))`.
  `QTest.mouseDClick` sends only the double-click event, and plain mouse moves need a
  `QMouseEvent` sent with `sendEvent` (see `testDrawSelectDeleteWire`; `_Drag` in
  `TestQtSelectionAndPanesTest` drags with any button). Calling `viewport().event()` directly
  bypasses the view and does nothing.
- Pane drags are tested through `DockManager.BeginDrag/DragTo/EndDrag` with global positions.
- Run: `.venv\Scripts\python -m pytest Test/TestSignalIntegrity/TestGuiCore/TestGuiCore.py Test/TestSignalIntegrity/TestQtApp/TestQtApp.py`
- For a visual check, script the window (open a project, trigger actions) and save `window.grab()`
  and `menu.grab()` images; look at them in light and dark themes.
