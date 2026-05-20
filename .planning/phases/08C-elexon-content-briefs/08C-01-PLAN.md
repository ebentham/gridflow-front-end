---
plan_id: 08C-01
phase: 08C
title: Triangulated content briefs for 33 Elexon datasets
status: ready_to_execute
autonomous: true
executor_model: opus
wave: 1
estimated_duration_hours: 5-8
expected_commits: 33-35
requirements:
  - BUG-01
  - BUG-02
  - BUG-03
depends_on: []
recipe: 08C-BRIEF-RECIPE.md
context: 08C-CONTEXT.md
references:
  - authored-pages/elexon/fuelhh.html
  - authored-pages/elexon/system_prices.html
  - gridflow:/src/gridflow/schemas/elexon.py
  - gridflow:/src/gridflow/silver/elexon/*.py
  - gridflow:/src/gridflow/connectors/elexon/endpoints.py
---

# Phase 8C / Plan 08C-01 — Content briefs for 33 Elexon datasets

## Goal

After this plan executes, `content-briefs/elexon/` contains 33 markdown files, one per Elexon dataset, each a self-contained brief ready for the user to paste into Claude Design alongside the visual reference (fuelhh.html / system_prices.html). Each brief triangulates three sources (vault + gridflow code + vendor docs), cites sources per claim, and surfaces discrepancies between sources in its frontmatter for downstream triage.

This plan is **fully autonomous**. Single background opus-4.7 agent. Sequential per-dataset (alphabetical). Per-brief structural checks before commit. Failures logged to `BRIEF-LOG.md`, not raised.

## Task list (35 tasks, sequential, single opus agent)

### Task 1: Pre-flight + dependency check

1. `git branch --show-current` → must be `docs/v2-milestone-start`
2. `git log --oneline -5 | head -1` → must include `1c6aab5` or later (Phase 8B closure landed)
3. `ls .planning/archive/08B-ai-ports/elexon/*.html | wc -l` → must be 31 (AI-ports archived per user direction 2026-05-20)
4. `ls authored-pages/elexon/*.html | wc -l` → must be 2 (fuelhh, system_prices remain)
5. Gridflow cross-repo accessible: `ls /c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/elexon.py` must succeed
6. Read `08C-CONTEXT.md` and `08C-BRIEF-RECIPE.md` in full
7. Read both reference outputs in full: `authored-pages/elexon/fuelhh.html`, `authored-pages/elexon/system_prices.html` (for voice/structure cues)
8. Create `content-briefs/elexon/` directory if absent
9. Create `.planning/phases/08C-elexon-content-briefs/BRIEF-LOG.md` (empty failure log)

If any pre-flight step fails: write to BRIEF-LOG.md and STOP. Otherwise proceed to Task 2.

### Tasks 2–34: Produce 33 content briefs (alphabetical)

Order: `agpt, agws, atl, bmunits_reference, boal, disbsad, fou2t14d, freq, fuelhh, fuelinst, imbalngc, inddem, indgen, indo, indod, itsdo, lolpdrm, market_depth, melngc, mid, ndf, ndfd, netbsad, nonbm, pn, remit, soso, system_prices, temp, tsdf, tsdfd, uou2t14d, windfor`

**Note**: Briefs for `fuelhh` and `system_prices` ARE produced (33 total, not 31). The existing Claude-Design output for fuelhh and the verified AI-port for system_prices become validation targets for the brief format — does the brief, in retrospect, contain everything Claude Design needed to produce the existing page?

For each dataset:

1. **Read vault file**: `vault/elexon/<slug>.md` in full
2. **Read gridflow Pydantic schema**:
   - `Grep` the schemas file for `class Elexon<Slug>`. If not found, try lower-case stem variants. If still not found, note in frontmatter as `pydantic_schema: absent (reason: ...)`.
   - Capture the class definition, all fields with their types/validators, and the file:line range
3. **Read gridflow silver transformer**:
   - `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/silver/elexon/<slug>.py` — read in full
   - Note the transformer class name, dedup_key value, point-in-time field, any non-trivial transformation logic
4. **Read gridflow connector registration**:
   - `Grep` `/c/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/connectors/elexon/endpoints.py` for the slug
   - Capture the canonical path, params, pagination behaviour
5. **Fetch vendor docs**: Use `WebFetch` against the appropriate Elexon BMRS Swagger UI URL (typically `https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/<API_CODE>` — but check vault's API endpoint section for non-`/datasets/` paths). Extract: response shape, any field definitions vendor publishes, rate-limit notes, deprecation notices.
   - If fetch fails (404, JS-only page, network error): note in frontmatter and proceed with vault + gridflow only.
6. **Cross-reference all four sources**: Identify discrepancies (vault says X, gridflow says Y, vendor says Z). Record in frontmatter `discrepancies_found:` with recommendation (per CONTEXT D-03: gridflow > vendor > vault in priority).
7. **Compose the brief** following `08C-BRIEF-RECIPE.md` section-by-section:
   - Editorial layer (tagline + lede + verified line)
   - Hero metadata
   - Stats strip
   - Sidebar siblings
   - Overview (3 paragraphs)
   - Sample chart (type + title + subtitle + seed)
   - Schema (one row per Pydantic field, with file:line citation)
   - Sample data (8 rows with source citations)
   - Dataset-specific section (per recipe decision tree, OR explicitly omitted)
   - API & ingestion (endpoint card + bronze/transformer card + 3 code tabs)
   - Caveats (3-6 with source citations)
   - Related datasets (4 cards)
8. **Write** to `content-briefs/elexon/<slug>.md`
9. **Run 12 structural checks** from `08C-BRIEF-RECIPE.md`
10. **If ALL pass**: `git add content-briefs/elexon/<slug>.md` then commit with the per-brief template:

   ```
   docs(08C): content brief for <slug> · triangulated against vault + gridflow + vendor docs

   <one-paragraph summary>:
   - N schema columns cross-referenced to gridflow schemas/elexon.py
   - M caveats cited (X from vault Known-Issues, Y from gridflow Impl-Delta, Z domain)
   - K discrepancies surfaced for downstream triage [if any]
   - Vendor docs <fetched | unfetchable: reason>
   - Sample data: <test fixture | vault sample | synthesised>

   Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
   ```

11. **If ANY check fails**: append to `.planning/phases/08C-elexon-content-briefs/BRIEF-LOG.md` with slug, failed checks, timestamp, 1-line reason. Do NOT commit. Continue to next dataset.

### Task 35: Phase 8C SUMMARY + cross-reference index

After all 33 briefs are attempted, the executor produces:

1. **`.planning/phases/08C-elexon-content-briefs/08C-01-SUMMARY.md`** with:
   - Outcome: success / partial / failed (success requires ≥30 of 33 briefs committed)
   - Per-dataset table: slug | status (✓ committed / ✗ failed) | brief size (KB) | discrepancy count | commit hash
   - Per-source coverage stats: how many briefs cited vendor docs successfully, how many fell back to vault+gridflow only
   - Aggregate discrepancy report: types of discrepancies found (vault drift / gridflow lag / vendor delta), with counts. If >5 of the same type appear, flag for potential Phase 7 mini-reconciliation.
   - Long-tail decision (CONTEXT Q-A): retained answer "produce all 33 including fuelhh + system_prices for format-validation"; record whether the fuelhh/system_prices briefs, read in retrospect, look like they would have produced the existing pages

2. **`.planning/phases/08C-elexon-content-briefs/DISCREPANCY-INDEX.md`** (separate file for user triage):
   - One section per discrepancy
   - Format: source_a vs source_b, recommendation, blast radius (which other datasets in vault might have similar drift?)
   - This file is the user's morning input for Phase 7-style reconciliation work, if needed

3. **Update `.planning/ROADMAP.md`**:
   - Mark Phase 8C as complete with completion date
   - Update progress table

4. **Commit**: `docs(08C): close phase 8C — 33 briefs ready for Claude Design`

## Definition of done

**Required**:
- [ ] At least 30 of 33 content briefs committed to `content-briefs/elexon/<slug>.md`
- [ ] Each committed brief passes all 12 structural checks
- [ ] Every brief has frontmatter with `sources_consulted` (≥3 entries) and explicit `discrepancies_found` (empty list or items)
- [ ] `08C-01-SUMMARY.md` written with per-dataset table + aggregate stats
- [ ] `DISCREPANCY-INDEX.md` written (even if empty — explicitly states no discrepancies found)
- [ ] ROADMAP.md progress-table updated

**Out of scope** (defer to next session if surfaced):
- Authoring HTML pages in Claude Design (user-side work)
- Reconciling discrepancies back into vault (Phase 7-style follow-up)
- Producing briefs for ENTSO-E (49 datasets — Phase 9)
- Producing briefs for ENTSO-G + GIE + NESO + Open-Meteo (81 datasets — Phase 10)

## Autonomy guarantees

- DO NOT use AskUserQuestion under any circumstance
- DO NOT pause between briefs — chain through all 33 in one run
- DO NOT use `git push`
- DO NOT use `--no-verify` on commits
- DO NOT modify `authored-pages/elexon/fuelhh.html` or `authored-pages/elexon/system_prices.html` (reference targets)
- DO NOT touch the archived AI-ports under `.planning/archive/08B-ai-ports/`
- DO NOT touch CLAUDE.md (pre-existing user modification)
- DO NOT fabricate data — if a source is absent, declare it absent in frontmatter
- DO NOT silently resolve discrepancies — every cross-source mismatch goes in `discrepancies_found`
- DO continue execution after any single-brief structural failure
- DO log every blocker to BRIEF-LOG.md
- DO produce SUMMARY + DISCREPANCY-INDEX at the end regardless of outcome
- DO use opus 4.7 reasoning fully — quality > throughput per CONTEXT D-05
