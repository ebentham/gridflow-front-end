# Research Brief: Drift Detection Across gridflow Code · Vault · Site

**Created:** 2026-05-17 (executes 2026-05-18+)
**Type:** Deep research, autonomous (no human input mid-run)
**Audience:** Fresh Claude Code instance with zero prior context
**Estimated depth:** Multi-hour, exhaustive, prefer too much detail over too little

---

## Mission

Produce a complete research package that v2 plan-phase can consume to design a CI-based drift detection system for the gridflow ecosystem (3 repos). This research is preparation work — **NOTHING is implemented**, only researched and documented. Output is 5 markdown files matching the existing `.planning/research/` pattern.

---

## Context (read this entire section before starting)

### What gridflow is

`gridflow` is a multi-repo ETL pipeline for UK/EU energy market data:

- **`gridflow` (main code repo)** — Python ETL: bronze → silver → gold layers, Pydantic schemas, connectors to vendor APIs (Elexon BMRS, ENTSO-E, ENTSO-G, GIE, Open-Meteo, NESO). **This is the canonical source of truth.**
- **`quant-vault` (Obsidian knowledge base)** — Authored markdown documentation per vendor/dataset. Derived from gridflow code + verified against live API responses. Contains `verify_curl_and_silver_schema.py` (the canonical drift-detection script that ALREADY EXISTS but doesn't run in CI).
- **`gridflow-front-end` (this repo, where this brief lives)** — Public-facing static site documenting the above. Currently shipping v1 cleanup milestone. Post-Phase-3 will read vault content via Jinja2 build → HTML.

### Cross-repo paths (Windows local — all three are accessible to you)

- Vault: `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\`
- Gridflow main repo: `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\`
- This repo: `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end\` (you are here)

### Source-of-truth hierarchy (LOCKED — do not relitigate)

1. **gridflow code** (`<gridflow>/src/gridflow/schemas/*.py`, `silver/**/*.py`, `connectors/**/*.py`) — canonical
2. **Live API responses** (verified by `verify_curl_and_silver_schema.py` in the vault)
3. **Obsidian Vault** (`<vault>/30-vendors/<vendor>/datasets/*.md`) — authored docs derived from #1+#2; **33 active Elexon datasets**
4. **On-site rendered pages** (`site/hifi/data-sources/<vendor>/<dataset>.html`) — published view generated from #3 via the build script (Phase 3 of v1, not yet built)

### Why this research exists now

The v1 milestone (`.planning/ROADMAP.md`) ships a build mechanism that reads vault → renders site. Phase 3 SC#4 bakes in a **one-time** verification snapshot per dataset (a `verified-against-vendor-docs: YYYY-MM-DD` micro-line + Pydantic class reference). But **ongoing drift detection is explicitly deferred to post-v1** — see `.planning/STATE.md:53` row in "Open Decisions Deferred to Plan-Phase": *"Per-dataset content verification cadence in CI vs manual"* → *"Out-of-scope for v1 milestone (machinery only; cadence is post-v1 discipline)."*

This research front-loads the thinking so when v2 (drift harmonization milestone) kicks off, plan-phase has a complete research package ready — exactly like v1 had `STACK.md` / `FEATURES.md` / `ARCHITECTURE.md` / `PITFALLS.md` / `SUMMARY.md` ready before its plan-phase ran.

### What's already decided (do not relitigate)

| # | Decision | Source |
|---|----------|--------|
| 1 | Code is canonical; vault derives from code; site derives from vault | CLAUDE.md SoT hierarchy |
| 2 | Templating mechanism: Python + Jinja2 + `gridflow-build` CLI | v1 Decision #1 (`.planning/PROJECT.md`) |
| 3 | Vault → site direction (vault is authored, site is rendered) | v1 Decision #3 |
| 4 | The `verify_curl_and_silver_schema.py` script in the vault is the canonical drift detector — do not propose replacing it; propose how to integrate it into CI | Established fact (script exists at `<vault>/30-vendors/scripts/verify_curl_and_silver_schema.py`) |
| 5 | CI will need cross-repo checkout (already needed for `gridflow-build` per v1 deferred decision about `GRIDFLOW_VAULT_PATH`) | `.planning/STATE.md:51` |
| 6 | Anti-goal: no fake-live framing; this is documentation not SaaS — drift checker must align with that ethos (fail-loud over warn-only where credibility is at stake) | CLAUDE.md "Anti-goals" |

---

## Reading list (must read before spawning any research subagents)

You MUST read each of these in full before beginning research. They establish the context the research must respect:

### This repo (`.planning/`)
1. `.planning/PROJECT.md` — full project context, core value, SoT hierarchy, key decisions
2. `.planning/REQUIREMENTS.md` — 50 REQ-IDs (note BUILD / VAULT / ELX / VEND categories; understand what v1 ships vs what's deferred)
3. `.planning/ROADMAP.md` — 7 phases, Phase 3 = build mechanism, Phase 6 = CI validation
4. `.planning/STATE.md` — current state; especially "Open Decisions Deferred to Plan-Phase" table
5. `.planning/research/SUMMARY.md` — v1 research synthesis (pattern to match for your output)
6. `.planning/research/PITFALLS.md` — v1 pitfalls (some apply to drift detection too)
7. `CLAUDE.md` — working agreements, SoT hierarchy, anti-goals

### Cross-repo
8. `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\CLAUDE.md` — vault-side working agreements
9. `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\30-vendors\scripts\verify_curl_and_silver_schema.py` — READ THIS IN FULL; it's the canonical drift detector that must be integrated into CI
10. `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\30-vendors\vault-curl-schema-validation.md` — companion document explaining what the validation script does and what it has found
11. `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\30-vendors\vault-amendment-plan.md` — vault-side planning context
12. `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\CLAUDE.md` — gridflow-side working agreements
13. `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\src\gridflow\schemas\` — all Pydantic schema files (audit them, note count, note patterns)
14. `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\src\gridflow\connectors\` — connector pattern (one per vendor)
15. `C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow\.github\workflows\` — existing CI patterns to extend

### One example vault dataset (to understand vault → site mapping)
16. List the contents of `C:\Users\Bobbo\OneDrive\Desktop\Learning\AI\quant-vault\30-vendors\elexon\datasets\` and read 2-3 representative `.md` files (e.g., `fuelhh.md` if present) to understand the vault frontmatter contract

---

## Deliverables (exactly 5 files, fixed paths)

Create all five at these exact paths:

```
.planning/research/post-v1/drift-detection/
├── DRIFT-SURFACES.md
├── TOOLING-AUDIT.md
├── INDUSTRY-PATTERNS.md
├── CI-ARCHITECTURE.md
└── SUMMARY.md          (synthesizes the other four — write LAST)
```

### File 1 — `DRIFT-SURFACES.md`

**Question:** What can go out of sync, between which artefacts, with what consequences?

**Required sections:**
- **Inventory of artefacts** — every source of truth in the ecosystem (gridflow Pydantic schemas, gridflow silver-layer transforms, vault `.md` frontmatter, vault prose, vault `verify_curl_and_silver_schema.py` outputs, generated site HTML, live API responses)
- **Drift edges** — for every pair of artefacts that could drift, document: detection difficulty (trivial / moderate / hard), blast radius (cosmetic / misleading / dangerous), example failure mode. Tabular format.
- **Drift taxonomy** — categorize drifts as: structural (schema shape changed), semantic (field meaning changed), referential (cross-references like Pydantic class names became stale), temporal (verification timestamp expired), volumetric (dataset count drifted across surfaces — already-witnessed v1 problem)
- **Existing in-tree examples** — find at least 3 real drifts that exist TODAY (e.g., the 22/25/28 dataset count discrepancy from v1 research). Cite file + line.
- **Worst-case drift scenario** — narrative paragraph: walk through what happens if (a) gridflow renames a Pydantic field, (b) vault doesn't update, (c) site rebuilds. Who notices when?

### File 2 — `TOOLING-AUDIT.md`

**Question:** What already exists, what are its gaps, and what new tooling would be needed?

**Required sections:**
- **`verify_curl_and_silver_schema.py` deep audit** — read it line-by-line. Document: inputs, outputs, what it validates, what it doesn't validate, its coverage across the 33 Elexon datasets, its output format (markdown? JSON?), how it's currently invoked, any external dependencies (API keys, network, secrets).
- **Other in-tree drift adjacent tooling** — search `gridflow/` for tests, `scripts/`, validation utilities. Document what's there. Search `gridflow-front-end/` and `quant-vault/` for similar.
- **Gap analysis** — concrete table: drift edge (from File 1) × tool that catches it × tool that's missing. The gap rows are the v2 build scope.
- **Reusable pieces** — what existing scripts can be lifted/wrapped vs need rewriting
- **Schema-introspection capabilities of Pydantic** — what `model_json_schema()` gives us (it's built into Pydantic v2; should be leveraged not reimplemented)

### File 3 — `INDUSTRY-PATTERNS.md`

**Question:** How do other projects/teams solve schema and content drift detection? What are the load-bearing patterns and named tools?

**Required sections (web research expected — use WebSearch / WebFetch / mcp__context7 tools):**
- **Schema drift detection patterns** — JSON Schema diffing, Pydantic v2 schema versioning, Buf/Protobuf schema breaking-change detection, OpenAPI diff tooling
- **Contract testing** — Pact, schemathesis, dredd — applicability to this REST-API-consumer use case
- **Data quality / drift frameworks** — Great Expectations, Soda Core, dbt tests, Pandera (Polars equivalent?) — for the silver-layer transform drift case
- **Documentation drift detection** — doc-tests, executable specifications, link checkers, content-freshness audits (e.g., docs.rs warnings, MDN content currency badges, vale linter)
- **CI patterns for cross-repo drift** — monorepo vs polyrepo strategies, scheduled jobs, label-based PR gating, "canary" deploys against vendor APIs
- **Three to five named exemplar projects** — find real open-source projects that do drift detection well. Link to their CI config + the drift checker file. Brief paragraph on what to steal.
- **Anti-patterns** — what to avoid. Especially around "drift detection that becomes flaky CI noise everyone learns to ignore." Cite at least 2 real-world examples.

### File 4 — `CI-ARCHITECTURE.md`

**Question:** What's the proposed end-state CI architecture? What needs deciding when v2 plan-phase runs?

**Required sections:**
- **Proposed architecture diagram** — ASCII or markdown of the data flow: gridflow code → schema export → vault frontmatter check → vault content check → site build → site curl check. Show where the new CI checks fit.
- **Repo placement decision matrix** — should the drift checker live in (a) gridflow main repo, (b) quant-vault, (c) this repo, (d) a new 4th repo? Pros/cons table. Pick a recommendation with rationale.
- **CI trigger taxonomy** — on push to main (which repo?), on PR open, on schedule (daily? hourly?), on manual dispatch. Recommend the trigger set.
- **Secret management** — Elexon BMRS API has no key, ENTSO-E API needs a key (per `.planning/research/`), other vendors TBD. How do these get into CI? GitHub Actions secrets, OIDC, action-level scoping.
- **Cross-repo checkout strategy** — `actions/checkout@v4` supports cross-repo with deploy keys / PATs / GitHub Apps. Pick one with rationale.
- **Failure-mode design** — fail-loud (block deploy) vs warn-only (annotation) vs report-only (artifact upload). Map drift edges → failure mode. Default to fail-loud per Decision #6 above; justify exceptions.
- **Cadence proposal** — per-drift-edge: how often does this need to run? Cost of missed-detection? Cost of false-positive?
- **MVP scope vs full scope** — what's the minimum viable drift checker that v2 ships first? What's the v2.1 expansion?
- **Open questions** — explicit list, each one a question v2 plan-phase will need to answer. Format: `- **Q-DD-NN:** <question> · default lean: <best guess with rationale>`.

### File 5 — `SUMMARY.md` (write LAST — synthesizes the other four)

Match the structure of `.planning/research/SUMMARY.md` exactly:

```
# Drift Detection Research Summary

**Project:** gridflow-front-end (post-v1 preparation)
**Domain:** Cross-repo schema + content drift detection
**Researched:** <date>
**Confidence:** <HIGH / MEDIUM / LOW per section — be honest>

## Executive Summary
<3-5 sentence dense paragraph: load-bearing findings only>

## Key Findings

### Recommended Approach
<2-3 paragraphs: the core architectural recommendation>

### Drift Surface Inventory
<bullet summary of File 1 findings>

### Tooling Reality
<bullet summary of File 2 findings — what exists, what's missing>

### Industry Pattern Adoption
<bullet summary of File 3 — which specific patterns to adopt and which to skip>

### Open Decisions for v2 Plan-Phase
<the Q-DD-NN list from File 4, with default leans>

### Risks
<3-5 risks, mirroring how v1 PITFALLS.md is structured>

## Confidence Calibration
<a table: each finding × confidence level × what would change the verdict>

---
*Research conducted <date>. Inputs: <list the 5 files above + reading list + cross-repo paths>.*
```

---

## Execution plan

You MUST follow this plan; do not improvise the structure.

### Phase 1 — Setup (you, the orchestrator, do this directly)

1. Read every file in the "Reading list" section above. All 16 items. In parallel where possible.
2. Verify all three cross-repo paths are accessible (`ls` each).
3. Create the deliverable folder: `.planning/research/post-v1/drift-detection/`

### Phase 2 — Parallel research (spawn 4 `gsd-project-researcher` subagents in ONE message)

Spawn all 4 in a single message (parallel tool calls). Each agent gets:
- Full context block (copy the "Context" section above)
- The list of files to read (subset of "Reading list" relevant to that agent)
- The deliverable spec (exact section requirements from above)
- Instruction: **DO NOT ask the user questions. DO NOT block on missing information. If something is genuinely undecidable, write it as an open question in the document and continue.**
- Instruction: **Write the file to the exact path specified. Do not deviate.**

The 4 agents:
- **Agent A** → writes `DRIFT-SURFACES.md`
- **Agent B** → writes `TOOLING-AUDIT.md` (this one needs to read `verify_curl_and_silver_schema.py` in full)
- **Agent C** → writes `INDUSTRY-PATTERNS.md` (this one needs WebSearch / WebFetch / context7 access for industry research)
- **Agent D** → writes `CI-ARCHITECTURE.md` (this one reads agents A and B's outputs — see below)

**Wait, dependency note:** Agent D should run AFTER A and B finish (it consumes their outputs). So actually:

**Wave 1 (parallel, single message):** Agents A, B, C
**Wave 2 (after wave 1 completes):** Agent D, then SUMMARY synthesizer

### Phase 3 — Synthesis (spawn `gsd-research-synthesizer`)

Once Agents A-D have written their files, spawn `gsd-research-synthesizer` with:
- Path to all 4 produced files
- The exact SUMMARY.md structure spec from File 5 above
- Instruction: produce SUMMARY.md at `.planning/research/post-v1/drift-detection/SUMMARY.md`

### Phase 4 — Verification (you, the orchestrator)

After all 5 files exist:
1. Verify each file exists at the correct path and is non-empty
2. Verify each file has the required sections (grep for the section headers)
3. Read SUMMARY.md in full — does it accurately reflect the other 4 files? If not, ask the synthesizer to revise.
4. Commit the 5 files as a single commit on the current branch (whatever branch the repo is on; do not create a new branch). Commit message: `docs(post-v1): drift detection research package (5 files)`. Conventional Commits required. **Do not push.** Leave the commit local for the user to review.
5. Print a summary to stdout: file paths created, total word count, key recommendation from SUMMARY.md, any open questions flagged.

### Phase 5 — Termination

After Phase 4 completes, **STOP**. Do not start v2 plan-phase. Do not modify any other planning artifacts. Do not update ROADMAP.md or STATE.md. The output is the 5 files + one commit — nothing else.

---

## Hard constraints

- **NO interactive questions.** Use `AskUserQuestion` zero times. If a decision is unclear, write it as an open question in the deliverable and continue.
- **NO modifications to v1 planning artifacts.** Do not touch `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/REQUIREMENTS.md`, `.planning/PROJECT.md`, any v1 phase folder, or any existing `.planning/research/*.md`. The 5 deliverables go in a NEW folder.
- **NO code changes.** Do not edit anything in `site/`, `src/`, `.github/`, the vault, or the gridflow repo. Read-only across all three repos.
- **NO branch creation.** Stay on whatever branch is checked out. Single commit at the end on the current branch.
- **NO push.** Local commit only.
- **NO scope creep into v2 planning.** This is research, not planning. If you want to write "Phase X should do Y," instead write "v2 plan-phase will need to decide whether to do Y in one phase or split across phases — see Q-DD-NN".
- **Depth over breadth where there's a tradeoff.** The user has explicitly chosen "as deep as possible" — when in doubt, dig further rather than summarize.
- **Cite sources.** Every claim about gridflow / vault / industry pattern needs a file path or URL.
- **Polars not pandas, uv not pip** — per user global preferences in `~/.claude/CLAUDE.md`. If any code snippet appears in deliverables, follow these.

---

## What "done" looks like

When you finish, the state should be:
- `.planning/research/post-v1/drift-detection/` folder exists with exactly 5 markdown files
- All 5 files are non-trivial (DRIFT-SURFACES.md and CI-ARCHITECTURE.md likely 1500+ words each; INDUSTRY-PATTERNS.md 2000+ with web citations; TOOLING-AUDIT.md 1000+; SUMMARY.md ~800-1200)
- Working tree contains exactly one new commit on the current branch
- `git status` shows clean working tree
- No interactive prompts were ever raised
- A stdout summary printed at end showing: file paths, sizes, top recommendation, open questions count

When the user (Bob) returns to this work, they should be able to run `/gsd-new-milestone v2-drift-harmonization` later and the research files will be picked up automatically by the milestone-research stage.

---

*End of brief. Begin Phase 1 immediately upon receiving this prompt.*
