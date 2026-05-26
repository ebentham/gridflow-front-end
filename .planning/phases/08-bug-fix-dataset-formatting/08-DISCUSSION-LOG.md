# Phase 8: Dataset-page formatting bug fix - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in [08-CONTEXT.md](./08-CONTEXT.md) — this log preserves the alternatives considered and the user-signal interpretation.

**Date:** 2026-05-19
**Phase:** 08-bug-fix-dataset-formatting
**Areas discussed:** Fix-scope discipline · Verification breadth · Regression prevention · Diagnosis-approval gate
**Mode:** Default flow, single multiSelect turn, user-condensed response

---

## Input signal

The user invoked `/gsd-discuss-phase 8 . The problem is clear.` with a screenshot of `fuelhh.html` attached. The screenshot showed:
- Top-left: breadcrumb, eyebrow chips, prefix (`fuelhh`), H1 title (`Half-Hourly Generation Outturn by Fuel Type (FUELHH)`) wrapping awkwardly narrow (each word on its own line), lede paragraph, and `verified-against-vendor-docs:` micro-line — all stacked in a narrow ~250-300px column.
- Top-right: large empty rectangle (~600×400px) with no content.
- Mid-right: the 6-cell metadata grid (SILVER PATH / API PATH / FREQUENCY / PUBLICATION LAG / VOLUME / PRIMARY KEY) appearing only on the right side, floating below the empty space.

User signal: "I've already eyeballed the bug; don't make me re-diagnose. Focus on the implementation decisions you need to know to plan."

## Provisional diagnosis (recorded in CONTEXT.md `<specifics>` D-S-01)

From scouting `templates/dataset.html.j2` lines 7-67 + `site/hifi/assets/theme.css`, the hero grid at `dataset.html.j2:18` has two interacting contributors to the visible bug:
1. `align-items: end` anchors the metadata grid to the BOTTOM of the row (the empty top-right rectangle).
2. `grid-template-columns: 1fr auto` + the unwrapped SILVER PATH mono string expand the `auto` column wide, squeezing the `1fr` left column narrow (the title wrapping).

---

## Gray areas presented

The multiSelect AskUserQuestion offered four gray areas:

| Option | Description | Selected |
|--------|-------------|----------|
| Fix-scope discipline | Minimal patch vs hygienic pass | (resolved by user signal — minimal) |
| Verification breadth | fuelhh + 1 random vs cross-vendor + mobile breakpoints | (resolved by user signal — moderate extension within ROADMAP guarantees) |
| Regression prevention | Just fix and ship vs structural guard (lint rule, snapshot test) | (resolved by user signal — no new guard) |
| Diagnosis-approval gate | Spawn researcher to verify diagnosis vs skip research | (resolved by user signal — light research) |

## User's response

The user did not select from the four options. Instead they pasted the ROADMAP Phase 8 goal text verbatim:

> "**Goal**: Root-cause and fix the top-of-page formatting bug confirmed on `fuelhh.html` before scaling 129 new pages off the same template. Whatever the offending location (Jinja2 template / shared `theme.css` / vault `.md` frontmatter / build-script transform), it gets named and corrected in one place; the fix propagates via `gridflow-build` to all 34 existing pages with zero regression on the v1 honesty / a11y / mobile guarantees. This phase is gating for the content phases: shipping 163 pages off a broken template multiplies the defect by 163×. Independent of Phase 7 (Reconciliation) per ADR-0001 D-03 — the bug is in the rendering layer, not the Vault content layer."

## Interpretation

Read as: **"The ROADMAP goal IS the decision basis. Don't bikeshed gray areas — apply sensible defaults anchored to the goal and move on."** Reinforces the original signal from the invocation arg ("The problem is clear."). Combined with the earlier plan-phase choice of `--skip-ui` (also "skip the optional gate"), the user is signalling: maximum velocity, minimum ceremony, lean on the ROADMAP contract.

## Claude's Discretion (defaults applied, all overridable)

For each of the four gray areas, Claude chose the option that best honors the ROADMAP goal + v2 scope discipline (PROJECT.md Key Decisions row 11) + the user's velocity preference:

| Area | Default applied | Rationale | Locked as |
|------|-----------------|-----------|-----------|
| Fix-scope discipline | Minimal patch only — single location, no opportunistic hygiene | ROADMAP says "**one place**"; Phase 8 is a bug-fix not a refactor; PR review surface stays tight | D-01 |
| Verification breadth | fuelhh + 1 random Elexon + ENTSO-E `actual_generation` on desktop, plus fuelhh at ≤720px and ≤480px mobile breakpoints | BUG-02 minimum + 1 ENTSO-E (Phase 9 will scale 48 more from this template) + ROADMAP "zero regression on v1 mobile guarantees" | D-02 |
| Regression prevention | No new structural guard; existing CI (htmlhint + lychee + gridflow-build --check) is the boundary; user-checkpoint is the visual regression boundary | PROJECT.md scope discipline; visual-regression infra is v3 candidate; bug class isn't catchable by existing CI but isn't catchable by adding lint either | D-03 |
| Diagnosis-approval gate | Light research pass — narrow brief to confirm/refute provisional diagnosis at named surfaces | Strong hypothesis from screenshot + template scout, but 1 LLM 1 reading; ~10min researcher catches missed contributing causes; cheap insurance | D-04 |

User can override any of D-01..D-04 by editing `08-CONTEXT.md` before invoking `/gsd-plan-phase 8 --skip-ui`.

## Deferred Ideas

Captured in CONTEXT.md `<deferred>`:

- **Hero-grid CSS extraction to `.dataset-hero` class** — opportunistic refactor, not Phase 8 work. Land during a Phase 9/10 content edit that already touches `theme.css`.
- **Adjacent template inline-style audit** — log similar fragile inline-style blocks as `needs-triage` findings under `.planning/issues/` rather than fixing in Phase 8.
- **Visual-regression infrastructure** — v3 candidate; requires Node toolchain (PROJECT.md anti-goal) which v3 conversation must justify.
- **Per-vendor longest-silver-path audit + max-width discipline** — surface in Phase 9 if ENTSO-E surfaces a similar auto-column expansion bug.

---

*Discussion log: 2026-05-19. Single-turn condensed flow per user signal. No checkpoint file produced (no multi-area drill-down was needed).*
