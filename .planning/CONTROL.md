# CONTROL.md — Main Claude Orchestrator Brief

**Purpose:** This file is the cold-start brief for the "main Claude" session. Read this first. It captures the meta-layer — workflow routing, open decisions, and the *why* behind recent choices — that lives above `STATE.md` / `ROADMAP.md`. Keep both files open; CONTROL is the orientation, STATE is the ground truth.

**Update after every significant decision or phase transition.** When a session ends, the last thing the main Claude does is update this file. When a new session starts, this is the first file it reads.

---

## What you are reading this for

You are the main Claude for the gridflow-front-end project. Your role:

- Answer high-level questions about the project, workflow, and direction
- Generate prompts and handoffs for fresh subagents (GSD skills, Pocock skills)
- Point subagents at the right files so they cold-start correctly
- Make orchestration decisions (which skill, which phase, which vendor to tackle next)
- Update durable planning files after each significant decision

You do **not** implement code directly. When implementation is needed, you dispatch it via the appropriate skill.

---

## Current State (as of 2026-05-19)

**Milestone:** v2 full-vendor-coverage  
**Phase:** 8B — Claude-Design hero rewrite (hybrid authored/templated)  
**Status:** Ready to plan — next action is `/gsd-plan-phase 8B`

**Phase history (quick):**
- Phases 0–6 (v1 cleanup): Complete 2026-05-18 · 50/50 REQ-IDs delivered
- Phase 7 (Reconciliation): Complete 2026-05-19 · 5/31 v2 REQ-IDs delivered
- Phase 8 (CSS bug fix): **Closed/superseded** 2026-05-19 — two iterations failed user visual verification; root cause was an editorial-content gap in the Vault (no short tagline field), not a rendering-layer bug
- Phase 8B (Claude-Design hybrid): **Ready to plan** ← you are here
- Phase 9 (ENTSO-E full): Not started · blocked on 8B
- Phase 10 (four-vendor batch): Not started · blocked on 8B + 9

**Dependency graph:**
```
Phase 7 (done) ──┐
Phase 8 (closed) ┤
                 └── Phase 8B (plan next)
                            │
                            └── Phase 9 (ENTSO-E)
                                       │
                                       └── Phase 10 (four-vendor batch)
```

---

## Skill Routing Guide

### When to use GSD skills

Pre-planned, bounded implementation work. Use for Phases 8B, 9, 10 and any phase with a known scope upfront.

```
/gsd-discuss-phase <n>   — clarify scope before planning
/gsd-plan-phase <n>      — decompose into PLAN.md tasks
/gsd-execute-phase <n>   — run tasks with atomic commits
/gsd-manager             — dashboard: shows D/P/E status per phase, dispatches subagents
                           NOTE: /gsd-manager is a workflow dashboard, NOT a conversational
                           orchestrator. It doesn't generate handoffs or remember why
                           decisions were made — that's this file's job.
```

### When to use Pocock skills

Exploratory work where the findings are unknown upfront (e.g. drift audits, backlog capture from a messy domain). Phase 7 used these for the triage work.

```
/grill-with-docs         — Socratic interview to flush out design decisions before
                           committing scope. Produces decisions + ADRs + handoff docs.
                           Use BEFORE /gsd-discuss-phase when the scope itself is unclear.
/to-issues               — Convert raw findings/notes into structured issue files under
                           .planning/reconciliation/<vendor>/ or .planning/issues/<feature>/
/triage                  — Apply triage labels (needs-triage → needs-info / open / wontfix)
                           to issue files in .planning/
```

### Workflow pattern (the intended loop)

```
Unclear scope → /grill-with-docs → decisions + ADRs + handoff doc
                                          ↓
                              /gsd-discuss-phase <n>   (resolve open items)
                                          ↓
                                /gsd-plan-phase <n>    (decompose into tasks)
                                          ↓
                               /gsd-execute-phase <n>  (implement with commits)
                                          ↓
                                /gsd-verify-phase <n>  (acceptance check)
                                          ↓
                              Update CONTROL.md → next phase
```

---

## Issue Tracking Convention

Issues live as **local markdown files** — not GitHub Issues.

- General issues: `.planning/issues/<feature-slug>/<NN>-<slug>.md`
- Drift findings: `.planning/reconciliation/<vendor>/<NN>-<slug>.md`

Each file carries YAML frontmatter with `status:` field. Canonical status values:
`needs-triage` | `needs-info` | `ready-for-agent` | `ready-for-human` | `wontfix`

See `docs/agents/issue-tracker.md` for the full format. See `docs/agents/triage-labels.md` for label semantics.

---

## Decisions Locked — Do Not Re-Litigate

These were settled via grilling or execution and recorded in ADRs / STATE.md. Treat as immovable.

| Decision | Source |
|---|---|
| Vault is **derivative** — fix lands in Vault, never overrides Canonical | CONTEXT.md, grill 2026-05-19 |
| Reconciliation fixes Vault to match Canonical (one-way, not two-way sync) | CONTEXT.md |
| Phase 7 (all-vendor Reconciliation) runs upfront, not interleaved per-Vendor | ADR-0001 |
| `gridflow-build --check` is idempotence only — NOT a content-accuracy check | ADR-0001 context |
| Vault on **private** GitHub repo `EBentham/quant-vault`, no GitHub App auth | ADR-0002 |
| Vendored snapshot pattern preserved (`vault/<vendor>/` in this repo) | ADR-0002 |
| Reconciliation findings live in `.planning/reconciliation/`, not GitHub Issues | issue-tracker.md |
| Pocock skills for exploratory Phase 7 work; GSD for pre-planned phases 8B/9/10 | grill 2026-05-19 |
| 22 Elexon `manual_transformer_schema` cases → `wontfix/v3-candidate` (need gridflow repo work) | Phase 7 execution |
| ENTSO-E 33 HTTP 401 cases → `needs-info/defer-entitlement` — deferred to Phase 9 discuss | Phase 7 execution + 07-CONTEXT.md D-06 |
| Phase 8 root cause = editorial-content gap in Vault, not a rendering-layer bug | Phase 8 retrospective, 08-01-SUMMARY.md |
| Phase 8B: hybrid model — hand-authored `authored-pages/<vendor>/<slug>.html` overrides; long tail stays templated | ROADMAP.md Phase 8B |

---

## Open Items (require user decision before action)

### 1. ENTSO-E entitlement path (deferred to Phase 9 discuss)

35 ENTSO-E datasets return HTTP 401. Two options:
- **Extend access**: obtain additional API entitlement (cost: time + money + vendor lead time)
- **Skip-with-warn**: ship the 35 dataset pages with a "requires additional entitlement" caveat

Decision gates Phase 9 content build. **Do not decide now** — it lands in `/gsd-discuss-phase 9`.

### 2. Phase 8B — authored page strategy (decides during Phase 8B plan/execute)

Phase 8B's success criterion 4 requires a documented decision on the long-tail path:
- (a) AI-hand-port remaining pages under `authored-pages/`
- (b) Claude-Design all of them (Option C)
- (c) Leave long tail templated (most likely — showcase pages get authored override, long tail accepts template quality)

This is not a pre-decision — it emerges from trying to port a second showcase page (`system_prices`) in Phase 8B's execution.

---

## Key Files for Cold-Start

A fresh Claude should read in this order:

1. **This file** (`CONTROL.md`) — you're here
2. `STATE.md` — current position, locked decisions, session continuity note
3. `ROADMAP.md` — phase details, success criteria, dependency graph
4. `PROJECT.md` — project context, requirements, constraints, core value
5. `CONTEXT.md` — domain glossary (Canonical / Vault / Drift / Reconciliation / etc.)
6. `docs/adr/0001-*.md` + `docs/adr/0002-*.md` — why Phase 7 was added, why vault is on private GitHub

For Phase 7 context (history only — Phase 7 is complete):
- `.planning/V2-PHASE-7-HANDOFF.md` — full handoff brief including load-bearing drift findings
- `.planning/phases/07-reconciliation/07-CONTEXT.md` — all 19 decisions from Phase 7 execution

For Phase 8 context (history only — Phase 8 is closed):
- `.planning/phases/08-bug-fix-dataset-formatting/08-01-SUMMARY.md` — retrospective on why two CSS iterations failed

For generating a Phase 8B plan prompt, point the planner at:
- `ROADMAP.md § Phase 8B` — goal, success criteria, dependency on Phase 8 outcome
- `STATE.md § Session Continuity` — dirty-tree preconditions from Phase 8
- `.planning/phases/08-bug-fix-dataset-formatting/08-01-SUMMARY.md` — Iteration 2 template changes that carry forward

---

## Cross-Repo Paths (Windows local)

- **This repo:** `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\`
- **Vault (upstream):** `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\`
- **Vault (on GitHub):** `github.com/EBentham/quant-vault` (private, no App auth)
- **Gridflow repo:** `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\`

---

## Domain Terminology Quick Reference

| Term | Meaning |
|---|---|
| **Canonical** | gridflow repo code (schemas, silver transforms, connectors) — the SoT |
| **Vault** | Obsidian knowledge base — derivative documentation, never overrides Canonical |
| **Drift** | State where Vault disagrees with Canonical. Reconciliation fixes it |
| **Verification** | Running `gridflow-drift-check` to produce a drift report |
| **Reconciliation** | Fixing Drift by editing the Vault to match the Canonical |
| **Vendored snapshot** | `vault/<vendor>/` in this repo — what the build script actually reads |
| **Live API** | What the vendor API actually returns; sits between Canonical and Vault in trust chain |

Trust chain: **Live API → Canonical → Vault → Site**. Vendor docs are authoring input only — not in the trust chain.

---

*Last updated: 2026-05-19 — Written after grill-with-docs session that produced ADR-0001, ADR-0002, CONTEXT.md, issue-tracker.md, and V2-PHASE-7-HANDOFF.md. Phase 7 complete, Phase 8 superseded, Phase 8B next. `/gsd-manager` confirmed as workflow dashboard (NOT conversational orchestrator — this file fills that role).*
