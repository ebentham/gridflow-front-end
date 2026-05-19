---
plan_id: 08B-01
phase: 08B
title: AI-port 31 Elexon datasets + wire build override
status: ready_to_execute
autonomous: true
executor_model: sonnet
wave: 1
estimated_duration_hours: 2.5-4.5
expected_commits: 33-35
requirements:
  - BUG-01
  - BUG-02
  - BUG-03
depends_on: []
recipe: 08B-PORT-RECIPE.md
context: 08B-CONTEXT.md
references:
  - authored-pages/elexon/fuelhh.html
  - authored-pages/elexon/system_prices.html
---

# Phase 8B / Plan 08B-01 — AI-port 31 Elexon datasets + wire build override

## Goal

After this plan executes successfully, **all 33 Elexon dataset pages** under `site/hifi/data-sources/elexon/` will be served from hand-quality HTML under `authored-pages/elexon/<slug>.html`, indistinguishable from the Claude-Design fuelhh reference. The build script (`src/gridflow_front_end/build.py`) will read authored pages first and fall back to the Jinja2 template only when an authored page does not exist — so future CI runs preserve the authored output without clobbering. Phase 9 can build on Phase 8B's pattern unchanged: drop ENTSO-E pages into `authored-pages/entsoe/<slug>.html` and they ship.

This plan is **fully autonomous**. The executor agent reads `08B-PORT-RECIPE.md` for the per-dataset porting recipe, applies the recipe to each of 31 Elexon datasets in alphabetical order, runs structural checks per port, commits atomically per port, and produces a SUMMARY at the end. **No user input is requested at any point during execution.** Failures are logged to `PORT-LOG.md`, the affected port is skipped (not committed), and the agent moves on. The final SUMMARY tallies success / failure counts for triage when the user returns.

## Execution context

- **Branch**: continue on `docs/v2-milestone-start` (current branch as of 2026-05-19 21:50 UTC)
- **Working tree at start**: must have `authored-pages/elexon/system_prices.html` already committed (Task 1's pre-flight check verifies this; if absent, the executor commits it as the first action)
- **Reference outputs to match**: `authored-pages/elexon/fuelhh.html` (Claude-Design) + `authored-pages/elexon/system_prices.html` (AI-port, verified)
- **Vault path**: `vault/elexon/*.md` (33 files; fuelhh + system_prices already done; 31 remaining)
- **Manifest path**: `site/hifi/data/elexon.json` (groups + per-slug freq/lag/rows)
- **Build script**: `src/gridflow_front_end/build.py`

## Task list (33 tasks, sequential, single executor agent)

### Task 1: Wire the build-script override path

**Goal**: Make `gridflow-build` respect `authored-pages/<vendor>/<slug>.html` overrides BEFORE any porting work commits. Once this lands, every authored page survives subsequent CI runs. This task is FIRST because all subsequent ports depend on `site/hifi/data-sources/elexon/<slug>.html` being preserved.

**Pre-flight**:
1. If `authored-pages/elexon/system_prices.html` is uncommitted (check `git status --short`), commit it:
   ```
   git add authored-pages/elexon/system_prices.html
   git commit -m "feat(08B): commit verified second showcase page (system_prices) under authored-pages/" (full message in commit-templates section below)
   ```

**Patch to apply** to `src/gridflow_front_end/build.py`:

Add a module-level constant near the existing `DEFAULT_VAULT` line (around line 51):

```python
AUTHORED_DIR = REPO_ROOT / "authored-pages"
```

Replace the per-dataset write loop inside `build_vendor` (currently lines 761–767):

```python
# BEFORE
n_pages = 0
for _path, doc in docs:
    html = render_dataset(env, doc, manifest)
    out_path = out_dataset_dir / f"{doc.slug}.html"
    out_path.write_text(html, encoding="utf-8")
    n_pages += 1
    print(f"  wrote: data-sources/{vendor_id}/{doc.slug}.html")

# AFTER
n_pages = 0
for _path, doc in docs:
    out_path = out_dataset_dir / f"{doc.slug}.html"
    authored = AUTHORED_DIR / vendor_id / f"{doc.slug}.html"
    if authored.exists():
        shutil.copy(authored, out_path)
        print(f"  wrote: data-sources/{vendor_id}/{doc.slug}.html (authored)")
    else:
        html = render_dataset(env, doc, manifest)
        out_path.write_text(html, encoding="utf-8")
        print(f"  wrote: data-sources/{vendor_id}/{doc.slug}.html")
    n_pages += 1
```

**Verification**:
1. Run `python -c "from gridflow_front_end.build import main; main()"` (with `PYTHONPATH=src`). It must succeed and print `(authored)` next to `fuelhh.html` and `system_prices.html`.
2. Run a second time (idempotence check). Output should be byte-identical.
3. Diff the regenerated `site/hifi/data-sources/elexon/fuelhh.html` against `authored-pages/elexon/fuelhh.html` — must be byte-equal.
4. Diff the regenerated `site/hifi/data-sources/elexon/system_prices.html` against `authored-pages/elexon/system_prices.html` — must be byte-equal.

**Commit**: `feat(08B): wire authored-pages override path in build.py`

```
feat(08B): wire authored-pages override path in build.py

Add AUTHORED_DIR = REPO_ROOT / "authored-pages" and check for
authored-pages/<vendor>/<slug>.html in build_vendor before invoking
the Jinja2 template. If present, copy the authored file to the output
path; if absent, fall through to the existing template render. Vault
manifest discoverability invariant is preserved — authored pages
still need a vault entry (the existing manifest_slugs check stays).

Two authored pages already exist under authored-pages/elexon/ (fuelhh,
system_prices). Both now survive CI builds. Subsequent tasks port the
remaining 31 Elexon datasets to authored-pages/, after which the full
33-dataset Elexon catalog is hand-quality.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

---

### Tasks 2–32: Port 31 Elexon datasets (one task per slug, alphabetical order)

For each dataset listed below, apply `08B-PORT-RECIPE.md` and produce `authored-pages/elexon/<slug>.html`. Order matters: process **alphabetically** so a mid-execution failure leaves a clear partial state.

The per-task structure is identical for every dataset:

1. Read `vault/elexon/<slug>.md` in full
2. Read `site/hifi/data/elexon.json` if not already cached; find the group + manifest entry for `<slug>`
3. Open `authored-pages/elexon/system_prices.html` as the structural template (the closer reference of the two)
4. Apply the recipe (08B-PORT-RECIPE.md) section by section, generating the new HTML
5. Write to `authored-pages/elexon/<slug>.html`
6. Copy to `site/hifi/data-sources/elexon/<slug>.html`
7. Run the 12 structural checks (see RECIPE § Structural checks)
8. If ALL checks pass: `git add authored-pages/elexon/<slug>.html site/hifi/data-sources/elexon/<slug>.html` then `git commit -m "feat(08B): port <slug> to authored-pages/"` (full commit message template below)
9. If ANY check fails: append failure record to `.planning/phases/08B-claude-design-hero-rewrite/PORT-LOG.md`, do NOT commit, move to next dataset

**Dataset list (alphabetical, 31 entries):**

| # | Slug | Group | Chart helper | Third section | Sibling siblings (sidebar) | Related cards (4) |
|---|---|---|---|---|---|---|
| T02 | agpt | Generation | barsH | PSR-type pill grid | fuelhh, fuelinst, agws, windfor | fuelhh, agws, windfor, fuelinst |
| T03 | agws | Generation | barsH | wind/solar split pill grid | fuelhh, fuelinst, agpt, windfor | agpt, fuelhh, windfor, fuelinst |
| T04 | atl | Settlement | sparkline | settlement-runs (II→DF) | system_prices, netbsad, boal, disbsad | boal, netbsad, disbsad, system_prices |
| T05 | bmunits_reference | Reference | barsH | BM-unit category pill grid | (any 5 BMU-adjacent) | boal, pn, atl, soso |
| T06 | boal | Settlement | sparkline | settlement-runs | netbsad, disbsad, system_prices, atl | netbsad, disbsad, system_prices, atl |
| T07 | disbsad | Settlement | sparkline | settlement-runs | netbsad, boal, system_prices, atl | netbsad, boal, system_prices, atl |
| T08 | fou2t14d | Operational | sparkline | (skip — long-horizon ops feed) | uou2t14d, melngc, lolpdrm, ndfd | uou2t14d, ndf, ndfd, lolpdrm |
| T09 | freq | System | sparkline | (skip — single time series) | temp, fuelinst, system_prices, indo | fuelinst, system_prices, indo, temp |
| T10 | fuelinst | Generation | stackedArea | fuel-type pill grid (16 codes — mirror fuelhh's grid) | fuelhh, agpt, agws, windfor | fuelhh, agpt, agws, freq |
| T11 | imbalngc | Demand | sparkline | (skip — single value series) | melngc, ndf, ndfd, tsdf | melngc, ndf, system_prices, netbsad |
| T12 | inddem | Demand | sparkline | (skip) | indo, indod, indgen, melngc | indo, indod, ndf, ndfd |
| T13 | indgen | Generation/Demand | sparkline | (skip) | inddem, indo, indod, melngc | inddem, indo, fuelhh, fuelinst |
| T14 | indo | Demand | sparkline | (skip — canonical demand outturn) | itsdo, inddem, indod, ndf | itsdo, inddem, ndf, ndfd |
| T15 | indod | Demand | sparkline | (skip) | indo, inddem, indgen, itsdo | indo, inddem, indgen, itsdo |
| T16 | itsdo | Demand | sparkline | (skip — TSD outturn) | indo, tsdf, tsdfd, inddem | indo, tsdf, tsdfd, ndf |
| T17 | lolpdrm | Operational | sparkline | (skip) | melngc, uou2t14d, fou2t14d, ndfd | melngc, ndf, fou2t14d, uou2t14d |
| T18 | market_depth | Operational | barsH | (depends — read vault first; if it has buy/sell ladders, use price-ladder treatment) | system_prices, netbsad, disbsad, boal | netbsad, system_prices, disbsad, mid |
| T19 | melngc | Demand/Margin | sparkline | (skip) | imbalngc, lolpdrm, ndf, ndfd | imbalngc, lolpdrm, ndf, fou2t14d |
| T20 | mid | Prices | priceLadder | settlement-runs (if applicable) | system_prices, netbsad, disbsad, boal | system_prices, netbsad, disbsad, atl |
| T21 | ndf | Demand | sparkline | (skip) | ndfd, tsdf, tsdfd, indo | ndfd, tsdf, indo, itsdo |
| T22 | ndfd | Demand | sparkline | (skip — day-ahead detail) | ndf, tsdf, tsdfd, indo | ndf, tsdf, tsdfd, indo |
| T23 | netbsad | Settlement | sparkline | settlement-runs | disbsad, boal, system_prices, atl | system_prices, disbsad, boal, atl |
| T24 | nonbm | Notifications | (omit chart, just use a section with table or empty placeholder) | (skip — notification feed) | pn, remit, soso, atl | pn, remit, soso, system_prices |
| T25 | pn | Notifications | sparkline (or omit) | (skip) | nonbm, remit, soso, bmunits_reference | nonbm, remit, bmunits_reference, soso |
| T26 | remit | Notifications | (omit chart) | (skip — REMIT publications feed) | pn, nonbm, soso, bmunits_reference | pn, nonbm, soso, system_prices |
| T27 | soso | Settlement | sparkline | settlement-runs (if applicable) | netbsad, disbsad, boal, system_prices | netbsad, system_prices, disbsad, mid |
| T28 | temp | System | sparkline | (skip — weather series) | freq, fuelinst, indo, ndf | freq, indo, ndf, fuelinst |
| T29 | tsdf | Demand | sparkline | (skip — TSD forecast) | tsdfd, ndf, ndfd, itsdo | tsdfd, ndf, itsdo, indo |
| T30 | tsdfd | Demand | sparkline | (skip) | tsdf, ndf, ndfd, itsdo | tsdf, ndf, ndfd, itsdo |
| T31 | uou2t14d | Operational | sparkline | (skip) | fou2t14d, melngc, lolpdrm, ndfd | fou2t14d, melngc, ndf, ndfd |
| T32 | windfor | Generation | sparkline | (skip — single forecast series) | fuelhh, agpt, agws, fuelinst | fuelhh, agws, agpt, fuelinst |

**Notes on the table**:
- "Chart helper" is a recommendation; if the vault reveals a more apt shape, the executor MAY override (e.g., if `market_depth` turns out to be a price-ladder, use `priceLadder` not `barsH`)
- "Third section" "(skip)" means: drop that section AND its sidebar anchor; sidebar goes from 8 to 7 anchors
- Sibling sidebar list and Related cards are starting points; the executor MAY substitute if a better semantic neighbour exists in the vault
- For `bmunits_reference`: the sample-data section may be a different shape (one row per BMU type, not one per settlement period). The executor adapts pragmatically; structural checks still apply

**Commit message template** (apply to every successful port):

```
feat(08B): port <slug> to authored-pages/

AI-hand-port of vault/elexon/<slug>.md into the Claude-Design hero
pattern (matching authored-pages/elexon/fuelhh.html and system_prices.html).
Vault content sources: <list specific sections used, e.g. "Overview, Silver
schema, Known issues">. Chart helper: <chart-type>. Structural checks
(12/12) passed.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

**On structural-check failure**: append to `PORT-LOG.md` with the slug, list of failed checks, and a 1-line reason (e.g., "vault Known-issues section missing — caveat section empty"). Do NOT commit the file. The agent continues to the next slug.

---

### Task 33: Phase 8B SUMMARY + final validation

After all 31 ports are attempted (whether all 31 succeeded or some failed), the executor produces the closure SUMMARY.

**Outputs**:

1. `.planning/phases/08B-claude-design-hero-rewrite/08B-01-SUMMARY.md` with:
   - **Outcome**: `success` (33/33 ports successful, including pre-existing fuelhh + system_prices), `partial` (≥1 failure), or `failed` (build-script override broke)
   - **Per-dataset table**: slug | status (✓ committed / ✗ failed) | failed-check (if applicable) | commit-hash
   - **Build-script change**: file path, lines added, idempotence-check result
   - **CI gate status** (run + capture exit codes):
     - `python -c "from gridflow_front_end.build import main; main()"` (full build)
     - `python -c "from gridflow_front_end.build import main; main()"` (second run = idempotence)
     - htmlhint over the regenerated set (`npx htmlhint --config .htmlhintrc 'site/hifi/data-sources/elexon/*.html'` — if htmlhint is on path; if not, log and skip with `htmlhint not installed locally; rely on CI`)
     - lychee (same skip-if-not-installed)
   - **Long-tail path decision** (Phase 8B CONTEXT Q-A → answer): `AI-port the rest` (proven by this plan's success rate; if ≥28/31 succeeded, the answer stands)
   - **Phase 9 implications**: 1 paragraph stating that ENTSO-E datasets follow the same pattern (drop into `authored-pages/entsoe/<slug>.html`); the build override already supports all vendors in `REAL_VENDORS`

2. Update ROADMAP.md Phase 8B progress-table entry: `1/1` plans complete, status `Complete`, completion date `2026-05-XX`

3. Run final CI gates and record exit codes in SUMMARY

**Commit**: `docs(08B): close phase 8B — 33/33 Elexon pages on authored-pages override` (or `partial` if some failed)

```
docs(08B): close phase 8B — N/33 Elexon pages on authored-pages override

Plan 08B-01 ran autonomously on the docs/v2-milestone-start branch
overnight. Outcome: <success | partial — N/31 ports succeeded>.
Build-script override path (src/gridflow_front_end/build.py) wired
and idempotent; subsequent `gridflow-build` runs preserve all authored
output. fuelhh + system_prices + 29..31 ports landed under
authored-pages/elexon/ with structural checks (12-point per page)
passing. CI gates: htmlhint <result>, lychee <result>, build-idempotence
<result>.

Long-tail decision (CONTEXT Q-A): AI-port confirmed as the production
path. Phase 9 (ENTSO-E full coverage) reuses this pattern unchanged
— authored-pages/entsoe/<slug>.html drops in and the override fires.
If any ports failed (see PORT-LOG.md), they are slated for human
re-port on next session.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

## Definition of done

**Required**:
- [ ] `src/gridflow_front_end/build.py` reads `authored-pages/<vendor>/<slug>.html` first when present (verified by inspection of the diff)
- [ ] `python -c "from gridflow_front_end.build import main; main()"` succeeds and prints `(authored)` next to fuelhh and system_prices (proves the override is wired)
- [ ] Build idempotence: second `main()` run produces byte-identical output (proves no regression)
- [ ] At least 25 of 31 dataset ports successful (committed with all 12 structural checks passing). If <25, the plan outcome is "partial" and the user investigates; if ≥25, outcome is "success" or "partial-acceptable"
- [ ] All committed authored pages pass: viewport=device-width, slug-in-title, schema≥3 rows, caveats≥1, related≥1, all sidebar anchors resolve, no Jinja2 syntax in HTML
- [ ] `08B-01-SUMMARY.md` written with per-dataset table + CI gate results
- [ ] ROADMAP.md progress-table updated for Phase 8B

**Out of scope** (defer to next session if surfaced):
- Visual quality variance — only structural checks possible without user-eyeballs
- Any port that fails ≥3 structural checks — logged for human re-port, not auto-retried
- Editing the existing fuelhh.html or system_prices.html — those are reference targets, not editable in this plan
- Phase 9 (ENTSO-E) — separate phase, separate plan
- Reverting the Iteration-2 template changes from Phase 8 — kept in place (per Phase 8 SUMMARY)

## Autonomy guarantees (for the executor)

- DO NOT use AskUserQuestion under any circumstance — the user is not available during execution
- DO NOT pause for confirmation between tasks — chain through all 33 tasks in one run
- DO NOT use `git push` — commits stay local on `docs/v2-milestone-start`; push is a separate manual step
- DO NOT use `--no-verify` on commits — let pre-commit hooks run (if any are configured)
- DO NOT delete or modify `authored-pages/elexon/fuelhh.html` or `authored-pages/elexon/system_prices.html` — these are reference targets
- DO NOT modify the embedded `<style>` block in any port — copy verbatim from system_prices.html
- DO NOT invent vault content — if a vault section is missing (e.g., no "Known issues"), the corresponding HTML section is omitted, not fabricated
- DO record every action in PORT-LOG.md if it would otherwise need user input
- DO continue execution after any single-port failure — failures are logged, not raised
- DO produce the SUMMARY at the end regardless of how many ports succeeded
