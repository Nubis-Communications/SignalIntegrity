// Minimal dependency-free SVG line plot with engineering-unit axes.
import { el } from './schematic.js';

const COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'];
const PREFIXES = [[1e12, 'T'], [1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'], [1e-6, 'u'], [1e-9, 'n'], [1e-12, 'p']];

export function engineering(values, unit) {
  let peak = 0;
  for (const v of values) if (v !== null && Math.abs(v) > peak) peak = Math.abs(v);
  for (const [scale, prefix] of PREFIXES) {
    if (peak >= scale || scale === 1e-12) return { scale, label: prefix + unit };
  }
  return { scale: 1, label: unit };
}

function niceTicks(lo, hi, count = 8) {
  if (!(hi > lo)) { hi = lo + 1; lo = lo - 1; }
  const raw = (hi - lo) / count;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => s >= raw);
  const ticks = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi + step * 1e-9; t += step) ticks.push(+t.toPrecision(12));
  return ticks;
}

function extent(series, key) {
  let lo = Infinity, hi = -Infinity;
  for (const s of series) for (const v of s[key]) if (v !== null && isFinite(v)) { if (v < lo) lo = v; if (v > hi) hi = v; }
  if (lo === Infinity) return [0, 1];
  if (lo === hi) return [lo - 1, hi + 1];
  const pad = (hi - lo) * 0.05;
  return [lo - pad, hi + pad];
}

// series: [{name, x:[...], y:[...]}]; xLabel/yLabel: axis titles
export function plot(host, series, xLabel, yLabel) {
  while (host.firstChild) host.removeChild(host.firstChild);
  const W = host.clientWidth || 900, H = host.clientHeight || 500;
  const m = { l: 70, r: 120, t: 15, b: 50 };
  const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'none' }, host);
  const [x0, x1] = extent(series, 'x'), [y0, y1] = extent(series, 'y');
  const sx = x => m.l + (x - x0) / (x1 - x0) * (W - m.l - m.r);
  const sy = y => H - m.b - (y - y0) / (y1 - y0) * (H - m.t - m.b);
  for (const t of niceTicks(x0, x1)) {
    el('line', { x1: sx(t), x2: sx(t), y1: m.t, y2: H - m.b, stroke: '#ddd' }, svg);
    el('text', { x: sx(t), y: H - m.b + 16, 'text-anchor': 'middle' }, svg).textContent = String(t);
  }
  for (const t of niceTicks(y0, y1)) {
    el('line', { x1: m.l, x2: W - m.r, y1: sy(t), y2: sy(t), stroke: '#ddd' }, svg);
    el('text', { x: m.l - 6, y: sy(t), 'text-anchor': 'end', 'dominant-baseline': 'central' }, svg).textContent = String(t);
  }
  el('rect', { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: 'none', stroke: '#444' }, svg);
  el('text', { x: (m.l + W - m.r) / 2, y: H - 10, 'text-anchor': 'middle' }, svg).textContent = xLabel;
  el('text', { x: 16, y: (m.t + H - m.b) / 2, 'text-anchor': 'middle', transform: `rotate(-90 16 ${(m.t + H - m.b) / 2})` }, svg).textContent = yLabel;
  series.forEach((s, i) => {
    const color = COLORS[i % COLORS.length];
    let d = '', pen = false;
    for (let k = 0; k < s.x.length; k++) {
      const y = s.y[k];
      if (y === null || !isFinite(y)) { pen = false; continue; }
      d += (pen ? 'L' : 'M') + sx(s.x[k]).toFixed(2) + ' ' + sy(y).toFixed(2);
      pen = true;
    }
    el('path', { d, fill: 'none', stroke: color, 'stroke-width': 1.5, class: 'trace' }, svg);
    if (i < 24) {
      const ly = m.t + 10 + i * 16;
      el('line', { x1: W - m.r + 10, x2: W - m.r + 30, y1: ly, y2: ly, stroke: color, 'stroke-width': 2 }, svg);
      el('text', { x: W - m.r + 34, y: ly, 'dominant-baseline': 'central' }, svg).textContent = s.name;
    }
  });
  return svg;
}
