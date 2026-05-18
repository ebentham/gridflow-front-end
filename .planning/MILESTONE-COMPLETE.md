# v1 Cleanup Milestone — Complete

**Completed:** 2026-05-18
**Deployed:** https://ebentham.github.io/gridflow-front-end/
**Mode:** Autonomous execution per `.planning/AUTONOMOUS-V1-BRIEF.md`

## Status

**7 / 7 phases shipped · 50 / 50 REQ-IDs delivered.** All 21 ROADMAP success criteria verified TRUE.

## Phase summary

| Phase | PR  | Branch                                | Commits | Net change          |
|-------|-----|---------------------------------------|---------|---------------------|
| 0 — Commit in-flight refactor       | #3  | `docs/codebase-map`                  | 8       | +commits, .gitattributes |
| 1 — Trivial bug fixes               | #4  | `docs/codebase-map` (continued)      | 3       | viewport ×22 / MIT LICENSE / rel=noopener |
| 2 — Shared CSS/JS extraction        | #5  | `refactor/phase-2-shared-assets`     | 4       | ~1,039 LOC of duplication retired |
| 3 — Build mechanism + Elexon depth  | #6  | `feat/phase-3-build-mechanism`       | 8       | gridflow-build CLI + 33 dataset pages |
| 4 — Cross-vendor proof + dead links | #7  | `feat/phase-4-cross-vendor`          | 2       | ENTSO-E + 5 stubs |
| 5 — Honesty + a11y + mobile + polish| #8  | `chore/phase-5-honesty-a11y-mobile`  | 4       | Atomic honesty pass + responsive CSS |
| 6 — CI validation                   | #9 (+ #10, #11 fix-ups) | `ci/phase-6-validation` | 4 | htmlhint + lychee + idempotence |

Total commits on `main` since the milestone began: ~37.

## Per-phase success-criteria verification

### Phase 0 — Commit in-flight refactor
- ✓ SC#1: 8 commits since 351c580 cover the in-flight refactor in logical chunks; `git status` clean
- ✓ SC#2: `.gitattributes` committed at repo root (eol=lf for `*.html`, `*.css`, `*.js`, `*.json`, `*.py`, `*.md`)
- ✓ SC#3: GitHub Pages deploy succeeded post-merge

### Phase 1 — Trivial bug fixes
- ✓ SC#1: `grep 'width=1280' site/hifi/` returns zero hits — viewport fixed on all 23 affected pages
- ✓ SC#2: `LICENSE` (MIT) at repo root; license strings aligned site-wide (no Apache-2.0 residuals)
- ✓ SC#3: Both `target="_blank"` links missing `rel="noopener"` now carry it

### Phase 2 — Shared CSS/JS extraction
- ✓ SC#1: No dataset page contains an inline `<style>` block except `fuelhh.html`'s `.fuel-grid` / `.fuel-pill` rules
- ✓ SC#2: `git grep setTab site/hifi` returns zero hits
- ✓ SC#3: Sidebar inactive items hover-to-ink via the `.muted:hover` rule (inline `color:var(--ink-faint)` overrides eliminated)
- ✓ SC#4: Exactly one scroll-spy `IntersectionObserver` in `site.js`, gated by `.sidebar a[href^="#"]` presence

### Phase 3 — Build mechanism + Elexon dataset depth
- ✓ SC#1: `gridflow-build --check` exits 0 — 33 Elexon dataset pages + vendor hub, idempotent across runs
- ✓ SC#2: All 33 dataset pages render all 6 sidebar anchors and each resolves to a real `<section id>` (Pitfall 2 closed)
- ✓ SC#3: Footer, index stat strip, data-sources hub, and `elexon.json` all show `33`; grep for `22|25|28 datasets` returns zero hits
- ✓ SC#4: Every dataset page shows the verified-against-vendor-docs date (`2026-05-08`) + BMRS doc link, plus the Pydantic schema reference (or drift-surface flag)
- ✓ SC#5: Deploy YAML runs `gridflow-build` before `upload-pages-artifact`; generated HTML gitignored under `site/hifi/data-sources/elexon/`; intentional diffs documented in `BUILD-DIFFS.md`

### Phase 4 — Cross-vendor proof + dead-link fix
- ✓ SC#1: ENTSO-E hub at `/data-sources/entsoe.html` + dataset at `/data-sources/entsoe/actual_generation.html` both render at fuelhh fidelity
- ✓ SC#2: 5 visually-distinct coming-soon stubs (entsog, gie_agsi, gie_alsi, openmeteo, neso) — no sidebar, no chart, "Planned · F6–F10" stage chips
- ✓ SC#3: `grep 'href="#"' site/hifi/data-sources.html` returns zero hits

### Phase 5 — Honesty + a11y + mobile + polish
- ✓ SC#1: The 9-string honesty grep checklist returns zero hits across `site/hifi/`; every chart container carries "Illustrative snapshot" framing; footer build-version replaced with documentation-site line
- ✓ SC#2: Every page renders mobile-functional at 480px and 720px via `body[data-page="dataset"]` / `body[data-page="vendor"]` / `body[data-page="sources"]` responsive rules in `theme.css`
- ✓ SC#3: `<main>` everywhere; both `<nav>` elements carry distinguishing `aria-label`s; `aria-current="page"` on top-nav; `aria-current="location"` on sidebar; `aria-hidden="true"` on decorative arrow/sep/dot/SVG icons
- ✓ SC#4: index.html honest + 33 Elexon in stat strip + no "Shipping" badge; architecture.html structure preserved; data-sources.html honest framing

### Phase 6 — CI validation
- ✓ SC#1: `htmlhint --config .htmlhintrc 'site/hifi/**/*.html'` runs before deploy and exits 0
- ✓ SC#2: `lychee --offline --include-fragments site/hifi/**/*.html` runs before deploy and exits 0
- ✓ SC#3: `gridflow-build --check` runs and exits 0; non-zero on output drift

## Key decisions (made via the Decision-making framework)

The brief authorised me to decide unresolved ambiguities autonomously and document them here. The decisions I made:

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | **Vendor vault content into this repo at `vault/elexon/` and `vault/entsoe/`** (instead of cross-repo checkout) | `EBentham/quant-vault` is not a GitHub repo, so CI cannot clone it. The build supports `--vault-path` / `$GRIDFLOW_VAULT_PATH` for local dev against the live vault; CI uses the vendored snapshot. Documented in README.md. |
| 2 | **Pydantic class drift policy: render-with-flag** (per advisor recommendation) | Where a class is declared in `gridflow.schemas.elexon`, the page cites it. Where it isn't (22 of 33 datasets), the page surfaces *"Schema enforced by transformer; no dedicated Pydantic class declared in `gridflow.schemas.elexon` yet — drift-surface flagged"*. ELX-08 satisfied while honestly flagging the gap. |
| 3 | **Templates born honest** (advisor pre-emption) | The dataset template never emits `chip live`, `LAST FETCH`, `N min ago`, or time-window pill chips. Phase 5's HON-01 grep checklist returns zero hits on generated pages by construction — saved a 33× regen cycle. |
| 4 | **Byte equivalence on the 6 originally-complete pages waived; 9 categories of intentional diff documented in `BUILD-DIFFS.md`** | Vault content is the new source of truth; preserving hand-curated HTML byte-for-byte defeats the architectural pivot. The brief and ROADMAP §3 SC#5 explicitly allow documented intentional diffs. |
| 5 | **Categorization of 8 vault-only datasets** | Per the vault overview text: indgen/inddem/imbalngc/melngc/atl/tsdfd → Demand & Forecasts (14 datasets total); market_depth → Prices & Balancing; lolpdrm → System & Reference. |
| 6 | **Phase 5 PAGE-02 (architecture) polish minimal** | Per Decision-making framework rule 3 (prefer smaller diffs): architecture.html structure stays from the recent redesign; only the residual `28 dataset` count was fixed. |
| 7 | **GIE row on data-sources.html links to gie_agsi stub** (instead of splitting into AGSI + ALSI rows) | The combined "GIE AGSI · ALSI" catalog row uses one outbound link to AGSI stub. ALSI has its own stub at `/data-sources/gie_alsi.html` accessible via the catalog table cells. Phase 5 polish can split if the editorial layout benefits. |
| 8 | **Phase 5 commit-version footer replaced with "Documentation site · last updated 2026-05-18"** | HON-03 — the dated line is acceptable to hand-update each milestone. |

## Deviations from the original plan

- **Phase 6 CI required 2 fix-up PRs** (#10, #11) — htmlhint's `attr-value-double-quotes` and `spec-char-escape` rules fought legitimate HTML5 patterns (single-quoted JSON attributes; `>` in `<pre>` SQL/code blocks). Both rules were disabled in `.htmlhintrc` after the first failed deploy; structural rules that catch real bugs (tag-pair, id-unique, doctype-html5, attr-no-duplication) remain enabled. Per the brief's error handling protocol: fixes were <10 lines each, opened in fix branches, merged.
- **Phase 4 inherited some Phase 5 honesty work** — the `vendor-hub.html.j2` and `vendor-coming-soon.html.j2` templates were born honest (no live framing), so when they merged on Phase 4 they already passed the HON grep checklist. Phase 5 HON-01 didn't have to touch them.

## What to look at, recruiter test

When a recruiter spends 30 seconds on https://ebentham.github.io/gridflow-front-end/, they should see:

1. **Editorial-quiet aesthetic** — cream paper, forest accent, Fraunces + Inter + JetBrains Mono. No SaaS chrome.
2. **Honest framing throughout** — "Illustrative snapshot" labels, no live timestamps, no "Shipping" badges.
3. **The catalogue is real** — 33 Elexon datasets at fuelhh fidelity, each with verified-against-vendor-docs micro-line, Pydantic schema reference, and 6-section anatomy (overview → snapshot chart → schema → sample → API → caveats → related).
4. **Cross-vendor proof** — ENTSO-E hub + 1 dataset at the same fidelity, demonstrating the template generalises.
5. **Intentional stubs** — 5 deferred vendors marked "Planned · F6–F10" with visually-distinct layout (no sidebar, no chart), so unfinished vendors don't read as broken.
6. **Mobile-functional** — the dataset pages were viewport-broken (1280px) on 23 of 27 pages before this milestone; now responsive at ≤480px and ≤720px.
7. **A11y baseline** — `<main>` landmark, distinguishing `aria-label`s on dual `<nav>`, `aria-current` on active items, `aria-hidden` on decorative icons.

The architectural lever this milestone introduces:

- One vault `.md` file + one manifest entry = one rendered page. Adding the next dataset is a 5-minute edit, not a 30-minute copy-paste-and-pray.
- One template edit propagates to all 34 dataset pages. The Phase 5 a11y additions to `dataset.html.j2` shipped as 34 page changes via a single re-build.

## Deferred to v2 (out of scope of this milestone)

Catalogued in `REQUIREMENTS.md § v2 Requirements`, `BUILD-DIFFS.md § Future v2 candidates`, and `PROJECT.md § Out of Scope`. Highlights:

- **Pydantic class drift surface** — 22 of 33 datasets render with the drift-flagged message. Closing the gap means declaring `ElexonAGPT`, `ElexonAGWS`, `ElexonFOU2T14D`, etc. in `gridflow.schemas.elexon` and re-running `gridflow-build`.
- **Per-dataset related-card blurbs** — the "Pair with X to do Y" hand-curated copy on fuelhh.html's related grid is not in vault content. Restoring via a `related_blurbs:` vault frontmatter field is a v2 candidate.
- **fuelhh fuel-pill grid** — the 16-pill fuel-type colour swatch grid is dataset-specific markup retired by the shared template. Restoring via a `fuel_types: [...]` vault frontmatter field is a v2 candidate.
- **ENTSO-E coverage beyond 1 dataset** — the cross-vendor proof shipped 1 dataset (`actual_generation`). Full ENTSO-E depth is a separate milestone.
- **Stubbed vendors at depth** — ENTSO-G, GIE AGSI, GIE ALSI, Open-Meteo, NESO each become their own per-vendor milestone.
- **Real Elexon API wiring** — nightly snapshot regeneration via GitHub Actions for one or more datasets. Anti-goal today; honest "Illustrative snapshot" framing is the v1 commitment.
- **More model case studies** — SRMC, wind, solar, fundamentals SMP. The demand-forecast page is the v1 reference for the model-case-study anatomy.
- **GitHub Actions Node 24 migration** — workflow currently uses Node 20 actions which deprecate September 2026. Trivial to upgrade when needed.

## Resume instructions

If a future session needs to continue from this state:

- `git log --oneline main --first-parent` shows the 11 merge commits + initial commit.
- `gh pr list --state merged --limit 20` shows PR titles and merge dates.
- `.planning/STATE.md` reflects milestone complete.
- `.planning/ROADMAP.md` progress table shows 7/7 complete (table will need a manual update if not done in this commit).
- The deployed site is at https://ebentham.github.io/gridflow-front-end/.
- The vault snapshot under `vault/elexon/` and `vault/entsoe/` was vendored on 2026-05-18 from the source `quant-vault` at the same date.

To pick up v2 work, start at `REQUIREMENTS.md § v2 Requirements` and `PROJECT.md § Active` (which will need to be transitioned per `gsd-new-milestone` workflow).

---

*Autonomous execution complete. Returning control.*
