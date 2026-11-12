// SignalIntegrity web GUI - talks to SignalIntegrity.Server over a token-protected local JSON API.
import { el, renderPrimitives } from './schematic.js';
import { plot, engineering } from './plot.js';

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
const state = { drawing: null, selected: null, busy: false, view: { s: 1, tx: 0, ty: 0 } };
const svg = $('schematic'), viewport = $('viewport');

function status(text) { $('status').textContent = text; }
function error(e) { status('Error: ' + (e.message || e)); alert(e.message || e); }

function updateEnables() {
  const open = !!state.drawing, busy = state.busy;
  const caps = open ? state.drawing.capabilities : {};
  $('btnOpen').disabled = busy;
  for (const id of ['btnSave', 'btnSaveAs', 'btnNetlist']) $(id).disabled = !open || busy;
  $('btnRotate').disabled = !open || busy || state.selected === null;
  for (const b of document.querySelectorAll('button.calc')) b.disabled = !open || busy || !caps[b.dataset.kind];
  document.title = 'SignalIntegrity' + (open ? ' - ' + state.drawing.title : '');
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
function setDrawing(drawing, fit = false) {
  state.drawing = drawing;
  renderPrimitives(viewport, drawing.items);
  const sel = drawing.devices.find(d => d.selected);
  state.selected = sel ? sel.index : null;
  if (fit) zoomFit(); else applyView();
  updateEnables();
}

let drag = null;
svg.addEventListener('pointerdown', async evt => {
  if (evt.button !== 0 || !state.drawing || state.busy) return;
  svg.setPointerCapture(evt.pointerId);
  const p = toScene(evt);
  const index = deviceAt(p);
  if (index !== null) {
    if (index !== state.selected) await selectDevice(index);
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
      try { setDrawing(await api('moveDevice', { index: d.index, dx: d.dx, dy: d.dy })); } catch (e) { error(e); }
    }
  }
});
svg.addEventListener('wheel', evt => {
  evt.preventDefault();
  const r = svg.getBoundingClientRect();
  zoomAt(evt.deltaY < 0 ? 1.15 : 1 / 1.15, evt.clientX - r.left, evt.clientY - r.top);
}, { passive: false });
window.addEventListener('resize', () => applyView());

// ---------- tables
function fillTable(tbody, rows, onEdit) {
  while (tbody.firstChild) tbody.removeChild(tbody.firstChild);
  for (const row of rows) {
    const tr = document.createElement('tr');
    const name = document.createElement('td'); name.textContent = row.label; name.title = row.title || row.label; tr.appendChild(name);
    const value = document.createElement('td');
    if (row.readOnly) { value.textContent = row.value; value.className = 'ro'; }
    else {
      const input = document.createElement('input');
      input.value = row.value; input.spellcheck = false;
      input.addEventListener('keydown', e => { if (e.key === 'Enter') input.blur(); if (e.key === 'Escape') { input.value = row.value; input.blur(); } });
      input.addEventListener('change', () => onEdit(row.key, input.value));
      value.appendChild(input);
    }
    tr.appendChild(value);
    const unit = document.createElement('td'); unit.textContent = row.unit || ''; tr.appendChild(unit);
    tbody.appendChild(tr);
  }
}
async function refreshVariables() {
  const vars = state.drawing ? await api('variables') : [];
  fillTable($('variables').tBodies[0], vars.map(v => ({ key: v.name, label: v.name, title: v.description, value: v.value, unit: v.units, readOnly: v.readOnly })),
    async (name, value) => {
      try { await api('setVariable', { name, value }); setDrawing(await api('render')); } catch (e) { error(e); }
      await refreshVariables(); await refreshProperties();
    });
}
async function refreshProperties() {
  const props = state.drawing && state.selected !== null ? await api('deviceProperties', { index: state.selected }) : [];
  fillTable($('properties').tBodies[0], props.map(p => ({ key: p.keyword, label: p.description || p.name, title: p.description, value: p.value, unit: p.unit, readOnly: p.readOnly })),
    async (keyword, value) => {
      try { await api('setDeviceProperty', { index: state.selected, keyword, value }); setDrawing(await api('render')); } catch (e) { error(e); }
      await refreshProperties();
    });
}
async function refreshCalculationProperties() {
  const form = $('calcProps');
  while (form.firstChild) form.removeChild(form.firstChild);
  if (!state.drawing) return;
  const values = await api('calculationProperties');
  for (const [name, value] of Object.entries(values)) {
    const label = document.createElement('label');
    label.append(name);
    const input = document.createElement('input'); input.name = name; input.value = value;
    label.appendChild(input); form.appendChild(label);
  }
  const apply = document.createElement('button'); apply.type = 'submit'; apply.textContent = 'Apply';
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
  try { setDrawing(await api('select', { index })); await refreshProperties(); } catch (e) { error(e); }
}

// ---------- files
async function openProject(filename) {
  try {
    setDrawing(await api('open', { filename }), true);
    await Promise.all([refreshVariables(), refreshProperties(), refreshCalculationProperties()]);
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
        const ul = $('fileList'); while (ul.firstChild) ul.removeChild(ul.firstChild);
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
    load(state.drawing ? null : '');
    dlg.showModal();
  });
}
$('btnOpen').onclick = async () => { const f = await fileDialog('open'); if (f) await openProject(f); };
$('btnSave').onclick = async () => { try { status('saved ' + (await api('save')).filename); } catch (e) { error(e); } };
$('btnSaveAs').onclick = async () => {
  const f = await fileDialog('save');
  if (!f) return;
  try { status('saved ' + (await api('save', { filename: f })).filename); setDrawing(await api('render')); } catch (e) { error(e); }
};
$('btnZoomIn').onclick = () => zoomAt(1.25, svg.clientWidth / 2, svg.clientHeight / 2);
$('btnZoomOut').onclick = () => zoomAt(0.8, svg.clientWidth / 2, svg.clientHeight / 2);
$('btnZoomFit').onclick = zoomFit;
$('btnRotate').onclick = async () => {
  if (state.selected === null) return;
  try { setDrawing(await api('rotateDevice', { index: state.selected })); } catch (e) { error(e); }
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
  if (job.state === 'done') { showResults(CALC_TITLES[kind] + ' - ' + state.drawing.title, job.result); status(CALC_TITLES[kind] + ' complete'); }
  else error(new Error(job.error || 'calculation failed'));
}
for (const b of document.querySelectorAll('button.calc')) b.onclick = () => calculate(b.dataset.kind);

function showResults(title, result) {
  const tabs = [];
  if (result.waveforms.length) {
    const ex = engineering(result.waveforms.flatMap(w => w.x), 's');
    tabs.push({ name: 'Waveforms', draw: host => plot(host, result.waveforms.map(w => ({ name: w.name, x: w.x.map(v => v * (1 / ex.scale)), y: w.y })), 'time (' + ex.label + ')', 'amplitude') });
  }
  for (const sp of result.sparameters) {
    const ef = engineering(sp.frequencies, 'Hz');
    const f = sp.frequencies.map(v => v / ef.scale);
    for (const [q, label] of [['dB', 'magnitude (dB)'], ['deg', 'phase (degrees)']]) {
      tabs.push({ name: sp.name + (q === 'dB' ? ' magnitude' : ' phase'),
        draw: host => plot(host, sp.traces.map(t => ({ name: t.name, x: f, y: t[q] })), 'frequency (' + ef.label + ')', label) });
    }
  }
  $('resultsTitle').textContent = title;
  const nav = $('resultsTabs'); while (nav.firstChild) nav.removeChild(nav.firstChild);
  const dlg = $('resultsDialog');
  dlg.showModal();
  const activate = i => {
    nav.querySelectorAll('button').forEach((b, k) => b.classList.toggle('active', k === i));
    tabs[i].draw($('resultsPlot'));
  };
  tabs.forEach((t, i) => { const b = document.createElement('button'); b.textContent = t.name; b.onclick = () => activate(i); nav.appendChild(b); });
  if (tabs.length) activate(0);
}
$('resultsClose').onclick = () => $('resultsDialog').close();

// ---------- keyboard
window.addEventListener('keydown', e => {
  if (!(e.ctrlKey || e.metaKey) || document.querySelector('dialog[open]')) return;
  const k = e.key.toLowerCase();
  const map = { o: 'btnOpen', s: 'btnSave', r: 'btnRotate', 0: 'btnZoomFit' };
  if (map[k] && !$(map[k]).disabled) { e.preventDefault(); $(map[k]).click(); }
});

// ---------- start-up
(async () => {
  updateEnables();
  if (!token) return status('No access token - start the GUI from SignalIntegrityServer or the desktop app.');
  try {
    const { version } = await api('version');
    status('SignalIntegrity ' + version + ' - open a project (.si) to begin');
    setDrawing(await api('render'), true);
    await Promise.all([refreshVariables(), refreshProperties(), refreshCalculationProperties()]);
    status('opened ' + state.drawing.filename);
  } catch (e) { /* no project open yet */ }
})();
