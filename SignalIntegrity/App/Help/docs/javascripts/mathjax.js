// MathJax v3 configuration for pymdownx.arithmatex (generic mode).
// arithmatex wraps math in elements with class "arithmatex" using \( \) and \[ \]
// delimiters; this tells MathJax to typeset only those.
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};
