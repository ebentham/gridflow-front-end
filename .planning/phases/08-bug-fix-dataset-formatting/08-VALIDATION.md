---
phase: 8
slug: bug-fix-dataset-formatting
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-19
---

# Phase 8 — Validation Strategy

> Per-phase validation contract. Phase 8 is a bug-fix phase with a rendering-only
> surface; the test pyramid is intentionally lean (D-02 user checkpoint + 3 v1
> CI gates), not a unit/integration framework. No new test infrastructure is
> added per D-03 (no visual-regression baselines — v3 candidate only).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none added — reuse v1 CI gates (htmlhint + lychee + gridflow-build --check) |
| **Config file** | `.htmlhintrc` (root) |
| **Quick run command** | `gridflow-build --check` (~3s) |
| **Full suite command** | `gridflow-build --check && htmlhint --config .htmlhintrc 'site/hifi/**/*.html' && lychee --offline --include-fragments site/hifi/**/*.html` |
| **Estimated runtime** | ~20-40 seconds (lychee dominates) |

---

## Sampling Rate

- **After every task commit:** Run `gridflow-build --check` (idempotence guard)
- **After every plan wave:** Only one wave; full suite at end of plan instead
- **Before `/gsd-verify-work`:** Full suite must be green AND user checkpoint signed off
- **Max feedback latency:** ~40 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 8-01-01 | 01 | 1 | BUG-01 | — | N/A (visual layout, no security surface) | manual | confirm root cause cited in commit message | n/a | ⬜ pending |
| 8-01-02 | 01 | 1 | BUG-01, BUG-02 | — | N/A | structural | `gridflow-build --check && grep -F 'align-items: start' site/hifi/data-sources/elexon/fuelhh.html` | n/a | ⬜ pending |
| 8-01-03 | 01 | 1 | BUG-02 | — | N/A | manual (user-verified) | open 3 pages × 1 desktop + 2 mobile breakpoints, user signs off | n/a | ⬜ pending |
| 8-01-04 | 01 | 1 | BUG-03 | — | N/A | automated | `gridflow-build --check && htmlhint --config .htmlhintrc 'site/hifi/**/*.html' && lychee --offline --include-fragments site/hifi/**/*.html` | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

(Phase 6 — v1 CI validation — already shipped `.htmlhintrc`, `htmlhint`,
`lychee`, and `gridflow-build --check` in `.github/workflows/deploy.yml`. No
new tests, no new tooling, no new config files for Phase 8.)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Hero block visually correct on `fuelhh.html` at desktop | BUG-02 | CSS layout glitch — no automated visual regression in v2 (D-03) | Open `site/hifi/data-sources/elexon/fuelhh.html` in a browser at ≥1280px viewport; confirm no tall empty rectangle in the top-right; confirm 6 metadata cells are visible and readable; confirm H1 wraps reasonably; confirm "Illustrative snapshot" chip stays in the left column top row alongside the eyebrow and frequency chip; confirm `verified-against-vendor-docs:` micro-line stays at the bottom of the left column |
| Hero block visually correct on 1 random Elexon page at desktop | BUG-02 | Spot-check per D-02 (extends BUG-02 acceptance to broader Elexon set) | Pick any one of `site/hifi/data-sources/elexon/*.html` (suggestion: `system_prices.html` or `boal.html` for varying silver-path length); open at ≥1280px; confirm hero render matches the visual contract above |
| Hero block visually correct on ENTSO-E `actual_generation.html` at desktop | BUG-02 (D-02 extension) | Cross-vendor sanity for Phase 9 scale-out — ENTSO-E silver-path shape differs from Elexon | Open `site/hifi/data-sources/entsoe/actual_generation.html` at ≥1280px; confirm hero render matches the visual contract above |
| Hero block stacks correctly on mobile (≤720px) | BUG-02 (D-02 mobile guarantee) | v1 Phase 5 mobile CSS regression check | Open `site/hifi/data-sources/elexon/fuelhh.html` in browser devtools, set viewport to 720px width; confirm hero stacks single-column; confirm metadata grid visible below text; confirm no horizontal scroll |
| Hero block stacks correctly on mobile (≤480px) | BUG-02 (D-02 mobile guarantee) | v1 Phase 5 mobile CSS regression check | Same page, resize viewport to 480px width; confirm hero stacks single-column; confirm 6 metadata cells stack 1-column (per theme.css line 977-979 ≤480px rule); confirm no horizontal scroll |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies — covered (existing CI gates)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify — covered (tasks 2 and 4 are automated; task 3 user-checkpoint is the explicit D-02 manual sign-off)
- [ ] Wave 0 covers all MISSING references — n/a (no new tests required)
- [ ] No watch-mode flags — confirmed (`gridflow-build --check`, `htmlhint`, `lychee` are all one-shot)
- [ ] Feedback latency < 60s — confirmed (~40s full suite)
- [ ] `nyquist_compliant: true` set in frontmatter — yes

**Approval:** pending — user signs off via the D-02 checkpoint embedded as
task 8-01-03 in `08-01-PLAN.md`.
