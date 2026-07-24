// Context-help anchor scrolling fix  (version tag: ANCHORFIX v4)
//
// Context-sensitive ("Control Help") requests open a help page at a fragment
// such as '...23-Built-in-Devices-Parts.html#device:Resistor'.  With the
// Read-the-Docs MkDocs theme the browser's native jump to that anchor
// frequently fails and the page is left at (or near) the very top, because the
// content reflows *after* the initial jump:
//   * MathJax typesets equations after it loads (from a CDN), moving everything
//     below it further down, and
//   * images / highlighted code blocks decode and lay out lazily.
// The browser performs its one-shot jump before these happen, so by the time
// the layout settles the target is no longer where the viewport was placed.
//
// This script re-resolves the URL hash and keeps the target aligned to the top
// of the viewport across late reflow.  It uses getElementById (which matches the
// exact id, including the ':' characters in our labels, unlike a CSS selector).
//
// Design notes:
//   * We compute an absolute page offset and use window.scrollTo instead of
//     Element.scrollIntoView, which behaves consistently regardless of theme
//     quirks and of the browser's scroll-anchoring heuristics.
//   * We disable overflow-anchor so the browser does not shift the viewport on
//     its own while content above the target reflows.
//   * We keep correcting for a generous period (MathJax from a CDN on a long
//     page can take several seconds) and re-assert specifically after MathJax
//     finishes and after every image loads.
//   * We stop only on genuine user input (wheel / touch / mouse / navigation
//     keys) so we never fight a deliberate scroll.
//   * A single console line ('ANCHORFIX v4 ...') is emitted so it is possible to
//     confirm at runtime that this script (and not a cached or stale online
//     copy) is the one actually running.
(function () {
    'use strict';

    var VERSION = 'ANCHORFIX v6';

    // Prevent the browser from restoring a previously saved scroll position
    // (typically the top of the page) when the same file:// URL is revisited or
    // restored from the back/forward cache.  Without this, Edge/Chrome restore
    // the old scroll position *after* the fragment jump, leaving the page at the
    // top even though the URL carries a '#anchor'.  We take over scrolling.
    try {
        if ('scrollRestoration' in history) { history.scrollRestoration = 'manual'; }
    } catch (e) { /* ignore */ }

    // How long to keep correcting for late reflow, and how often to re-check.
    var MAX_WATCH_MS = 10000;
    var POLL_MS = 100;

    // Keys that scroll the page; pressing any of these means the user is taking
    // over navigation and we should stop auto-correcting.
    var NAV_KEYS = {
        PageUp: 1, PageDown: 1, End: 1, Home: 1,
        ArrowUp: 1, ArrowDown: 1, ' ': 1, Spacebar: 1
    };

    // Turn off browser scroll anchoring so it does not shift the viewport while
    // MathJax / images reflow the content above our target.
    try {
        var de = document.documentElement;
        if (de && de.style) { de.style.overflowAnchor = 'none'; }
    } catch (e) { /* ignore */ }

    function hashId() {
        if (!window.location.hash) { return null; }
        var raw = window.location.hash.substring(1);
        if (!raw) { return null; }
        var id;
        try { id = decodeURIComponent(raw); } catch (e) { id = raw; }
        return { decoded: id, raw: raw };
    }

    function targetElement() {
        var h = hashId();
        if (!h) { return null; }
        return document.getElementById(h.decoded) ||
               document.getElementById(h.raw);
    }

    // Find the nearest ancestor that is actually scrollable.  With some themes
    // (e.g. Read-the-Docs) the content scrolls inside a container rather than the
    // window; in that case window.scrollTo() is a no-op and the page stays at the
    // top.  Returning the real scroll parent lets us handle both layouts.
    function scrollParentOf(el) {
        var node = el.parentElement;
        while (node && node !== document.body && node !== document.documentElement) {
            var style = window.getComputedStyle(node);
            var oy = style.overflowY;
            if ((oy === 'auto' || oy === 'scroll') &&
                node.scrollHeight > node.clientHeight + 1) {
                return node;
            }
            node = node.parentElement;
        }
        return null;
    }

    // Absolute Y offset of an element from the top of the document.
    function pageTopOf(el) {
        var rect = el.getBoundingClientRect();
        return rect.top + (window.pageYOffset ||
                           document.documentElement.scrollTop || 0);
    }

    function align(el) {
        el = el || targetElement();
        if (!el) { return false; }

        // Case 1: the content scrolls inside a container (theme-dependent).
        var sp = scrollParentOf(el);
        if (sp) {
            var wantC = sp.scrollTop +
                        (el.getBoundingClientRect().top - sp.getBoundingClientRect().top);
            if (Math.abs(Math.round(wantC) - Math.round(sp.scrollTop)) > 2) {
                sp.scrollTop = wantC;
            }
        }

        // Case 2: the window scrolls (most themes).  Do this as well so we cover
        // both layouts without needing to know which one is in effect.
        var want = Math.round(pageTopOf(el));
        var have = Math.round(window.pageYOffset ||
                              document.documentElement.scrollTop || 0);
        if (Math.abs(want - have) > 2) {
            window.scrollTo(0, want);
        }

        // Belt-and-braces: let the browser align it too.  Harmless if the above
        // already did the job.
        if (typeof el.scrollIntoView === 'function') {
            try { el.scrollIntoView({ block: 'start', inline: 'nearest' }); }
            catch (e) { el.scrollIntoView(true); }
        }
        return true;
    }

    function watchAndAlign() {
        var initial = targetElement();
        // Emit a diagnostic line regardless, so the running version is visible.
        try {
            var h = hashId();
            console.log(VERSION + ': hash=' + (h ? '#' + h.decoded : '(none)') +
                        ' target=' + (initial ? 'found' : 'MISSING'));
        } catch (e) { /* ignore */ }

        if (!initial) { return; }

        var userTookOver = false;
        var ro = null, mo = null, timer = null;

        function cleanup() {
            window.removeEventListener('wheel', onUserInput, { capture: true });
            window.removeEventListener('touchstart', onUserInput, { capture: true });
            window.removeEventListener('mousedown', onUserInput, { capture: true });
            window.removeEventListener('keydown', onKeyDown, { capture: true });
            if (ro) { ro.disconnect(); ro = null; }
            if (mo) { mo.disconnect(); mo = null; }
            if (timer) { clearInterval(timer); timer = null; }
        }
        function stop() { userTookOver = true; cleanup(); }
        function onUserInput() { stop(); }
        function onKeyDown(ev) { if (NAV_KEYS[ev.key]) { stop(); } }
        function tryAlign() { if (!userTookOver) { align(); } }

        window.addEventListener('wheel', onUserInput, { capture: true, passive: true });
        window.addEventListener('touchstart', onUserInput, { capture: true, passive: true });
        window.addEventListener('mousedown', onUserInput, { capture: true });
        window.addEventListener('keydown', onKeyDown, { capture: true });

        if (typeof ResizeObserver !== 'undefined') {
            ro = new ResizeObserver(function () { tryAlign(); });
            ro.observe(document.documentElement);
            if (document.body) { ro.observe(document.body); }
        }
        if (typeof MutationObserver !== 'undefined') {
            mo = new MutationObserver(function () { tryAlign(); });
            mo.observe(document.documentElement, {
                childList: true, subtree: true, attributes: true,
                attributeFilter: ['style', 'class', 'height', 'width']
            });
        }

        // MathJax reflows equations once typesetting finishes; re-assert across
        // the frames right after, when heights settle.
        if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
            window.MathJax.startup.promise.then(function () {
                tryAlign();
                requestAnimationFrame(function () {
                    tryAlign();
                    requestAnimationFrame(tryAlign);
                });
            }).catch(function () { /* ignore */ });
        }

        // Late-decoding images shift content as they lay out.
        var imgs = document.images;
        for (var i = 0; i < imgs.length; i++) {
            if (!imgs[i].complete) {
                imgs[i].addEventListener('load', tryAlign);
                imgs[i].addEventListener('error', tryAlign);
            }
        }

        // Initial alignment plus a bounded polling loop that catches any reflow
        // the observers miss, then stops so it never lingers.
        align(initial);
        var elapsed = 0;
        timer = setInterval(function () {
            elapsed += POLL_MS;
            tryAlign();
            if (userTookOver || elapsed >= MAX_WATCH_MS) { cleanup(); }
        }, POLL_MS);
    }

    if (document.readyState === 'complete') {
        watchAndAlign();
    } else {
        window.addEventListener('load', watchAndAlign);
    }

    // Restore from the back/forward cache: 'load' does NOT fire in this case, so
    // without this handler the anchor would never be re-aligned and the page
    // would show at whatever position the cache saved (often the top).
    window.addEventListener('pageshow', function (ev) {
        if (ev && ev.persisted) { watchAndAlign(); }
    });

    // Handle in-page navigation between anchors on an already-loaded page.
    window.addEventListener('hashchange', watchAndAlign);
})();
