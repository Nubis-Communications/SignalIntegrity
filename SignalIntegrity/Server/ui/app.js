// SignalIntegrity web GUI - talks to SignalIntegrity.Server over a token-protected local JSON API.
import { el, renderPrimitives } from './schematic.js';
import { Plot, COLORS, engineering } from './plot.js';

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
const state = { drawing: null, selected: null, busy: false, view: { s: 1, tx: 0, ty: 0 }, lastCalculation: null };
const svg = $('schematic'), viewport = $('viewport');

function status(text) { $('status').textContent = text; }
function error(e) { status('Error: ' + (e.message || e)); alert(e.message || e); }
const readOnly = () => !!(state.drawing && state.drawing.readOnly);

function updateEnables() {
  const open = !!state.drawing, busy = state.busy, ro = readOnly();
  const caps = open ? state.drawing.capabilities : {};
  $('btnOpen').disabled = busy;
  for (const id of ['btnSave', 'btnSaveAs']) $(id).disabled = !open || busy || ro;
  $('btnNetlist').disabled = !open || busy;
  $('btnRotate').disabled = !open || busy || ro || state.selected === null;
  $('btnView').disabled = !open || busy || state.selected === null || !(state.viewActions && state.viewActions.length);
  $('btnUp').disabled = !open || busy || !state.drawing.canAscend;
  for (const b of document.querySelectorAll('button.calc')) b.disabled = !open || busy || !caps[b.dataset.kind];
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
  renderPrimitives(viewport, drawing.items);
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
  hideContextMenu();
  if (evt.button !== 0 || !state.drawing || state.busy) return;
  svg.setPointerCapture(evt.pointerId);
  const p = toScene(evt);
  const index = deviceAt(p);
  if (index !== null) {
    if (index !== state.selected) await selectDevice(index);
    if (readOnly()) return;
    const d = state.drawing.devices.find(x => x.index === index);
    const [x0, y0, x1, y1] = d.bbox;
    const ghost = el('rect', { x: Math.min(x0, x1), y: Math.min(y0, y1), width: Math.abs(x1 - x0), height: Math.abs(y1 - y0),
      fill: 'none', stroke: '#0a64c8', 'stroke-dasharray': '4 3', visibility: 'hidden' }, viewport);
    drag = { kind: 'device', index, start: p, ghost, dx: 0, dy: 0 };
  } else {
    if (state.selected !== null) await selectDevice(null);
    drag = { kind: 'pan', x: evt.clientX, y: evt.clientY };
    svg.classList.add('panning');
  }
});
svg.addEventListener('pointermove', evt => {
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

// ---------- device context menu: the tk View / Open Project actions
function hideContextMenu() { $('contextMenu').hidden = true; }
document.addEventListener('pointerdown', e => { if (!$('contextMenu').contains(e.target)) hideContextMenu(); });
function preferredAction(actions) {
  const keys = actions.map(a => a.action);
  return keys.includes('openproject') ? 'openproject' : keys[0];
}
svg.addEventListener('contextmenu', async evt => {
  evt.preventDefault();
  if (!state.drawing || state.busy) return;
  const index = deviceAt(toScene(evt));
  if (index === null) return;
  if (index !== state.selected) await selectDevice(index);
  const actions = state.viewActions || [];
  if (evt.ctrlKey && actions.length) return viewDevice(index, preferredAction(actions));
  const items = actions.map(a => [a.label, () => viewDevice(index, a.action)]);
  if (!readOnly()) {
    if (items.length) items.push(null);
    items.push(['Edit Properties', () => { const i = $('properties').querySelector('input:not([type=checkbox]),select'); if (i) i.focus(); }]);
    items.push(['Rotate', () => $('btnRotate').click()]);
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
$('btnView').onclick = () => state.selected !== null && state.viewActions.length && viewDevice(state.selected, preferredAction(state.viewActions));
$('btnUp').onclick = ascend;

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
  return new Promise(resolve => {
    const dlg = $('fileDialog');
    let current = null, chosen = null;
    $('fileDialogTitle').textContent = mode === 'open' ? 'Open Project' : 'Save Project As';
    $('fileOk').textContent = mode === 'open' ? 'Open' : 'Save';
    $('fileName').value = mode === 'save' && state.drawing ? state.drawing.title : '';
    $('fileName').style.display = mode === 'save' ? '' : 'none';
    const finish = value => { dlg.close(); resolve(value); };
    const load = async path => {
      try {
        const listing = await api('listDirectory', path ? { path } : {});
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
      if (mode === 'save') {
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
$('btnOpen').onclick = async () => { const f = await fileDialog('open'); if (f) await openProject(f); };
$('btnSave').onclick = async () => { try { status('saved ' + (await api('save')).filename); } catch (e) { error(e); } };
$('btnSaveAs').onclick = async () => {
  const f = await fileDialog('save');
  if (!f) return;
  try { status('saved ' + (await api('save', { filename: f })).filename); await setDrawing(await api('render')); } catch (e) { error(e); }
};
$('btnZoomIn').onclick = () => zoomAt(1.25, svg.clientWidth / 2, svg.clientHeight / 2);
$('btnZoomOut').onclick = () => zoomAt(0.8, svg.clientWidth / 2, svg.clientHeight / 2);
$('btnZoomFit').onclick = zoomFit;
$('btnRotate').onclick = async () => {
  if (state.selected === null) return;
  try { await setDrawing(await api('rotateDevice', { index: state.selected })); } catch (e) { error(e); }
};
$('btnNetlist').onclick = async () => {
  try {
    $('textDialogTitle').textContent = 'Netlist';
    $('textDialogBody').textContent = (await api('netlist')).netlist;
    $('textDialog').showModal();
  } catch (e) { error(e); }
};
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
for (const b of document.querySelectorAll('button.calc')) b.onclick = () => calculate(b.dataset.kind);

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
  for (const sp of result.sparameters) { tabs.push(sparameterTab(sp, 'dB')); tabs.push(sparameterTab(sp, 'deg')); }
  for (const eye of result.eyes) {
    tabs.push({ kind: 'eye', name: 'Eye: ' + eye.name, show() { $('eyeImage').src = eye.image; }, hide() {}, autoscale() {} });
  }
  $('resultsTitle').textContent = title;
  const nav = $('resultsTabs'); clear(nav);
  const activate = i => {
    if (currentTab) currentTab.hide();
    currentTab = tabs[i];
    nav.querySelectorAll('button').forEach((b, k) => b.classList.toggle('active', k === i));
    const isWave = currentTab.kind === 'waveforms', isEye = currentTab.kind === 'eye';
    $('simControls').style.display = isWave ? '' : 'none';
    $('plotToolbar').style.display = isEye ? 'none' : '';
    $('resultsStatus').textContent = isEye ? '' : statusText();
    $('simRecalculate').disabled = !sim.recalculable;
    $('resultsBody').classList.toggle('no-selection', !isWave);
    $('resultsBody').classList.toggle('eye', isEye);
    $('selectionList').style.display = isWave ? '' : 'none';
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
window.addEventListener('keydown', e => {
  if (document.querySelector('dialog[open]:modal')) return;
  if (e.altKey && e.key === 'ArrowUp' && !$('btnUp').disabled) { e.preventDefault(); return ascend(); }
  if (!(e.ctrlKey || e.metaKey)) return;
  const k = e.key.toLowerCase();
  const map = { o: 'btnOpen', s: 'btnSave', r: 'btnRotate', e: 'btnView', 0: 'btnZoomFit' };
  if (map[k] && !$(map[k]).disabled) { e.preventDefault(); $(map[k]).click(); }
});

// ---------- start-up
(async () => {
  updateEnables();
  if (!token) return status('No access token - start the GUI from SignalIntegrityServer or the desktop app.');
  try {
    const { version } = await api('version');
    status('SignalIntegrity ' + version + ' - open a project (.si) to begin');
    await showLevel(await api('render'));
    status('opened ' + state.drawing.filename);
  } catch (e) { /* no project open yet */ }
})();
