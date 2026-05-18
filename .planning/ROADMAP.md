# Roadmap

**Milestone:** v1 cleanup — credibility-recovery pass on the gridflow-front-end portfolio site
**Created:** 2026-05-17
**Granularity:** standard (5–8 phases)
**Parallelization:** enabled (Phase 1 ‖ Phase 2 after Phase 0)
**Coverage:** 50/50 REQ-IDs mapped to exactly one phase

## Goal

When a recruiter spends 30 seconds on the site, the dominant impression is "this person genuinely knows UK/EU energy market data." Ship the site to that bar — 33 Elexon datasets at `fuelhh` fidelity, an ENTSO-E cross-vendor proof, no fake-live framing, mobile-functional, single source of truth for content (Obsidian Vault → Jinja2 build → static HTML).

## Phases

- [x] **Phase 0: Commit in-flight refactor** — Land the 26 modified files as 4 logical commits + `.gitattributes`; clean working tree is the gating prerequisite for everything else *(completed 2026-05-18)*
- [ ] **Phase 1: Trivial bug fixes** — Mobile viewport tag find-and-replace, `LICENSE` file + aligned strings, `rel="noopener"` on the two missing links (parallelisable with Phase 2)
- [ ] **Phase 2: Shared CSS/JS extraction** — Move the duplicated dataset-page `<style>` block + scroll-spy IIFE + `setTab()` declarations into `theme.css` + `site.js`; fix the sidebar hover bug (parallelisable with Phase 1)
- [ ] **Phase 3: Build mechanism + Elexon dataset depth** — Author the Python+Jinja2 `gridflow-build` CLI, the dataset/vendor-hub templates, vault-content reader; regenerate the 6 complete pages to byte-equivalent state, then ship all 33 Elexon datasets at `fuelhh` fidelity from vault content
- [ ] **Phase 4: Cross-vendor proof + dead-link real fix** — ENTSO-E hub + "Generation by PSR type" dataset via the same templates; 5 visually-distinct coming-soon vendor stubs; every `<a href="#">` on `data-sources.html` resolves to a real page
- [ ] **Phase 5: Honesty sweep + a11y + mobile CSS + main-page polish** — Atomic kill of all 6 "live"-framing surfaces; mobile CSS in `theme.css`; `<main>` + `aria-current` + `aria-label` + `aria-hidden` minimums; editorial polish pass on index, architecture, data-sources hub
- [ ] **Phase 6: CI validation** — `htmlhint` + `lychee` + build-idempotence check in `.github/workflows/deploy.yml` before `upload-pages-artifact`

## Phase Details

### Phase 0: Commit in-flight refactor
**Goal**: Clean working tree with the 26-file refactor split into 4 logical commits, line-ending churn permanently stopped via `.gitattributes`. Every subsequent commit can be reviewed without entangling three concurrent refactors.
**Depends on**: Nothing (gating prerequisite — blocks all other phases per all four research streams)
**Requirements**: HYG-01, HYG-02
**Success Criteria** (what must be TRUE):
  1. `git status` shows zero modified files and zero untracked files; `git log --oneline` since `351c580` shows 6 commits in the documented order — 4 cleanup chunks (typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks) plus 2 repo-hygiene chunks (`.gitattributes` + `.gitignore` bundled · renormalize line endings) per `00-CONTEXT.md` D-03
  2. `.gitattributes` exists at repo root with `text eol=lf` rules covering `*.html`, `*.css`, `*.js`, `*.json`, `*.py`, and a Windows-edited commit produces no LF/CRLF warnings on `git diff`
  3. GitHub Pages-deployed site matches the current `main` HEAD (working tree and deployed view are no longer diverged)
**Plans**: 1 plan
- [x] 00-01-PLAN.md — Planner-record commit + 4 cleanup chunks + 2 hygiene + ROADMAP SC#1 reconciliation + PR/merge/Pages-verify (11 sequential tasks, Wave 1) *(completed 2026-05-18, PR #3 merged)*

### Phase 1: Trivial bug fixes
**Goal**: Ship the no-architectural-dependency one-line fixes that block mobile usability and license credibility, in parallel with Phase 2. These are cosmetic-class to a recruiter spot-check yet high-leverage (mobile viewport is the single highest-leverage fix in the milestone per Pitfall 10).
**Depends on**: Phase 0
**Requirements**: MOB-01, HON-04, A11Y-06
**Success Criteria** (what must be TRUE):
  1. Every page in `site/hifi/` carries `<meta name="viewport" content="width=device-width, initial-scale=1">`; `grep` for `width=1280` returns zero hits
  2. `LICENSE` file exists at repo root with one chosen license; `grep` across `site/hifi/` and `src/` shows zero contradictory license strings (no MIT vs Apache-2.0 split)
  3. Both `target="_blank"` links currently missing `rel="noopener"` (architecture.html ~line 1156, data-sources/elexon.html ~line 41) now carry the attribute
**Plans**: TBD

### Phase 2: Shared CSS/JS extraction
**Goal**: Remove the structural duplication that blocks templating in Phase 3 and inflates every cross-cutting change to a 22-file edit. Output is a single source of truth for dataset-page styling and the scroll-spy + tabs helpers, used by the Phase 3 template.
**Depends on**: Phase 0
**Requirements**: REF-01, REF-02, REF-03, A11Y-05
**Success Criteria** (what must be TRUE):
  1. No dataset page under `site/hifi/data-sources/elexon/*.html` contains an inline `<style>` block (except `fuelhh.html`'s truly page-specific `.fuel-grid` rules); the ~30-line duplicated block now lives in `theme.css` under a `/* dataset pages */` section
  2. Zero per-page `setTab(...)` global function declarations or inline `onclick="setTab(...)"` handlers remain in the repo; dataset-page tabs use the existing `[data-tabs]` convention read by `site.js`
  3. Sidebar inactive items on a dataset page show the documented hover color change (the inline `color:var(--ink-faint)` no longer overrides `:hover` because the dim color is delivered via a CSS class)
  4. `grep` returns exactly one scroll-spy `IntersectionObserver` implementation in the repo (in `site.js`, gated by `.sidebar a[href^="#"]` presence) — zero inline scroll-spy IIFEs remain on dataset pages
**Plans**: TBD
**UI hint**: yes

### Phase 3: Build mechanism + Elexon dataset depth
**Goal**: Stand up the Python+Jinja2 `gridflow-build` CLI over Obsidian Vault content (vault → site direction), regenerate the 6 currently-complete pages to byte-equivalent state to validate the template captures existing fidelity, then ship all 33 Elexon datasets at `fuelhh` fidelity. After this phase, editing dataset content means editing one vault `.md` file; layout changes mean editing one template.
**Depends on**: Phase 0, Phase 2 (template inputs must reference shared CSS/JS, not duplicated inline blocks)
**Requirements**: BUILD-01, BUILD-02, BUILD-03, BUILD-04, BUILD-05, BUILD-06, BUILD-07, BUILD-08, VAULT-01, VAULT-02, VAULT-03, VAULT-04, ELX-01, ELX-02, ELX-03, ELX-04, ELX-05, ELX-06, ELX-07, ELX-08
**Success Criteria** (what must be TRUE):
  1. Running `gridflow-build` (Python 3.11+, Jinja2 from `[build]` extras only — `gridflow-serve` runtime stays stdlib-only) reads from `<vault>/30-vendors/elexon/datasets/*.md` and writes 33 dataset HTML files; running it twice produces zero diff under `site/hifi/data-sources/elexon/` (idempotence)
  2. Visiting any of the 33 Elexon dataset pages renders all six sidebar anchors (`#overview`, `#schema`, `#sample`, `#api`, `#caveats`, `#related`) and each resolves to a real `<section id>` on the page (zero phantom-coverage anchors per Pitfall 2)
  3. Footer, `site/hifi/index.html` stat strip, `site/hifi/data-sources/elexon.html` catalog UI, and `site/hifi/data/elexon.json` all show the number `33` for Elexon datasets — no other count (22, 25, 28) appears anywhere on the site
  4. Every Elexon dataset page shows (a) a `verified-against-vendor-docs: YYYY-MM-DD` micro-line linking to the dataset's specific Elexon BMRS doc page, and (b) the matching Pydantic schema class name as an inline `<code>` reference (e.g. `gridflow/schemas/elexon.py · ElexonFuelHH`)
  5. The 6 originally-complete pages (`fuelhh`, `fuelinst`, `agpt`, `agws`, `nonbm`, `windfor`) regenerate byte-equivalently from the new template + vault content vs the pre-Phase-3 committed files (or with documented intentional diffs); `.github/workflows/deploy.yml` runs `gridflow-build` before `actions/upload-pages-artifact@v3` and generated HTML is gitignored under `site/hifi/data-sources/elexon/`
**Plans**: TBD
**UI hint**: yes

### Phase 4: Cross-vendor proof + dead-link real fix
**Goal**: Prove the templating from Phase 3 generalises across vendors by shipping an ENTSO-E hub + "Generation by PSR type" dataset at `fuelhh` fidelity (template-stretching choice: quarter-hour settlement + PSR-type taxonomy). In the same pass, replace every `<a href="#">` placeholder on the data-sources hub with a real link — either a real vendor hub (Elexon, ENTSO-E) or a visually-distinct coming-soon stub for the 5 deferred vendors.
**Depends on**: Phase 3 (cross-vendor extrapolation requires Elexon template consistency; coming-soon stubs use `vendor-coming-soon.html.j2`)
**Requirements**: VEND-01, VEND-02, VEND-03, VEND-04, VEND-05, PAGE-03
**Success Criteria** (what must be TRUE):
  1. Visiting `/data-sources/entsoe.html` renders an ENTSO-E vendor hub (built from `vendor-hub.html.j2` over `site/hifi/data/entsoe.json`); visiting `/data-sources/entsoe/<psr-slug>.html` renders the "Generation by PSR type" dataset page at `fuelhh` fidelity (all six sidebar anchors resolve, schema/sample/caveats sections present, verified-against-vendor-docs micro-line)
  2. Each of the 5 deferred vendors (ENTSO-G, GIE AGSI, GIE ALSI, Open-Meteo, NESO) has a coming-soon stub rendered from `vendor-coming-soon.html.j2` that is visually distinguishable from a real vendor hub at a glance — no sidebar, no chart container, single-screen layout, "Planned · F<n>" stage chip (per Pitfall 9 prevention)
  3. `grep` for `href="#"` over `site/hifi/data-sources.html` returns zero hits; every vendor row clicks through to either a real vendor hub or a coming-soon stub
**Plans**: TBD
**UI hint**: yes

### Phase 5: Honesty sweep + a11y + mobile CSS + main-page polish
**Goal**: Run the atomic honesty pass that kills all 6 "live"-framing surfaces in one go (per Pitfall 1 — touching only some is worse than touching none), land the mobile CSS the dataset pages never had, add the a11y landmark minimums, and polish the three hand-authored main pages (home, architecture, data-sources hub). Because Phase 3 made dataset pages template-generated, this is a small number of template edits rather than 33 per-page find-and-replace.
**Depends on**: Phase 3 (template-generated pages absorb the changes in one place), Phase 4 (newly-shipped ENTSO-E and coming-soon stubs are cleaned in the same pass)
**Requirements**: HON-01, HON-02, HON-03, MOB-02, MOB-03, A11Y-01, A11Y-02, A11Y-03, A11Y-04, PAGE-01, PAGE-02, PAGE-04
**Success Criteria** (what must be TRUE):
  1. The fixed grep checklist (`chip live`, `class="dot live"`, `LAST FETCH`, `last sync`, `last fetch`, ` min ago`, ` s ago`, `live · `, `Live chart`) returns zero hits over `site/hifi/`; each chart container instead carries an explicit "Illustrative snapshot" chip; footer build-version string replaced with the documentation-site line
  2. Every page renders mobile-functional at 480px and 720px viewports: no horizontal scroll, sidebar collapses, hero stacks vertically, stats strip reflows, mobile menu toggle reaches every page (the `width=1280` bug previously prevented this on 23 pages)
  3. Every page wraps primary content in `<main>`; the injected top-nav `<nav>` and dataset-page sidebar `<nav>` carry distinguishing `aria-label`s; the active nav link has `aria-current="page"` and active sidebar link has `aria-current="location"` (or `="true"`); decorative arrow/dot/hamburger/chip-dot icons carry `aria-hidden="true"`
  4. `site/hifi/index.html` reads as editorial/quiet (no fake-live chrome, no "Shipping" badges, `33 Elexon datasets` in the stat strip); `site/hifi/architecture.html` passes a polish pass on writing and diagrams (structure stays); `site/hifi/data-sources.html` has the honest framing pivot complete
**Plans**: TBD
**UI hint**: yes

### Phase 6: CI validation
**Goal**: Lock in the milestone's structural wins with cheap automated checks that catch the exact bug class motivating v1 — broken dataset stubs, dead links, phantom sidebar anchors, build-idempotence regressions.
**Depends on**: Phase 3 (build-idempotence check requires the build script to exist), Phase 5 (link-checker assumes pages have stabilised)
**Requirements**: CI-01, CI-02, CI-03
**Success Criteria** (what must be TRUE):
  1. `.github/workflows/deploy.yml` runs `htmlhint` (or equivalent) over the built site before `actions/upload-pages-artifact@v3` and fails the deploy on structural HTML breakage of the broken-stub class
  2. `lychee` (or equivalent link checker) runs over the built site before deploy and fails on internal dead links (catches dead-anchor regressions)
  3. CI runs `gridflow-build` twice on the same vault checkout and fails the deploy if `git diff` of the output directory is non-empty (build-idempotence smoke test)
**Plans**: TBD

## Phase Dependencies

```
Phase 0 (commit in-flight refactor) — GATING
   │
   ├── Phase 1 (trivial bug fixes)              ┐
   │                                            │ parallel
   └── Phase 2 (CSS/JS extraction)              ┘
          │
          └── Phase 3 (build mechanism + Elexon depth)
                 │
                 └── Phase 4 (cross-vendor proof + dead-link real fix)
                        │
                        └── Phase 5 (honesty + a11y + mobile CSS + main-page polish)
                               │
                               └── Phase 6 (CI validation)
```

**Parallelisation note:** Phase 1 and Phase 2 are independent after Phase 0 lands. Both can be developed and reviewed in parallel; merge order does not matter between them. Phases 3–6 are strictly sequential because each consumes the output of the previous (template + content depth → cross-vendor template proof → atomic sweep over the template-generated set → CI guarding the stabilised pages).

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 0. Commit in-flight refactor | 1/1 | Complete | 2026-05-18 |
| 1. Trivial bug fixes | 0/? | Not started | - |
| 2. Shared CSS/JS extraction | 0/? | Not started | - |
| 3. Build mechanism + Elexon dataset depth | 0/? | Not started | - |
| 4. Cross-vendor proof + dead-link real fix | 0/? | Not started | - |
| 5. Honesty + a11y + mobile + main-page polish | 0/? | Not started | - |
| 6. CI validation | 0/? | Not started | - |

(Plan counts populated by `/gsd-plan-phase` per phase.)

---
*Roadmap created 2026-05-17. Coverage: 50/50 REQ-IDs mapped. Source: PROJECT.md + REQUIREMENTS.md + research/SUMMARY.md + research/ARCHITECTURE.md + research/PITFALLS.md + codebase/CONCERNS.md.*
