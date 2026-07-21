#!/usr/bin/env python
"""Convert ``Help.lyx`` into the MkDocs ``docs/`` Markdown tree.

Pipeline (replaces the old LyX + eLyXer ``Convert.sh``):

    Help.lyx  --(LyX)-->  Help.tex  --(Pandoc)-->  docs/_full.md
                                              |
                                              +--> split per H1 into docs/NN-*.md

The key requirement is that LyX ``\\label{...}`` markers survive as explicit
Markdown/HTML anchor ids (e.g. ``{#Control-Help:New-Project}``) so that the
context-help labels referenced by ``AddHelpElement(...)`` in the application keep
resolving.  Pandoc's LaTeX reader preserves ``\\label`` on section headings as the
heading id; the ``gfm+attributes`` output writer then emits those ids.

Requirements (must be on PATH):
    * lyx      (to export Help.lyx -> Help.tex)
    * pandoc   (to convert LaTeX -> Markdown and extract media)

Usage::

    python convert_help.py            # full pipeline
    python convert_help.py --no-lyx   # skip LyX export, reuse existing Help.tex

After running this, build the site with ``build.sh`` / ``build.bat``.
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LYX_FILE = os.path.join(HERE, 'Help.lyx')
TEX_FILE = os.path.join(HERE, 'Help.tex')
DOCS_DIR = os.path.join(HERE, 'docs')
FULL_MD = os.path.join(DOCS_DIR, '_full.md')
MEDIA_DIR = os.path.join(DOCS_DIR, 'media')


def _require(tool):
    if shutil.which(tool) is None:
        sys.stderr.write(
            "error: required tool '%s' not found on PATH.\n" % tool)
        return False
    return True


def export_tex():
    """Export Help.lyx to Help.tex using the LyX command line."""
    if not _require('lyx'):
        return False
    # 'lyx -e latex <file>' writes <file>.tex alongside the source.
    subprocess.check_call(['lyx', '-e', 'latex', LYX_FILE])
    if not os.path.isfile(TEX_FILE):
        sys.stderr.write('error: LyX did not produce %s\n' % TEX_FILE)
        return False
    return True


# LyX 2.4 modernised the automatic cross-reference label prefixes: subsections
# (and subsubsections) are now emitted as 'subsec:'.  The application and the
# legacy helpkeys, however, use 'sub:'.  Normalise the exported LaTeX back to the
# prefixes the application expects so the generated anchors keep matching the
# labels referenced by AddHelpElement(...).  Order matters: replace the longer
# 'subsubsec:' before 'subsec:' (one is a substring of the other).
LABEL_PREFIX_MAP = (
    ('subsubsec:', 'sub:'),
    ('subsec:', 'sub:'),
)


# Some labels were spelled differently in older releases of Help.lyx (and thus in
# the frozen legacy helpkeys the application may still reference).  When the
# canonical label changes we keep the retired spelling(s) alive as additional
# anchors so context-help requests for the old label keep resolving.  Map:
#   canonical-label -> (legacy-alias, ...)
LEGACY_LABEL_ALIASES = {
    # Historically written with a space instead of a hyphen.
    'sub:Output-Probes-for-Simulation': ('sub:Output-Probes-for Simulation',),
}


def normalize_labels(tex_path):
    """Rewrite LyX-2.4 label prefixes to the legacy prefixes the app expects."""
    with open(tex_path, 'r', encoding='utf-8') as f:
        tex = f.read()
    for old, new in LABEL_PREFIX_MAP:
        tex = tex.replace('{' + old, '{' + new)   # \label{..}, \ref{..}, \nameref{..}
        tex = tex.replace('[' + old, '[' + new)   # \hyperref[..]
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(tex)


# Headings with an embedded \label, e.g. '\subsubsection{Resistor\label{device:Resistor}}'.
_TEX_HEADING_RE = re.compile(
    r'\\(?:subsubsection|subsection|section)\*?\{([^{}]*)\\label\{([^}]+)\}([^{}]*)\}')
_NAMEREF_RE = re.compile(r'\\nameref\{([^}]+)\}')


def fix_namerefs(tex_path):
    """Replace \\nameref{LABEL} with \\hyperref[LABEL]{Title}.

    Pandoc drops \\nameref (its rendered text is the target section's title,
    which only LaTeX resolves at compile time), leaving empty links/bullets.
    We look up each label's heading title and emit an explicit hyperlink so
    Pandoc produces a proper '[Title](#LABEL)' link."""
    with open(tex_path, 'r', encoding='utf-8') as f:
        tex = f.read()

    title_map = {}
    for m in _TEX_HEADING_RE.finditer(tex):
        label = m.group(2)
        title = (m.group(1) + m.group(3)).strip()
        if title:
            title_map[label] = title

    def _humanize(label):
        return label.split(':', 1)[-1].replace('-', ' ')

    def repl(m):
        label = m.group(1)
        text = title_map.get(label) or _humanize(label)
        return '\\hyperref[%s]{%s}' % (label, text)

    tex = _NAMEREF_RE.sub(repl, tex)
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(tex)




def run_pandoc():
    """Convert Help.tex to a single Markdown file, extracting images.

    Pandoc is run with its working directory set to docs/ and a *relative*
    media path so that image links are written relative to the Markdown
    (media/...) rather than as absolute paths."""
    if not _require('pandoc'):
        return False
    if not os.path.isdir(DOCS_DIR):
        os.makedirs(DOCS_DIR)
    subprocess.check_call([
        'pandoc', TEX_FILE,
        '-f', 'latex',
        # gfm for tables/attributes, but use standard '$...$' / '$$...$$' math
        # delimiters (tex_math_dollars) instead of GitHub's '$`...`$' (tex_math_gfm),
        # which MkDocs/MathJax do not understand.
        '-t', 'gfm+tex_math_dollars-tex_math_gfm+attributes',
        '--wrap=none',
        '--quiet',                 # suppress benign 'Could not fetch resource'
        '--extract-media', 'media',  # warnings; images are resolved by resolve_images()
        '-o', '_full.md',
    ], cwd=DOCS_DIR)
    return True


# A label span emitted by Pandoc for a LyX \label{...}, e.g.
#   <span id="sec:About" data-label="sec:About"></span>
_SPAN_RE = re.compile(r'<span id="([^"]+)"[^>]*>\s*</span>')
_HEADING_RE = re.compile(r'^(#{1,6})[ \t]+(.*?)[ \t]*$', re.M)
# An ATX heading whose only content is an id attribute, e.g. '##### {#label}'.
# attr_list does not attach ids to empty headings, so these must become anchors.
_EMPTY_HEADING_RE = re.compile(r'^#{1,6}[ \t]*\{#([^}]+)\}[ \t]*$', re.M)


def _attr_safe(label):
    """True if *label* can be used as an attr_list heading id '{#label}'.

    attr_list treats '.' as a class separator and ' ' as an attribute
    separator, so labels containing those must use an explicit HTML anchor
    instead to preserve the exact id."""
    return '.' not in label and ' ' not in label


# Known context-help label prefixes (see gen_helpkeys / BuildHelpSystem).
_KNOWN_PREFIX = r'(?:sec|sub|Control-Help|device|par|pc):'
_HEADING_ANY_RE = re.compile(r'^(#{1,6})[ \t]+(.*)$', re.M)
_LABEL_BLOCK_RE = re.compile(r'\{#(' + _KNOWN_PREFIX + r'[^}\s]*)[^}]*\}')
_ANY_ATTR_BLOCK_RE = re.compile(r'\{[^}]*\}')


def _consolidate_heading_ids(text):
    """Make our label the sole id on headings Pandoc gave multiple attr blocks.

    Pandoc can emit a heading with both an auto-generated id and our \\label,
    e.g. '## Title {#autoid .unnumbered} {#sub:Foo}'.  attr_list only honours one
    block (and dotted auto-ids confuse it), so the wanted 'sub:Foo' id is lost.
    Rewrite such headings to carry only our label id."""
    def fix(m):
        hashes, content = m.group(1), m.group(2)
        lm = _LABEL_BLOCK_RE.search(content)
        if not lm:
            return m.group(0)
        label = lm.group(1)
        title = _ANY_ATTR_BLOCK_RE.sub('', content).strip()
        if _attr_safe(label):
            return '%s %s {#%s}' % (hashes, title, label)
        return '<div id="%s"></div>\n\n%s %s' % (label, hashes, title)
    return _HEADING_ANY_RE.sub(fix, text)


def _promote_heading_anchors(text):
    """Turn heading-trailing label spans into clean '{#label}' heading ids.

    Pandoc appends '<span id="LABEL" ...></span>' to the heading text.  This
    moves the first such LABEL into a MkDocs/attr_list heading id and drops the
    empty span.  Any additional label spans on the same heading are re-emitted as
    standalone anchor spans immediately after the heading so their ids survive."""
    def promote(m):
        hashes, title = m.group(1), m.group(2)
        ids = _SPAN_RE.findall(title)
        if not ids:
            return m.group(0)
        clean = _SPAN_RE.sub('', title).strip()
        primary = ids[0]
        if _attr_safe(primary):
            result = '%s %s {#%s}' % (hashes, clean, primary)
        else:
            # A block anchor preserves ids that attr_list would mangle (dots).
            result = '<div id="%s"></div>\n\n%s %s' % (primary, hashes, clean)
        for extra in ids[1:]:
            # Emit additional labels as block-level anchors so MkDocs/md_in_html
            # reliably preserves their ids (an inline <span> can be dropped).
            result += '\n\n<div id="%s"></div>' % extra
        return result
    return _HEADING_RE.sub(promote, text)


def _fix_image_paths(text):
    """Normalise extracted-media image links to relative, forward-slashed paths."""
    # Absolute media dir (either slash flavour) -> relative 'media'
    text = text.replace(MEDIA_DIR + os.sep, 'media/')
    text = text.replace(MEDIA_DIR + '/', 'media/')
    text = text.replace(MEDIA_DIR, 'media')
    # Forward-slash any remaining backslashes inside markdown image/link targets.
    def _slash(m):
        return '](' + m.group(1).replace('\\', '/') + ')'
    return re.sub(r'\]\(([^)]*)\)', _slash, text)


# --- Image resolution -------------------------------------------------------
#
# Pandoc cannot resolve LaTeX's extension-less \includegraphics{Name} against a
# real file, so it emits placeholders like:
#   <span class="image placeholder" data-original-image-src="Name" ...>image</span>
# The figures exist next to Help.lyx and, pre-rendered as PNG, in the frozen
# Help.html.LyXconv directory.  This pass resolves each placeholder to a real
# raster, copies (or converts) it into docs/media, and replaces the placeholder
# with a normal Markdown image link.
IMAGE_SEARCH_DIRS = [HERE, os.path.join(HERE, 'Help.html.LyXconv')]
# Preference order: already-raster formats first, then formats we convert.
_RASTER_EXTS = ('.png', '.jpg', '.jpeg', '.gif')
_CONVERT_EXTS = ('.bmp', '.eps', '.pdf')
_PLACEHOLDER_RE = re.compile(
    r'<span class="image placeholder"[^>]*data-original-image-src="([^"]*)"[^>]*>.*?</span>')

# figure name -> LaTeX \includegraphics scale factor (populated from Help.tex).
# LyX exports explicit graphic scaling as '\includegraphics[scale=S]{Name}'.
# Pandoc drops this, so we re-apply it as a pixel width on the emitted <img>.
GRAPHIC_SCALES = {}
_INCLUDEGRAPHICS_RE = re.compile(r'\\includegraphics(?:\[([^\]]*)\])?\{([^}]+)\}')

# figure name -> (width, height) in px, harvested from the frozen eLyXer help.
# eLyXer already computed the correct display size for every image (honouring
# LyX scaling and DPI, and capping oversized images), so reusing those values
# reproduces the known-good sizing exactly.
ELYXER_SIZES = {}
_ELYXER_IMG_RE = re.compile(r'<img[^>]*src="([^"/]+)\.png"[^>]*style="([^"]*)"')


def _parse_elyxer_style(style):
    """Return (width, height) px from an eLyXer <img> style.

    eLyXer uses 'max-width/max-height' for images shown at natural size, and adds
    an explicit 'width/height' (the actual display size) for scaled images.  The
    display size is 'width/height' when present, else 'max-width/max-height'."""
    def val(prop):
        m = re.search(r'(?:^|;)\s*' + prop + r':\s*(\d+)px', style)
        return int(m.group(1)) if m else None
    w = val('width') or val('max-width')
    h = val('height') or val('max-height')
    return w, h


def load_elyxer_sizes():
    """Harvest each image's display size from the frozen eLyXer help HTML."""
    sizes = {}
    lyxconv = os.path.join(HERE, 'Help.html.LyXconv')
    if not os.path.isdir(lyxconv):
        return sizes
    for fn in os.listdir(lyxconv):
        if not fn.endswith('.html'):
            continue
        try:
            with open(os.path.join(lyxconv, fn), 'r', encoding='utf-8',
                      errors='replace') as f:
                html = f.read()
        except OSError:
            continue
        for m in _ELYXER_IMG_RE.finditer(html):
            w, h = _parse_elyxer_style(m.group(2))
            if w and h:
                sizes.setdefault(m.group(1), (w, h))
    return sizes


def load_graphic_scales(tex_path):
    """Map each figure name to its \\includegraphics[scale=..] factor, if any."""
    scales = {}
    with open(tex_path, 'r', encoding='utf-8') as f:
        tex = f.read()
    for m in _INCLUDEGRAPHICS_RE.finditer(tex):
        opts = m.group(1) or ''
        name = m.group(2)
        sm = re.search(r'scale=([0-9.]+)', opts)
        if sm:
            scales[name] = float(sm.group(1))
    return scales


def _display_width(path, scale):
    """Return (display_width, natural_width) in pixels for an image.

    LaTeX sizes a bitmap by its stored DPI (natural size = pixels / dpi inches),
    then applies any '[scale=..]' factor.  Browsers ignore DPI (1 image px = 1
    CSS px), so a high-DPI image looks huge.  We reproduce LaTeX's sizing by
    scaling to a 96-CSS-px-per-inch basis: display = pixels * (96 / dpi) * scale.
    Missing DPI is treated as 96 (i.e. natural size)."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            natural = im.width
            dpi = im.info.get('dpi')
    except Exception:
        return None, None
    xdpi = dpi[0] if dpi and dpi[0] else 96.0
    display = max(1, round(natural * (96.0 / xdpi) * scale))
    return display, natural


def _find_image_source(name):
    """Locate a source image file for *name* using the extension preference."""
    for ext in _RASTER_EXTS + _CONVERT_EXTS:
        for d in IMAGE_SEARCH_DIRS:
            p = os.path.join(d, name + ext)
            if os.path.isfile(p):
                return p
    return None


def _ensure_media(src):
    """Copy (or convert to PNG) *src* into docs/media; return the media filename."""
    if not os.path.isdir(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)
    base = os.path.basename(src)
    stem, ext = os.path.splitext(base)
    if ext.lower() in _RASTER_EXTS:
        shutil.copy2(src, os.path.join(MEDIA_DIR, base))
        return base
    # Convert non-web rasters/vectors to PNG via Pillow (EPS/PDF need Ghostscript).
    dst_name = stem + '.png'
    try:
        from PIL import Image
        with Image.open(src) as im:
            im.save(os.path.join(MEDIA_DIR, dst_name))
        return dst_name
    except Exception as exc:  # pragma: no cover - depends on installed tooling
        sys.stderr.write('warning: could not convert %s (%s); copying as-is\n'
                         % (base, exc))
        shutil.copy2(src, os.path.join(MEDIA_DIR, base))
        return base


def resolve_images(text):
    """Replace Pandoc image placeholders with real Markdown image links."""
    missing = []

    def repl(m):
        name = m.group(1)
        src = _find_image_source(name)
        if src is None:
            missing.append(name)
            return m.group(0)
        # Emit an HTML <img> rather than Markdown '![]()': the placeholders sit
        # inside Pandoc's raw-HTML wrappers (e.g. <div class="center">), where
        # Markdown image syntax is not parsed and would render as literal text.
        media_name = _ensure_media(src)
        # Prefer the display size eLyXer already computed for this image; fall
        # back to a DPI/scale calculation for images not in the frozen help.
        esz = ELYXER_SIZES.get(name)
        if esz:
            width_attr = ' width="%d" height="%d"' % esz
        else:
            width_attr = ''
            scale = GRAPHIC_SCALES.get(name, 1.0)
            display, natural = _display_width(
                os.path.join(MEDIA_DIR, media_name), scale)
            if display and natural and display != natural:
                width_attr = ' width="%d"' % display
        return '<img src="media/%s" alt="%s"%s />' % (media_name, name, width_attr)

    text = _PLACEHOLDER_RE.sub(repl, text)
    if missing:
        sys.stderr.write('warning: %d figure(s) unresolved: %s\n'
                         % (len(missing), ', '.join(sorted(set(missing)))))
    return text



def _inject_legacy_aliases(text):
    """Emit a block anchor for every retired spelling of a still-present label.

    For each canonical label in LEGACY_LABEL_ALIASES that appears as a heading id
    ('{#canonical}') in *text*, insert a '<div id="alias"></div>' anchor right
    after that heading for each retired alias, so the old label still resolves."""
    for canonical, aliases in LEGACY_LABEL_ALIASES.items():
        heading_re = re.compile(
            r'^(#{1,6}[ \t]+.*\{#' + re.escape(canonical) + r'\}[ \t]*)$', re.M)
        anchors = ''.join('\n\n<div id="%s"></div>' % a for a in aliases)
        text, n = heading_re.subn(lambda m: m.group(1) + anchors, text)
        if not n:
            sys.stderr.write(
                'warning: legacy alias target not found for %s\n' % canonical)
    return text


def _slugify(text):
    text = re.sub(r'\{#[^}]*\}', '', text)           # drop any {#id}
    text = re.sub(r'<[^>]+>', '', text)              # drop any HTML tags
    text = re.sub(r'[`*_]', '', text).strip()
    text = re.sub(r'[^A-Za-z0-9]+', '-', text).strip('-')
    return text or 'section'


_ANCHOR_ID_RE = re.compile(r'\{#([^}]+)\}')
_ID_ATTR_RE = re.compile(r'id="([^"]+)"')
_INTERNAL_LINK_RE = re.compile(r'\]\(#([^)]+)\)')


def _build_anchor_map(named_sections):
    """Map every anchor id to the .md file that contains it."""
    amap = {}
    for heading, body, fname in named_sections:
        blob = heading + ''.join(body)
        for lbl in _ANCHOR_ID_RE.findall(blob):
            amap.setdefault(lbl, fname)
        for lbl in _ID_ATTR_RE.findall(blob):
            amap.setdefault(lbl, fname)
    return amap


def _rewrite_internal_links(text, amap):
    """Point same-doc '#label' links at the .md page that owns the anchor.

    Pandoc emits cross-references as same-page '#label' links, but the single
    document is split across many pages.  Rewriting to 'page.md#label' makes the
    links navigate correctly (MkDocs resolves .md targets and validates anchors)."""
    def repl(m):
        label = m.group(1)
        target = amap.get(label)
        return '](%s#%s)' % (target, label) if target else m.group(0)
    return _INTERNAL_LINK_RE.sub(repl, text)


def split_sections():
    """Split docs/_full.md at level-1 headings into ordered per-section files."""
    with open(FULL_MD, 'r', encoding='utf-8') as f:
        text = f.read()

    # Clean up the raw Pandoc output before splitting.
    text = _promote_heading_anchors(text)
    # Consolidate headings that Pandoc gave multiple attr blocks onto our label.
    text = _consolidate_heading_ids(text)
    # Empty id-only headings can't carry ids; convert them to block anchors.
    text = _EMPTY_HEADING_RE.sub(lambda m: '<div id="%s"></div>' % m.group(1), text)
    # Keep retired label spellings resolvable via extra block anchors.
    text = _inject_legacy_aliases(text)
    text = resolve_images(text)
    text = _fix_image_paths(text)
    lines = text.splitlines(keepends=True)

    # Everything before the first H1 becomes the landing page preamble.
    sections = []           # list of (heading_line, [body_lines])
    preamble = []
    current = None
    h1re = re.compile(r'^#\s+')
    for line in lines:
        if h1re.match(line):
            if current is not None:
                sections.append(current)
            current = [line, []]
        elif current is None:
            preamble.append(line)
        else:
            current[1].append(line)
    if current is not None:
        sections.append(current)

    # Assign each section its output filename, then build the anchor->file map so
    # cross-page links can be rewritten to target the correct page.
    named = []
    for i, (heading, body) in enumerate(sections, start=1):
        title = h1re.sub('', heading).strip()
        fname = '%02d-%s.md' % (i, _slugify(title))
        named.append((heading, body, fname))
    amap = _build_anchor_map(named)

    # Clean out previously generated section files (but keep hand-written index).
    for name in os.listdir(DOCS_DIR):
        if re.match(r'^\d\d-.*\.md$', name):
            os.remove(os.path.join(DOCS_DIR, name))

    index_path = os.path.join(DOCS_DIR, 'index.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('# SignalIntegrity Help\n\n')
        f.write(_rewrite_internal_links(''.join(preamble), amap))

    for heading, body, fname in named:
        content = _rewrite_internal_links(heading + ''.join(body), amap)
        with open(os.path.join(DOCS_DIR, fname), 'w', encoding='utf-8') as f:
            f.write(content)

    os.remove(FULL_MD)
    sys.stdout.write('wrote %d section pages to %s\n' % (len(named), DOCS_DIR))


def main(argv):
    do_lyx = '--no-lyx' not in argv
    if do_lyx and not export_tex():
        return 1
    if not os.path.isfile(TEX_FILE):
        sys.stderr.write('error: %s not found (run without --no-lyx)\n' % TEX_FILE)
        return 1
    normalize_labels(TEX_FILE)
    fix_namerefs(TEX_FILE)
    GRAPHIC_SCALES.update(load_graphic_scales(TEX_FILE))
    ELYXER_SIZES.update(load_elyxer_sizes())
    if not run_pandoc():
        return 1
    split_sections()
    sys.stdout.write('conversion complete. Now run build.sh / build.bat.\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
