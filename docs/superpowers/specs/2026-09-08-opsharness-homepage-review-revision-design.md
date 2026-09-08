# OpsHarness Homepage Review Revision Design

Date: 2026-09-08

## 1. Objective

Revise the completed OpsHarness paper homepage in response to the first visual review.
The revision should reduce hero density, sharpen the paper's central argument, introduce
self-evolution earlier, improve figure scale and framing, and make the complete overall
effectiveness table a first-class result.

The website remains a dependency-free static site with English as the default language
and Chinese available through the existing toggle. Text embedded inside paper figures,
model and dataset names, commands, metrics, citations, URLs, and BibTeX remain in
English in both modes.

## 2. Review Decisions

The revision implements the ten approved review decisions:

1. Shorten the displayed hero title to “OpsHarness: A Self-Evolving Harness for Root
   Cause Analysis.”
2. Add Self-Evolve to the hero capability visual so the defining behavior appears on
   first view.
3. Remove “Individual Researcher” from displayed affiliations.
4. Attribute mature general capability to the model and general agent infrastructure,
   not to the entire task-specific agent system.
5. Fix insufficient text contrast on the violet OpsHarness comparison card.
6. Merge the former Shift and Self-Evolution sections into one earlier narrative about
   the RCA harness gap and the need to learn from repeated diagnosis.
7. Replace the current motivating case figure with a web-rendered copy of
   `paper/figs/moti_v2.pdf`.
8. Reduce the visual footprint of large figures and place them inside deliberate
   editorial figure frames.
9. Add a web-rendered copy of `paper/figs/self-evolveV2.pdf` to the Method section.
10. Rebuild the complete overall-effectiveness Table II as semantic HTML.

## 3. Narrative and Information Architecture

### 3.1 Hero

The displayed heading becomes:

> OpsHarness: A Self-Evolving Harness for Root Cause Analysis

This shorter heading is a homepage display title, not a replacement for the paper's
official title. The exact paper title remains in page metadata where appropriate, the
abstract context, and BibTeX.

The hero thesis remains concise and describes a verified, self-evolving external
harness. The author order remains unchanged. Displayed affiliations become “The Chinese
University of Hong Kong · ByteDance.”

The existing CSS illustration remains on the right. Its capability list expands from
Skills, Knowledge, Tools, and Verification to include Self-Evolve. The composition must
make self-evolution legible without increasing the card height or recreating the crowded
title layout.

### 3.2 Section 01 — The RCA Harness Gap

The former “The agent is capable / The harness is the missing layer” section and the
separate Self-Evolution section are consolidated into one section. The heading becomes:

> General models are capable.
> The RCA gap is a harness that learns.

The narrative follows the paper's Introduction and Motivation:

1. Modern general models and general-purpose agent infrastructure already provide
   strong reasoning, tool use, code execution, sandboxing, and planning.
2. RCA remains unreliable when the surrounding harness lacks system-specific
   operational knowledge, diagnostic procedures, and evidence-aware tools.
3. A static harness is insufficient because RCA is a continuous process and similar
   incidents recur.
4. The missing layer is therefore a self-evolving RCA harness that accumulates reusable
   system expertise while verifying changes before promotion.

The current three comparison cards are rewritten as:

- General capability is no longer the main bottleneck.
- RCA-specific adaptation lives in the harness.
- Static adaptation must become verified self-evolution.

The violet OpsHarness card uses high-contrast light text for its body copy.

The paper's “OpsHarness Injects Superpowers” figure remains in this section but changes
from a full-width presentation to a contained editorial figure with adjacent explanatory
copy. Its purpose is to summarize the external capabilities supplied by the harness.

The human-SRE motivation case from `moti_v2.pdf` appears later in the same section. It is
presented faithfully as motivation: an SRE is first misled by a database-session drop,
records the CPU-to-RemoteProcess propagation chain and caveat, and reuses the lesson on
a later incident. The text does not claim this particular illustrated event was an
OpsHarness run. A short bridge explains that OpsHarness automates this accumulation and
subjects generated proposals to verification.

The old standalone `<section id="evolution">`, incident-story cards, and duplicated
verification strip are removed. Results, Usage, Paper, and Citation section numbers are
shifted accordingly.

### 3.3 Section 02 — Method

The Data Plane and Control Plane cards remain because they provide a readable method
overview. The main architecture figure remains but receives a narrower maximum width,
more surrounding whitespace, and an editorial label/caption frame.

The Method section adds a second focused block for `self-evolveV2.pdf`. Its adjacent copy
summarizes:

- contrasting successful and failed evaluated trajectories;
- converting evidence into atomic, reviewable proposals;
- applying proposals in an isolated stage environment;
- requiring improvement on source cases; and
- preventing regression on a disjoint held-out testbed before promotion.

This is the only detailed self-evolution explanation after Section 01, preventing the
previous narrative duplication.

### 3.4 Section 03 — Results

The four result-summary cards remain. Immediately after them, Table II becomes the
primary evidence artifact.

The complete table is rebuilt in HTML and includes:

- all four backbone groups: GPT-5.5, Claude Sonnet 4.0, GLM-5.2, and DeepSeek-V4;
- all six frameworks in each group: RCA-Agent, mABC, Direct, ICL, OpsHarness
  (no-evolve), and OpsHarness;
- the Telecom, Bank, Market, Online Boutique, Sock Shop, and Train Ticket sub-datasets;
- A@1, A@3, and Avg for every sub-dataset; and
- Final A@1.

Every value is copied from the LaTeX source, not transcribed from the screenshot. The
table uses multi-row semantic headers, `<caption>`, `<thead>`, and `<tbody>`. Backbone
groups receive restrained color bands matching the paper. The OpsHarness row is bold and
lightly tinted, and best values retain the paper's emphasis where practical.

The table is allowed to break out wider than the normal reading column on large screens.
At narrower widths it lives inside a labeled horizontal scroll region with a sticky
Framework column and a visible scroll hint. Horizontal scrolling must remain inside the
table container and never create page-level overflow.

The existing evolution, industrial, and cost result figures remain below the table in a
compact mosaic. No result figure should occupy approximately a full viewport height.

### 3.5 Remaining Sections

Usage, Abstract, Citation, language switching, mobile navigation, tabs, copy feedback,
and the figure lightbox retain their current behavior. Their displayed section numbers
are updated after removal of the standalone evolution section.

## 4. Figure Processing and Presentation

Two source PDFs are added:

- `paper/figs/moti_v2.pdf` → an optimized WebP under `static/images/`;
- `paper/figs/self-evolveV2.pdf` → an optimized WebP under `static/images/`.

The original PDFs are never modified. Web copies are rendered at a resolution that keeps
embedded English labels readable when enlarged, then optimized for delivery. Intrinsic
width and height, lazy loading, asynchronous decoding, meaningful English alternative
text, and click-to-enlarge behavior are required.

Large figure frames use per-role maximum widths rather than one universal full-width
rule. Approximate targets are 800–980 px for narrative figures and 960–1120 px for dense
method figures, with smaller limits on narrow displays. Captions and contextual copy
remain outside the raster image.

## 5. Internationalization

All new headings, prose, captions, scroll instructions, and interface labels are added to
both English and Chinese catalogs with identical key sets. The following remain English:

- hero display title and official paper title;
- author names and displayed institution names;
- labels embedded in figures;
- model, framework, and dataset names;
- table metric abbreviations and numeric values;
- usage commands and BibTeX.

Chinese text must describe general model capability rather than claiming that the full
RCA agent is already complete without a harness.

## 6. Accessibility and Progressive Enhancement

- The full Table II remains readable without JavaScript.
- The table has a useful caption, scoped headers, and an accessible scroll-region label.
- Sticky columns and color bands are enhancements; meaning never depends only on color.
- Figures keep descriptive alternatives and keyboard-accessible enlargement controls.
- New text and the violet comparison card meet WCAG AA normal-text contrast.
- Reduced-motion mode and the no-JavaScript baseline continue to expose all content.

## 7. Testing and Verification

Static contract tests will verify:

- the shorter display title and preserved official title/BibTeX;
- removal of “Individual Researcher” from the homepage;
- Self-Evolve in the hero capability list;
- removal of the standalone evolution section;
- existence, format, dimensions, and loading attributes of the two new figure assets;
- full Table II structure, four backbone groups, expected framework rows, and selected
  sentinel values from each group;
- English/Chinese key parity;
- the corrected violet-card contrast; and
- absence of stale references to the replaced figure.

Browser QA will re-check English-first behavior, Chinese persistence, translated
accessible labels, tabs, copy feedback, lightbox focus, no-JavaScript rendering,
reduced-motion behavior, local image loading, and page-level overflow at 390, 768, and
1440 px. Visual screenshots will be reviewed at desktop and mobile widths, with special
attention to hero density, figure scale, Table II scrolling, and long Chinese wrapping.

## 8. Scope Boundaries

This revision does not add a backend, analytics, a live demo, repository URLs, or new
experimental claims. Code and Demo remain Coming Soon. The complete results table is
static paper content, not a sortable or continuously updated leaderboard.
