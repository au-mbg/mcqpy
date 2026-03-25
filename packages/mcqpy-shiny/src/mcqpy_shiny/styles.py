"""Styling and MathJax bootstrap for the quiz app."""

from __future__ import annotations


def build_css(card_width: str) -> str:
    return """
.mcqpy-shell {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}
.mcqpy-card {
  width: __CARD_WIDTH__;
  max-width: __CARD_WIDTH__;
  min-width: __CARD_WIDTH__;
  margin: 0 auto;
  box-sizing: border-box;
  overflow-x: hidden;
}
.mcqpy-card .card-body {
  overflow-x: hidden;
}
.mcqpy-question-text,
.mcqpy-question-text p,
.mcqpy-question-text li {
  font-size: 1.05rem;
  line-height: 1.65;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.mcqpy-question-meta {
  margin: 0.25rem 0 1rem;
  color: #475569;
  font-size: 0.98rem;
}
.mcqpy-media {
  margin: 1rem 0 1.5rem;
  min-height: 0;
}
.mcqpy-media img {
  display: block;
  max-width: min(100%, 900px);
  height: auto;
  margin: 0 auto;
}
.mcqpy-media pre {
  max-width: 100%;
  overflow-x: auto;
  white-space: pre-wrap;
}
.mcqpy-media code,
.mcqpy-question-text code {
  overflow-wrap: anywhere;
  word-break: break-word;
}
.mcqpy-answer-group .shiny-input-radiogroup,
.mcqpy-answer-group .shiny-input-checkboxgroup {
  width: 100%;
}
.mcqpy-answer-group .radio,
.mcqpy-answer-group .checkbox {
  display: block;
  width: 100%;
  margin-bottom: 0.9rem;
}
.mcqpy-answer-group label.radio,
.mcqpy-answer-group label.checkbox {
  display: block;
  width: 100%;
  padding: 0.9rem 1rem;
  border: 1px solid #d9dee5;
  border-radius: 0.75rem;
  background: #fff;
}
.mcqpy-answer-group input[type="radio"],
.mcqpy-answer-group input[type="checkbox"] {
  margin-right: 0.65rem;
}
.mcqpy-nav-row {
  margin-top: 1.25rem;
}
.mcqpy-jump-row {
  margin: 0.5rem 0 1rem;
  align-items: end;
}
.mcqpy-results-chart {
  margin: 1.25rem 0 0.75rem;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.85rem;
  background: #fcfdff;
}
.mcqpy-results-chart svg {
  display: block;
  width: 100%;
  height: auto;
}
.mcqpy-overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(68px, 1fr));
  gap: 0.6rem;
  margin: 0.9rem 0 1.25rem;
}
.mcqpy-overview-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 58px;
  padding: 0.7rem;
  border: 1px solid #d9dee5;
  border-radius: 0.75rem;
  background: #fff;
  text-align: center;
}
.mcqpy-overview-button.is-answered {
  background: #eff6ff;
  border-color: #93c5fd;
}
.mcqpy-overview-button.is-current {
  border-color: #2563eb;
  box-shadow: inset 0 0 0 1px #2563eb;
}
.mcqpy-overview-number {
  font-size: 1rem;
  font-weight: 700;
  color: #2563eb;
}
@media (max-width: 820px) {
  .mcqpy-card {
    width: 100%;
    max-width: 100%;
    min-width: 0;
  }
}
""".replace("__CARD_WIDTH__", card_width)


MATHJAX_HEAD = """
window.MathJax = {
  tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']] },
  svg: { fontCache: 'global' }
};
"""


MATHJAX_BOOTSTRAP = """
(() => {
  let timer = null;
  let observer = null;
  const typeset = () => {
    if (!window.MathJax || !window.MathJax.typesetPromise) return;
    const nodes = document.querySelectorAll('.mcqpy-math');
    if (nodes.length) window.MathJax.typesetPromise(Array.from(nodes)).catch(() => {});
  };
  const schedule = () => {
    clearTimeout(timer);
    timer = setTimeout(typeset, 125);
  };
  const install = () => {
    schedule();
    if (observer || !document.body) return;
    observer = new MutationObserver(schedule);
    observer.observe(document.body, { childList: true, subtree: true });
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', install, { once: true });
  } else {
    install();
  }
  window.addEventListener('load', schedule);
})();
"""
