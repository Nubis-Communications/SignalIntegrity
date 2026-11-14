// Renders GuiCore RecordingCanvas primitives (tk.Canvas semantics) as SVG elements.
const NS = 'http://www.w3.org/2000/svg';

export function el(name, attrs = {}, parent = null) {
  const node = document.createElementNS(NS, name);
  for (const [k, v] of Object.entries(attrs)) {
    if (v !== null && v !== undefined) node.setAttribute(k, String(v));
  }
  if (parent) parent.appendChild(node);
  return node;
}

function pointsAttr(pts) {
  const out = [];
  for (let k = 0; k + 1 < pts.length; k += 2) out.push(pts[k] + ',' + pts[k + 1]);
  return out.join(' ');
}

// tk arrowshape (d1,d2,d3): d1 tip-to-neck, d2 tip-to-trailing points, d3 half width
function arrowhead(tip, tail, shape) {
  const [d1, d2, d3] = shape;
  const dx = tip[0] - tail[0], dy = tip[1] - tail[1];
  const len = Math.hypot(dx, dy) || 1;
  const ux = dx / len, uy = dy / len, px = -uy, py = ux;
  return [tip[0], tip[1],
    tip[0] - ux * d2 + px * d3, tip[1] - uy * d2 + py * d3,
    tip[0] - ux * d1, tip[1] - uy * d1,
    tip[0] - ux * d2 - px * d3, tip[1] - uy * d2 - py * d3];
}

function normBox(b) {
  return [Math.min(b[0], b[2]), Math.min(b[1], b[3]), Math.max(b[0], b[2]), Math.max(b[1], b[3])];
}

function arcPath(item) {
  const [x0, y0, x1, y1] = normBox(item.bbox);
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, rx = (x1 - x0) / 2, ry = (y1 - y0) / 2;
  const a0 = item.start * Math.PI / 180, a1 = (item.start + item.extent) * Math.PI / 180;
  // tk angles run counter-clockwise on screen (y down), so y uses -sin
  const sx = cx + rx * Math.cos(a0), sy = cy - ry * Math.sin(a0);
  const ex = cx + rx * Math.cos(a1), ey = cy - ry * Math.sin(a1);
  const large = Math.abs(item.extent) > 180 ? 1 : 0;
  const sweep = item.extent > 0 ? 0 : 1;
  return `M ${sx} ${sy} A ${rx} ${ry} 0 ${large} ${sweep} ${ex} ${ey}`;
}

const H_ANCHOR = a => a.includes('w') ? 'start' : a.includes('e') ? 'end' : 'middle';
const V_BASELINE = a => a.includes('n') ? 'hanging' : a.includes('s') ? 'text-after-edge' : 'central';

// colorMap maps the tk colors the part pictures use (black, blue, salmon, white) to theme colors;
// skipText leaves out labels, for small stencil thumbnails
export function renderPrimitives(group, items, colorMap = null, skipText = false) {
  while (group.firstChild) group.removeChild(group.firstChild);
  const c = v => (v && colorMap && colorMap[v]) || v;
  for (const item of items) {
    switch (item.type) {
      case 'line': {
        const p = item.points;
        el('polyline', {
          points: pointsAttr(p), fill: 'none', stroke: c(item.color), 'stroke-width': item.width,
          'stroke-linecap': 'round', 'stroke-linejoin': 'round',
          'stroke-dasharray': item.dash ? item.dash.join(' ') : null,
        }, group);
        if (item.arrow && p.length >= 4) {
          const shape = item.arrowshape || [8, 10, 3];
          if (item.arrow === 'last' || item.arrow === 'both')
            el('polygon', { points: pointsAttr(arrowhead(p.slice(-2), p.slice(-4, -2), shape)), fill: c(item.color) }, group);
          if (item.arrow === 'first' || item.arrow === 'both')
            el('polygon', { points: pointsAttr(arrowhead(p.slice(0, 2), p.slice(2, 4), shape)), fill: c(item.color) }, group);
        }
        break;
      }
      case 'polygon':
        el('polygon', { points: pointsAttr(item.points), fill: c(item.fill) || 'none', stroke: c(item.outline) || 'none' }, group);
        break;
      case 'rectangle': {
        const [x0, y0, x1, y1] = normBox(item.bbox);
        el('rect', { x: x0, y: y0, width: x1 - x0, height: y1 - y0, fill: c(item.fill) || 'none', stroke: c(item.outline) || 'none' }, group);
        break;
      }
      case 'oval': {
        const [x0, y0, x1, y1] = normBox(item.bbox);
        el('ellipse', { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, rx: (x1 - x0) / 2, ry: (y1 - y0) / 2,
          fill: c(item.fill) || 'none', stroke: c(item.outline) || 'none' }, group);
        break;
      }
      case 'arc':
        if (Math.abs(item.extent) >= 360) {
          const [x0, y0, x1, y1] = normBox(item.bbox);
          el('ellipse', { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, rx: (x1 - x0) / 2, ry: (y1 - y0) / 2, fill: 'none', stroke: c(item.outline) }, group);
        } else {
          el('path', { d: arcPath(item), fill: 'none', stroke: c(item.outline) }, group);
        }
        break;
      case 'text': {
        if (skipText) break;
        const anchor = item.anchor || 'center';
        const t = el('text', { x: item.x, y: item.y, fill: c(item.color), 'text-anchor': H_ANCHOR(anchor),
          'dominant-baseline': V_BASELINE(anchor) }, group);
        t.textContent = item.text;
        break;
      }
    }
  }
}

// bounding box of the drawn geometry (labels excluded when skipText)
export function primitivesBox(items, skipText = false) {
  const xs = [], ys = [];
  for (const item of items) {
    if (item.type === 'line' || item.type === 'polygon') {
      for (let k = 0; k + 1 < item.points.length; k += 2) { xs.push(item.points[k]); ys.push(item.points[k + 1]); }
    } else if (item.type === 'text') {
      if (!skipText) { xs.push(item.x); ys.push(item.y); }
    } else {
      xs.push(item.bbox[0], item.bbox[2]); ys.push(item.bbox[1], item.bbox[3]);
    }
  }
  if (!xs.length) return null;
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
}
