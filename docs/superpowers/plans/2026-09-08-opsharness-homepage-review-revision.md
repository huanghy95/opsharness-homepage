# OpsHarness Homepage Review Revision Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task by task. Apply test-driven-development for markup and behavior changes, pdf for the two paper figures, browser:browser for visual QA, requesting-code-review before handoff, and verification-before-completion before claiming completion.

**Goal:** Apply the ten approved review changes to the bilingual OpsHarness paper homepage: simplify the hero, rebuild the motivation narrative around an RCA-specific self-evolving harness, add the two requested paper figures, render Table II as a complete responsive HTML table, and reduce oversized visuals.

**Architecture:** Keep the site dependency-free and statically deployable. Continue using semantic HTML in index.html, design tokens and responsive layout in static/css/style.css, the existing English/Chinese dictionary in static/js/i18n.js, and the existing progressive-enhancement JavaScript in static/js/main.js. Convert the two source PDFs into optimized WebP assets at build time; do not add a PDF renderer or a table-rendering dependency to the browser.

**Tech Stack:** HTML5, CSS3, vanilla JavaScript, Python unittest, Playwright browser QA, Poppler PDF utilities, WebP tooling.

---

## Content and data invariants

- The visible hero title is exactly “OpsHarness: A Self-Evolving Harness for Root Cause Analysis.”
- The official paper title remains unchanged in BibTeX: “From General Agents to RCA Experts: A Self-Evolving Harness for Root Cause Analysis.”
- The displayed affiliations are “The Chinese University of Hong Kong · ByteDance”; “Individual Researcher” appears nowhere in the rendered page.
- English remains the default. Every new prose key has matching English and Chinese values. Figure labels, framework/model names, metrics, commands, and BibTeX remain English in both language modes.
- The former standalone evolution section is removed. Its motivation belongs in Overview; its mechanism belongs in Method.
- Table II is semantic HTML and contains all 24 framework rows from paper/tabs/exp_1.tex, grouped under GPT-5.5, Claude Sonnet 4.6, GLM-5.2, and DeepSeek-V4.
- The table uses paper/tabs/exp_1.tex as its source of truth. Do not infer numbers from the screenshot.
- paper/figs/moti_v2.pdf is described as a motivating SRE case, not as an automated OpsHarness trace.
- paper/figs/self-evolveV2.pdf is described as the method-level self-evolution mechanism.

## Task 1: Lock the revised static contracts with failing tests

**Files:**

- Modify: tests/test_site.py
- Test: tests/test_site.py

**Step 1: Change the section contract**

The required IDs become overview, method, results, usage, abstract, and citation. Add an explicit assertion that evolution is absent.

**Step 2: Add a hero and affiliation contract**

Add test_reviewed_hero_and_affiliations_are_exact. It must assert:

    OpsHarness: <em>A Self-Evolving Harness</em> for Root Cause Analysis
    Skills
    Knowledge
    Tools
    Verification
    Self-Evolve
    The Chinese University of Hong Kong · ByteDance

It must also assert that “Individual Researcher” is absent.

**Step 3: Replace the obsolete incident-story contract**

Remove test_incident_story_does_not_merge_distinct_paper_cases. Add assertions for:

    src="static/images/motivation-case.webp"
    src="static/images/self-evolve-loop.webp"

Also assert that incident-learning.webp and class="incident-story" are absent.

**Step 4: Lock the revised narrative**

Add test_shift_copy_names_the_model_and_the_harness_gap. Assert that the English source contains:

    General models are capable.
    The RCA gap is a harness that learns.

Assert that “The agent is capable.” is absent from index.html and static/js/i18n.js.

**Step 5: Add a table-row extractor and Table II contract**

Add a small regular-expression helper that:

1. Locates a tbody by data-backbone.
2. Locates a tr within it by data-framework.
3. Extracts th/td text, strips tags, and normalizes whitespace.

Add test_full_table_ii_is_rendered_as_semantic_html. Assert:

- One table with class results-table.
- Four tbody groups with data-backbone values gpt-5.5, claude-sonnet-4.6, glm-5.2, deepseek-v4.
- Exactly 24 framework data rows.
- Every framework data row has 19 numeric cells after its row header, for 20 cells total.
- Four sentinel OpsHarness rows exactly match:

    gpt-5.5:
    OpsHarness, 72.7, 72.7, 77.0, 64.2, 71.4, 78.0, 37.1, 66.5, 72.0, 72.2, 88.9, 96.0, 77.8, 88.9, 93.0, 72.2, 94.4, 96.0, 66.0

    claude-sonnet-4.6:
    OpsHarness, 63.6, 63.6, 73.0, 57.1, 63.7, 81.9, 35.7, 64.2, 72.0, 61.1, 83.3, 95.0, 55.6, 77.8, 89.0, 61.1, 77.8, 93.0, 55.7

    glm-5.2:
    OpsHarness, 72.7, 81.8, 87.0, 57.1, 64.3, 74.0, 42.9, 50.0, 61.0, 77.8, 88.9, 89.0, 55.6, 66.7, 76.0, 88.9, 94.4, 98.0, 65.8

    deepseek-v4:
    OpsHarness, 45.5, 63.6, 68.0, 46.4, 50.0, 64.0, 28.6, 42.9, 60.0, 53.3, 73.3, 80.0, 50.0, 72.2, 90.0, 66.7, 77.8, 89.0, 48.4

**Step 6: Add visual-system contracts**

Extend the CSS contract to require:

    .editorial-media
    .results-table-shell
    .results-table
    position: sticky
    overflow-x: auto

Add a contrast test for the accent comparison card. Parse its background and paragraph color declarations and require a WCAG contrast ratio of at least 4.5.

**Step 7: Run the tests and confirm the new tests fail for the intended reasons**

Run:

    python3 -m unittest discover -s tests -v

Expected: failures for the old evolution section, old hero, missing figure assets, missing Table II, and missing CSS hooks. Existing unrelated contracts should stay green.

## Task 2: Convert the two approved PDF figures into web assets

**Files:**

- Read: ../../../../paper/figs/moti_v2.pdf
- Read: ../../../../paper/figs/self-evolveV2.pdf
- Create: static/images/motivation-case.webp
- Create: static/images/self-evolve-loop.webp
- Delete after references are removed: static/images/incident-learning.webp

**Step 1: Inspect the PDFs**

Read the pdf skill in full. Then run:

    pdfinfo /Users/huanghaiyu/Workspace/OpsHarness-Arxiv/paper/figs/moti_v2.pdf
    pdfinfo /Users/huanghaiyu/Workspace/OpsHarness-Arxiv/paper/figs/self-evolveV2.pdf

Confirm that each source has one intended figure page and note its aspect ratio.

**Step 2: Render temporary PNGs**

Create a task-specific temporary directory with mktemp -d. Render each page with pdftoppm at 180 DPI and single-file mode. Keep all temporary output outside the repository.

**Step 3: Visually inspect both renders**

Open each rendered PNG and verify:

- No clipping at any edge.
- Text remains legible.
- The motivation graphic is moti_v2 rather than the old generated case-study graphic.
- The self-evolution graphic is self-evolveV2.

**Step 4: Encode optimized WebP assets**

Use cwebp with high-quality near-lossless settings. Record exact pixel dimensions with sips or identify; those numbers will be used as the HTML width and height attributes.

Target budgets:

- motivation-case.webp: at most 900 KB.
- self-evolve-loop.webp: at most 900 KB.
- Total raster payload: at most 3.5 MB after incident-learning.webp is removed.

**Step 5: Run signature and payload tests**

Run:

    python3 -m unittest tests.test_site.HomepageContractTests.test_raster_asset_extensions_match_their_file_signatures -v
    python3 -m unittest tests.test_site.HomepageContractTests.test_deployable_figure_payload_is_web_sized -v

Expected: asset signatures and payload limit pass; markup-reference tests remain red until the next tasks.

## Task 3: Simplify the hero and rebuild Overview around the RCA gap

**Files:**

- Modify: index.html
- Modify: static/js/i18n.js
- Modify: static/css/style.css
- Test: tests/test_site.py

**Step 1: Update the hero**

Replace the h1 with:

    OpsHarness: <em>A Self-Evolving Harness</em> for Root Cause Analysis

Keep the compact title on no more than three lines at 390 px and no more than two lines at desktop widths. Remove “Individual Researcher” from the hero affiliation and footer. Add a fifth hero legend item, “Self-Evolve,” and change the legend layout from a fixed two-by-two grid into a responsive five-item capability strip.

Do not change the metadata title or BibTeX title.

**Step 2: Replace the Overview heading and opening paragraph**

Use the following English narrative:

- Lead: “General models are capable.”
- Emphasis: “The RCA gap is a harness that learns.”
- Intro: “Modern models already provide strong reasoning, planning, and tool use. What RCA still lacks is an external harness that adapts those capabilities to each system—and keeps improving as incidents reveal new patterns.”

Chinese counterpart:

- Lead: “通用模型的能力已经成熟。”
- Emphasis: “RCA 真正缺少的是一个会学习的 Harness。”
- Intro: “现代模型已经具备强大的推理、规划与工具使用能力。RCA 仍缺少的，是一个能将这些通用能力适配到具体系统、并持续从故障中学习的外部 Harness。”

**Step 3: Rewrite the three comparison cards**

Use these concepts and statuses:

1. General capability is no longer the bottleneck — models can reason and use tools, but do not know the target system — status “Capable model · missing system context.”
2. RCA adaptation belongs in the harness — put skills, system knowledge, observability, and RCA tools around the model — status “General model · system-specific harness.”
3. Static adaptation must become verified self-evolution — distill success and failure into atomic updates, then gate every promotion — status “Learn · verify · promote.”

Provide natural Chinese translations under the same keys.

**Step 4: Turn the two Overview figures into editorial media blocks**

For intro-superpowers.webp:

- Use a two-column editorial-media layout with a short English/Chinese explanatory text block.
- Limit the figure column to approximately 720 px.
- Use the eyebrow “RCA superpowers” and title “Specialization belongs outside the model.”
- Keep the existing lightbox interaction.

For motivation-case.webp:

- Place it later in Overview as a separate editorial-media block with the text column on the opposite side.
- Use the eyebrow “Why self-evolution matters” and title “One corrected incident should improve the next.”
- Explain that the figure is the human-SRE motivation: one misleading symptom is corrected, the propagation pattern and caveat are recorded, and a later incident is diagnosed faster.
- Add an explicit bridge sentence: “OpsHarness turns this manual learning loop into a reviewable, verified system process.”
- Keep technical content and figure text English in both language modes.

**Step 5: Remove the old standalone evolution section**

Delete the entire section whose id is evolution, including incident-story, verification-gate, and the old Figure 3. Remove its now-unused i18n keys. Renumber later section kickers so Results is 03, Usage is 04, Abstract is 05, and Citation is 06.

**Step 6: Fix accent-card contrast**

Give comparison-card--accent its own high-contrast body and secondary-text colors. The paragraph contrast against the violet background must be at least 4.5:1. Keep the title and status visually distinct without reducing readability.

**Step 7: Run focused tests**

Run:

    python3 -m unittest tests.test_site.HomepageContractTests.test_reviewed_hero_and_affiliations_are_exact -v
    python3 -m unittest tests.test_site.HomepageContractTests.test_shift_copy_names_the_model_and_the_harness_gap -v
    python3 -m unittest tests.test_site.HomepageContractTests.test_motivation_and_self_evolution_use_reviewed_paper_figures -v
    python3 -m unittest tests.test_site.HomepageContractTests.test_every_markup_i18n_key_has_both_languages -v
    python3 -m unittest tests.test_site.HomepageContractTests.test_accent_card_body_meets_wcag_aa_contrast -v

Expected: hero, affiliations, Overview narrative, motivation asset, language parity, and contrast pass. The self-evolution asset test can remain red until Task 4 if the contract is split into two tests.

**Step 8: Commit**

    git add index.html static/css/style.css static/js/i18n.js static/images/motivation-case.webp static/images/incident-learning.webp tests/test_site.py
    git commit -m "feat: refocus homepage narrative on the evolving harness"

## Task 4: Add the self-evolution figure to Method and compact the method visuals

**Files:**

- Modify: index.html
- Modify: static/js/i18n.js
- Modify: static/css/style.css
- Add: static/images/self-evolve-loop.webp
- Test: tests/test_site.py

**Step 1: Keep the existing method explanation**

Retain the Data Plane, Control Plane, and Setup → Diagnose → Evolve → Verify material. Keep method-architecture.webp, but present it in a bounded figure frame with a maximum content width around 1040 px rather than letting it visually fill the viewport.

**Step 2: Add a self-evolution mechanism block**

After the architecture figure, add a two-column editorial-media block containing self-evolve-loop.webp and method copy:

- Eyebrow: “Verified self-evolution.”
- Title: “Learn from both success and failure—without learning the wrong lesson.”
- Body: “OpsHarness compares successful and failed trajectories, turns their evidence into atomic proposals, and evaluates a staged harness before any update reaches production.”
- Three compact steps:
  1. “Mine trajectories” — contrast useful and failed diagnostic paths.
  2. “Propose atomic updates” — create reviewable skills, rules, and caveats.
  3. “Pass two gates” — improve source cases and avoid regression on held-out cases.

Provide equivalent Chinese prose while leaving the three short technical labels in the figure itself unchanged.

**Step 3: Preserve lightbox and image contracts**

Give the new figure a unique caption ID and translated expansion aria-label. Set its exact rendered width and height. Keep loading="lazy" and decoding="async".

**Step 4: Run focused tests**

Run the asset, i18n, required-sections, and local-assets tests. All must pass.

**Step 5: Commit**

    git add index.html static/css/style.css static/js/i18n.js static/images/self-evolve-loop.webp tests/test_site.py
    git commit -m "feat: explain verified self-evolution in the method"

## Task 5: Render complete Table II as semantic HTML

**Files:**

- Read: ../../../../paper/tabs/exp_1.tex
- Modify: index.html
- Modify: static/js/i18n.js
- Test: tests/test_site.py

**Step 1: Add a table introduction**

After the four result-summary cards and before the existing result figures, add:

- Eyebrow: “Complete benchmark results.”
- Title: “24 configurations across two benchmarks and six sub-datasets.”
- Body: “OpsHarness is evaluated with four model backbones. Specialized RCA agents are marked †; within each backbone, the OpsHarness row is emphasized.”

Translate the prose into Chinese. Keep all model, framework, dataset, and metric labels English.

**Step 2: Build the semantic header**

Use:

- table class results-table.
- caption describing Table II for screen readers.
- A first header row grouping OpenRCA over Telecom, Bank, Market and RCAEval over Online Boutique, Sock Shop, Train Ticket.
- A second header row naming the six sub-datasets.
- A third header row repeating A@1, A@3, Avg.
- Final A@1 as the last column.
- scope="col", scope="colgroup", and scope="row" where appropriate.

**Step 3: Transcribe all 24 data rows**

Create four tbody elements with:

    data-backbone="gpt-5.5"
    data-backbone="claude-sonnet-4.6"
    data-backbone="glm-5.2"
    data-backbone="deepseek-v4"

Each tbody starts with a full-width group heading row. Under every heading, transcribe the six rows from paper/tabs/exp_1.tex in this exact order:

1. RCA-Agent†
2. mABC†
3. Codex (Direct) or Claude Code (Direct), following the source
4. Codex (ICL) or Claude Code (ICL), following the source
5. OpsHarness (no-evolve)
6. OpsHarness

Each data row uses data-framework with stable slugs: rca-agent, mabc, direct, icl, opsharness-no-evolve, opsharness. Each row must contain all 19 metrics plus the framework row header. Preserve one decimal place, including trailing zeroes.

Use every number directly from paper/tabs/exp_1.tex. The four full OpsHarness rows are independently locked by Task 1 tests; manually cross-check the other 20 rows against the LaTeX source before committing.

**Step 4: Encode emphasis semantically**

Give full OpsHarness rows a results-table__ours class and strong text. Use an accessible background tint per backbone group. Keep emphasis restrained so the table remains readable at high density.

**Step 5: Run the Table II contract**

Run:

    python3 -m unittest tests.test_site.HomepageContractTests.test_full_table_ii_is_rendered_as_semantic_html -v

Expected: four backbone groups, 24 data rows, 20 cells per data row, and all four exact sentinel rows pass.

**Step 6: Commit**

    git add index.html static/js/i18n.js tests/test_site.py
    git commit -m "feat: publish complete benchmark table"

## Task 6: Make Table II responsive and reduce oversized result figures

**Files:**

- Modify: static/css/style.css
- Modify: index.html
- Test: tests/test_site.py
- Test: tests/browser_qa.py

**Step 1: Add a breakout table shell**

Wrap the table in results-table-shell and results-table-scroll:

- Desktop: allow a controlled breakout wider than the normal text shell while keeping margins.
- All widths: use overflow-x: auto on the inner scroller.
- Keep the table minimum width large enough for readable metrics.
- Give the first column position: sticky with an opaque background and visible right border.
- Use tabular-nums for numeric cells.
- Use a subtle shadow or edge fade to communicate horizontal scrolling.

The page body itself must never overflow horizontally.

**Step 2: Compact the result-figure gallery**

Keep existing evidence figures, but replace full-width stacking with an editorial mosaic:

- overview comparison figure: maximum width around 760 px.
- learning-curve and deployment figures: paired at desktop, stacked at mobile, each in a bordered frame.
- Keep captions and lightbox controls.
- Do not enlarge a source image beyond its intrinsic dimensions.

**Step 3: Add browser assertions**

In tests/browser_qa.py:

- At 1440 px, assert the table exists, has 24 framework rows, and its first column computes to position: sticky.
- At 768 px, assert the table scroller scrollWidth is greater than clientWidth while document scrollWidth remains no greater than viewport width.
- At 390 px, repeat the document-overflow assertion and assert the scroller can change scrollLeft.
- Assert the old evolution section does not exist.
- Assert all five hero capability labels are present.

**Step 4: Run focused and browser tests**

Run:

    python3 -m unittest discover -s tests -v
    python3 tests/browser_qa.py

Expected: all static contracts and browser checks pass at desktop, tablet/no-JavaScript, mobile, and reduced-motion contexts.

**Step 5: Commit**

    git add index.html static/css/style.css tests/test_site.py tests/browser_qa.py
    git commit -m "style: refine benchmark and figure layouts"

## Task 7: Update review instructions and perform full verification

**Files:**

- Modify: README.md

**Step 1: Update the review checklist**

Add a concise “Review this revision” checklist:

1. Start python3 -m http.server 8000 from the homepage worktree.
2. Open http://localhost:8000.
3. Verify the short hero title, five hero capabilities, and absence of Individual Researcher.
4. Verify Overview contains both the compact superpowers figure and moti_v2 motivation figure.
5. Verify Method contains self-evolveV2.
6. Verify Table II contains four backbones and scrolls within its frame on mobile.
7. Toggle 中文 and verify prose changes while figures, metrics, commands, framework names, and BibTeX remain English.
8. Open each figure lightbox and close with Escape.

Document the source mapping:

    paper/figs/moti_v2.pdf → static/images/motivation-case.webp
    paper/figs/self-evolveV2.pdf → static/images/self-evolve-loop.webp
    paper/tabs/exp_1.tex → complete HTML Table II

**Step 2: Run syntax and contract verification**

Run:

    python3 -m unittest discover -s tests -v
    node --check static/js/i18n.js
    node --check static/js/main.js
    python3 tests/browser_qa.py

All commands must exit successfully.

**Step 3: Run manual visual QA**

Serve the worktree locally and inspect at:

- 1440 × 1000
- 768 × 900
- 390 × 844

Capture screenshots of Hero/Overview, Method/self-evolution, and Results/Table II. Verify:

- The hero title is calm and not crowded.
- Self-Evolve is visible in the first viewport.
- The violet card body is clearly readable.
- Overview tells one continuous model → harness gap → self-evolution story.
- Neither the superpowers figure nor method figures dominate a full viewport.
- The motivation and self-evolution figures are sharp and not clipped.
- Table II headers, row groupings, sticky framework column, and internal horizontal scrolling work.
- There is no body-level horizontal overflow.
- Chinese copy does not cause collisions or clipped controls.

**Step 4: Request independent code review**

Use requesting-code-review. Ask the reviewer to inspect all changes since commit 9de2ef4, prioritizing:

- Accuracy of all 24 Table II rows against paper/tabs/exp_1.tex.
- English/Chinese parity and absence of stale evolution keys.
- Figure provenance and captions.
- Accessibility and responsive overflow behavior.
- Contrast in the violet comparison card.

Fix Important or higher findings, rerun the relevant tests, then rerun the full suite.

**Step 5: Inspect the final diff**

Run:

    git status --short
    git diff --check
    git diff --stat 9de2ef4..HEAD

Confirm there are no untracked temporary renders and no unrelated changes.

**Step 6: Commit documentation and final fixes**

    git add README.md
    git commit -m "docs: update homepage review workflow"

If review fixes touched code, include those exact files in a separate commit named:

    fix: address homepage revision review

**Step 7: Present integration choices**

Use finishing-a-development-branch. Report the exact worktree path, preview command, verification results, and branch/commit state. Do not merge to main without the user selecting the merge option.
