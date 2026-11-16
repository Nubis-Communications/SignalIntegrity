// Interactive SVG plot reproducing the matplotlib navigation used by the tk simulator and
// s-parameter dialogs: the toolbar starts in pan mode (left-drag pans, right-drag zooms x and y
// independently about the pointer), zoom mode draws a box (left zooms in, right zooms out),
// holding 'x' or 'y' constrains to that axis, and Home/Back/Forward walk the view history.
import { el } from './schematic.js';

export const COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'];
const PREFIXES = [[1e12, 'T'], [1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'], [1e-6, 'u'], [1e-9, 'n'], [1e-12, 'p'], [1e-15, 'f']];

// SignalIntegrity's ToSI(span, unit) choice of display unit for an axis span
export function engineering(span, unit) {
  span = Math.abs(span);
  for (const [scale, prefix] of PREFIXES) {
    if (span >= scale) return { divisor: scale, label: prefix + unit };
  }
  return { divisor: 1e-15, label: 'f' + unit };
}

function niceTicks(lo, hi, count = 8) {
  if (!(hi > lo)) return [lo];
  const raw = (hi - lo) / count;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => s >= raw);
  const ticks = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + step * 1e-9; t += step) ticks.push(Math.abs(t) < step * 1e-6 ? 0 : +t.toPrecision(12));
  return ticks;
}
function logTicks(lo, hi) {
  const ticks = [];
  for (let e = Math.floor(Math.log10(lo)); e <= Math.ceil(Math.log10(hi)); e++) {
    const t = Math.pow(10, e);
    if (t >= lo && t <= hi) ticks.push(t);
  }
  return ticks;
}
const fmt = v => {
  const a = Math.abs(v);
  return (a !== 0 && (a < 1e-3 || a >= 1e5)) ? v.toExponential(2) : String(+v.toPrecision(6));
};

export class Plot {
  constructor(host, { onViewChange = null, onCursor = null } = {}) {
    this.host = host;
    this.onViewChange = onViewChange;
    this.onCursor = onCursor;
    this.series = [];
    this.xLabel = ''; this.yLabel = '';
    this.logX = false;
    this.grid = true;
    this.mode = 'pan';
    this.limits = [0, 1, 0, 1];
    this.history = []; this.historyIndex = -1;
    this.keys = new Set();
    this.margin = { l: 72, r: 16, t: 12, b: 46 };
    this.svg = el('svg', { class: 'plot' }, host);
    this.svg.addEventListener('contextmenu', e => e.preventDefault());
    this.svg.addEventListener('pointerdown', e => this._down(e));
    this.svg.addEventListener('pointermove', e => this._move(e));
    this.svg.addEventListener('pointerup', e => this._up(e));
    this.svg.addEventListener('pointerleave', () => this.onCursor && this.onCursor(null));
    window.addEventListener('keydown', e => this.keys.add(e.key.toLowerCase()));
    window.addEventListener('keyup', e => this.keys.delete(e.key.toLowerCase()));
    new ResizeObserver(() => this.draw()).observe(host);
  }
  setData(series, xLabel, yLabel) {
    this.series = series; this.xLabel = xLabel; this.yLabel = yLabel;
    this.draw();
  }
  // sets the view; resetHistory makes it the Home view
  setLimits(limits, { resetHistory = false, notify = false } = {}) {
    this.limits = limits.slice();
    if (resetHistory) { this.history = [this.limits.slice()]; this.historyIndex = 0; }
    this.draw();
    if (notify && this.onViewChange) this.onViewChange(this.limits.slice());
  }
  _push() {
    this.history = this.history.slice(0, this.historyIndex + 1);
    this.history.push(this.limits.slice());
    this.historyIndex = this.history.length - 1;
    if (this.onViewChange) this.onViewChange(this.limits.slice());
  }
  home() { if (this.history.length) { this.historyIndex = 0; this.setLimits(this.history[0], { notify: true }); } }
  back() { if (this.historyIndex > 0) { this.historyIndex--; this.setLimits(this.history[this.historyIndex], { notify: true }); } }
  forward() { if (this.historyIndex < this.history.length - 1) { this.historyIndex++; this.setLimits(this.history[this.historyIndex], { notify: true }); } }
  setMode(mode) { this.mode = mode; this.svg.classList.toggle('zoom-mode', mode === 'zoom'); }

  // ---- coordinate transforms
  _box() {
    const W = this.host.clientWidth || 800, H = this.host.clientHeight || 400, m = this.margin;
    return { W, H, x0: m.l, x1: W - m.r, y0: m.t, y1: H - m.b };
  }
  _fx(x) { return this.logX ? Math.log10(Math.max(x, 1e-300)) : x; }
  _ifx(u) { return this.logX ? Math.pow(10, u) : u; }
  _sx(x, b = this._box()) { const a = this._fx(this.limits[0]), c = this._fx(this.limits[1]); return b.x0 + (this._fx(x) - a) / (c - a) * (b.x1 - b.x0); }
  _sy(y, b = this._box()) { return b.y1 - (y - this.limits[2]) / (this.limits[3] - this.limits[2]) * (b.y1 - b.y0); }
  _data(px, py, b = this._box()) {
    const a = this._fx(this.limits[0]), c = this._fx(this.limits[1]);
    return [this._ifx(a + (px - b.x0) / (b.x1 - b.x0) * (c - a)),
      this.limits[2] + (b.y1 - py) / (b.y1 - b.y0) * (this.limits[3] - this.limits[2])];
  }
  _local(e) { const r = this.svg.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; }

  // ---- interaction
  _down(e) {
    if (e.button !== 0 && e.button !== 2) return;
    e.preventDefault();
    this.svg.setPointerCapture(e.pointerId);
    const [px, py] = this._local(e);
    this.drag = { button: e.button, px, py, start: this.limits.slice(), moved: false };
  }
  _move(e) {
    const [px, py] = this._local(e);
    const b = this._box();
    if (this.onCursor) {
      const inside = px >= b.x0 && px <= b.x1 && py >= b.y0 && py <= b.y1;
      this.onCursor(inside ? this._data(px, py, b) : null);
    }
    const d = this.drag;
    if (!d) return;
    let dx = px - d.px, dy = py - d.py;
    if (Math.abs(dx) + Math.abs(dy) > 2) d.moved = true;
    if (this.keys.has('x')) dy = 0;
    if (this.keys.has('y')) dx = 0;
    const W = b.x1 - b.x0, H = b.y1 - b.y0;
    const [lx0, lx1, ly0, ly1] = d.start;
    const ux0 = this._fx(lx0), ux1 = this._fx(lx1);
    if (this.mode === 'pan' && d.button === 0) {
      const sx = (ux1 - ux0) / W, sy = (ly1 - ly0) / H;
      this.limits = [this._ifx(ux0 - dx * sx), this._ifx(ux1 - dx * sx), ly0 + dy * sy, ly1 + dy * sy];
      this.draw();
    } else if (this.mode === 'pan' && d.button === 2) {
      // matplotlib: scale = 10**(-dx/width), 10**(dy/height) about the press point
      const ax = Math.pow(10, -dx / W), ay = Math.pow(10, dy / H);
      const cx = ux0 + (d.px - b.x0) / W * (ux1 - ux0), cy = ly0 + (b.y1 - d.py) / H * (ly1 - ly0);
      this.limits = [this._ifx(cx + ax * (ux0 - cx)), this._ifx(cx + ax * (ux1 - cx)), cy + ay * (ly0 - cy), cy + ay * (ly1 - cy)];
      this.draw();
    } else if (this.mode === 'zoom') {
      this.draw();
      el('rect', { x: Math.min(d.px, px), y: Math.min(d.py, py), width: Math.abs(px - d.px), height: Math.abs(py - d.py), class: 'zoom-box' }, this.svg);
    }
  }
  _up(e) {
    const d = this.drag; this.drag = null;
    if (!d) return;
    if (this.mode === 'zoom' && d.moved) {
      const [px, py] = this._local(e);
      const b = this._box();
      let [x0, y1] = this._data(Math.min(d.px, px), Math.min(d.py, py), b);
      let [x1, y0] = this._data(Math.max(d.px, px), Math.max(d.py, py), b);
      // a nearly flat box zooms only one axis, as in matplotlib
      if (Math.abs(py - d.py) < 5 || this.keys.has('x')) { y0 = this.limits[2]; y1 = this.limits[3]; }
      if (Math.abs(px - d.px) < 5 || this.keys.has('y')) { x0 = this.limits[0]; x1 = this.limits[1]; }
      if (d.button === 2) {
        // zoom out: the current view shrinks into the drawn box
        const lx0 = this._fx(this.limits[0]), lx1 = this._fx(this.limits[1]), ly0 = this.limits[2], ly1 = this.limits[3];
        const bx0 = this._fx(x0), bx1 = this._fx(x1);
        const kx = (lx1 - lx0) / Math.max(bx1 - bx0, 1e-300), ky = (ly1 - ly0) / Math.max(y1 - y0, 1e-300);
        this.limits = [this._ifx(lx0 - (bx0 - lx0) * kx), this._ifx(lx1 + (lx1 - bx1) * kx), ly0 - (y0 - ly0) * ky, ly1 + (ly1 - y1) * ky];
      } else {
        this.limits = [x0, x1, y0, y1];
      }
    }
    this.draw();
    if (d.moved) this._push();
  }

  // ---- rendering
  draw() {
    const svg = this.svg;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    const b = this._box();
    svg.setAttribute('viewBox', `0 0 ${b.W} ${b.H}`);
    const [x0, x1, y0, y1] = this.limits;
    if (!(x1 > x0) || !(y1 > y0)) return;
    const clipId = 'clip' + Math.random().toString(36).slice(2);
    const defs = el('defs', {}, svg);
    el('rect', { x: b.x0, y: b.y0, width: b.x1 - b.x0, height: b.y1 - b.y0 }, el('clipPath', { id: clipId }, defs));
    const xt = this.logX ? logTicks(x0, x1) : niceTicks(x0, x1);
    for (const t of xt) {
      const X = this._sx(t, b);
      if (this.grid) el('line', { x1: X, x2: X, y1: b.y0, y2: b.y1, class: 'grid' }, svg);
      el('line', { x1: X, x2: X, y1: b.y1, y2: b.y1 + 4, class: 'tick' }, svg);
      el('text', { x: X, y: b.y1 + 16, 'text-anchor': 'middle' }, svg).textContent = fmt(t);
    }
    for (const t of niceTicks(y0, y1)) {
      const Y = this._sy(t, b);
      if (this.grid) el('line', { x1: b.x0, x2: b.x1, y1: Y, y2: Y, class: 'grid' }, svg);
      el('line', { x1: b.x0 - 4, x2: b.x0, y1: Y, y2: Y, class: 'tick' }, svg);
      el('text', { x: b.x0 - 7, y: Y, 'text-anchor': 'end', 'dominant-baseline': 'central' }, svg).textContent = fmt(t);
    }
    const plotArea = el('g', { 'clip-path': `url(#${clipId})` }, svg);
    for (const s of this.series) {
      if (s.dc !== null && s.dc !== undefined) {
        const Y = this._sy(s.dc, b);
        el('line', { x1: b.x0, x2: b.x1, y1: Y, y2: Y, stroke: s.color, class: 'trace' }, plotArea);
        continue;
      }
      let d = '', pen = false;
      for (let k = 0; k < s.x.length; k++) {
        const y = s.y[k], x = s.x[k];
        if (y === null || !isFinite(y) || (this.logX && x <= 0)) { pen = false; continue; }
        d += (pen ? 'L' : 'M') + this._sx(x, b).toFixed(1) + ' ' + this._sy(y, b).toFixed(1);
        pen = true;
      }
      el('path', { d, stroke: s.color, class: 'trace' }, plotArea);
    }
    el('rect', { x: b.x0, y: b.y0, width: b.x1 - b.x0, height: b.y1 - b.y0, class: 'frame' }, svg);
    el('text', { x: (b.x0 + b.x1) / 2, y: b.H - 8, 'text-anchor': 'middle' }, svg).textContent = this.xLabel;
    const my = (b.y0 + b.y1) / 2;
    el('text', { x: 14, y: my, 'text-anchor': 'middle', transform: `rotate(-90 14 ${my})` }, svg).textContent = this.yLabel;
    const named = this.series.filter(s => s.name);
    const lx = b.x1 - 110;
    if (named.length) el('rect', { x: lx - 6, y: b.y0 + 3, width: 112, height: Math.min(named.length, 24) * 15 + 4, class: 'legend-box' }, svg);
    named.slice(0, 24).forEach((s, i) => {
      const ly = b.y0 + 12 + i * 15;
      el('line', { x1: lx, x2: lx + 18, y1: ly, y2: ly, stroke: s.color, 'stroke-width': 2 }, svg);
      el('text', { x: lx + 22, y: ly, 'dominant-baseline': 'central', class: 'legend' }, svg).textContent = s.name;
    });
  }
}
