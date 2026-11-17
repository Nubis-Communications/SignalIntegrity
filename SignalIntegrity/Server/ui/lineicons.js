// Line icons in the style of VS Code's codicons: 16x16 grid, 1.2px strokes in currentColor, so
// they follow the theme. Built with createElementNS (the UI never uses innerHTML).
// Each icon is a list of path data strings and [cx, cy, r] circles.
const SVG_NS = 'http://www.w3.org/2000/svg';

const ICONS = {
  new: ['M9 1.5H3.5v13h9V5z', 'M9 1.5V5h3.5', 'M8 8v4.5', 'M5.75 10.25h4.5'],
  open: ['M1.5 12.5v-9h4l1.5 1.5h5.5v2', 'M1.5 12.5l2-5.5h11l-2 5.5z'],
  save: ['M2.5 2.5h9l2 2v9h-11z', 'M5 2.5V6h5V2.5', 'M4.5 13.5v-4h7v4'],
  saveAs: ['M2.5 2.5h9l2 2v3', 'M2.5 2.5v11h5', 'M5 2.5V6h5V2.5', 'M9.5 14.5v-1.6l4-4 1.6 1.6-4 4z'],
  undo: ['M4 6.5h6.5a3 3 0 0 1 0 6H7', 'M6.5 4L4 6.5 6.5 9'],
  redo: ['M12 6.5H5.5a3 3 0 0 0 0 6H9', 'M9.5 4L12 6.5 9.5 9'],
  zoomIn: [[6.5, 6.5, 4.5], 'M9.8 9.8l4.7 4.7', 'M4.5 6.5h4', 'M6.5 4.5v4'],
  zoomOut: [[6.5, 6.5, 4.5], 'M9.8 9.8l4.7 4.7', 'M4.5 6.5h4'],
  zoomFit: ['M1.5 5V1.5H5', 'M11 1.5h3.5V5', 'M14.5 11v3.5H11', 'M5 14.5H1.5V11', 'M5 5h6v6H5z'],
  pan: ['M8 1.5v13', 'M1.5 8h13', 'M6 3.5l2-2 2 2', 'M6 12.5l2 2 2-2', 'M3.5 6l-2 2 2 2', 'M12.5 6l2 2-2 2'],
  wire: ['M3.5 12.5h3.5v-9h5.5', [2.5, 12.5, 1], [13.5, 3.5, 1]],
  rotate: ['M13.5 8a5.5 5.5 0 1 1-1.6-3.9', 'M12.2 1.5v2.8H9.4'],
  flipHorizontal: ['M8 1.5v2 M8 6.5v3 M8 12.5v2', 'M6 4.5L2 12h4z', 'M10 4.5l4 7.5h-4z'],
  flipVertical: ['M1.5 8h2 M6.5 8h3 M12.5 8h2', 'M4.5 6L12 2v4z', 'M4.5 10l7.5 4v-4z'],
  duplicate: ['M5.5 5.5h8v8h-8z', 'M3.5 10.5h-1v-8h8v1', 'M9.5 7.5v4', 'M7.5 9.5h4'],
  copy: ['M5.5 5.5h8v8h-8z', 'M3.5 10.5h-1v-8h8v1'],
  cut: [[4.5, 12, 2], [11.5, 12, 2], 'M5.7 10.4L12 2', 'M10.3 10.4L4 2'],
  paste: ['M5.5 1.5h5v2.5h-5z', 'M5.5 3h-2.5v11.5h10V3h-2.5'],
  delete: ['M2.5 4h11', 'M6 4V2.5h4V4', 'M3.5 4l.8 10h7.4l.8-10', 'M6.5 6.5v5', 'M9.5 6.5v5'],
  viewDevice: ['M2.5 2.5h11v11h-11z', 'M5.5 5.5l5 5', 'M10.5 6.5v4h-4'],
  up: ['M8 13.5V3', 'M4.5 6.5L8 3l3.5 3.5', 'M3 14.5h10'],
  simulate: ['M4.5 2.5v11l9-5.5z'],
  sparameters: ['M5 4h6v8H5z', 'M1.5 6H5', 'M1.5 10H5', 'M11 6h3.5', 'M11 10h3.5'],
  virtualprobe: ['M9.5 2.5l4 4-6.5 6.5-4-4z', 'M4.75 11.25L1.5 14.5', 'M8 5.5l2.5 2.5'],
  deembed: ['M5 3.5H2.5v9H5', 'M11 3.5h2.5v9H11', 'M5.5 8h5', 'M8.5 6l2 2-2 2'],
  help: [[8, 8, 6.5], 'M6 6.2a2 2 0 1 1 2.6 1.9c-.4.15-.6.5-.6.9v.6', 'M8 11.4v.2'],
  about: [[8, 8, 6.5], 'M8 7v4.5', 'M8 4.6v.2'],
  documentation: ['M1.5 3h4.5A2 2 0 0 1 8 5v9a1.5 1.5 0 0 0-1.5-1.5h-5z', 'M14.5 3H10a2 2 0 0 0-2 2v9a1.5 1.5 0 0 1 1.5-1.5h5z'],
  archive: ['M1.5 2.5h13v3h-13z', 'M2.5 5.5v8h11v-8', 'M6 8.5h4'],
  extractArchive: ['M1.5 2.5h13v3h-13z', 'M2.5 5.5v8h11v-8', 'M8 12V8', 'M6 10l2-2 2 2'],
  cancel: [[8, 8, 6], 'M3.8 12.2l8.4-8.4'],
  deleteVertex: ['M1.5 13.5l5-5', 'M9.5 8.5l5 5', [8, 7, 1.5], 'M10.5 2.5h4'],
  duplicateVertex: ['M1.5 13.5l5-5', 'M9.5 8.5l5 5', [8, 7, 1.5], 'M10.5 2.5h4', 'M12.5 .5v4'],
  equations: ['M12 3H4l4 5-4 5h8'],
  exportImage: ['M1.5 2.5h13v11h-13z', [5, 6, 1.2], 'M1.5 11.5l4-4 3 3 2-2 4 4'],
  exportNetlist: ['M1.5 4h8', 'M1.5 8h8', 'M1.5 12h5', 'M12.5 8.5v6', 'M10 12l2.5 2.5L15 12'],
  exportTikz: ['M5.5 4l-4 4 4 4', 'M10.5 4l4 4-4 4', 'M9 2.5l-2 11'],
  netlist: ['M5.5 4h9', 'M5.5 8h9', 'M5.5 12h9', 'M2 4h.5', 'M2 8h.5', 'M2 12h.5'],
  postProcessing: ['M2 14l8-8', 'M9 3.5v-2', 'M12.5 7h2', 'M11.5 4.5L13 3', 'M12 9.5l1.5 1.5', 'M6.5 4.5L5 3'],
  preferences: ['M1.5 4h7.5', 'M12 4h2.5', 'M1.5 8h2.5', 'M7 8h7.5', 'M1.5 12h9.5', 'M14 12h.5', [10.5, 4, 1.5], [5.5, 8, 1.5], [12.5, 12, 1.5]],
  properties: ['M2.5 2.5h11v11h-11z', 'M5 6h6', 'M5 8.5h6', 'M5 11h3'],
  // pane controls
  close: ['M4 4l8 8', 'M12 4l-8 8'],
  popOut: ['M9 2.5h4.5V7', 'M13.5 2.5L7.5 8.5', 'M12 9.5v4H2.5V4h4'],
  dockBack: ['M14 2L8.5 7.5', 'M8.5 3.5v4h4', 'M6.5 2.5h-4v11h11v-4'],
};
const ALIASES = { deletePart: 'delete', deleteWire: 'delete' };

export function hasLineIcon(id) { return !!ICONS[ALIASES[id] || id]; }

export function lineIcon(id, size = 16) {
  const shapes = ICONS[ALIASES[id] || id];
  if (!shapes) return null;
  const svg = document.createElementNS(SVG_NS, 'svg');
  svg.setAttribute('viewBox', '0 0 16 16');
  svg.setAttribute('width', size);
  svg.setAttribute('height', size);
  svg.setAttribute('class', 'icon line-icon');
  svg.setAttribute('aria-hidden', 'true');
  for (const shape of shapes) {
    const node = document.createElementNS(SVG_NS, Array.isArray(shape) ? 'circle' : 'path');
    if (Array.isArray(shape)) {
      node.setAttribute('cx', shape[0]); node.setAttribute('cy', shape[1]); node.setAttribute('r', shape[2]);
    } else node.setAttribute('d', shape);
    svg.appendChild(node);
  }
  return svg;
}
