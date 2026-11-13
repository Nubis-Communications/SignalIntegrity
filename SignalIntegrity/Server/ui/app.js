// SignalIntegrity web GUI - talks to SignalIntegrity.Server over a token-protected local JSON API.
import { el, renderPrimitives, primitivesBox } from './schematic.js';
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
const state = { drawing: null, selected: null, busy: false, view: { s: 1, tx: 0, ty: 0 }, lastCalculation: null,
  colorMap: null, palette: null, theme: null, catalog: [], placing: null };
const svg = $('schematic'), viewport = $('viewport');

function status(text) { $('status').textContent = text; }
function error(e) { status('Error: ' + (e.message || e)); alert(e.message || e); }
const readOnly = () => !!(state.drawing && state.drawing.readOnly);

function updateEnables() {
  const open = !!state.drawing, busy = state.busy, ro = readOnly();
  const caps = open ? state.drawing.capabilities : {};
  $('btnOpen').disabled = busy;
  $('btnNew').disabled = busy;
  for (const id of ['btnSave', 'btnSaveAs']) $(id).disabled = !open || busy || ro;
  $('btnNetlist').disabled = !open || busy;
  $('btnRotate').disabled = !open || busy || ro || state.selected === null;
  $('btnDelete').disabled = !open || busy || ro || state.selected === null;
  $('parts').classList.toggle('disabled', !open || busy || ro);
  if ((!open || busy || ro) && state.placing !== null) stopPlacing();
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
  renderPrimitives(viewport, drawing.items, state.colorMap);
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
    items.push(['Delete', () => $('btnDelete').click()]);
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
  // mode: open | save | new | theme
  const TITLES = { open: 'Open Project', save: 'Save Project As', new: 'New Project File', theme: 'Load Theme (VS Code .json or .vsix)' };
  const naming = mode === 'save' || mode === 'new';
  return new Promise(resolve => {
    const dlg = $('fileDialog');
    let current = null, chosen = null;
    $('fileDialogTitle').textContent = TITLES[mode];
    $('fileOk').textContent = naming ? (mode === 'new' ? 'Create' : 'Save') : 'Open';
    $('fileName').value = mode === 'save' && state.drawing ? state.drawing.title : '';
    $('fileName').style.display = naming ? '' : 'none';
    const finish = value => { dlg.close(); resolve(value); };
    const load = async path => {
      try {
        const params = path ? { path } : {};
        if (mode === 'theme') params.extensions = ['.json', '.vsix'];
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
$('btnOpen').onclick = async () => { const f = await fileDialog('open'); if (f) await openProject(f); };
$('btnNew').onclick = async () => {
  const f = await fileDialog('new');
  if (!f) return;
  try {
    closeResults(true);
    await showLevel(await api('new', { filename: f }));
    status('created ' + state.drawing.filename + '  -  drag parts from the Parts stencil onto the schematic');
  } catch (e) { error(e); }
};
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
$('btnDelete').onclick = async () => {
  if (state.selected === null || readOnly()) return;
  try { await setDrawing(await api('deleteDevice', { index: state.selected })); await refreshProperties(); } catch (e) { error(e); }
};

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
function hideThemeMenu() { $('themeMenu').hidden = true; }
document.addEventListener('pointerdown', e => { if (!$('themeMenu').contains(e.target) && e.target !== $('btnTheme')) hideThemeMenu(); });
$('btnTheme').onclick = async () => {
  const menu = $('themeMenu');
  if (!menu.hidden) return hideThemeMenu();
  let themes;
  try { themes = await api('themes'); } catch (e) { return error(e); }
  clear(menu);
  const add = (text, cls, onClick) => {
    const li = document.createElement('li'); li.textContent = text; if (cls) li.className = cls;
    if (onClick) li.addEventListener('click', () => { hideThemeMenu(); onClick(); });
    menu.appendChild(li);
  };
  const groups = [['SignalIntegrity', t => t.extension === 'SignalIntegrity'],
    ['VS Code dark themes', t => t.extension !== 'SignalIntegrity' && !['vs', 'hc-light'].includes(t.uiTheme)],
    ['VS Code light themes', t => t.extension !== 'SignalIntegrity' && ['vs', 'hc-light'].includes(t.uiTheme)]];
  for (const [heading, rule] of groups) {
    const list = themes.filter(rule);
    if (!list.length) continue;
    add(heading, 'heading');
    for (const t of list) add(t.label, state.theme && state.theme.id === t.id ? 'current' : '', () => setTheme(t.id, t.label));
  }
  add('', 'sep');
  add('Load Theme File...', '', loadThemeFile);
  const r = $('btnTheme').getBoundingClientRect();
  menu.hidden = false;
  menu.style.top = r.bottom + 2 + 'px';
  menu.style.left = Math.max(4, r.right - menu.offsetWidth) + 'px';
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
  if (e.key === 'Escape') { if (state.placing !== null) { stopPlacing(); status('placement cancelled'); } hideThemeMenu(); hideContextMenu(); return; }
  const typing = /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement && document.activeElement.tagName);
  if (!typing && (e.key === 'Delete' || e.key === 'Backspace') && !$('btnDelete').disabled) { e.preventDefault(); return $('btnDelete').click(); }
  if (e.altKey && e.key === 'ArrowUp' && !$('btnUp').disabled) { e.preventDefault(); return ascend(); }
  if (!(e.ctrlKey || e.metaKey)) return;
  const k = e.key.toLowerCase();
  const map = { n: 'btnNew', o: 'btnOpen', s: 'btnSave', r: 'btnRotate', e: 'btnView', 0: 'btnZoomFit' };
  if (map[k] && !$(map[k]).disabled) { e.preventDefault(); $(map[k]).click(); }
});

// ---------- start-up
(async () => {
  updateEnables();
  if (!token) return status('No access token - start the GUI from SignalIntegrityServer or the desktop app.');
  try {
    const { version } = await api('version');
    status('SignalIntegrity ' + version + ' - open a project (.si) to begin');
    applyTheme(await api('theme'));
    await loadStencil();
    await showLevel(await api('render'));
    status('opened ' + state.drawing.filename);
  } catch (e) { /* no project open yet */ }
})();
