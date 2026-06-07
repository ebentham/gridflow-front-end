# Requirements

REQ-IDs are stable references used by `ROADMAP.md` traceability.

This file holds the **v1 cleanup milestone** (complete, 50/50 delivered) and the **v2 full-vendor-coverage milestone** (active). v1 items stay here as a historical record so future contributors can trace what each REQ-ID maps to.

---

## v2 Requirements (Active)

Scope: **v2 full-vendor-coverage** — first reconcile the Vault layer so all six Vendors carry verified content (per ADR-0001 / Phase 7), then ship the remaining 129 dataset pages at `fuelhh` fidelity across ENTSO-E (48 new), ENTSO-G (33), GIE (8), NESO (33), and Open-Meteo (6). Bring the site catalogue from 34 to 162 datasets. Every vendor on the site moves from "coming soon" to a complete dataset catalog.

### Reconciliation (RECON) — Phase 7, gating for content phases 9 and 10
- [x] **RECON-01** — `gridflow-drift-check` exists as a console script on path (renamed from `quant-vault/30-vendors/scripts/verify_curl_and_silver_schema.py` → `gridflow_drift_check.py`); portable to Linux CI — both Windows-specific blockers (the `args[0] = "curl.exe"` line at L180 and the hardcoded `C:\Users\Bobbo\...` default at L20-26) are parameterised; a `[drift]` extra is declared in the appropriate `pyproject.toml` (Q-DD-16 default lean: `quant-vault` if it has one, else `gridflow-front-end`) *(completed 07-01, 2026-05-19)*
- [x] **RECON-02** — Verification runs across all 6 Vendors and produces JSON + markdown reports; every Vendor under `.planning/reconciliation/<vendor>/` has a finding file (`<NN>-<slug>.md`) for every Drift instance Verification surfaces; each finding carries a `status:` (`open` | `wontfix` | `needs-info`) and where applicable a `reason:` (`v3-candidate` | `defer-entitlement`); the load-bearing findings from `DRIFT-SURFACES.md` §§ 4.1 (ndf/ndfd), 4.2 (fuelhh), 4.4 (33 ENTSO-E 401s), 4.5 (4 ENTSO-G 404s), 4.6 (`physical_flows` 35-field mismatch) are all surfaced (acceptance gate) *(completed 07-02, 2026-05-19)*
- [ ] **RECON-03** — The `open` bucket is closed: Vault edits land in the upstream `quant-vault` and re-vendored into `gridflow-front-end/vault/<vendor>/`; the vendored snapshot matches the reconciled upstream Vault byte-equivalently; re-running `gridflow-drift-check` returns "no new Drift" (or only documented `wontfix-v3` / `needs-info` Drift); specific fixes include `published_at` added to `ndf.md` / `ndfd.md` / `fuelhh.md` schema tables, 18 ENTSO-E `resolution` field nullability flags added, 4 ENTSO-G 404 endpoints handled (delete or mark `removed:`), `physical_flows.md` schema table rewritten to match Pydantic shape (`flow_gwh_per_day`, `timestamp_utc`)
- [ ] **RECON-04** — The upstream Vault is committed to a new private GitHub repo `EBentham/quant-vault` per ADR-0002; no GitHub App auth configured (cross-repo automated drift CI explicitly deferred); the v1 vendoring pattern (`gridflow-front-end/vault/<vendor>/` as a snapshot) is preserved
- [ ] **RECON-05** — v1 CI gates remain green on `gridflow-front-end` after Reconciliation: `htmlhint`, `lychee --offline --include-fragments`, and `gridflow-build --check` idempotence all pass on the regenerated set (Phase 7 changes only the Vault content the build consumes, not the deploy contract)

### Dataset-page formatting bug (BUG) — Phase 8 (parallel-eligible with Phase 7), gating for content phases 9 and 10
- [ ] **BUG-01** — The dataset-page top-of-page formatting bug (confirmed on `fuelhh.html`) is root-caused; the offending location is named (Jinja2 template / shared `theme.css` rules / vault `.md` frontmatter / build-script transform) and a fix path is chosen
- [ ] **BUG-02** — Fix applied; `gridflow-build` re-renders all 34 existing pages with the top-of-page section visually correct on `fuelhh.html` plus one randomly-spot-checked page (user-verified)
- [ ] **BUG-03** — v1 CI gates stay green on the post-fix output: `htmlhint`, `lychee --offline --include-fragments`, and `gridflow-build --check` idempotence all pass

### ENTSO-E full coverage (ENTSOE) — Phase 9
- [ ] **ENTSOE-01** — All 48 new ENTSO-E vault `.md` files vendored from the reconciled upstream `quant-vault/30-vendors/entsoe/datasets/` into this repo's `vault/entsoe/`; final count: 49 `.md` files (1 existing + 48 new); ENTSO-E entitlement decision (extend access vs `skip-with-warn`) documented in this phase's CONTEXT.md per Phase 7 D-06
- [ ] **ENTSOE-02** — `site/hifi/data/entsoe.json` manifest contains all 49 ENTSO-E datasets, grouped into ENTSO-E categories (generation / load / transmission / outages / capacity / prices, or whatever taxonomy the vault carries)
- [ ] **ENTSOE-03** — All 49 ENTSO-E dataset pages render at `fuelhh` fidelity: 6-anchor sidebar (`#overview`, `#schema`, `#sample`, `#api`, `#caveats`, `#related`) resolves to real `<section id>` elements; `verified-against-vendor-docs: YYYY-MM-DD` micro-line present; ENTSO-E codelist / PSR-type vocabulary handled cleanly; schema reference present (or `requires additional entitlement` caveat where applicable per the entitlement decision)
- [ ] **ENTSOE-04** — `/data-sources/entsoe.html` hub upgraded from 1-dataset proof to a 49-dataset catalog, built from the expanded manifest via `vendor-hub.html.j2`
- [ ] **ENTSOE-05** — `gridflow-build --check` idempotence stays green on the expanded ENTSO-E set; `htmlhint` + `lychee` gates stay green; no new dead anchors or structural HTML breakage

### ENTSO-G coverage (ENTSOG) — Phase 10
- [x] **ENTSOG-01** — All 33 ENTSO-G vault `.md` files vendored from upstream into `vault/entsog/`
- [x] **ENTSOG-02** — `site/hifi/data/entsog.json` manifest authored with 33 datasets, grouped into 5 ENTSO-G categories
- [x] **ENTSOG-03** — All 33 ENTSO-G dataset pages render at `fuelhh` fidelity (D-22: synthesised `#overview` + rendered `#caveats`; authored via Claude Design)
- [x] **ENTSOG-04** — `/data-sources/entsog.html` is a real vendor hub (8D-authored `_landing.html`, served via the authored-hub override — not the coming-soon stub); `entsog` moved from `COMING_SOON_VENDORS` to `REAL_VENDORS` in `src/gridflow_front_end/build.py`

### GIE coverage (GIE) — Phase 10
- [x] **GIE-01** — All 8 GIE vault `.md` files vendored from upstream into `vault/gie/` (unified — AGSI+ALSI in one folder)
- [x] **GIE-02** — `site/hifi/data/gie.json` manifest authored: 8 datasets in 2 groups (Storage AGSI+ 7 · LNG ALSI 1)
- [x] **GIE-03** — All 8 GIE dataset pages render at `fuelhh` fidelity (D-22; authored via Claude Design)
- [x] **GIE-04** — GIE is one consolidated real hub at `/data-sources/gie.html`; the `gie_agsi`/`gie_alsi` coming-soon split is collapsed into a single `REAL_VENDORS["gie"]`; `gie_agsi.html`/`gie_alsi.html` no longer emitted

### NESO Carbon Intensity coverage (NESO) — Phase 10
- [x] **NESO-01** — All 33 NESO vault `.md` files vendored from upstream into `vault/neso/` *(corrected 34→33: vendored snapshot has 33 dataset `.md`, no README — the "34" was a doc-era miscount)*
- [x] **NESO-02** — `site/hifi/data/neso.json` manifest authored with 33 datasets in 4 groups
- [x] **NESO-03** — All 33 NESO dataset pages render at `fuelhh` fidelity (D-22; authored via Claude Design)
- [x] **NESO-04** — `/data-sources/neso.html` is a real vendor hub (8D-authored, authored-hub override); `neso` moved from `COMING_SOON_VENDORS` to `REAL_VENDORS` in `build.py`

### Open-Meteo coverage (METEO) — Phase 10
- [x] **METEO-01** — All 6 Open-Meteo vault `.md` files vendored from upstream into `vault/openmeteo/`
- [x] **METEO-02** — `site/hifi/data/openmeteo.json` manifest authored with 6 datasets in 2 groups (Forecast 3 · Historical 3)
- [x] **METEO-03** — All 6 Open-Meteo dataset pages render at `fuelhh` fidelity (D-22; authored via Claude Design)
- [x] **METEO-04** — `/data-sources/openmeteo.html` is a real vendor hub (8D-authored, authored-hub override); `openmeteo` moved from `COMING_SOON_VENDORS` to `REAL_VENDORS` in `build.py`

### Site-wide consistency (SITE) — Phase 10
- [x] **SITE-01** — Site-wide dataset count strings are consistent and reflect the v2 total of **162** datasets across 6 vendors (corrected 163→162: 33 Elexon + 49 ENTSO-E + 33 ENTSO-G + 8 GIE + 33 NESO + 6 Open-Meteo): `site/hifi/index.html` stat strip + pillar, footer-line in `site/hifi/assets/site.js`, and `site/hifi/data-sources.html` catalog header + per-section totals all align; stale `163`/`7 vendors`/`34 datasets` greps return zero hits
- [x] **SITE-02** — `site/hifi/data-sources.html` catalog: every vendor row links to a real vendor hub (GIE → unified `gie.html`); zero coming-soon stub links remain in the catalog table

---

## v1 Requirements (Complete — historical record)

All 50 v1 REQ-IDs delivered on 2026-05-18. Site deployed at https://ebentham.github.io/gridflow-front-end/. Full success-criteria audit in [`MILESTONE-COMPLETE.md`](./MILESTONE-COMPLETE.md).

### Repo hygiene (HYG)
- [x] **HYG-01** · **HYG-02** — In-flight refactor split into 4 logical commits; `.gitattributes` with `text eol=lf` rules committed

### Main pages (PAGE)
- [x] **PAGE-01** · **PAGE-02** · **PAGE-03** · **PAGE-04** — Home / architecture / data-sources hub polished; mobile-functional; honest framing

### Build mechanism (BUILD)
- [x] **BUILD-01** through **BUILD-08** — `gridflow-build` CLI; `[build]` extras; dataset/vendor-hub/coming-soon templates; idempotent CI build; generated HTML gitignored; 6 originally-complete pages regenerated (with documented `BUILD-DIFFS.md`)

### Vault integration (VAULT)
- [x] **VAULT-01** through **VAULT-04** — Build reads vault `.md` files; vault path configurable; `--check` flag surfaces missing sections; vault→site mapping documented in `README.md`

### Elexon dataset depth (ELX) — 33 datasets at `fuelhh` fidelity
- [x] **ELX-01** through **ELX-08** — 6 complete pages regenerated; 16 broken stubs completed; 3 manifest-only datasets shipped; 8 vault-only datasets added; count of 33 propagated site-wide; 6 sidebar anchors resolve; verified-against-vendor-docs micro-line; Pydantic schema reference or drift-surface flag

### Cross-vendor proof (VEND)
- [x] **VEND-01** through **VEND-05** + **PAGE-03** — ENTSO-E hub + `actual_generation` (A75/A16) at `fuelhh` fidelity; 5 visually-distinct coming-soon vendor stubs; zero `href="#"` placeholders

### Honesty sweep (HON)
- [x] **HON-01** through **HON-04** — All 6 "live"-framing surfaces removed; charts carry "Illustrative snapshot" chips; footer build-version replaced; MIT license at repo root with aligned strings

### Accessibility minimums (A11Y)
- [x] **A11Y-01** through **A11Y-06** — `<main>` landmark; `aria-current` on active nav; `aria-hidden` on decorative icons; distinguishing `aria-label`s on dual `<nav>`; sidebar hover affordance; `rel="noopener"` on external links

### Mobile / responsive (MOB)
- [x] **MOB-01** through **MOB-03** — Viewport meta fixed on 23 pages; responsive CSS for ≤480px and ≤720px in `theme.css`; mobile menu reachable

### Structural refactor (REF)
- [x] **REF-01** through **REF-03** — Duplicated dataset `<style>` block moved to `theme.css`; scroll-spy consolidated; `[data-tabs]` convention site-wide

### CI / validation (CI)
- [x] **CI-01** · **CI-02** · **CI-03** — `htmlhint` + `lychee --offline --include-fragments` + `gridflow-build --check` idempotence gates in `.github/workflows/deploy.yml`

---

## v3 Requirements (Deferred)

Considered for v2 and explicitly deferred to keep v2 focused on full-vendor-coverage. These were on the v1-MILESTONE-COMPLETE deferred list and remain deferred:

- **Pydantic schema drift closure** — 22 of 33 Elexon datasets render with "no dedicated Pydantic class declared yet — drift-surface flagged" rather than blocking the build. Closing the gap means declaring `ElexonAGPT`, `ElexonAGWS`, `ElexonFOU2T14D`, etc. in `gridflow.schemas.elexon` (cross-repo work) and re-running build
- **Per-dataset related-card blurbs** — `fuelhh.html`'s hand-curated "Pair with X to do Y" related-card copy was retired by the shared template. Restoring via a `related_blurbs:` vault frontmatter field
- **`fuelhh` fuel-pill grid** — 16-pill fuel-type colour swatch retired by the shared template. Restoring via a `fuel_types: [...]` vault frontmatter field
- **Drift-detection automation** — Research package lives at `.planning/research/post-v1/drift-detection/`. Post-v2 work
- **More model case studies** — SRMC, wind, solar, fundamentals SMP. `demand-forecast.html` is the v1 reference for the model-case-study anatomy
- **Real API wiring / nightly snapshot regeneration** — Illustrative-snapshot framing stays; live wiring is a separate, scoped milestone
- **GitHub Actions Node 24 migration** — Workflow currently uses Node 20 actions (deprecate Sep 2026); trivial upgrade when needed
- **Search UI / dark mode / blog index** — Aesthetic discipline; not v3-priority

---

## Out of Scope

Explicit boundaries — included with reasoning to prevent re-adding:

- **Adopting a Node/Go SSG (11ty / Astro / Hugo)** — Rejected after v1 research; introduces a non-Python toolchain to a Python-first portfolio for negligible benefit. v1+v2 use Python + Jinja2
- **Live performance metrics, uptime badges, dashboard-y elements** — Anti-goal per PROJECT.md; would imply the site is a SaaS product, not a portfolio documentation site
- **Real-time data fetches from the browser** — Deploy artifact stays pure-static; any "live" semantics would go through a build-time regeneration mechanism in a future milestone
- **New visual identity / design system rebuild** — Cream/forest/Fraunces aesthetic stays; revisit only if evidence demands it
- **Hand-authored dataset pages bypassing the build script** — Every dataset page MUST be generated from vault + manifest; otherwise the single-source-of-truth claim breaks
- **Author photos, testimonials, hire-me CTAs, blog index** — Editorial-quiet aesthetic; not a personal brand site
- **Cross-repo schema-as-source-of-truth auto-wiring** — Considered for v2, deferred to v3 candidates; would eliminate Pydantic drift structurally but requires committing to a cross-repo build dependency

---

## Traceability — v2 (Active)

Every v2 REQ-ID maps to exactly one v2 phase in `ROADMAP.md`. 31/31 coverage; no orphans. (5 RECON-* REQ-IDs added 2026-05-19 with the Phase 7 Reconciliation rescope per ADR-0001; existing BUG/ENTSOE/ENTSOG/GIE/NESO/METEO/SITE rows renumbered to phases 8/9/10.)

| REQ-ID | Phase | Status |
|--------|-------|--------|
| RECON-01 | Phase 7 — Reconciliation | Delivered (07-01, 2026-05-19) |
| RECON-02 | Phase 7 — Reconciliation | Delivered (07-02, 2026-05-19) |
| RECON-03 | Phase 7 — Reconciliation | Pending |
| RECON-04 | Phase 7 — Reconciliation | Pending |
| RECON-05 | Phase 7 — Reconciliation | Pending |
| BUG-01 | Phase 8 — Dataset-page formatting bug fix | Pending |
| BUG-02 | Phase 8 — Dataset-page formatting bug fix | Pending |
| BUG-03 | Phase 8 — Dataset-page formatting bug fix | Pending |
| ENTSOE-01 | Phase 9 — ENTSO-E full coverage | Pending |
| ENTSOE-02 | Phase 9 — ENTSO-E full coverage | Pending |
| ENTSOE-03 | Phase 9 — ENTSO-E full coverage | Pending |
| ENTSOE-04 | Phase 9 — ENTSO-E full coverage | Pending |
| ENTSOE-05 | Phase 9 — ENTSO-E full coverage | Pending |
| ENTSOG-01 | Phase 10 — Four-vendor batch coverage | Delivered |
| ENTSOG-02 | Phase 10 — Four-vendor batch coverage | Delivered |
| ENTSOG-03 | Phase 10 — Four-vendor batch coverage | Delivered |
| ENTSOG-04 | Phase 10 — Four-vendor batch coverage | Delivered |
| GIE-01 | Phase 10 — Four-vendor batch coverage | Delivered |
| GIE-02 | Phase 10 — Four-vendor batch coverage | Delivered |
| GIE-03 | Phase 10 — Four-vendor batch coverage | Delivered |
| GIE-04 | Phase 10 — Four-vendor batch coverage | Delivered |
| NESO-01 | Phase 10 — Four-vendor batch coverage | Delivered |
| NESO-02 | Phase 10 — Four-vendor batch coverage | Delivered |
| NESO-03 | Phase 10 — Four-vendor batch coverage | Delivered |
| NESO-04 | Phase 10 — Four-vendor batch coverage | Delivered |
| METEO-01 | Phase 10 — Four-vendor batch coverage | Delivered |
| METEO-02 | Phase 10 — Four-vendor batch coverage | Delivered |
| METEO-03 | Phase 10 — Four-vendor batch coverage | Delivered |
| METEO-04 | Phase 10 — Four-vendor batch coverage | Delivered |
| SITE-01 | Phase 10 — Four-vendor batch coverage | Delivered |
| SITE-02 | Phase 10 — Four-vendor batch coverage | Delivered |

**Coverage check:** 31 v2 REQ-IDs mapped to 4 v2 phases. Each REQ-ID appears exactly once. Each phase has at least 3 REQ-IDs. No orphans.

**Category distribution across v2 phases:**

| Category | Phase 7 | Phase 8 | Phase 9 | Phase 10 | Total |
|----------|---------|---------|---------|----------|-------|
| RECON | 5 | – | – | – | 5 |
| BUG | – | 3 | – | – | 3 |
| ENTSOE | – | – | 5 | – | 5 |
| ENTSOG | – | – | – | 4 | 4 |
| GIE | – | – | – | 4 | 4 |
| NESO | – | – | – | 4 | 4 |
| METEO | – | – | – | 4 | 4 |
| SITE | – | – | – | 2 | 2 |
| **Total** | **5** | **3** | **5** | **18** | **31** |

---

## Traceability — v1 (Complete, historical)

| REQ-ID | Phase | Status |
|--------|-------|--------|
| HYG-01, HYG-02 | Phase 0 — Commit in-flight refactor | ✓ Delivered (PR #3) |
| MOB-01, HON-04, A11Y-06 | Phase 1 — Trivial bug fixes | ✓ Delivered (PR #4) |
| REF-01, REF-02, REF-03, A11Y-05 | Phase 2 — Shared CSS/JS extraction | ✓ Delivered (PR #5) |
| BUILD-01..08, VAULT-01..04, ELX-01..08 | Phase 3 — Build mechanism + Elexon depth | ✓ Delivered (PR #6) |
| VEND-01..05, PAGE-03 | Phase 4 — Cross-vendor proof + dead-link fix | ✓ Delivered (PR #7) |
| HON-01..03, MOB-02..03, A11Y-01..04, PAGE-01, PAGE-02, PAGE-04 | Phase 5 — Honesty + a11y + mobile + polish | ✓ Delivered (PR #8) |
| CI-01..03 | Phase 6 — CI validation | ✓ Delivered (PR #9 + #10 + #11) |

**v1 coverage:** 50/50 REQ-IDs delivered across 7 phases. See `MILESTONE-COMPLETE.md` for the per-success-criterion audit.
