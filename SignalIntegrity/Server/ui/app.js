// SignalIntegrity web GUI - talks to SignalIntegrity.Server over a token-protected local JSON API.
import { el, renderPrimitives, primitivesBox } from './schematic.js';
import { Plot, COLORS, engineering } from './plot.js';
import { initDock } from './dock.js';

const $ = id => document.getElementById(id);
const CALC_TITLES = { simulate: 'Simulate', sparameters: 'S-parameters', virtualprobe: 'Virtual Probe', deembed: 'De-embed' };

// ---------- API
const token = (() => {
  const m = location.hash.match(/token=([A-Za-z0-9_\-]+)/);
  if (m) {
    sessionStorage.setItem('si-token', m[1]);
    history.replaceState(null, '', location.pathname);
  }
  return sessionStorage.getItem('si-token');
})();

export async function api(method, params = {}) {
  const response = await fetch('/api/' + method, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
    body: JSON.stringify(params),
  });
  let body;
  try { body = await response.json(); } catch { throw new Error('server returned ' + response.status); }
  if (!response.ok) throw new Error(body.error || ('server returned ' + response.status));
  return body.result;
}

// ---------- state
const state = { drawing: null, selected: null, busy: false, view: { s: 1, tx: 0, ty: 0 }, lastCalculation: null,
  colorMap: null, palette: null, theme: null, catalog: [], placing: null,
  wiring: false, wirePoints: [], wireCursor: null, menus: null };
const svg = $('schematic'), viewport = $('viewport');

function status(text) { $('status').textContent = text; }
function error(e) { status('Error: ' + (e.message || e)); alert(e.message || e); }
const readOnly = () => !!(state.drawing && state.drawing.readOnly);

function updateEnables() {
  const open = !!state.drawing, busy = state.busy, ro = readOnly();
  $('parts').classList.toggle('disabled', !open || busy || ro);
  if ((!open || busy || ro) && state.placing !== null) stopPlacing();
  if ((!open || busy || ro) && state.wiring) stopWiring();
  refreshCommands();
  for (const input of $('calcProps').querySelectorAll('input,button')) input.disabled = ro;
  document.title = 'SignalIntegrity' + (open ? ' - ' + state.drawing.path.join(' > ') + (ro ? ' (Read Only)' : '') : '');
  const bar = $('hierarchy');
  bar.classList.toggle('visible', open && state.drawing.path.length > 1);
  while (bar.firstChild) bar.removeChild(bar.firstChild);
  if (open && state.drawing.path.length > 1) {
    bar.append(state.drawing.path.join(' \u203a '));
    if (ro) { const s = document.createElement('span'); s.className = 'ro'; s.textContent = '(Read Only)'; bar.appendChild(s); }
  }
}

// ---------- schematic view
function applyView() {
  const { s, tx, ty } = state.view;
  viewport.setAttribute('transform', `translate(${tx} ${ty}) scale(${s})`);
}
function zoomFit() {
  if (!state.drawing || !state.drawing.bbox) return;
  const [x0, y0, x1, y1] = state.drawing.bbox;
  const margin = 2 * state.drawing.grid;
  const W = svg.clientWidth, H = svg.clientHeight;
  const s = Math.min(W / (x1 - x0 + 2 * margin), H / (y1 - y0 + 2 * margin));
  state.view = { s, tx: (W - (x1 + x0) * s) / 2, ty: (H - (y1 + y0) * s) / 2 };
  applyView();
}
function zoomAt(factor, cx, cy) {
  const v = state.view;
  v.tx = cx - (cx - v.tx) * factor; v.ty = cy - (cy - v.ty) * factor; v.s *= factor;
  applyView();
}
function toScene(evt) {
  const r = svg.getBoundingClientRect();
  return { x: (evt.clientX - r.left - state.view.tx) / state.view.s, y: (evt.clientY - r.top - state.view.ty) / state.view.s };
}
function deviceAt(p) {
  if (!state.drawing) return null;
  const tol = 0.1 * state.drawing.grid;
  for (let i = state.drawing.devices.length - 1; i >= 0; i--) {
    const d = state.drawing.devices[i], [x0, y0, x1, y1] = d.bbox;
    if (p.x >= Math.min(x0, x1) - tol && p.x <= Math.max(x0, x1) + tol && p.y >= Math.min(y0, y1) - tol && p.y <= Math.max(y0, y1) + tol) return d.index;
  }
  return null;
}
async function setDrawing(drawing, fit = false) {
  state.drawing = drawing;
  renderPrimitives(viewport, drawing.items, state.colorMap);
  drawWirePreview();
  const sel = drawing.devices.find(d => d.selected);
  state.selected = sel ? sel.index : null;
  state.viewActions = state.selected === null ? [] : await api('viewActions', { index: state.selected });
  if (fit) zoomFit(); else applyView();
  updateEnables();
}
async function showLevel(drawing) {
  await setDrawing(drawing, true);
  await Promise.all([refreshVariables(), refreshProperties(), refreshCalculationProperties()]);
}

let drag = null;
svg.addEventListener('pointerdown', async evt => {
  hideContextMenu(); closeMenus();
  if (state.wiring) {
    if (evt.button === 0) { addWirePoint(snap(toScene(evt))); drawWirePreview(); }
    return;
  }
  if (evt.button !== 0 || !state.drawing || state.busy) return;
  if (state.placing !== null) {
    const part = state.placing;
    stopPlacing();
    return addPart(part, toScene(evt));
  }
  svg.setPointerCapture(evt.pointerId);
  const p = toScene(evt);
  const index = deviceAt(p);
  if (index !== null) {
    if (index !== state.selected) await selectDevice(index);
    if (readOnly()) return;
    const d = state.drawing.devices.find(x => x.index === index);
    const [x0, y0, x1, y1] = d.bbox;
    const ghost = el('rect', { x: Math.min(x0, x1), y: Math.min(y0, y1), width: Math.abs(x1 - x0), height: Math.abs(y1 - y0),
      fill: 'none', stroke: state.palette ? state.palette.accent : '#0a64c8', 'stroke-dasharray': '4 3', visibility: 'hidden' }, viewport);
    drag = { kind: 'device', index, start: p, ghost, dx: 0, dy: 0 };
  } else {
    const vertex = vertexAt(p);
    if (vertex !== null) {
      try { await setDrawing(await api('selectVertex', { wire: vertex[0], vertex: vertex[1] })); await refreshProperties(); } catch (e) { return error(e); }
      status('wire corner selected: drag it, or use Wires > Delete Vertex / Duplicate Vertex');
      if (!readOnly()) {
        const q = state.drawing.wires[vertex[0]].points;
        const corners = []; for (let k = 0; k + 1 < q.length; k += 2) corners.push([q[k], q[k + 1]]);
        drag = { kind: 'vertex', wire: vertex[0], vertex: vertex[1], from: corners[vertex[1]], to: null,
          neighbours: [corners[vertex[1] - 1], corners[vertex[1] + 1]].filter(Boolean) };
      }
      return;
    }
    const wire = wireAt(p);
    if (wire !== null) {
      try { await setDrawing(await api('selectWire', { index: wire })); await refreshProperties(); } catch (e) { error(e); }
      return status('wire selected (Del deletes it)');
    }
    if (state.selected !== null || selectedWire() !== null) await selectDevice(null);
    drag = { kind: 'pan', x: evt.clientX, y: evt.clientY };
    svg.classList.add('panning');
  }
});
svg.addEventListener('pointermove', evt => {
  if (state.wiring) { state.wireCursor = snap(toScene(evt)); drawWirePreview(); return; }
  if (drag && drag.kind === 'vertex') { drag.to = snap(toScene(evt)); drawVertexPreview(drag); return; }
  if (!drag) return;
  if (drag.kind === 'pan') {
    state.view.tx += evt.clientX - drag.x; state.view.ty += evt.clientY - drag.y;
    drag.x = evt.clientX; drag.y = evt.clientY;
    applyView();
  } else {
    const p = toScene(evt), g = state.drawing.grid;
    drag.dx = Math.round((p.x - drag.start.x) / g); drag.dy = Math.round((p.y - drag.start.y) / g);
    drag.ghost.setAttribute('transform', `translate(${drag.dx * g} ${drag.dy * g})`);
    drag.ghost.setAttribute('visibility', drag.dx || drag.dy ? 'visible' : 'hidden');
  }
});
svg.addEventListener('pointerup', async () => {
  const d = drag; drag = null;
  svg.classList.remove('panning');
  if (d && d.kind === 'vertex') {
    drawVertexPreview(null);
    if (d.to && (d.to[0] !== d.from[0] || d.to[1] !== d.from[1])) {
      try { await setDrawing(await api('moveVertex', { wire: d.wire, vertex: d.vertex, x: d.to[0], y: d.to[1] })); status('wire corner moved'); } catch (e) { error(e); }
    }
    return;
  }
  if (d && d.kind === 'device') {
    d.ghost.remove();
    if (d.dx || d.dy) {
      try { await setDrawing(await api('moveDevice', { index: d.index, dx: d.dx, dy: d.dy })); } catch (e) { error(e); }
    }
  }
});
svg.addEventListener('wheel', evt => {
  evt.preventDefault();
  const r = svg.getBoundingClientRect();
  zoomAt(evt.deltaY < 0 ? 1.15 : 1 / 1.15, evt.clientX - r.left, evt.clientY - r.top);
}, { passive: false });
window.addEventListener('resize', () => applyView());

// ---------- wires: click each corner, double-click or right-click finishes, Esc cancels (as in tk)
function snap(p) { const g = state.drawing.grid; return [Math.round(p.x / g) * g, Math.round(p.y / g) * g]; }
function addWirePoint(pt) {
  const last = state.wirePoints[state.wirePoints.length - 1];
  if (!last || last[0] !== pt[0] || last[1] !== pt[1]) state.wirePoints.push(pt);
}
function drawWirePreview() {
  const old = $('wirePreview');
  if (old) old.remove();
  const pts = state.wirePoints.concat(state.wiring && state.wirePoints.length && state.wireCursor ? [state.wireCursor] : []);
  if (pts.length < 2) return;
  el('polyline', { id: 'wirePreview', points: pts.map(p => p.join(',')).join(' '), fill: 'none',
    stroke: state.colorMap ? state.colorMap.blue : 'blue', 'stroke-width': 1.5, 'stroke-dasharray': '5 3' }, viewport);
}
function startWiring() {
  stopPlacing();
  state.wiring = true; state.wirePoints = [];
  svg.classList.add('wiring');
  status('Add Wire: click each corner, double-click or right-click to finish a wire, Esc to stop');
  refreshCommands();
}
function stopWiring() {
  state.wiring = false; state.wirePoints = []; state.wireCursor = null;
  svg.classList.remove('wiring');
  drawWirePreview();
  refreshCommands();
}
async function finishWire() {
  const points = state.wirePoints;
  state.wirePoints = [];
  drawWirePreview();
  if (points.length < 2) return;
  try {
    await setDrawing(await api('addWire', { points }));
    await refreshProperties();
    status('wire added - keep clicking to draw another, Esc to stop');
  } catch (e) { error(e); }
}
svg.addEventListener('dblclick', evt => { if (state.wiring) { evt.preventDefault(); finishWire(); } });
function selectedWire() {
  const w = state.drawing && (state.drawing.wires || []).find(x => x.selected);
  return w ? w.index : null;
}
// within 5 screen pixels at any zoom, but never less than a quarter grid
function hitTolerance() { return Math.max(0.25 * state.drawing.grid, 5 / state.view.s); }
function vertexAt(p) {
  if (!state.drawing) return null;
  const tol = hitTolerance();
  for (const w of state.drawing.wires || []) {
    for (let k = 0; k + 1 < w.points.length; k += 2) {
      if (Math.abs(w.points[k] - p.x) <= tol && Math.abs(w.points[k + 1] - p.y) <= tol) return [w.index, k / 2];
    }
  }
  return null;
}
function drawVertexPreview(d) {
  const old = $('vertexPreview');
  if (old) old.remove();
  if (!d || !d.to) return;
  const parts = (d.neighbours.length ? d.neighbours : [d.to]).map(n => `M ${n[0]} ${n[1]} L ${d.to[0]} ${d.to[1]}`);
  el('path', { id: 'vertexPreview', d: parts.join(' '), fill: 'none', stroke: state.colorMap ? state.colorMap.blue : 'blue',
    'stroke-width': 1.5, 'stroke-dasharray': '5 3' }, viewport);
}
function wireAt(p) {
  if (!state.drawing) return null;
  const tol = hitTolerance();
  for (const w of state.drawing.wires || []) {
    const q = w.points;
    for (let k = 0; k + 3 < q.length; k += 2) {
      const [x0, y0, x1, y1] = [q[k], q[k + 1], q[k + 2], q[k + 3]];
      const L = (x1 - x0) ** 2 + (y1 - y0) ** 2;
      const t = L ? Math.max(0, Math.min(1, ((p.x - x0) * (x1 - x0) + (p.y - y0) * (y1 - y0)) / L)) : 0;
      if (Math.hypot(p.x - (x0 + t * (x1 - x0)), p.y - (y0 + t * (y1 - y0))) <= tol) return w.index;
    }
  }
  return null;
}

// ---------- device context menu: the tk View / Open Project actions
function hideContextMenu() { $('contextMenu').hidden = true; }
document.addEventListener('pointerdown', e => { if (!$('contextMenu').contains(e.target)) hideContextMenu(); });
function preferredAction(actions) {
  const keys = actions.map(a => a.action);
  return keys.includes('openproject') ? 'openproject' : keys[0];
}
svg.addEventListener('contextmenu', async evt => {
  evt.preventDefault();
  if (state.wiring) return finishWire();
  if (!state.drawing || state.busy) return;
  const index = deviceAt(toScene(evt));
  if (index === null) return;
  if (index !== state.selected) await selectDevice(index);
  const actions = state.viewActions || [];
  if (evt.ctrlKey && actions.length) return viewDevice(index, preferredAction(actions));
  const items = actions.map(a => [a.label, () => viewDevice(index, a.action)]);
  if (!readOnly()) {
    if (items.length) items.push(null);
    items.push(['Edit Properties', () => runCommand('properties')]);
    items.push(['Rotate', () => runCommand('rotate')]);
    items.push(['Delete', () => runCommand('deletePart')]);
  }
  if (state.drawing.canAscend) { items.push(null); items.push(['Up to Parent Project', ascend]); }
  const menu = $('contextMenu');
  while (menu.firstChild) menu.removeChild(menu.firstChild);
  for (const item of items) {
    const li = document.createElement('li');
    if (item === null) li.className = 'sep';
    else { li.textContent = item[0]; li.addEventListener('click', () => { hideContextMenu(); item[1](); }); }
    menu.appendChild(li);
  }
  menu.style.left = evt.clientX + 'px'; menu.style.top = evt.clientY + 'px';
  menu.hidden = false;
});
async function viewDevice(index, action) {
  try {
    status('working...');
    const r = await api('view', { index, action });
    if (r.kind === 'project') {
      await showLevel(r.drawing);
      status('opened ' + r.drawing.filename + ' (read only)');
    } else {
      showResults(r.result, (r.result.waveforms.length ? 'Waveform: ' : 'S-parameters: ') + r.result.title, null);
      status('');
    }
  } catch (e) { error(e); }
}
async function ascend() {
  try { await showLevel(await api('ascend')); status('returned to ' + state.drawing.title); } catch (e) { error(e); }
}

// ---------- commands: one handler and one enable rule per GuiCore/Menus.py command id
const COMMANDS = {
  new: { run: newProject, always: true },
  open: { run: async () => { const f = await fileDialog('open'); if (f) await openProject(f); }, always: true },
  save: { run: async () => { try { status('saved ' + (await api('save')).filename); } catch (e) { error(e); } }, when: c => c.writable },
  saveAs: { run: saveAs, when: c => c.writable },
  archive: { run: archiveProject, when: c => c.writable },
  extractArchive: { run: extractArchive, always: true },
  exportNetlist: { run: () => exportAs('netlist'), when: c => c.open },
  exportTikz: { run: () => exportAs('tikz'), when: c => c.open },
  exportImage: { run: () => exportAs('image'), when: c => c.open },
  netlist: { run: showNetlist, when: c => c.open },
  undo: { run: () => edit('undo', {}, (d, before) => 'undid ' + before.undoName, true), when: c => c.writable && state.drawing.canUndo },
  redo: { run: () => edit('redo', {}, d => 'redid ' + d.undoName, true), when: c => c.writable && state.drawing.canRedo },
  cut: { run: () => edit('cut', { index: state.selected }, 'part cut (Ctrl+V pastes it)'), when: c => c.writable && c.device },
  copy: { run: () => edit('copy', { index: state.selected }, 'part copied (Ctrl+V pastes it)'), when: c => c.device },
  paste: { run: () => edit('paste', {}, 'part pasted - drag it into place'), when: c => c.writable && state.drawing.canPaste },
  duplicate: { run: () => edit('duplicate', { index: state.selected }, 'part duplicated - drag it into place'), when: c => c.writable && c.device },
  delete: { run: () => runCommand(selectedWire() !== null ? 'deleteWire' : 'deletePart'), when: c => c.writable && (c.device || c.wire) },
  cancel: { run: cancel, always: true },
  rotate: { run: rotate, when: c => c.writable && c.device },
  flipHorizontal: { run: () => edit('flipDevice', { index: state.selected, direction: 'horizontal' }, 'flipped horizontally'), when: c => c.writable && c.device },
  flipVertical: { run: () => edit('flipDevice', { index: state.selected, direction: 'vertical' }, 'flipped vertically'), when: c => c.writable && c.device },
  properties: { run: editProperties, when: c => c.open && c.device },
  deletePart: { run: deletePart, when: c => c.writable && c.device },
  wire: { run: () => (state.wiring ? stopWiring() : startWiring()), when: c => c.writable, checked: () => state.wiring },
  deleteVertex: { run: () => edit('deleteVertex', vertexParams(), 'wire corner deleted'), when: c => c.writable && c.vertex },
  duplicateVertex: { run: () => edit('duplicateVertex', vertexParams(), 'wire corner duplicated - drag it to make a bend'), when: c => c.writable && c.vertex },
  deleteWire: { run: deleteWire, when: c => c.writable && c.wire },
  zoomIn: { run: () => zoomAt(1.25, svg.clientWidth / 2, svg.clientHeight / 2), when: c => c.open, idle: true },
  zoomOut: { run: () => zoomAt(0.8, svg.clientWidth / 2, svg.clientHeight / 2), when: c => c.open, idle: true },
  zoomFit: { run: zoomFit, when: c => c.open, idle: true },
  viewDevice: { run: () => viewDevice(state.selected, preferredAction(state.viewActions)), when: c => c.device && c.viewable },
  up: { run: ascend, when: c => c.open && state.drawing.canAscend },
  postProcessing: { run: editPostProcessing, when: c => c.writable },
  equations: { run: editEquations, when: c => c.writable },
  help: { run: () => openHelp('introduction'), always: true, idle: true },
  documentation: { run: () => openHelp('documentation'), always: true, idle: true },
  preferences: { run: showPreferences, always: true },
  about: { run: showAbout, always: true, idle: true },
};
for (const kind of Object.keys(CALC_TITLES)) COMMANDS[kind] = { run: () => calculate(kind), when: c => c.open && !!c.caps[kind] };

function commandContext() {
  const open = !!state.drawing;
  return { open, writable: open && !readOnly(), device: open && state.selected !== null, wire: open && selectedWire() !== null,
    vertex: open && !!state.drawing.selectedVertex,
    viewable: !!(state.viewActions && state.viewActions.length), caps: open ? state.drawing.capabilities : {} };
}
const vertexParams = () => ({ wire: state.drawing.selectedVertex[0], vertex: state.drawing.selectedVertex[1] });
// runs an editing api method that returns the render; refreshAll also reloads the tables an undo can change
async function edit(method, params, message, refreshAll = false) {
  try {
    const before = state.drawing;
    const drawing = await api(method, params);
    await setDrawing(drawing);
    await (refreshAll ? Promise.all([refreshVariables(), refreshProperties(), refreshCalculationProperties()]) : refreshProperties());
    if (message) status(typeof message === 'function' ? message(drawing, before) : message);
  } catch (e) { error(e); }
}
function commandEnabled(id) {
  const cmd = COMMANDS[id];
  if (!cmd) return false;
  if (state.busy && !cmd.idle) return false;
  return cmd.always || cmd.when(commandContext());
}
function runCommand(id) {
  closeMenus();
  if (commandEnabled(id)) return COMMANDS[id].run();
}
function refreshCommands() {
  for (const b of $('toolbar').querySelectorAll('button[data-cmd]')) {
    b.disabled = !commandEnabled(b.dataset.cmd);
    const cmd = COMMANDS[b.dataset.cmd];
    b.classList.toggle('checked', !!(cmd && cmd.checked && cmd.checked()));
  }
}
async function newProject() {
  const f = await fileDialog('new');
  if (!f) return;
  try {
    closeResults(true);
    await showLevel(await api('new', { filename: f }));
    status('created ' + state.drawing.filename + '  -  drag parts from the Parts stencil onto the schematic');
  } catch (e) { error(e); }
}
async function saveAs() {
  const f = await fileDialog('save');
  if (!f) return;
  try { status('saved ' + (await api('save', { filename: f })).filename); await setDrawing(await api('render')); } catch (e) { error(e); }
}
async function rotate() {
  try { await setDrawing(await api('rotateDevice', { index: state.selected })); } catch (e) { error(e); }
}
async function deletePart() {
  try { await setDrawing(await api('deleteDevice', { index: state.selected })); await refreshProperties(); } catch (e) { error(e); }
}
async function deleteWire() {
  try { await setDrawing(await api('deleteWire', { index: selectedWire() })); status('wire deleted'); } catch (e) { error(e); }
}
function editProperties() {
  const input = $('properties').querySelector('input:not([type=checkbox]),select');
  if (input) input.focus();
}
function cancel() {
  hideContextMenu(); closeMenus();
  if (state.wiring) {
    if (state.wirePoints.length) { state.wirePoints = []; drawWirePreview(); }
    else { stopWiring(); status('wire mode off'); }
  } else if (state.placing !== null) { stopPlacing(); status('placement cancelled'); }
}
async function showNetlist() {
  try {
    $('textDialogTitle').textContent = 'Netlist';
    $('textDialogBody').textContent = (await api('netlist')).netlist;
    $('textDialog').showModal();
  } catch (e) { error(e); }
}
async function showAbout() {
  const { version } = await api('version');
  $('textDialogTitle').textContent = 'About SignalIntegrity';
  $('textDialogBody').textContent = 'SignalIntegrity ' + version + '\nSignal and power integrity tools\n\n' +
    'Copyright (c) 2021 Nubis Communications, Inc.\nCopyright (c) 2018-2020 Teledyne LeCroy, Inc.\nGNU General Public License v3 or later';
  $('textDialog').showModal();
}

// ---------- equations, post-processing, preferences and help
// resolves to the edited text, or null; check (optional) returns a promise of an error message or null
function editText(title, text, check, helpTopic) {
  return new Promise(resolve => {
    const dlg = $('editorDialog'), area = $('editorText');
    $('editorTitle').textContent = title;
    area.value = text;
    let timer = null;
    const runCheck = async () => {
      if (!check) { $('editorStatus').textContent = ''; return; }
      try { const e = await check(area.value); $('editorStatus').textContent = e ? e : 'No Errors'; } catch (e) { $('editorStatus').textContent = e.message; }
    };
    area.oninput = () => { clearTimeout(timer); timer = setTimeout(runCheck, 400); };
    area.onkeydown = e => {
      if (e.key !== 'Tab') return;
      e.preventDefault();
      const s = area.selectionStart;
      area.setRangeText('    ', s, area.selectionEnd, 'end');
    };
    const finish = value => { clearTimeout(timer); dlg.close(); resolve(value); };
    $('editorOk').onclick = () => finish(area.value);
    $('editorCancel').onclick = () => finish(null);
    $('editorHelp').style.display = helpTopic ? '' : 'none';
    $('editorHelp').onclick = () => openHelp(helpTopic);
    dlg.oncancel = () => resolve(null);
    runCheck();
    dlg.showModal();
    area.focus();
  });
}
async function editEquations() {
  try {
    const { text } = await api('equations');
    const edited = await editText('Schematic Equations', text, t => api('checkEquations', { text: t }).then(r => r.error), 'equations');
    if (edited === null) return;
    const r = await api('setEquations', { text: edited });
    await setDrawing(r.drawing);
    await Promise.all([refreshVariables(), refreshProperties()]);
    status(r.error ? 'equations stored, but they have an error: ' + r.error : 'equations applied');
  } catch (e) { error(e); }
}
async function editPostProcessing() {
  try {
    const { text } = await api('postProcessing');
    const edited = await editText('Post-Processing', text, null, 'postprocessing');
    if (edited === null) return;
    await setDrawing(await api('setPostProcessing', { text: edited }));
    status('post-processing applied');
  } catch (e) { error(e); }
}
async function openHelp(topic) {
  try { status('opened ' + (await api('help', { topic })).url); } catch (e) { error(e); }
}
async function showPreferences() {
  let prefs;
  try { prefs = await api('preferences'); } catch (e) { return error(e); }
  const tabs = $('prefsTabs'), form = $('prefsForm');
  clear(tabs);
  $('prefsStatus').textContent = 'Saved to ' + prefs.file;
  const showSection = section => {
    tabs.querySelectorAll('button').forEach(b => b.classList.toggle('active', b.textContent === section.label));
    clear(form);
    for (const item of section.items) {
      const label = document.createElement('label');
      label.append(item.label);
      const input = document.createElement('input');
      const save = async value => {
        try {
          const r = await api('setPreference', { path: item.path, value });
          item.value = r.value;
          $('prefsStatus').textContent = 'saved ' + item.path + ' = ' + r.value;
        } catch (e) { $('prefsStatus').textContent = e.message; }
      };
      if (item.type === 'bool') {
        input.type = 'checkbox'; input.checked = !!item.value;
        input.onchange = () => save(input.checked);
      } else {
        input.type = 'text'; input.spellcheck = false;
        input.value = item.value === null || item.value === 'None' ? '' : String(item.value);
        input.onchange = () => save(input.value);
      }
      label.appendChild(input);
      form.appendChild(label);
    }
  };
  for (const section of prefs.sections) {
    const b = document.createElement('button'); b.type = 'button'; b.textContent = section.label;
    b.onclick = () => showSection(section);
    tabs.appendChild(b);
  }
  if (prefs.sections.length) showSection(prefs.sections[0]);
  $('prefsClose').onclick = () => $('prefsDialog').close();
  $('prefsDialog').showModal();
}

// ---------- archives and exports
async function archiveProject() {
  try { status('archived to ' + (await api('archive')).filename); } catch (e) { error(e); }
}
async function extractArchive() {
  const f = await fileDialog('archive');
  if (!f) return;
  try {
    closeResults(true);
    await showLevel(await api('extractArchive', { filename: f }));
    status('extracted and opened ' + state.drawing.filename);
  } catch (e) { error(e); }
}
const EXPORTS = { netlist: 'exportNetlist', tikz: 'exportTikz', image: 'exportImage' };
async function exportAs(kind) {
  const f = await fileDialog('export-' + kind);
  if (!f) return;
  try { status('exported ' + (await api(EXPORTS[kind], { filename: f })).filename); } catch (e) { error(e); }
}

// ---------- menu bar (dropdowns) and toolbar, built from api('menus')
const SUBMENUS = { recent: recentItems, theme: themeItems };
let openMenu = null;
function closeMenus() {
  clear($('dropdowns'));
  for (const b of $('menubar').querySelectorAll('button.open')) b.classList.remove('open');
  openMenu = null;
}
function iconImg(id, size) {
  const svgText = state.menus && state.menus.icons[id];
  if (!svgText) return null;
  const img = document.createElement('img');
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgText);
  img.width = img.height = size; img.alt = '';
  return img;
}
function shortcutText(s) { return s ? s.replace('Del', 'Delete') : ''; }
// items: menu entries from Menus.py, or {label, run, checked, heading, disabled} built by a submenu
async function showDropdown(items, x, y, depth = 0) {
  const host = $('dropdowns');
  while (host.children.length > depth) host.lastChild.remove();
  const ul = document.createElement('ul'); ul.className = 'dropdown';
  for (const item of items) {
    const li = document.createElement('li');
    if (item.kind === 'separator') { li.className = 'sep'; ul.appendChild(li); continue; }
    if (item.heading) { li.className = 'heading'; li.textContent = item.label; ul.appendChild(li); continue; }
    const label = document.createElement('span'); label.className = 'label';
    const icon = item.kind === 'command' ? iconImg(item.id, 18) : null;
    if (icon) label.appendChild(icon);
    const named = (item.id === 'undo' || item.id === 'redo') && state.drawing && state.drawing[item.id + 'Name'];
    label.append(named ? item.label + ' ' + named : item.label);
    const keys = document.createElement('span'); keys.className = 'shortcut'; keys.textContent = shortcutText(item.shortcut);
    li.append(label, keys);
    if (item.kind === 'submenu') {
      li.classList.add('submenu');
      const open = async () => {
        for (const s of ul.querySelectorAll('li.open')) s.classList.remove('open');
        li.classList.add('open');
        const r = li.getBoundingClientRect();
        showDropdown(await SUBMENUS[item.id](), r.right - 2, r.top - 5, depth + 1);
      };
      li.addEventListener('pointerenter', open); li.addEventListener('click', open);
    } else {
      const enabled = item.kind === 'command' ? commandEnabled(item.id) : !item.disabled;
      const checked = item.kind === 'command' ? !!(COMMANDS[item.id] && COMMANDS[item.id].checked && COMMANDS[item.id].checked()) : item.checked;
      if (!enabled) li.classList.add('disabled');
      if (checked) li.classList.add('checked');
      if (item.title) li.title = item.title;
      li.addEventListener('pointerenter', () => { while (host.children.length > depth + 1) host.lastChild.remove(); });
      if (enabled) li.addEventListener('click', () => (item.kind === 'command' ? runCommand(item.id) : (closeMenus(), item.run())));
    }
    ul.appendChild(li);
  }
  host.appendChild(ul);
  ul.style.left = Math.max(0, Math.min(x, window.innerWidth - ul.offsetWidth - 4)) + 'px';
  ul.style.top = Math.max(0, Math.min(y, window.innerHeight - ul.offsetHeight - 4)) + 'px';
}
function buildMenus(spec) {
  state.menus = spec;
  const bar = $('menubar');
  for (const b of bar.querySelectorAll('button')) b.remove();
  for (const menu of spec.menus) {
    const b = document.createElement('button'); b.type = 'button'; b.textContent = menu.title;
    const open = () => {
      closeMenus(); b.classList.add('open'); openMenu = b;
      const r = b.getBoundingClientRect();
      showDropdown(menu.items, r.left, r.bottom);
    };
    b.addEventListener('click', () => (openMenu === b ? closeMenus() : open()));
    b.addEventListener('pointerenter', () => { if (openMenu && openMenu !== b) open(); });
    bar.appendChild(b);
  }
  const labels = {};
  for (const menu of spec.menus) for (const item of menu.items) if (item.kind === 'command') labels[item.id] = item;
  const toolbar = $('toolbar'); clear(toolbar);
  for (const id of spec.toolbar) {
    if (id === null) { const s = document.createElement('span'); s.className = 'sep'; toolbar.appendChild(s); continue; }
    const item = labels[id];
    const b = document.createElement('button'); b.type = 'button'; b.dataset.cmd = id;
    b.title = item.label.replace(/\.+$/, '') + (item.shortcut ? ' (' + shortcutText(item.shortcut) + ')' : '');
    const caption = document.createElement('span'); caption.textContent = spec.toolbarLabels[id] || item.label;
    const img = iconImg(id, spec.iconSize || 24);
    if (img) b.appendChild(img);
    b.appendChild(caption);
    b.addEventListener('click', () => runCommand(id));
    toolbar.appendChild(b);
  }
  refreshCommands();
}
document.addEventListener('pointerdown', e => {
  if (!e.target.closest('#dropdowns') && !e.target.closest('#menubar')) closeMenus();
});
async function recentItems() {
  let recent = [];
  try { recent = await api('recentProjects'); } catch (e) { /* show none */ }
  const items = recent.map((f, i) => ({ label: (i + 1) % 10 + '  ' + f.split(/[\\/]/).pop(), title: f, run: () => openProject(f), disabled: state.busy }));
  if (!items.length) items.push({ label: '(no recent projects)', disabled: true });
  items.push({ kind: 'separator' });
  items.push({ label: 'Clear Recent Projects', disabled: !recent.length, run: () => api('clearRecentProjects').then(() => status('recent projects cleared')) });
  return items;
}
async function themeItems() {
  let themes = [];
  try { themes = await api('themes'); } catch (e) { error(e); }
  const items = [];
  const groups = [['SignalIntegrity', t => t.extension === 'SignalIntegrity'],
    ['VS Code dark themes', t => t.extension !== 'SignalIntegrity' && !['vs', 'hc-light'].includes(t.uiTheme)],
    ['VS Code light themes', t => t.extension !== 'SignalIntegrity' && ['vs', 'hc-light'].includes(t.uiTheme)]];
  for (const [heading, rule] of groups) {
    const list = themes.filter(rule);
    if (!list.length) continue;
    items.push({ label: heading, heading: true });
    for (const t of list) items.push({ label: t.label, checked: !!(state.theme && state.theme.id === t.id), run: () => setTheme(t.id, t.label) });
  }
  items.push({ kind: 'separator' });
  items.push({ label: 'Load Theme File...', run: loadThemeFile });
  return items;
}

// ---------- tables
function checkCell(checked, enabled, onChange) {
  const td = document.createElement('td'); td.className = 'chk';
  const input = document.createElement('input'); input.type = 'checkbox';
  input.checked = checked; input.disabled = !enabled;
  input.addEventListener('change', () => onChange(input.checked));
  td.appendChild(input);
  return td;
}
function valueCell(row, onEdit) {
  const td = document.createElement('td');
  if (row.choices && row.choices.length) {
    const select = document.createElement('select');
    for (const c of row.choices) { const o = document.createElement('option'); o.value = o.textContent = c; select.appendChild(o); }
    select.value = row.value; select.disabled = row.readOnly;
    select.addEventListener('change', () => onEdit(row.key, select.value));
    td.appendChild(select);
  } else if (row.readOnly) { td.textContent = row.value; td.className = 'ro'; }
  else {
    const input = document.createElement('input');
    input.value = row.value; input.spellcheck = false;
    input.addEventListener('keydown', e => { if (e.key === 'Enter') input.blur(); if (e.key === 'Escape') { input.value = row.value; input.blur(); } });
    input.addEventListener('change', () => onEdit(row.key, input.value));
    td.appendChild(input);
  }
  return td;
}
function textCell(text, title) { const td = document.createElement('td'); td.textContent = text || ''; if (title) td.title = title; return td; }
function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }

async function afterEdit(promise) {
  try { await promise; await setDrawing(await api('render')); } catch (e) { error(e); }
  await Promise.all([refreshVariables(), refreshProperties()]);
}
async function refreshVariables() {
  const tbody = $('variables').tBodies[0]; clear(tbody);
  const vars = state.drawing ? await api('variables') : [];
  for (const v of vars) {
    const tr = document.createElement('tr');
    tr.appendChild(checkCell(v.visible, !readOnly(), checked => afterEdit(api('setVariableVisible', { name: v.name, visible: checked }))));
    tr.appendChild(textCell(v.name, v.description));
    tr.appendChild(valueCell({ key: v.name, value: v.value, readOnly: v.readOnly }, (name, value) => afterEdit(api('setVariable', { name, value }))));
    tr.appendChild(textCell(v.units));
    tbody.appendChild(tr);
  }
}
async function refreshProperties() {
  const tbody = $('properties').tBodies[0]; clear(tbody);
  const props = state.drawing && state.selected !== null ? await api('deviceProperties', { index: state.selected }) : [];
  const index = state.selected, writable = !readOnly();
  for (const p of props) {
    const tr = document.createElement('tr');
    tr.appendChild(checkCell(p.visible, writable, checked => afterEdit(api('setPropertyVisibility', { index, keyword: p.keyword, visible: checked }))));
    tr.appendChild(checkCell(p.keywordVisible, writable, checked => afterEdit(api('setPropertyVisibility', { index, keyword: p.keyword, keywordVisible: checked }))));
    tr.appendChild(textCell(p.description || p.name, p.description));
    tr.appendChild(valueCell({ key: p.keyword, value: p.value, readOnly: p.readOnly, choices: p.validEntries },
      (keyword, value) => afterEdit(api('setDeviceProperty', { index, keyword, value }))));
    tr.appendChild(textCell(p.unit));
    tbody.appendChild(tr);
  }
}
async function refreshCalculationProperties() {
  const form = $('calcProps'); clear(form);
  if (!state.drawing) return;
  const values = await api('calculationProperties');
  for (const [name, value] of Object.entries(values)) {
    const label = document.createElement('label');
    label.append(name);
    const input = document.createElement('input'); input.name = name; input.value = value; input.disabled = readOnly();
    label.appendChild(input); form.appendChild(label);
  }
  const apply = document.createElement('button'); apply.type = 'submit'; apply.textContent = 'Apply'; apply.disabled = readOnly();
  form.appendChild(apply);
}
$('calcProps').addEventListener('submit', async evt => {
  evt.preventDefault();
  const values = {};
  for (const input of $('calcProps').querySelectorAll('input')) {
    const v = Number(input.value);
    if (!isFinite(v)) return error(new Error(input.name + ' must be a number'));
    values[input.name] = input.name === 'FrequencyPoints' ? Math.round(v) : v;
  }
  try { await api('setCalculationProperties', { values }); status('calculation properties applied'); } catch (e) { error(e); }
  await refreshCalculationProperties();
});
async function selectDevice(index) {
  try { await setDrawing(await api('select', { index })); await refreshProperties(); } catch (e) { error(e); }
}

// ---------- files
async function openProject(filename) {
  try {
    closeResults(true);
    await showLevel(await api('open', { filename }));
    status('opened ' + state.drawing.filename);
  } catch (e) { error(e); }
}
function fileDialog(mode) {
  // mode: open | save | new | theme | archive | export-netlist | export-tikz | export-image
  const TITLES = { open: 'Open Project', save: 'Save Project As', new: 'New Project File', theme: 'Load Theme (VS Code .json or .vsix)',
    archive: 'Extract Archived Project (.siz)', 'export-netlist': 'Export NetList', 'export-tikz': 'Export LaTeX (TikZ: .TpX or .tex)',
    'export-image': 'Export Bitmap Image (.png or .jpg)' };
  const EXTENSIONS = { theme: ['.json', '.vsix'], archive: ['.siz'], 'export-netlist': ['.txt'], 'export-tikz': ['.tpx', '.tex'],
    'export-image': ['.png', '.jpg'] };
  const DEFAULT_EXTENSION = { 'export-netlist': '.txt', 'export-tikz': '.TpX', 'export-image': '.png' };
  const naming = mode === 'save' || mode === 'new' || mode.startsWith('export-');
  return new Promise(resolve => {
    const dlg = $('fileDialog');
    let current = null, chosen = null;
    $('fileDialogTitle').textContent = TITLES[mode];
    $('fileOk').textContent = naming ? (mode === 'new' ? 'Create' : mode.startsWith('export-') ? 'Export' : 'Save') : 'Open';
    const base = state.drawing ? state.drawing.title.replace(/\.si$/i, '') : '';
    $('fileName').value = mode === 'save' && state.drawing ? state.drawing.title : DEFAULT_EXTENSION[mode] ? base + DEFAULT_EXTENSION[mode] : '';
    $('fileName').style.display = naming ? '' : 'none';
    const finish = value => { dlg.close(); resolve(value); };
    const load = async path => {
      try {
        const params = path ? { path } : {};
        if (EXTENSIONS[mode]) params.extensions = EXTENSIONS[mode];
        const listing = await api('listDirectory', params);
        current = listing; $('filePath').value = listing.path;
        const ul = $('fileList'); clear(ul);
        for (const entry of listing.entries) {
          const li = document.createElement('li');
          li.textContent = entry.name; if (entry.directory) li.className = 'dir';
          li.addEventListener('click', () => {
            if (entry.directory) return load(entry.path);
            for (const x of ul.children) x.classList.remove('sel');
            li.classList.add('sel'); chosen = entry.path; $('fileName').value = entry.name;
          });
          li.addEventListener('dblclick', () => { if (!entry.directory) finish(entry.path); });
          ul.appendChild(li);
        }
      } catch (e) { error(e); }
    };
    $('fileUp').onclick = () => current && current.parent && load(current.parent);
    $('filePath').onkeydown = e => { if (e.key === 'Enter') load($('filePath').value); };
    $('fileCancel').onclick = () => finish(null);
    $('fileOk').onclick = () => {
      if (naming) {
        const name = $('fileName').value.trim();
        if (!name || !current) return;
        finish(current.path + (current.path.includes('\\') ? '\\' : '/') + name);
      } else finish(chosen);
    };
    dlg.oncancel = () => resolve(null);
    load(null);
    dlg.showModal();
  });
}

// ---------- parts stencil
const PART_TYPE = 'text/x-si-part';
function partThumbnail(part) {
  const s = el('svg', { viewBox: '0 0 1 1', preserveAspectRatio: 'xMidYMid meet' });
  const g = el('g', {}, s);
  renderPrimitives(g, part.preview.items, state.colorMap, true);
  const box = primitivesBox(part.preview.items, true);
  if (box) s.setAttribute('viewBox', `${box[0] - 2} ${box[1] - 2} ${box[2] - box[0] + 4} ${box[3] - box[1] + 4}`);
  return s;
}
function buildStencil() {
  const host = $('partGroups');
  const open = new Set([...host.querySelectorAll('details[open]')].map(d => d.dataset.group));
  clear(host);
  const groups = new Map();
  for (const part of state.catalog) {
    for (const group of part.categories.length ? part.categories : ['Miscellaneous']) {
      if (!groups.has(group)) groups.set(group, []);
      groups.get(group).push(part);
    }
  }
  for (const [group, parts] of groups) {
    const details = document.createElement('details');
    details.dataset.group = group;
    details.open = open.has(group);
    const summary = document.createElement('summary');
    const count = document.createElement('span'); count.className = 'count';
    summary.append(group, count);
    details.appendChild(summary);
    for (const part of parts) {
      const row = document.createElement('div');
      row.className = 'part'; row.draggable = true; row.dataset.part = part.index;
      row.dataset.search = (part.partname + ' ' + part.description + ' ' + part.categories.join(' ')).toLowerCase();
      row.title = part.partname + '\n' + part.description;
      const label = document.createElement('span'); label.textContent = part.description || part.partname;
      row.append(partThumbnail(part), label);
      row.addEventListener('dragstart', e => {
        e.dataTransfer.setData(PART_TYPE, String(part.index));
        e.dataTransfer.setData('text/plain', part.description);
        e.dataTransfer.effectAllowed = 'copy';
      });
      row.addEventListener('click', () => startPlacing(part.index));
      details.appendChild(row);
    }
    host.appendChild(details);
  }
  filterStencil();
}
function filterStencil() {
  const words = $('partSearch').value.toLowerCase().split(/\s+/).filter(Boolean);
  for (const details of $('partGroups').children) {
    let shown = 0;
    for (const row of details.querySelectorAll('.part')) {
      const show = words.every(w => row.dataset.search.includes(w));
      row.hidden = !show; shown += show;
    }
    details.hidden = shown === 0;
    details.querySelector('.count').textContent = '(' + shown + ')';
    if (words.length) details.open = shown > 0;
  }
}
$('partSearch').addEventListener('input', filterStencil);
function startPlacing(index) {
  if (!state.drawing || readOnly() || state.busy) return;
  stopPlacing();
  state.placing = index;
  svg.classList.add('placing');
  const row = $('partGroups').querySelector(`.part[data-part="${index}"]`);
  if (row) row.classList.add('armed');
  const part = state.catalog[index];
  status('click on the schematic to place ' + (part ? part.description : 'the part') + ' (Esc cancels)');
}
function stopPlacing() {
  state.placing = null;
  svg.classList.remove('placing');
  for (const row of $('partGroups').querySelectorAll('.part.armed')) row.classList.remove('armed');
}
async function addPart(index, p) {
  try {
    await setDrawing(await api('addPart', { part: index, x: p.x, y: p.y }));
    await refreshProperties();
    const d = state.drawing.devices[state.selected];
    status('added ' + (d ? (d.ref ? d.ref + ' ' : '') + d.partname : 'part'));
  } catch (e) { error(e); }
}
const canvasHost = $('canvasHost');
const acceptsPart = e => state.drawing && !readOnly() && !state.busy && [...e.dataTransfer.types].includes(PART_TYPE);
canvasHost.addEventListener('dragover', e => {
  if (!acceptsPart(e)) return;
  e.preventDefault(); e.dataTransfer.dropEffect = 'copy';
  canvasHost.classList.add('drop-target');
});
canvasHost.addEventListener('dragleave', () => canvasHost.classList.remove('drop-target'));
canvasHost.addEventListener('drop', e => {
  canvasHost.classList.remove('drop-target');
  if (!acceptsPart(e)) return;
  e.preventDefault();
  const index = parseInt(e.dataTransfer.getData(PART_TYPE), 10);
  if (Number.isInteger(index)) addPart(index, toScene(e));
});
async function loadStencil() {
  try { state.catalog = await api('partCatalog'); buildStencil(); } catch (e) { status('could not load the parts catalog: ' + e.message); }
}

// ---------- themes (VS Code color themes)
const CSS_VARS = { '--bg': 'panel', '--panel': 'panel', '--fg': 'panelForeground', '--border': 'border', '--accent': 'accent',
  '--toolbar': 'toolbar', '--button-bg': 'buttonBackground', '--button-fg': 'buttonForeground', '--input-bg': 'inputBackground',
  '--input-fg': 'inputForeground', '--selection': 'selection', '--selection-fg': 'selectionForeground', '--hover': 'hover',
  '--status-bg': 'statusBar', '--status-fg': 'statusBarForeground', '--canvas': 'schematicBackground',
  '--plot-bg': 'background', '--plot-fg': 'foreground', '--grid': 'grid', '--muted': 'grid' };
function applyTheme(theme) {
  state.theme = theme; state.palette = theme.palette; state.colorMap = theme.colorMap;
  const root = document.documentElement.style;
  for (const [name, key] of Object.entries(CSS_VARS)) if (theme.palette[key]) root.setProperty(name, theme.palette[key]);
  root.setProperty('color-scheme', theme.palette.dark ? 'dark' : 'light');
  COLORS.splice(0, COLORS.length, ...theme.palette.traces);
  if (state.drawing) renderPrimitives(viewport, state.drawing.items, state.colorMap);
  if (state.catalog.length) buildStencil();
  if ($('resultsDialog').open && currentTab) {
    if (currentTab.kind === 'waveforms') buildSelectionList();
    currentTab.show();
  }
}
async function setTheme(id, name) {
  try { applyTheme(await api('setTheme', name ? { id, name } : { id })); status('theme: ' + state.theme.name); } catch (e) { error(e); }
}
function choose(title, labels) {
  return new Promise(resolve => {
    const dlg = $('choiceDialog'), list = $('choiceList');
    $('choiceTitle').textContent = title; clear(list);
    labels.forEach((label, i) => { const o = document.createElement('option'); o.value = i; o.textContent = label; list.appendChild(o); });
    list.selectedIndex = 0;
    const finish = v => { dlg.close(); resolve(v); };
    $('choiceOk').onclick = () => finish(list.selectedIndex);
    list.ondblclick = () => finish(list.selectedIndex);
    $('choiceCancel').onclick = () => finish(null);
    dlg.oncancel = () => resolve(null);
    dlg.showModal();
  });
}
async function loadThemeFile() {
  const f = await fileDialog('theme');
  if (!f) return;
  if (!f.toLowerCase().endsWith('.vsix')) return setTheme(f);
  try {
    const themes = await api('themesInPackage', { path: f });
    if (!themes.length) return error(new Error('no color themes in ' + f));
    const i = themes.length === 1 ? 0 : await choose('Choose a theme', themes.map(t => t.label));
    if (i !== null) await setTheme(themes[i].id, themes[i].label);
  } catch (e) { error(e); }
}
$('textDialogClose').onclick = () => $('textDialog').close();

// ---------- calculation
async function calculate(kind) {
  state.busy = true; updateEnables();
  const dlg = $('progressDialog');
  $('progressTitle').textContent = CALC_TITLES[kind] + '...';
  $('progressBar').value = 0;
  let job;
  try {
    job = await api('calculate', { kind });
    $('progressCancel').onclick = () => api('cancel', { id: job.id }).catch(() => {});
    dlg.showModal();
    while (job.state === 'running') {
      await new Promise(r => setTimeout(r, 150));
      job = await api('job', { id: job.id });
      $('progressBar').value = Math.max(0, Math.min(100, job.progress));
    }
  } catch (e) {
    job = { state: 'failed', error: e.message };
  } finally {
    dlg.close();
    state.busy = false;
    updateEnables();
  }
  if (job.state === 'done') {
    state.lastCalculation = kind;
    showResults(job.result, (job.result.waveforms.length ? 'Sim: ' : CALC_TITLES[kind] + ': ') + state.drawing.title, kind);
    status(CALC_TITLES[kind] + ' complete');
  } else error(new Error(job.error || 'calculation failed'));
}

// ---------- results: a port of the tk simulator dialog
// the simulator view keeps its zoom and selections across recalculations, like SimulatorDialog
const sim = { result: null, selected: {}, view: 'time', limits: null, divisor: 1, recalculable: null, fetchSeq: 0 };
let currentTab = null;
const plot = new Plot($('resultsPlot'), {
  onViewChange: limits => { if (currentTab && currentTab.kind === 'waveforms') { sim.limits = limits; fetchSeries(); } },
  onCursor: p => { $('resultsStatus').textContent = p ? 'x=' + p[0].toPrecision(6) + '  y=' + p[1].toPrecision(6) : statusText(); },
});
function setPlotMode(mode) {
  plot.setMode(mode);
  $('plotPan').classList.toggle('active', mode === 'pan');
  $('plotZoom').classList.toggle('active', mode === 'zoom');
}
$('plotPan').onclick = () => setPlotMode(plot.mode === 'pan' ? 'none' : 'pan');
$('plotZoom').onclick = () => setPlotMode(plot.mode === 'zoom' ? 'none' : 'zoom');
$('plotHome').onclick = () => plot.home();
$('plotBack').onclick = () => plot.back();
$('plotForward').onclick = () => plot.forward();
$('plotGrid').onchange = () => { plot.grid = $('plotGrid').checked; plot.draw(); };
$('plotAutoscale').onclick = () => { if (currentTab) currentTab.autoscale(); };
$('simView').onchange = () => { sim.view = $('simView').value; sim.limits = null; drawWaveforms(); };
$('simLog').onchange = () => drawWaveforms();
$('simRecalculate').onclick = () => { if (sim.recalculable && !state.busy) calculate(sim.recalculable); };
$('selAll').onclick = () => setSelections(() => true);
$('selNone').onclick = () => setSelections(() => false);
$('selToggle').onclick = () => setSelections(v => !v);
$('resultsClose').onclick = () => closeResults(false);
function closeResults(forget) {
  $('resultsDialog').close();
  if (forget) { sim.result = null; sim.limits = null; sim.selected = {}; }
}

function selectedIndices() { return sim.result ? sim.result.waveforms.filter(w => sim.selected[w.name] !== false).map(w => w.index) : []; }
function setSelections(rule) {
  for (const w of sim.result.waveforms) sim.selected[w.name] = rule(sim.selected[w.name] !== false);
  buildSelectionList(); drawWaveforms();
}
function statusText() {
  if (!currentTab || currentTab.kind !== 'waveforms' || !sim.result) return '';
  const idx = selectedIndices();
  if (idx.length === 0) return 'No Waveforms';
  if (idx.length > 1) return 'Multiple Waveforms';
  const w = sim.result.waveforms[idx[0]];
  if (w.dc !== null) return 'DC waveform  = ' + w.dc;
  const e = v => { const u = engineering(v, ''); return +(v / u.divisor).toPrecision(6) + ' ' + u.label; };
  return w.points + ' Pts starting at ' + e(w.start) + 's at ' + e(w.sampleRate) + 'S/s (T = ' + e(1 / w.sampleRate) + 's)';
}
function buildSelectionList() {
  const list = $('selectionList'); clear(list);
  for (const w of sim.result.waveforms) {
    const label = document.createElement('label');
    const input = document.createElement('input'); input.type = 'checkbox';
    input.checked = sim.selected[w.name] !== false;
    input.onchange = () => { sim.selected[w.name] = input.checked; drawWaveforms(); };
    const swatch = document.createElement('span'); swatch.className = 'swatch'; swatch.style.background = COLORS[w.index % COLORS.length];
    label.append(input, swatch, w.name);
    list.appendChild(label);
  }
}
function axisInfo(view, limits) {
  if (!limits || limits[0] === null || limits[1] === null) return { divisor: 1, label: view === 'time' ? 's' : 'Hz' };
  return engineering(limits[1] - limits[0], view === 'time' ? 's' : 'Hz');
}
// first draw of a view autoscales; afterwards the user's zoom is kept, as in the tk dialog
async function drawWaveforms() {
  if (!sim.result) return;
  const view = sim.view, indices = selectedIndices();
  $('plotLabel').textContent = view === 'time' ? 'Time-domain View' : view === 'content' ? 'Spectral Content' : 'Spectral Density';
  plot.logX = view !== 'time' && $('simLog').checked;
  try {
    const full = await api('plotData', { resultId: sim.result.resultId, view, indices, points: 16 });
    const auto = full.autoscale;
    const axis = axisInfo(view, auto);
    sim.divisor = axis.divisor;
    const adder = view === 'density' ? 10 * Math.log10(axis.divisor) : 0;
    sim.adder = adder;
    sim.xLabel = (view === 'time' ? 'time (' : 'frequency (') + axis.label + ')';
    sim.yLabel = view === 'time' ? 'amplitude' : view === 'content' ? 'magnitude (dBm)' : 'magnitude (dBm/' + axis.label + ')';
    const autoLimits = auto[0] === null ? [0, 1, 0, 1] : [auto[0] / axis.divisor, auto[1] / axis.divisor,
      (auto[2] ?? 0) + adder, (auto[3] ?? 1) + adder];
    if (autoLimits[2] === autoLimits[3]) { autoLimits[2] -= 1; autoLimits[3] += 1; }
    if (plot.logX && autoLimits[0] <= 0) {
      const s = full.series.find(x => x.x.some(v => v > 0));
      if (s) autoLimits[0] = s.x.find(v => v > 0) / axis.divisor;
    }
    sim.autoLimits = autoLimits;
    if (!sim.limits) plot.setLimits(autoLimits, { resetHistory: true });
    else plot.setLimits(sim.limits);
    sim.limits = plot.limits.slice();
    await fetchSeries();
  } catch (e) { error(e); }
}
// fetches only the visible x range at screen resolution, so long waveforms stay complete when zoomed
async function fetchSeries() {
  const seq = ++sim.fetchSeq;
  const [x0, x1] = plot.limits;
  const span = x1 - x0;
  const r = await api('plotData', { resultId: sim.result.resultId, view: sim.view, indices: selectedIndices(),
    xmin: (x0 - span * 0.05) * sim.divisor, xmax: (x1 + span * 0.05) * sim.divisor,
    points: Math.max(400, Math.round(($('resultsPlot').clientWidth || 800) * 2)) });
  if (seq !== sim.fetchSeq) return;
  plot.setData(r.series.map(s => ({ name: s.name, color: COLORS[s.index % COLORS.length], dc: s.dc,
    x: s.x.map(v => v / sim.divisor), y: s.y.map(v => v === null ? null : v + sim.adder) })), sim.xLabel, sim.yLabel);
  $('resultsStatus').textContent = statusText();
}

function sparameterTab(sp, quantity) {
  const range = sp.frequencies.length > 1 ? sp.frequencies[sp.frequencies.length - 1] - sp.frequencies[0] : 1;
  const axis = engineering(range, 'Hz');
  const f = sp.frequencies.map(v => v / axis.divisor);
  const series = sp.traces.map((t, i) => ({ name: sp.ports <= 4 ? t.name : '', color: COLORS[i % COLORS.length], x: f, y: t[quantity] }));
  const limits = () => {
    let lo = Infinity, hi = -Infinity;
    for (const s of series) for (const v of s.y) if (v !== null && v > -2999) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
    if (!(hi > lo)) { lo -= 1; hi += 1; }
    return [f[0], f[f.length - 1] > f[0] ? f[f.length - 1] : f[0] + 1, lo, hi];
  };
  return {
    kind: 'sparameters', name: sp.name + (quantity === 'dB' ? ' magnitude' : ' phase'), state: null,
    show() {
      $('plotLabel').textContent = this.name;
      plot.logX = false;
      plot.setData(series, 'frequency (' + axis.label + ')', quantity === 'dB' ? 'magnitude (dB)' : 'phase (degrees)');
      if (this.state) { plot.history = this.state.history; plot.historyIndex = this.state.historyIndex; plot.setLimits(this.state.limits); }
      else plot.setLimits(limits(), { resetHistory: true });
    },
    hide() { this.state = { limits: plot.limits.slice(), history: plot.history, historyIndex: plot.historyIndex }; },
    autoscale() { plot.setLimits(limits()); plot._push(); },
  };
}

// a plot tab whose traces are loaded on first show: load() resolves to [{name,index?,x,y}] in SI units;
// opts: xUnit, xPrefix ('time', 'frequency', ...), yLabel and density (y in dB per Hz, rescaled per x unit)
function seriesTab(name, load, opts) {
  let cache = null, scaled = null;
  const tab = {
    kind: 'series', name, state: null,
    async show() {
      $('plotLabel').textContent = name;
      plot.logX = false;
      try { if (!cache) cache = await load(); } catch (e) { $('resultsStatus').textContent = e.message; return; }
      if (currentTab !== tab) return;
      let lo = Infinity, hi = -Infinity;
      for (const t of cache) for (const v of t.x) if (v !== null) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
      const axis = engineering(hi > lo ? hi - lo : 1, opts.xUnit);
      const adder = opts.density ? 10 * Math.log10(axis.divisor) : 0;
      scaled = cache.map((t, i) => ({ name: cache.length <= 16 ? t.name : '', color: COLORS[(t.index ?? i) % COLORS.length],
        x: t.x.map(v => v === null ? null : v / axis.divisor), y: t.y.map(v => v === null ? null : v + adder) }));
      tab.adder = adder; tab.divisor = axis.divisor;
      plot.setData(scaled, opts.xPrefix + ' (' + axis.label + ')', opts.yLabel + (opts.density ? '/' + axis.label + ')' : ''));
      if (this.state) { plot.history = this.state.history; plot.historyIndex = this.state.historyIndex; plot.setLimits(this.state.limits); }
      else plot.setLimits(this.limits(), { resetHistory: true });
    },
    limits() {
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      for (const s of scaled || []) {
        for (const v of s.x) if (v !== null) { x0 = Math.min(x0, v); x1 = Math.max(x1, v); }
        for (const v of s.y) if (v !== null && isFinite(v)) { y0 = Math.min(y0, v); y1 = Math.max(y1, v); }
      }
      if (tab.serverLimits && tab.serverLimits[2] !== null) { y0 = tab.serverLimits[2] + tab.adder; y1 = tab.serverLimits[3] + tab.adder; }
      if (!(x1 > x0)) { x0 = 0; x1 = 1; }
      if (!(y1 > y0)) { y0 -= 1; y1 += 1; }
      const pad = (y1 - y0) * 0.05;
      return [x0, x1, y0 - pad, y1 + pad];
    },
    hide() { if (scaled) this.state = { limits: plot.limits.slice(), history: plot.history, historyIndex: plot.historyIndex }; },
    autoscale() { plot.setLimits(this.limits()); plot._push(); },
  };
  return tab;
}
function buildNoiseTable(measurements) {
  const host = $('noiseTable'); clear(host);
  const table = document.createElement('table');
  const head = document.createElement('tr');
  for (const h of ['Output / contribution', 'RMS', 'dBm', 'RMS density', 'dBm density', 'SNR (dB)', 'Salz SNR (dB)']) {
    const th = document.createElement('th'); th.textContent = h; head.appendChild(th);
  }
  table.appendChild(head);
  const si = (v, unit) => { if (v === null || v === undefined) return ''; const u = engineering(Math.abs(v) || 1, unit); return +(v / u.divisor).toPrecision(4) + ' ' + u.label; };
  const db = v => v === null || v === undefined ? '' : v.toFixed(2);
  const row = (cells, sub) => {
    const tr = document.createElement('tr');
    cells.forEach((c, i) => { const td = document.createElement('td'); td.textContent = c; if (sub && i === 0) td.className = 'sub'; tr.appendChild(td); });
    table.appendChild(tr);
  };
  for (const m of measurements) {
    const unit = m.type === 'current' ? 'A' : 'V';
    row([m.name, si(m.rms, unit), db(m.dBm), si(m.rmsPerRootHz, unit + '/rtHz'), m.dBmPerHz === null ? '' : db(m.dBmPerHz) + ' /Hz', db(m.SNR), db(m.SalzSNR)]);
    for (const c of m.contributions) row(['from ' + c.name, si(c.rms, unit), db(c.dBm), '', '', db(c.SNR), ''], true);
  }
  host.appendChild(table);
}

function showResults(result, title, recalculable) {
  const dlg = $('resultsDialog');
  const tabs = [];
  if (result.waveforms.length) {
    // keep zoom and selections when the same waveforms come back from a recalculation
    const sameSet = sim.result && recalculable && sim.recalculable === recalculable;
    if (!sameSet) { sim.limits = null; sim.selected = {}; }
    sim.result = result;
    sim.recalculable = recalculable;
    tabs.push({
      kind: 'waveforms', name: 'Waveforms',
      show() { buildSelectionList(); drawWaveforms(); },
      hide() { sim.history = { history: plot.history, historyIndex: plot.historyIndex }; },
      autoscale() { plot.setLimits(sim.autoLimits); sim.limits = plot.limits.slice(); plot._push(); },
    });
  }
  result.sparameters.forEach((sp, k) => {
    tabs.push(sparameterTab(sp, 'dB')); tabs.push(sparameterTab(sp, 'deg'));
    for (const [view, xPrefix, yLabel] of [['impulse', 'time', 'amplitude'], ['step', 'time', 'amplitude'], ['impedance', 'length', 'impedance (Ohms)']]) {
      tabs.push(seriesTab(sp.name + ' ' + view, () => api('sparameterTime', { resultId: result.resultId, index: k, view, points: 4000 })
        .then(r => r.traces), { xUnit: 's', xPrefix, yLabel }));
    }
  });
  if (result.noise && result.noise.length) {
    const tab = seriesTab('Statistical Noise', () => api('noiseSeries', { resultId: result.resultId, points: 4000 })
      .then(r => { tab.serverLimits = r.autoscale; return r.series; }), { xUnit: 'Hz', xPrefix: 'frequency', yLabel: 'magnitude (dBm', density: true });
    tab.kind = 'noise';
    tab.measurements = result.noise;
    tabs.push(tab);
  }
  for (const eye of result.eyes) {
    tabs.push({ kind: 'eye', name: 'Eye: ' + eye.name, show() { $('eyeImage').src = eye.image; }, hide() {}, autoscale() {} });
  }
  $('resultsTitle').textContent = title;
  const nav = $('resultsTabs'); clear(nav);
  const activate = i => {
    if (currentTab) currentTab.hide();
    currentTab = tabs[i];
    nav.querySelectorAll('button').forEach((b, k) => b.classList.toggle('active', k === i));
    const isWave = currentTab.kind === 'waveforms', isEye = currentTab.kind === 'eye', isNoise = currentTab.kind === 'noise';
    $('simControls').style.display = isWave ? '' : 'none';
    $('plotToolbar').style.display = isEye ? 'none' : '';
    $('resultsStatus').textContent = isEye ? '' : statusText();
    $('simRecalculate').disabled = !sim.recalculable;
    $('resultsBody').classList.toggle('no-selection', !isWave);
    $('resultsBody').classList.toggle('eye', isEye);
    $('selectionList').style.display = isWave ? '' : 'none';
    dlg.classList.toggle('noise', isNoise);
    if (isNoise) buildNoiseTable(currentTab.measurements);
    currentTab.show();
  };
  tabs.forEach((t, i) => { const b = document.createElement('button'); b.textContent = t.name; b.onclick = () => activate(i); nav.appendChild(b); });
  nav.style.display = tabs.length > 1 ? '' : 'none';
  if (!dlg.open) dlg.show();
  currentTab = null;
  setPlotMode(plot.mode === 'none' ? 'none' : plot.mode);
  if (tabs.length) activate(0);
}

// ---------- keyboard
// shortcuts come from Menus.py, e.g. 'Ctrl+Shift+S', 'Alt+Up', 'Del', 'W'
const KEY_NAMES = { ArrowUp: 'Up', ArrowDown: 'Down', ArrowLeft: 'Left', ArrowRight: 'Right', Delete: 'Del', Backspace: 'Del',
  Escape: 'Esc', '=': '+' };
const TEXT_EDITING_KEYS = new Set(['Ctrl+Z', 'Ctrl+Shift+Z', 'Ctrl+X', 'Ctrl+C', 'Ctrl+V']);
function keyCombo(e) {
  const key = KEY_NAMES[e.key] || (e.key.length === 1 ? e.key.toUpperCase() : e.key);
  // Shift counts for letters and named keys; for punctuation like '+' it is part of the character
  const shift = e.shiftKey && /^([A-Z0-9]|[A-Z][a-z]+)$/.test(key);
  return [(e.ctrlKey || e.metaKey) && 'Ctrl', shift && 'Shift', e.altKey && 'Alt', key].filter(Boolean).join('+');
}
window.addEventListener('keydown', e => {
  if (document.querySelector('dialog[open]:modal') || !state.menus) return;
  if (state.wiring && e.key === 'Enter') { e.preventDefault(); return finishWire(); }
  const typing = /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement && document.activeElement.tagName);
  const combo = keyCombo(e);
  for (const menu of state.menus.menus) for (const item of menu.items) {
    if (item.kind !== 'command' || item.shortcut !== combo) continue;
    // while typing, single keys and the text-editing shortcuts belong to the text field
    if (typing && item.id !== 'cancel' && (!/^(Ctrl|Alt)\+/.test(combo) || TEXT_EDITING_KEYS.has(combo))) return;
    e.preventDefault();
    return runCommand(item.id);
  }
});

// ---------- start-up
(async () => {
  updateEnables();
  initDock(token ? { load: () => api('layout'), store: layout => api('setLayout', { layout }) }
    : { load: () => null, store: () => {} });
  if (!token) return status('No access token - start the GUI from SignalIntegrityServer or the desktop app.');
  try {
    const { version } = await api('version');
    status('SignalIntegrity ' + version + ' - open a project (.si) to begin');
    buildMenus(await api('menus'));
    applyTheme(await api('theme'));
    await loadStencil();
    await showLevel(await api('render'));
    status('opened ' + state.drawing.filename);
  } catch (e) { /* no project open yet */ }
})();
