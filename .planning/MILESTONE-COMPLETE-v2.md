# v2 Full-Vendor-Coverage Milestone — Complete + Deployed

**Completed + deployed:** 2026-06-07
**Final state:** All phases done; **PRs #24 (`e323242`) + #25 (`9fac779`) merged to `main` and deployed to GitHub Pages** (deploy workflow run succeeded, all 3 CI gates green in CI).
**Live:** https://ebentham.github.io/gridflow-front-end/

> v2 milestone closed. Only an optional `v2` release tag remains (cosmetic). The v1 record lives
> in `MILESTONE-COMPLETE.md`.

## Status

**Phases 7 → 11 shipped.** v2 goal met: a recruiter clicks any vendor and gets a complete
catalogue; clicks any dataset and gets full documentation at `fuelhh` fidelity. Site-wide total:
**162 datasets across 6 vendors** (Elexon 33 · ENTSO-E 49 · ENTSO-G 33 · GIE 8 · NESO 33 ·
Open-Meteo 6). Build idempotent, CI-gated, vault-driven; editorial-quiet + honest framing hold
across all new pages. Phase 11 added a WCAG/consistency cleanup pass on top.

## Phase summary

| Phase | What shipped | PR | Status |
|-------|--------------|----|--------|
| 7 — Reconciliation | `gridflow-drift-check`; all-vendor drift triage; vault → private GitHub | — | Complete 2026-05-19 |
| 8 — CSS bug fix | Closed/superseded (root cause = vault content gap, not rendering) | — | Closed 2026-05-19 |
| 8B/8C/8D — Brief + authored-page infra | authored-pages override path; 33 Elexon + 5 hub briefs | — | Complete 2026-05-20 |
| 9 — ENTSO-E full | 49 briefs + 49 authored pages + 49-entry manifest | (feat/phase-9) | Complete 2026-06-03 |
| 10 — Four-vendor batch | 80 pages (entsog/gie/neso/openmeteo) + 4 manifests + REAL_VENDORS migration; counts → 162 | **#24** | Complete 2026-06-07 |
| 11 — Site cleanup | 19 audit findings (a11y/WCAG, consistency, anti-fake-freshness, dead-code, SEO meta) + adversarial code review | **#25** | Complete / shipped 2026-06-07 |

## CI evidence (cold rebuild, 2026-06-07)

- `gridflow-build` → 162 dataset pages + 6 real hubs; `--check` idempotent.
- `htmlhint` → 172 files, 0 errors. `lychee --offline --include-fragments` → 0 errors.
- Phase 11 adversarial code review: 13 raw → 6 confirmed → 2 remediated (models-page a11y miss;
  architecture silver-transformer counts reconciled to gridflow SoT) + 2 resolved (D-1 sacred-ref
  sign-off accepted) + 1 deferred follow-up.

## Key v2 decisions (full detail in STATE.md § Accumulated Context)

- Vault is **derivative**; Reconciliation fixes vault to match gridflow Canonical (one-way).
- Hybrid authored/templated: showcase + all v2 pages hand-authored under `authored-pages/`;
  long-tail template path retained as dormant fallback.
- Site-wide count = **162** (empirical vault count; legacy "163/NESO 34" was a doc-era miscount).
- GIE unified into one hub (AGSI + ALSI as two groups).
- **D-1 (Phase 11):** sacred refs un-frozen for 3 non-visual a11y attrs; "byte-identical visual"
  relaxed to "byte-identical HTML + static layout" — shared-CSS a11y fixes apply site-wide
  (user-accepted) so fuelhh/system_prices are now AA-compliant.

## Outstanding

- **Done:** #24 + #25 merged to `main` → GitHub Pages deploy succeeded (2026-06-07).
- Optional only: a `v2` release tag / `/gsd-complete-milestone` ceremony (cosmetic).

## Deferred to v3 (carried forward)

- **AA contrast — inline spans:** ~679 inline `style="color:var(--ink-faint)"` text spans (chart
  axis labels / micro-text, 132 pages) still compute <4.5:1. Per-context judgment (some sit inside
  now-`aria-hidden` decorative charts); not a blind sweep. Candidate Phase 12 / v3.
- Pydantic class-drift closure (22 Elexon `manual_transformer_schema` cases) — needs gridflow work.
- ENTSO-E live-API verification for the 35 entitlement-gated datasets (needs registered key).
- Cross-repo CI (vault + gridflow checkouts) for `gridflow-build` in CI.
