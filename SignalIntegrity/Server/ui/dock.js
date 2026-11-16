// VS Code style docking: panes live in the left or right side bar or the bottom panel. Drag a pane
// header to move it, click it to collapse it, right-click it for a menu, and drag the sashes to resize.
const AREAS = ['left', 'right', 'bottom'];
const AREA_NAMES = { left: 'Primary Side Bar', right: 'Secondary Side Bar', bottom: 'Panel' };
const DEFAULT = {
  areas: { left: ['parts', 'variables', 'calc'], right: ['properties'], bottom: [] },
  size: { left: 300, right: 300, bottom: 220 },
  weight: { parts: 3, variables: 1, calc: 1, properties: 1 },
  collapsed: {},
};
const MIN_SIZE = { left: 170, right: 170, bottom: 90 };
const DRAG_THRESHOLD = 5;

const panes = {};
let layout = structuredClone(DEFAULT);
let persist = () => {};
let saveTimer = null;
const $ = id => document.getElementById(id);
const dock = area => $('dock-' + area);
const dockSash = area => document.querySelector(`#workbench > .sash[data-area="${area}"], #center > .sash[data-area="${area}"]`);
const horizontal = area => area === 'bottom';
const areaOf = id => AREAS.find(a => layout.areas[a].includes(id));

function save() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => Promise.resolve(persist(structuredClone(layout))).catch(() => {}), 300);
}

// a stored layout is used only if it places every pane exactly once
function sanitize(stored) {
  try {
    const ids = Object.keys(panes);
    const placed = AREAS.flatMap(a => stored.areas[a]);
    if (placed.length !== ids.length || !ids.every(id => placed.includes(id))) return null;
    const out = structuredClone(DEFAULT);
    for (const a of AREAS) {
      out.areas[a] = stored.areas[a].slice();
      const size = stored.size && stored.size[a];
      if (Number.isFinite(size)) out.size[a] = Math.max(MIN_SIZE[a], Math.min(size, 4000));
    }
    for (const id of ids) {
      const w = stored.weight && stored.weight[id];
      if (Number.isFinite(w) && w > 0) out.weight[id] = w;
      if (stored.collapsed && stored.collapsed[id] === true) out.collapsed[id] = true;
    }
    return out;
  } catch { return null; }
}

function render() {
  for (const area of AREAS) {
    const host = dock(area), ids = layout.areas[area];
    host.replaceChildren();
    ids.forEach((id, i) => {
      if (i) host.appendChild(paneSash(area, i));
      const pane = panes[id];
      const collapsed = !horizontal(area) && !!layout.collapsed[id];
      pane.classList.toggle('collapsed', collapsed);
      pane.querySelector('.pane-header').setAttribute('aria-expanded', String(!collapsed));
      pane.style.flex = collapsed ? '0 0 auto' : `${layout.weight[id] || 1} 1 0`;
      host.appendChild(pane);
    });
    host.hidden = dockSash(area).hidden = !ids.length;
    host.style[horizontal(area) ? 'height' : 'width'] = layout.size[area] + 'px';
  }
}

// ---------- sashes
function trackSash(sash, evt, onMove, onEnd) {
  if (evt.button !== 0) return;
  evt.preventDefault();
  sash.setPointerCapture(evt.pointerId);
  const cursor = sash.classList.contains('ns') ? 'sashing-ns' : 'sashing-ew';
  sash.classList.add('active');
  document.body.classList.add(cursor);
  const x0 = evt.clientX, y0 = evt.clientY;
  const move = e => onMove(e.clientX - x0, e.clientY - y0);
  const up = () => {
    sash.removeEventListener('pointermove', move);
    sash.removeEventListener('pointerup', up);
    sash.removeEventListener('pointercancel', up);
    sash.classList.remove('active');
    document.body.classList.remove(cursor);
    onEnd();
  };
  sash.addEventListener('pointermove', move);
  sash.addEventListener('pointerup', up);
  sash.addEventListener('pointercancel', up);
}

function initDockSash(area) {
  const sash = dockSash(area), host = dock(area);
  sash.addEventListener('pointerdown', evt => {
    const start = horizontal(area) ? host.offsetHeight : host.offsetWidth;
    trackSash(sash, evt, (dx, dy) => {
      const delta = area === 'left' ? dx : area === 'right' ? -dx : -dy;
      layout.size[area] = Math.max(MIN_SIZE[area], start + delta);
      host.style[horizontal(area) ? 'height' : 'width'] = layout.size[area] + 'px';
    }, () => {
      // the CSS maximum may have limited the drag
      layout.size[area] = horizontal(area) ? host.offsetHeight : host.offsetWidth;
      save();
    });
  });
  sash.addEventListener('dblclick', () => { layout.size[area] = DEFAULT.size[area]; render(); save(); });
}

// resizes the nearest expanded panes on either side of the sash between ids[index-1] and ids[index]
function paneSash(area, index) {
  const sash = document.createElement('div');
  sash.className = 'sash ' + (horizontal(area) ? 'ew' : 'ns');
  sash.addEventListener('pointerdown', evt => {
    const ids = layout.areas[area];
    const open = id => horizontal(area) || !layout.collapsed[id];
    const before = ids.slice(0, index).reverse().find(open), after = ids.slice(index).find(open);
    if (!before || !after) return;
    const size = id => { const r = panes[id].getBoundingClientRect(); return horizontal(area) ? r.width : r.height; };
    const a = size(before), b = size(after), weight = layout.weight[before] + layout.weight[after];
    const min = Math.min(60, (a + b) / 2);
    trackSash(sash, evt, (dx, dy) => {
      const next = Math.max(min, Math.min(a + b - min, a + (horizontal(area) ? dx : dy)));
      layout.weight[before] = weight * next / (a + b);
      layout.weight[after] = weight - layout.weight[before];
      panes[before].style.flex = `${layout.weight[before]} 1 0`;
      panes[after].style.flex = `${layout.weight[after]} 1 0`;
    }, save);
  });
  return sash;
}

// ---------- moving panes
function move(id, area, index) {
  const from = areaOf(id), old = layout.areas[from].indexOf(id);
  layout.areas[from].splice(old, 1);
  if (from === area && old < index) index--;
  layout.areas[area].splice(Math.max(0, Math.min(index, layout.areas[area].length)), 0, id);
  render();
  save();
}

// where a pane dropped at x,y goes: {area,index,rect} with rect the highlighted drop region
function dropTarget(x, y) {
  const hit = document.elementFromPoint(x, y);
  if (!hit) return null;
  const host = hit.closest('.dock');
  if (host) {
    const area = host.dataset.area, ids = layout.areas[area];
    const pane = hit.classList.contains('sash') ? hit.nextElementSibling : hit.closest('.pane');
    if (pane) {
      const r = pane.getBoundingClientRect();
      const after = horizontal(area) ? x > r.left + r.width / 2 : y > r.top + r.height / 2;
      const rect = horizontal(area)
        ? { left: after ? r.left + r.width / 2 : r.left, top: r.top, width: r.width / 2, height: r.height }
        : { left: r.left, top: after ? r.top + r.height / 2 : r.top, width: r.width, height: r.height / 2 };
      return { area, index: ids.indexOf(pane.dataset.pane) + (after ? 1 : 0), rect };
    }
    return { area, index: ids.length, rect: host.getBoundingClientRect() };
  }
  // over the schematic: the nearest edge docks to that side, as dragging a view to an editor edge does
  const center = hit.closest('#canvasHost');
  if (!center) return null;
  const r = center.getBoundingClientRect();
  const edges = { left: (x - r.left) / r.width, right: (r.right - x) / r.width, bottom: (r.bottom - y) / r.height };
  const area = Object.keys(edges).reduce((m, k) => edges[k] < edges[m] ? k : m);
  if (edges[area] > 0.3) return null;
  const width = Math.min(layout.size[area], r.width / 2), height = Math.min(layout.size.bottom, r.height / 2);
  const rect = area === 'left' ? { left: r.left, top: r.top, width, height: r.height }
    : area === 'right' ? { left: r.right - width, top: r.top, width, height: r.height }
    : { left: r.left, top: r.bottom - height, width: r.width, height };
  return { area, index: layout.areas[area].length, rect };
}

function showDrop(target) {
  const overlay = $('dropOverlay');
  overlay.classList.toggle('visible', !!target);
  if (target) for (const k of ['left', 'top', 'width', 'height']) overlay.style[k] = target.rect[k] + 'px';
}

function initHeader(id) {
  const pane = panes[id], header = pane.querySelector('.pane-header');
  header.tabIndex = 0;
  header.setAttribute('role', 'button');
  header.title = 'Click to collapse or expand; drag to move; right-click for more';
  header.addEventListener('pointerdown', evt => {
    if (evt.button !== 0) return;
    header.setPointerCapture(evt.pointerId);
    const x0 = evt.clientX, y0 = evt.clientY, label = $('dragLabel');
    let dragging = false, target = null;
    const moveHandler = e => {
      if (!dragging && Math.hypot(e.clientX - x0, e.clientY - y0) < DRAG_THRESHOLD) return;
      if (!dragging) {
        dragging = true;
        pane.classList.add('dragging');
        document.body.classList.add('docking');
        label.textContent = pane.querySelector('h2').textContent;
        label.classList.add('visible');
      }
      label.style.left = e.clientX + 12 + 'px';
      label.style.top = e.clientY + 8 + 'px';
      target = dropTarget(e.clientX, e.clientY);
      showDrop(target);
    };
    const upHandler = e => {
      header.removeEventListener('pointermove', moveHandler);
      header.removeEventListener('pointerup', upHandler);
      header.removeEventListener('pointercancel', upHandler);
      if (!dragging) { if (e.type === 'pointerup') toggle(id); return; }
      pane.classList.remove('dragging');
      document.body.classList.remove('docking');
      label.classList.remove('visible');
      showDrop(null);
      if (target && e.type === 'pointerup') move(id, target.area, target.index);
    };
    header.addEventListener('pointermove', moveHandler);
    header.addEventListener('pointerup', upHandler);
    header.addEventListener('pointercancel', upHandler);
  });
  header.addEventListener('keydown', evt => {
    if (evt.key === 'Enter' || evt.key === ' ') { evt.preventDefault(); evt.stopPropagation(); toggle(id); }
  });
  header.addEventListener('contextmenu', evt => { evt.preventDefault(); openMenu(id, evt.clientX, evt.clientY); });
}

function toggle(id) {
  if (horizontal(areaOf(id))) return;
  layout.collapsed[id] = !layout.collapsed[id];
  render();
  save();
}

// ---------- header context menu
function closeMenu() { $('paneMenu').hidden = true; }
function openMenu(id, x, y) {
  const menu = $('paneMenu'), area = areaOf(id);
  menu.replaceChildren();
  const item = (label, run) => {
    const li = document.createElement('li');
    const span = document.createElement('span'); span.className = 'label'; span.textContent = label;
    li.appendChild(span);
    li.addEventListener('click', () => { closeMenu(); run(); });
    menu.appendChild(li);
  };
  const separator = () => { const li = document.createElement('li'); li.className = 'sep'; menu.appendChild(li); };
  if (!horizontal(area)) item(layout.collapsed[id] ? 'Expand' : 'Collapse', () => toggle(id));
  for (const a of AREAS) if (a !== area) item('Move to ' + AREA_NAMES[a], () => move(id, a, layout.areas[a].length));
  separator();
  item('Reset Layout', () => { layout = structuredClone(DEFAULT); render(); save(); });
  menu.hidden = false;
  const r = menu.getBoundingClientRect();
  menu.style.left = Math.min(x, innerWidth - r.width - 4) + 'px';
  menu.style.top = Math.min(y, innerHeight - r.height - 4) + 'px';
}

/** load(): Promise of a stored layout or null; store(layout): saves it */
export function initDock({ load, store }) {
  for (const pane of document.querySelectorAll('.pane')) panes[pane.dataset.pane] = pane;
  for (const id of Object.keys(panes)) initHeader(id);
  for (const area of AREAS) initDockSash(area);
  document.addEventListener('pointerdown', evt => { if (!evt.target.closest('#paneMenu')) closeMenu(); }, true);
  document.addEventListener('keydown', evt => { if (evt.key === 'Escape') closeMenu(); });
  window.addEventListener('blur', closeMenu);
  render();
  Promise.resolve(load()).then(stored => {
    const restored = stored && sanitize(stored);
    if (restored) { layout = restored; render(); }
  }).catch(() => {}).finally(() => { persist = store; });
}
