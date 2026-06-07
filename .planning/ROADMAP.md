# Roadmap

**Milestone:** v2 full-vendor-coverage (Active) · v1 cleanup (Complete, historical record below)
**Created:** 2026-05-17 (v1) · Extended 2026-05-18 (v2) · Rescoped 2026-05-19 (Phase 7 Reconciliation inserted; existing 7→8, 8→9, 9→10 per ADR-0001)
**Granularity:** standard
**Parallelization:** enabled (sequential 7 → 8 → 9 → 10 recommended; Phase 8 — bug fix — is independent of Phase 7 per ADR-0001 D-03; see Phase Dependencies)
**Coverage:** 31/31 v2 REQ-IDs mapped (5 RECON-* added with the Phase 7 rescope) + 50/50 v1 REQ-IDs delivered

## Goal

**v2 milestone goal:** A recruiter clicks any vendor on the data-sources hub and sees a complete dataset catalog; clicks any dataset and gets full documentation (overview · schema · sample · API · caveats · related) at `fuelhh` fidelity. Site-wide total: **162 datasets across 6 vendors** (Elexon 33 · ENTSO-E 49 · ENTSO-G 33 · GIE 8 · NESO 33 · Open-Meteo 6). The build script stays idempotent, CI-gated, and vault-driven across the expanded surface; the editorial-quiet aesthetic and honest framing established in v1 hold across all 129 new pages.

**v1 milestone goal (delivered 2026-05-18):** Recruiter-credible portfolio at `fuelhh` fidelity for 33 Elexon datasets + ENTSO-E cross-vendor proof, no fake-live framing, mobile-functional, vault → site templating pipeline shipped.

---

## v2 Phases (Active)

- [x] **Phase 7: Reconciliation** — Wrap the existing verifier as `gridflow-drift-check`; run Verification across all 6 Vendors; triage every Drift finding into `open` / `wontfix-v3` / `needs-info`+`defer-entitlement`; land Vault edits for the fixable bucket; commit the upstream Vault to a private GitHub repo (`EBentham/quant-vault`) per ADR-0002 *(gating for content phases 9 and 10; independent of Phase 8 per ADR-0001 D-03)* **[Complete 2026-05-19 — RECON-01..RECON-05 satisfied]**
- [~] **Phase 8: Dataset-page formatting bug fix** — Attempted as locked-scope minimal CSS patch; **two iterations failed visual verification** at BUG-02 user-checkpoint; root cause turned out to be editorial-content gap in vault, not a rendering-layer bug *(closed as superseded 2026-05-19; see `phases/08-bug-fix-dataset-formatting/08-01-SUMMARY.md`)*
- [~] **Phase 8B: Claude-Design hero rewrite (AI-port output deprecated)** — Built the `authored-pages/<vendor>/<slug>.html` build-script override path (kept) and AI-ported all 33 Elexon pages (output deemed sub-optimal in editorial quality; archived to `.planning/archive/08B-ai-ports/elexon/` 2026-05-20). The two reference pages (fuelhh + system_prices) remain in `authored-pages/elexon/` as visual targets for the Claude-Design pivot *(milestone direction changed 2026-05-20 toward Option C — fully authored via Claude Design)*
- [x] **Phase 8C: Elexon content briefs (triangulated research for Claude Design)** — Produced 33 self-contained markdown content briefs at `content-briefs/elexon/<slug>.md`, one per Elexon dataset. Each brief triangulates vault + gridflow Pydantic schemas/transformers/connectors + live vendor docs; surfaces cross-source discrepancies in frontmatter for downstream triage; ready to paste into Claude Design alongside the visual reference (fuelhh.html / system_prices.html) *(replaces Phase 8B's AI-port path; gating for Phase 9 and Phase 10 which adopt the same brief → Claude Design pattern)* **[Complete 2026-05-20 — all 33 briefs committed, 12/12 structural checks pass, 45 discrepancies surfaced for downstream triage; see `phases/08C-elexon-content-briefs/08C-01-SUMMARY.md` + `DISCREPANCY-INDEX.md`]**
- [x] **Phase 8D: Vendor landing-page content briefs (5 hubs)** — Produce 5 vendor-hub content briefs at `content-briefs/<vendor>/_landing.md` (one per non-Elexon vendor: entsoe, entsog, gie, neso, openmeteo), emulating the Elexon landing page (`site/hifi/data-sources/elexon.html`). Each brief defines vendor identity (heading + italic accent + lede), 6-cell access metadata (BASE URL / AUTH / RATE LIMIT / FORMAT / EARLIEST / TIMEZONE), 4-cell stats strip, group definitions with blurbs, and per-dataset listing rows. User Claude-Designs each into `authored-pages/<vendor>/_landing.html`; build override path serves them as `/data-sources/<vendor>.html`. Decouples vendor-hub design from per-dataset brief production so Phase 9 / Phase 10 can focus on dataset content. **[Complete 2026-05-20 — 5 briefs committed (entsoe 49 datasets 6 groups, entsog 33 datasets 5 groups, gie 8 datasets 2 groups, neso 33 datasets 4 groups, openmeteo 6 datasets 2 groups); build override patch shipped (build.py authored_hub check); all 10 structural checks pass per-brief; 15 discrepancies surfaced across vendors; see `phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md`]**
- [x] **Phase 9: ENTSO-E full coverage** — Produce 49 content briefs for ENTSO-E datasets following the Phase 8C pattern, then Claude-Design each into `authored-pages/entsoe/<slug>.html` and author the `site/hifi/data/entsoe.json` manifest. The ENTSO-E vendor hub itself is delivered by Phase 8D. **[Complete 2026-06-03 — 49 briefs (7 commits `aab2128..9b5e296`; 35 flagged `entitlement_required: true` per STATE D-21, resolving Phase 7 D-06) + 49 authored pages (5 Claude Design batches) + 49-entry manifest in 9 groups; `gridflow-build` writes 49 ENTSO-E pages, `gridflow-build --check` exits 0 (idempotent across 86 pages + 8 hubs). Pages carry synthesised `#overview` + `#caveats` (D-22 applied to ENTSO-E — exceeds SC#3's D-20 no-Overview baseline). ENTSOE-01..ENTSOE-05 satisfied. See `phases/09-entsoe-content-briefs/09-01-SUMMARY.md`.]**
- [x] **Phase 10: Four-vendor batch coverage + site-wide consistency** — 80 dataset pages across ENTSO-G (33) + GIE (8) + NESO (33) + Open-Meteo (6) authored via Claude Design (D-22: synthesised `#overview` + rendered `#caveats`, matching Phase 9); 4 manifests authored; the four vendors moved from `COMING_SOON_VENDORS` to `REAL_VENDORS` in `build.py` (GIE unified from the gie_agsi/gie_alsi split); site-wide count strings reconciled to **162**; every vendor row links to a real hub. **[Complete 2026-06-07 — 162 dataset pages + 6 real hubs; `gridflow-build --check` idempotent, `htmlhint` + `lychee --offline` 0 errors. NESO corrected 34→33 and total 163→162 (empirical vault count). Commits `d3620a4..` on `feat/phase-10-four-vendor`. See `phases/10-four-vendor-briefs/10-01-SUMMARY.md`. Closes the v2 milestone.]**

## v2 Phase Details

### Phase 7: Reconciliation
**Goal**: A verified Vault layer trusted as the input for content phases. Wrap the existing `quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py` as the `gridflow-drift-check` console script (renaming, fixing the two Windows-specific portability blockers); run Verification across all 6 Vendors; surface findings as local markdown under `.planning/reconciliation/<vendor>/<NN>-<slug>.md`; triage each into `open` (fixable in v2) / `wontfix` `reason: v3-candidate` (needs gridflow code changes) / `needs-info` `reason: defer-entitlement` (e.g. ENTSO-E entitlement); fix the `open` bucket via upstream Vault edits and re-vendor into `gridflow-front-end/vault/<vendor>/`; commit the upstream Vault to a new private GitHub repo `EBentham/quant-vault` (no GitHub App auth — cross-repo CI explicitly deferred per ADR-0002). After Phase 7, content phases (9 — ENTSO-E, 10 — four-vendor batch) build pages from a Vault we trust. Overrides the v1 "no upfront audit phase" decision per ADR-0001.
**Depends on**: Nothing (gating for content phases 9 and 10; independent of Phase 8 — bug fix — per Phase 7 D-03)
**Requirements**: RECON-01, RECON-02, RECON-03, RECON-04, RECON-05
**Success Criteria** (what must be TRUE):
  1. `gridflow-drift-check` exists as a console script on path (renamed from `verify_curl_and_silver_schema.py`), portable to Linux CI — the two Windows-specific blockers (`args[0] = "curl.exe"` at L180, hardcoded `C:\Users\Bobbo\...` default at L20-26) are parameterised; a `[drift]` extra is declared in the relevant `pyproject.toml` (planner picks vault vs front-end per Q-DD-16)
  2. Verification runs against all 6 Vendors and produces JSON + markdown reports; every Vendor under `.planning/reconciliation/<vendor>/` has a finding file for every Drift instance Verification surfaces; each finding carries a `status:` (`open` | `wontfix` | `needs-info`) and a `reason:` (where applicable: `v3-candidate` | `defer-entitlement`); the load-bearing findings from `DRIFT-SURFACES.md` §§ 4.1, 4.2, 4.4, 4.5, 4.6 are all surfaced (acceptance gate — if the verifier misses one of these, the wiring is wrong)
  3. The `open` bucket is closed: Vault edits land in the upstream `quant-vault` (now on GitHub — see #4) and re-vendored into `gridflow-front-end/vault/<vendor>/`; the vendored snapshot matches the reconciled upstream Vault; re-running `gridflow-drift-check` returns "no new Drift" (or only documented `wontfix-v3` / `needs-info` Drift)
  4. The upstream Vault is committed to a new private GitHub repo `EBentham/quant-vault`, no GitHub App auth configured (per ADR-0002); the v1 vendoring pattern (`gridflow-front-end/vault/<vendor>/` as a snapshot) is preserved
  5. v1 CI gates remain green on `gridflow-front-end`: `htmlhint`, `lychee --offline --include-fragments`, and `gridflow-build --check` idempotence (Phase 7 should not change the deploy contract; it only changes the Vault content the build consumes)
**Plans**: 4 sub-plans created and verified by plan-checker (per Phase 7 D-05):
- [07-01-verifier-wrap-PLAN.md](./phases/07-reconciliation/07-01-verifier-wrap-PLAN.md) — RECON-01 · Wave 1
- [07-02-run-verification-and-triage-PLAN.md](./phases/07-reconciliation/07-02-run-verification-and-triage-PLAN.md) — RECON-02 · Wave 1 · depends on 07-01
- [07-03-fix-open-bucket-and-revendor-PLAN.md](./phases/07-reconciliation/07-03-fix-open-bucket-and-revendor-PLAN.md) — RECON-03, RECON-05 · Wave 2 · depends on 07-02
- [07-04-push-vault-to-private-github-PLAN.md](./phases/07-reconciliation/07-04-push-vault-to-private-github-PLAN.md) — RECON-04 · Wave 2 · depends on 07-03 · `autonomous: false` (gh auth checkpoint)
**UI hint**: no (this phase has no UI surface; Site-rendering is downstream)

### Phase 8: Dataset-page formatting bug fix *(closed — superseded)*
**Goal (original)**: Root-cause and fix the top-of-page formatting bug confirmed on `fuelhh.html` before scaling 129 new pages off the same template. Locked to D-01 minimal-patch scope (no visual redesign).
**Outcome**: **Failed.** Two iterations of the locked-scope CSS patch (Iteration 1: `align-items: end` → `start`; Iteration 2: `align-items: stretch` + `grid-template-rows: repeat(3, 1fr)` + short silver-path display) both failed user visual verification at the BUG-02 checkpoint. Root cause was an **editorial-content gap in the vault** (no short H1 tagline field, no accent-styled fragments) — not a rendering-layer bug. The "alignment bug" was the most visible symptom of an underlying source-layer gap that no rendering-layer patch can fix.
**Decision**: Phase 8 closed as superseded by Phase 8B. The Iteration 2 template changes are kept in place (best-effort layout for long-tail templated pages under the Phase 8B hybrid model). Full retrospective: [`phases/08-bug-fix-dataset-formatting/08-01-SUMMARY.md`](./phases/08-bug-fix-dataset-formatting/08-01-SUMMARY.md).
**Requirements re-mapped to Phase 8B**: BUG-01, BUG-02, BUG-03

### Phase 8B: Claude-Design hero rewrite (hybrid authored/templated)
**Goal**: Adopt hand-authored HTML pages for showcase dataset pages (starting with `fuelhh.html`, generated externally via Claude Design), and add an `authored-pages/<vendor>/<slug>.html` override path to `src/gridflow_front_end/build.py` so the build script reads authored pages first and falls back to the Jinja2 template for the long-tail. This replaces Phase 8's locked-scope minimal patch with a hybrid model: ~5–15 showcase pages hand-authored at full editorial quality; ~150 long-tail pages template-rendered from vault. The Iteration 2 template changes from Phase 8 (stretch layout + `silver.{slug}` short-form) carry forward for the templated branch. If AI-hand-porting a second showcase page (e.g., `system_prices`) does not produce Claude-Design–equivalent quality, fall back to **Option C** (all 163 pages hand-designed in Claude Design and committed under `authored-pages/`).
**Depends on**: Phase 8 (closed/superseded) — Phase 8B's hybrid architecture is the explicit alternative to Phase 8's failed minimal-patch approach. Independent of Phase 7 (operates on rendering layer, not Vault content). Like Phase 8, runs parallel-eligible to Phase 7 but Phase 7 is already complete.
**Requirements**: BUG-01, BUG-02, BUG-03 (re-mapped from Phase 8 with re-scoped acceptance — see below)
**Success Criteria** (what must be TRUE):
  1. `authored-pages/elexon/fuelhh.html` exists, committed, byte-equal to the Claude-Design output verified 2026-05-19, and copied/preserved by the build at `site/hifi/data-sources/elexon/fuelhh.html` on every `gridflow-build` run (no clobbering)
  2. `src/gridflow_front_end/build.py` reads `authored-pages/<vendor>/<slug>.html` before invoking the Jinja2 template; if present, the authored file is the source; if absent, the template renders from vault as today. This logic lives in one named function (e.g., `_resolve_page_source`) with a one-line docstring naming the override semantics
  3. At least **one** additional page exists in `authored-pages/` and passes user visual verification at fuelhh-equivalent fidelity — either AI-hand-ported by the orchestrator (cheap path) or externally generated via Claude Design (fallback to Option C). Initial test target: `system_prices` (different schema, no fuel-pill section — stress-tests the design generalisation)
  4. The decision on the long-tail path is recorded in this phase's SUMMARY.md: either (a) **AI-hand-port** the remaining 32 Elexon + 1 ENTSO-E pages under `authored-pages/`, or (b) **Claude-Design all of them** (Option C), or (c) **leave them templated** (most-likely outcome — long tail accepts template quality, showcase pages get authored override)
  5. All v1 CI gates remain green on the regenerated set: `gridflow-build --check` exits 0 (idempotence holds across both authored and templated branches), `htmlhint --config .htmlhintrc 'site/hifi/**/*.html'` exits 0, `lychee --offline --include-fragments site/hifi/**/*.html` exits 0
**Plans**: TBD (likely 2–3 sub-plans: build-script override path, second-page port + verification, long-tail decision)
**UI hint**: yes

### Phase 9: ENTSO-E full coverage
**Goal**: Render the remaining 48 ENTSO-E datasets at `fuelhh` fidelity; upgrade `/data-sources/entsoe.html` from a 1-dataset proof to a 49-dataset catalog. This is the biggest single vendor in v2 and uses materially different schema vocabulary from Elexon — codelists, PSR-type taxonomy, BIDDING_ZONE references, quarter-hour settlement — so it stress-tests the post-Phase-8 template against a non-Elexon vendor at scale before the simpler four-vendor batch in Phase 10. The ENTSO-E entitlement question (33 HTTP 401 datasets deferred from Phase 7 per D-06) is resolved in this phase's discuss-phase before content build proceeds.
**Depends on**: Phase 7 (reconciled Vault input — including ENTSO-E `needs-info` finding files for the 33 entitlement-blocked datasets) AND **Phase 8B** (hybrid authored/templated path must be in place — replaces the original Phase 8 dependency, which was closed as superseded 2026-05-19)
**Requirements**: ENTSOE-01, ENTSOE-02, ENTSOE-03, ENTSOE-04, ENTSOE-05
**Success Criteria** (what must be TRUE):
  1. `ls vault/entsoe/*.md | wc -l` returns 49 (1 existing + 48 newly vendored from the reconciled `quant-vault/30-vendors/entsoe/datasets/`); upstream provenance recorded in the vendoring commit; ENTSO-E entitlement decision (extend access vs `skip-with-warn`) documented in this phase's CONTEXT.md per Phase 7 D-06
  2. `site/hifi/data/entsoe.json` contains exactly 49 dataset entries, grouped into ENTSO-E categories (generation / load / transmission / outages / capacity / prices, or whatever taxonomy the vault carries); the manifest validates against the build script's expectations
  3. Running `gridflow-build` produces 49 HTML files under `site/hifi/data-sources/entsoe/`; visiting any one renders the post-D-20 sidebar anchor set (`#snapshot`, `#schema`, `#sample`, the dataset-specific codelist anchor, `#api`, `#related`) and each resolves to a real `<section id>` — note `#overview` and `#caveats` are intentionally absent per D-20; every page shows the `verified-against-vendor-docs: YYYY-MM-DD` micro-line; ENTSO-E codelist / PSR-type vocabulary renders cleanly (no raw codelist IDs leaking into prose); schema reference present or `requires additional entitlement` flag inline in the schema notes where applicable (per the entitlement decision)
  4. Visiting `/data-sources/entsoe.html` shows a 49-dataset catalog rendered from `vendor-hub.html.j2` over the expanded `entsoe.json`; the hub header reflects 49 datasets, not 1
  5. `gridflow-build --check` exits 0 on the expanded ENTSO-E set (idempotence holds across 49 pages); `htmlhint` and `lychee --offline --include-fragments` exit 0 with zero new dead anchors or structural HTML breakage
**Plans**: TBD
**UI hint**: yes

### Phase 10: Four-vendor batch coverage + site-wide consistency
**Goal**: Ship the remaining four vendors as a batch — ENTSO-G (33) + GIE (8) + NESO (34) + Open-Meteo (6) = 81 new dataset pages — and close the v2 milestone with site-wide consistency: every vendor on `data-sources.html` links to a real hub, dataset count strings reflect the v2 total of 163, and zero coming-soon stub links remain in the catalog table. Content shape for these four vendors is simpler than ENTSO-E (smaller per-vendor surface, fewer codelist quirks), and by this point the template has been proven by Phase 9 at scale on a non-Elexon vendor, so the work is mechanical: vendor `.md` (from the reconciled Vault), author manifest, move `build.py` entry from `COMING_SOON_VENDORS` to `REAL_VENDORS`, run build, verify CI.
**Depends on**: Phase 7 (reconciled Vault input, including ENTSO-G `physical_flows` 35-field rewrite and the 4 ENTSO-G 404 endpoints handled) AND **Phase 8B** (hybrid authored/templated path — replaces the original Phase 8 dependency, which was closed as superseded 2026-05-19). Sequential execution after Phase 9 is recommended (not required) to avoid merge conflicts on `data-sources.html` and on the `REAL_VENDORS` dict in `src/gridflow_front_end/build.py`, and to keep PR review surfaces tractable.
**Requirements**: ENTSOG-01, ENTSOG-02, ENTSOG-03, ENTSOG-04, GIE-01, GIE-02, GIE-03, GIE-04, NESO-01, NESO-02, NESO-03, NESO-04, METEO-01, METEO-02, METEO-03, METEO-04, SITE-01, SITE-02
**Success Criteria** (what must be TRUE):
  1. Vault snapshot expanded: `ls vault/entsog/*.md | wc -l` = 33; `ls vault/gie/*.md | wc -l` = 8 (or split across `vault/gie_agsi/` + `vault/gie_alsi/` if the Phase 9 plan keeps the split — totalling 8); `ls vault/neso/*.md | wc -l` = 34; `ls vault/openmeteo/*.md | wc -l` = 6 — 81 new files in total, vendored from upstream `quant-vault`
  2. Four manifests authored and validated: `site/hifi/data/entsog.json` (33 datasets), `site/hifi/data/gie.json` or split `gie_agsi.json` + `gie_alsi.json` (8 datasets), `site/hifi/data/neso.json` (34 datasets), `site/hifi/data/openmeteo.json` (6 datasets); each lists the correct dataset count; each groups datasets per vendor taxonomy
  3. Running `gridflow-build` produces 81 new HTML files (33 + 8 + 34 + 6) under `site/hifi/data-sources/<vendor>/`; spot-checking any one across each vendor confirms `fuelhh` fidelity (all six sidebar anchors resolve to real `<section id>`s; `verified-against-vendor-docs` micro-line present; schema reference or drift-surface flag)
  4. In `src/gridflow_front_end/build.py`, the `entsog`, `gie` (or `gie_agsi` + `gie_alsi`), `neso`, and `openmeteo` entries are removed from `COMING_SOON_VENDORS` and added to `REAL_VENDORS` with full `vendor_meta` config (label, doc_base, description, etc.); `grep -n COMING_SOON_VENDORS src/gridflow_front_end/build.py` shows none of those four vendor keys remain; the four hubs at `/data-sources/<vendor>.html` render from `vendor-hub.html.j2`, not `vendor-coming-soon.html.j2`
  5. Site-wide dataset count strings consistently show 163 across `site/hifi/index.html` stat strip, footer line in `site/hifi/assets/site.js`, and `site/hifi/data-sources.html` catalog header; `grep -rn "33 Elexon" site/hifi/` returns only the on-purpose Elexon-specific row (not a stale total); `grep -rn 'href="/data-sources/[a-z_]*\.html"' site/hifi/data-sources.html` confirms every vendor row links to a real hub with zero remaining coming-soon stub links in the catalog table
  6. `gridflow-build --check` exits 0 across all 163 pages (idempotence holds at the v2 final scale); `htmlhint --config .htmlhintrc 'site/hifi/**/*.html'` exits 0; `lychee --offline --include-fragments site/hifi/**/*.html` exits 0 — all three v1 CI gates green on the expanded 6-vendor surface

**As-built (2026-06-07 — amendments to the original SC above):** NESO is **33** datasets, not 34 (empirical: `vault/neso` has 33 dataset `.md`, no README), so the batch is **80** new pages and the site total is **162**, not 163 (SC#1/#2/#3/#5/#6 numbers shift accordingly — see STATE D-2). GIE is **unified** into one `REAL_VENDORS["gie"]` hub (D-3), not the `gie_agsi`/`gie_alsi` split. Vendor hubs render from the **8D-authored `_landing.html`** via the authored-hub override, not `vendor-hub.html.j2` (SC#4) — D-22 was applied (synthesised `#overview` + `#caveats`), exceeding the original D-20 baseline. All other SC met as written; full record in `phases/10-four-vendor-briefs/10-01-SUMMARY.md`.
**Plans**: [10-01-PLAN.md](./phases/10-four-vendor-briefs/10-01-PLAN.md) — 18 REQ-IDs · executed 2026-06-05..07
**UI hint**: yes

## Phase Dependencies

```
v1 milestone (Phases 0–6) — Complete 2026-05-18
   │
   ├── Phase 7 (Reconciliation) — Complete 2026-05-19
   │
   ├── Phase 8 (CSS bug fix) — Closed/superseded 2026-05-19 (failed visual verification ×2)
   │
   ├── Phase 8B (Claude-Design hybrid) — GATING for 9 and 10
   │      │
   │      └── Phase 8C (Elexon content briefs) — Complete 2026-05-20
   │
   ├── Phase 8D (Vendor landing-page briefs) — Complete 2026-05-20 — GATING for 9 and 10 (hub layer)
   │
   └── Phase 9 (ENTSO-E full coverage) ← needs 8B + 8C + 8D
          │
          └── Phase 10 (four-vendor batch + site-wide consistency) ← needs 8D
```

**Sequential note:** Phase 7 (Reconciliation) completed 2026-05-19; Phase 8 was attempted parallel to it but closed as superseded the same day (see Phase 8 outcome above and `08-01-SUMMARY.md`). Phase 8B replaces Phase 8 as the rendering-layer gate for content phases. Phase 9 (ENTSO-E) and Phase 10 (four-vendor batch) both depend on Phase 7 (reconciled Vault input) **and** Phase 8B (hybrid authored/templated path in place). Running 8B → 9 → 10 in series is **recommended** to keep merge surfaces tractable and to let the long-tail-path decision from Phase 8B (templated vs. authored vs. Claude-Design-all) inform Phase 9's vendoring approach.

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 0. Commit in-flight refactor | 1/1 | Complete | 2026-05-18 |
| 1. Trivial bug fixes | inline | Complete | 2026-05-18 (PR #4) |
| 2. Shared CSS/JS extraction | inline | Complete | 2026-05-18 (PR #5) |
| 3. Build mechanism + Elexon dataset depth | inline | Complete | 2026-05-18 (PR #6) |
| 4. Cross-vendor proof + dead-link real fix | inline | Complete | 2026-05-18 (PR #7) |
| 5. Honesty + a11y + mobile + main-page polish | inline | Complete | 2026-05-18 (PR #8) |
| 6. CI validation | inline | Complete | 2026-05-18 (PR #9 + #10 + #11) |
| 7. Reconciliation | 4/4 | Complete | 2026-05-19 |
| 8. Dataset-page formatting bug fix | 1/1 (failed) | Closed/superseded by 8B | 2026-05-19 |
| 8B. Claude-Design hero rewrite (build override kept; AI-ports archived) | 1/1 (output sub-optimal) | Partial — output archived 2026-05-20; superseded by 8C | 2026-05-20 |
| 8C. Elexon content briefs (triangulated research) | 1/1 | Complete (33/33 briefs ✓ all 12 structural checks; 45 discrepancies surfaced) | 2026-05-20 |
| 8D. Vendor landing-page briefs (5 hubs) | 1/1 | Complete (5/5 briefs ✓ all 10 structural checks; build override patch shipped; 15 discrepancies surfaced; see `phases/08D-vendor-landing-page-briefs/08D-01-SUMMARY.md`) | 2026-05-20 |
| 9. ENTSO-E full coverage | 2/2 | Complete (49 briefs + 49 authored pages + 49-entry manifest in 9 groups; build idempotent; ENTSOE-01..05) | 2026-06-03 |
| 10. Four-vendor batch coverage + site-wide consistency | 0/? | Not started (blocked on 8D + 9) | — |

v1 milestone complete · 50/50 REQ-IDs delivered. v2 milestone active · Phases 7–9 complete (RECON-01..05 · BUG-01..03 · ENTSOE-01..05 = 13 REQ-IDs delivered, plus the 8C/8D content-brief infrastructure phases); only Phase 10 (four-vendor batch: ENTSOG/GIE/NESO/METEO/SITE) remains.

---

## v1 Phases (Complete — historical record)

The v1 cleanup milestone completed 2026-05-18 with 50/50 REQ-IDs delivered. Full per-success-criterion audit in [`MILESTONE-COMPLETE.md`](./MILESTONE-COMPLETE.md). Phase details below are preserved verbatim from the original v1 roadmap so future contributors can trace what each REQ-ID mapped to.

### v1 Phase Summary

- [x] **Phase 0: Commit in-flight refactor** — Land the 26 modified files as 4 logical commits + `.gitattributes`; clean working tree is the gating prerequisite for everything else *(completed 2026-05-18)*
- [x] **Phase 1: Trivial bug fixes** — Mobile viewport tag find-and-replace, `LICENSE` file + aligned strings, `rel="noopener"` on the two missing links (parallelisable with Phase 2) *(completed 2026-05-18)*
- [x] **Phase 2: Shared CSS/JS extraction** — Move the duplicated dataset-page `<style>` block + scroll-spy IIFE + `setTab()` declarations into `theme.css` + `site.js`; fix the sidebar hover bug *(completed 2026-05-18, PR #5)*
- [x] **Phase 3: Build mechanism + Elexon dataset depth** — Author the Python+Jinja2 `gridflow-build` CLI, the dataset/vendor-hub templates, vault-content reader; ship all 33 Elexon datasets at `fuelhh` fidelity from vault content *(completed 2026-05-18, PR #6)*
- [x] **Phase 4: Cross-vendor proof + dead-link real fix** — ENTSO-E hub + `actual_generation` (A75/A16) dataset via the same templates; 5 visually-distinct coming-soon vendor stubs; every `<a href="#">` on `data-sources.html` resolves to a real page *(completed 2026-05-18, PR #7)*
- [x] **Phase 5: Honesty sweep + a11y + mobile CSS + main-page polish** — Atomic kill of all 6 "live"-framing surfaces; mobile CSS in `theme.css`; `<main>` + `aria-current` + `aria-label` + `aria-hidden` minimums; editorial polish pass on index, architecture, data-sources hub *(completed 2026-05-18, PR #8)*
- [x] **Phase 6: CI validation** — `htmlhint` + `lychee` + build-idempotence check in `.github/workflows/deploy.yml` before `upload-pages-artifact` *(completed 2026-05-18, PR #9 + #10 + #11 fix-ups)*

### v1 Phase Details

#### Phase 0: Commit in-flight refactor
**Goal**: Clean working tree with the 26-file refactor split into 4 logical commits, line-ending churn permanently stopped via `.gitattributes`. Every subsequent commit can be reviewed without entangling three concurrent refactors.
**Depends on**: Nothing (gating prerequisite — blocks all other phases per all four research streams)
**Requirements**: HYG-01, HYG-02
**Success Criteria** (what must be TRUE):
  1. `git status` shows zero modified files and zero untracked files; `git log --oneline` since `351c580` shows 6 commits in the documented order — 4 cleanup chunks (typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks) plus 2 repo-hygiene chunks (`.gitattributes` + `.gitignore` bundled · renormalize line endings) per `00-CONTEXT.md` D-03
  2. `.gitattributes` exists at repo root with `text eol=lf` rules covering `*.html`, `*.css`, `*.js`, `*.json`, `*.py`, and a Windows-edited commit produces no LF/CRLF warnings on `git diff`
  3. GitHub Pages-deployed site matches the current `main` HEAD (working tree and deployed view are no longer diverged)
**Plans**: 1 plan
- [x] 00-01-PLAN.md — Planner-record commit + 4 cleanup chunks + 2 hygiene + ROADMAP SC#1 reconciliation + PR/merge/Pages-verify (11 sequential tasks, Wave 1) *(completed 2026-05-18, PR #3 merged)*

#### Phase 1: Trivial bug fixes
**Goal**: Ship the no-architectural-dependency one-line fixes that block mobile usability and license credibility, in parallel with Phase 2. These are cosmetic-class to a recruiter spot-check yet high-leverage (mobile viewport is the single highest-leverage fix in the milestone per Pitfall 10).
**Depends on**: Phase 0
**Requirements**: MOB-01, HON-04, A11Y-06
**Success Criteria** (what must be TRUE):
  1. Every page in `site/hifi/` carries `<meta name="viewport" content="width=device-width, initial-scale=1">`; `grep` for `width=1280` returns zero hits
  2. `LICENSE` file exists at repo root with one chosen license; `grep` across `site/hifi/` and `src/` shows zero contradictory license strings (no MIT vs Apache-2.0 split)
  3. Both `target="_blank"` links currently missing `rel="noopener"` (architecture.html ~line 1156, data-sources/elexon.html ~line 41) now carry the attribute
**Plans**: TBD

#### Phase 2: Shared CSS/JS extraction
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

#### Phase 3: Build mechanism + Elexon dataset depth
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

#### Phase 4: Cross-vendor proof + dead-link real fix
**Goal**: Prove the templating from Phase 3 generalises across vendors by shipping an ENTSO-E hub + "Generation by PSR type" dataset at `fuelhh` fidelity (template-stretching choice: quarter-hour settlement + PSR-type taxonomy). In the same pass, replace every `<a href="#">` placeholder on the data-sources hub with a real link — either a real vendor hub (Elexon, ENTSO-E) or a visually-distinct coming-soon stub for the 5 deferred vendors.
**Depends on**: Phase 3 (cross-vendor extrapolation requires Elexon template consistency; coming-soon stubs use `vendor-coming-soon.html.j2`)
**Requirements**: VEND-01, VEND-02, VEND-03, VEND-04, VEND-05, PAGE-03
**Success Criteria** (what must be TRUE):
  1. Visiting `/data-sources/entsoe.html` renders an ENTSO-E vendor hub (built from `vendor-hub.html.j2` over `site/hifi/data/entsoe.json`); visiting `/data-sources/entsoe/<psr-slug>.html` renders the "Generation by PSR type" dataset page at `fuelhh` fidelity (all six sidebar anchors resolve, schema/sample/caveats sections present, verified-against-vendor-docs micro-line)
  2. Each of the 5 deferred vendors (ENTSO-G, GIE AGSI, GIE ALSI, Open-Meteo, NESO) has a coming-soon stub rendered from `vendor-coming-soon.html.j2` that is visually distinguishable from a real vendor hub at a glance — no sidebar, no chart container, single-screen layout, "Planned · F<n>" stage chip (per Pitfall 9 prevention)
  3. `grep` for `href="#"` over `site/hifi/data-sources.html` returns zero hits; every vendor row clicks through to either a real vendor hub or a coming-soon stub
**Plans**: TBD
**UI hint**: yes

#### Phase 5: Honesty sweep + a11y + mobile CSS + main-page polish
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

#### Phase 6: CI validation
**Goal**: Lock in the milestone's structural wins with cheap automated checks that catch the exact bug class motivating v1 — broken dataset stubs, dead links, phantom sidebar anchors, build-idempotence regressions.
**Depends on**: Phase 3 (build-idempotence check requires the build script to exist), Phase 5 (link-checker assumes pages have stabilised)
**Requirements**: CI-01, CI-02, CI-03
**Success Criteria** (what must be TRUE):
  1. `.github/workflows/deploy.yml` runs `htmlhint` (or equivalent) over the built site before `actions/upload-pages-artifact@v3` and fails the deploy on structural HTML breakage of the broken-stub class
  2. `lychee` (or equivalent link checker) runs over the built site before deploy and fails on internal dead links (catches dead-anchor regressions)
  3. CI runs `gridflow-build` twice on the same vault checkout and fails the deploy if `git diff` of the output directory is non-empty (build-idempotence smoke test)
**Plans**: TBD

### v1 Phase Dependencies

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

**Parallelisation note (v1):** Phase 1 and Phase 2 were independent after Phase 0 landed. Phases 3–6 were strictly sequential because each consumed the output of the previous (template + content depth → cross-vendor template proof → atomic sweep over the template-generated set → CI guarding the stabilised pages).

Phases 1–6 were planned inline during autonomous execution per `AUTONOMOUS-V1-BRIEF.md`'s authorization to skip `/gsd-plan-phase` for non-Phase-0 work.

---

*v1 roadmap created 2026-05-17 (50/50 REQ-IDs delivered 2026-05-18). v2 roadmap added 2026-05-18 (26 v2 REQ-IDs mapped, 0/26 delivered). Rescoped 2026-05-19 — Phase 7 Reconciliation inserted; existing 7→8, 8→9, 9→10. 5 RECON-* REQ-IDs added → 31/31 v2 coverage. Source for v2: PROJECT.md § Active + REQUIREMENTS.md § v2 Requirements + MILESTONE-COMPLETE.md + docs/adr/0001-reconciliation-phase-added-to-v2.md + docs/adr/0002-vault-hosted-private-github-repo.md + .planning/V2-PHASE-7-HANDOFF.md + .planning/phases/07-reconciliation/07-CONTEXT.md.*
