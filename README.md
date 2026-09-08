# OpsHarness Paper Homepage

Static bilingual homepage for the paper “From General Agents to RCA Experts: A
Self-Evolving Harness for Root Cause Analysis.”

- arXiv: <https://arxiv.org/abs/2608.25661>
- PDF: <https://arxiv.org/pdf/2608.25661>

## Local preview

To review the current feature branch before it is merged, serve the isolated worktree:

```bash
cd /Users/huanghaiyu/Workspace/OpsHarness-Arxiv/homepage/ops_harness_homepage/.worktrees/opsharness-homepage
python3 -m http.server 8000
```

Open <http://127.0.0.1:8000/>. Stop the server with `Ctrl+C`. If port 8000 is
already occupied, use another port in both the command and URL.

## Review this revision

1. Confirm the hero uses the short title, shows five capabilities including
   `Self-Evolve`, and does not display `Individual Researcher`.
2. In **Overview**, confirm the narrative progresses from capable general models to
   the RCA harness gap and then to verified self-evolution.
3. Confirm the violet self-evolution card has clearly readable body text.
4. Confirm the compact superpowers figure and the `moti_v2` motivation figure are
   both framed and do not dominate a full viewport.
5. In **Method**, confirm the architecture figure is bounded and the
   `self-evolveV2` figure explains trajectory mining, proposal synthesis, and staged
   verification.
6. In **Results**, confirm Table II contains four backbone groups and six framework
   rows per group. On a narrow window, scroll the table inside its frame and verify
   that the framework column remains fixed.
7. Toggle **中文**. Prose should switch to Chinese; figure text, model/framework
   names, metrics, commands, and BibTeX should remain English.
8. Open several figures, then close the lightbox with both its Close button and the
   `Escape` key.

Source mapping for the reviewed assets and results:

- `paper/figs/moti_v2.pdf` → `static/images/motivation-case.webp`
- `paper/figs/self-evolveV2.pdf` → `static/images/self-evolve-loop.webp`
- `paper/tabs/exp_1.tex` → complete semantic HTML Table II

## Validation

Run from `homepage/ops_harness_homepage`:

```bash
python3 -m unittest discover -s tests -v
node --check static/js/i18n.js
node --check static/js/main.js
```

For optional end-to-end browser coverage (requires Playwright and Chrome or Chromium):

```bash
python3 tests/browser_qa.py
```

The tests verify section structure, official links, intentional Coming Soon resources,
figure assets and alternative text, paper claims, all 24 Table II rows, author order,
bilingual key parity, responsive CSS contracts, contrast, and accessible interaction
hooks. The browser QA covers the no-JavaScript fallback, language persistence and
translated ARIA labels, pointer and keyboard interactions, modal focus containment,
internal table scrolling, sticky framework labels, reduced motion, and viewport
overflow.

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
