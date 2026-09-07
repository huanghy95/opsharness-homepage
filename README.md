# OpsHarness Paper Homepage

Static bilingual homepage for the paper “From General Agents to RCA Experts: A
Self-Evolving Harness for Root Cause Analysis.”

- arXiv: <https://arxiv.org/abs/2608.25661>
- PDF: <https://arxiv.org/pdf/2608.25661>

## Local preview

From the `OpsHarness-Arxiv` workspace:

```bash
cd homepage/ops_harness_homepage
python3 -m http.server 8000
```

Open <http://127.0.0.1:8000/>. Stop the server with `Ctrl+C`.

## Validation

Run from `homepage/ops_harness_homepage`:

```bash
python3 -m unittest discover -s tests -v
node --check static/js/i18n.js
node --check static/js/main.js
```

The tests verify section structure, official links, intentional Coming Soon resources,
figure assets and alternative text, paper claims, author order, bilingual key parity,
responsive CSS contracts, and accessible interaction hooks.

## Content updates

- Paper and arXiv URLs live in `index.html`.
- Code and Demo are intentionally non-clickable Coming Soon controls.
- English and Chinese interface copy lives in `static/js/i18n.js`; keep both key sets
  identical.
- Figures under `static/images/` are deployable copies rendered from `paper/figs/`.
- The page is English-first and remains readable without JavaScript. JavaScript adds
  language persistence, navigation state, tabs, copy feedback, counters, reveal effects,
  and the figure lightbox.

## Deployment

Serve the directory root as a static site. No package installation or build step is
required. For GitHub Pages, publish the repository root from the branch used for the
site.
