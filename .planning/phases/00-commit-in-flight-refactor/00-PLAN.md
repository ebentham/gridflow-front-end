---
phase: 00-commit-in-flight-refactor
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - site/hifi/architecture.html
  - site/hifi/data-sources.html
  - site/hifi/data-sources/elexon.html
  - site/hifi/data-sources/elexon/agpt.html
  - site/hifi/data-sources/elexon/agws.html
  - site/hifi/data-sources/elexon/boal.html
  - site/hifi/data-sources/elexon/disbsad.html
  - site/hifi/data-sources/elexon/fou2t14d.html
  - site/hifi/data-sources/elexon/freq.html
  - site/hifi/data-sources/elexon/fuelhh.html
  - site/hifi/data-sources/elexon/fuelinst.html
  - site/hifi/data-sources/elexon/indo.html
  - site/hifi/data-sources/elexon/indod.html
  - site/hifi/data-sources/elexon/itsdo.html
  - site/hifi/data-sources/elexon/mid.html
  - site/hifi/data-sources/elexon/ndf.html
  - site/hifi/data-sources/elexon/ndfd.html
  - site/hifi/data-sources/elexon/netbsad.html
  - site/hifi/data-sources/elexon/nonbm.html
  - site/hifi/data-sources/elexon/pn.html
  - site/hifi/data-sources/elexon/system_prices.html
  - site/hifi/data-sources/elexon/temp.html
  - site/hifi/data-sources/elexon/tsdf.html
  - site/hifi/data-sources/elexon/uou2t14d.html
  - site/hifi/data-sources/elexon/windfor.html
  - site/hifi/index.html
  - site/hifi/models/demand-forecast.html
  - .gitattributes
  - .gitignore
  - .planning/ROADMAP.md
  - .planning/STATE.md
  - .planning/phases/00-commit-in-flight-refactor/00-PLAN.md
autonomous: false
requirements:
  - HYG-01
  - HYG-02

must_haves:
  truths:
    - "Working tree shows zero modified files and zero untracked files on main post-merge (docs/codebase-map will have 00-PLAN.md tracked from Task 0; .claude/ and .codex-assessment-shots/ are gitignored from Task 5) per D-05, ROADMAP §0 SC#1"
    - "git log shows 4 cleanup commits (typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks) per D-01"
    - ".gitattributes exists at repo root with text eol=lf rules covering .html, .css, .js, .json, .py per HYG-02"
    - "Line endings renormalized as a separate 6th commit per D-03"
    - "PR opened from docs/codebase-map to main with 17 commits (10 planning + 6 cleanup + 1 ROADMAP doc) per D-04 + C1"
    - "Merge into main uses Create-a-merge-commit (NOT squash, NOT rebase) per D-04"
    - "GitHub Pages-deployed site matches current main HEAD post-merge per ROADMAP §0 SC#3"
    - "ROADMAP §0 SC#1 wording reconciled with the 6-commit reality (Option A: in-plan update) per C1"
  artifacts:
    - path: .gitattributes
      provides: "Line-ending normalization rules for cross-platform editing"
      contains: "*.html text eol=lf"
    - path: .gitignore
      provides: "Ignore .claude/ and .codex-assessment-shots/ tooling artifacts (D-05)"
      contains: ".claude/"
    - path: .planning/ROADMAP.md
      provides: "Updated Phase 0 success criterion wording (C1, Option A)"
      contains: "4 cleanup chunks"
  key_links:
    - from: "docs/codebase-map branch HEAD"
      to: "main branch (via PR merge)"
      via: "gh pr create then GitHub UI Create-a-merge-commit"
      pattern: "git log main --oneline.*typography sweep"
    - from: "main branch merge commit"
      to: "https://ebentham.github.io/gridflow-front-end/"
      via: ".github/workflows/deploy.yml push-to-main trigger"
      pattern: "curl.*ebentham\\.github\\.io.*A pipeline and catalogue"
---

<objective>
Land the 27 uncommitted modified files as 4 logical cleanup commits + 2 repo-hygiene commits on `docs/codebase-map`, then open a PR to `main`, merge with a merge-commit strategy, and verify GitHub Pages catches up. This is the gating prerequisite for every other phase per `.planning/research/PITFALLS.md § Pitfall 0`.

Purpose: A clean working tree with concern-per-commit history unblocks Phases 1-6. Bisect works at concern granularity. Line-ending churn between Windows-edits and Linux-CI deploys stops permanently. Deployed site stops being a different version from the working tree.

Output:
- 6 atomic git commits on `docs/codebase-map` (4 cleanup + 2 hygiene)
- 1 atomic commit updating ROADMAP §0 SC#1 wording (Option A per C1)
- `.gitattributes` (new file)
- `.gitignore` updated (2 appended entries)
- 1 merged PR (`docs/codebase-map → main`, 17 commits total: 10 planning + 6 cleanup + 1 ROADMAP doc)
- `git status` clean on `main` post-merge
- GitHub Pages serving the working-tree content
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.planning/phases/00-commit-in-flight-refactor/00-CONTEXT.md
@.planning/research/PITFALLS.md
@.planning/codebase/CONCERNS.md
@CLAUDE.md

<canonical_diffs>
<!-- The exact text substitutions for chunks 1-4 are documented here. The executor MUST -->
<!-- read these before staging anything. Strings are drawn from `git diff HEAD` taken -->
<!-- at planning time on 2026-05-17. Use the Edit tool with these as `old_string` / -->
<!-- `new_string` arguments. All strings are unique within their files (verified). -->

CHUNK 1 (typography sweep — applies to ALL 27 modified files):
  Global find/replace:
    old: `<span class="italic fg-accent">`
    new: `<span class="italic">`
  Notes:
    - This pattern appears in: architecture.html (2), data-sources.html (1), data-sources/elexon.html (1), data-sources/elexon/*.html × 22 (1 each), index.html (4), models/demand-forecast.html (8).
    - Total occurrences across the 27 files: 39. All have the same find/replace pair.
    - `data-sources.html` is typography-ONLY (does NOT get viewport fix here — that's Phase 1 MOB-01).

CHUNK 2 (pillar-status removal — index.html ONLY):
  Three deletions, each is the literal whole-line `<span class="pillar-status">…</span>` element. Use Edit tool with these exact `old_string` values:

  Deletion A (Pillar 1, "Shipping"):
    `          <span class="pillar-status live"><span class="dot live"></span>Shipping</span>\n`
    (Delete the entire line including its leading whitespace and trailing newline.)

  Deletion B (Pillar 2, "Elexon complete · 6 vendors in progress"):
    `          <span class="pillar-status"><span class="dot live"></span><span style="color:var(--accent);">Elexon complete</span> · 6 vendors in progress</span>\n`

  Deletion C (Pillar 3, "Demand shipping · 4 more planned"):
    `          <span class="pillar-status"><span class="dot live"></span><span style="color:var(--accent);">Demand</span> shipping · 4 more planned</span>\n`

CHUNK 3 (fuelhh.html honesty edits — fuelhh.html ONLY):

  Edit 1 (stat-card hero, LAST FETCH → PRIMARY KEY):
    old:
      `            <div class="tiny mb-6">LAST FETCH</div>
            <div class="small"><span class="dot live"></span> 42 s ago</div>`
    new:
      `            <div class="tiny mb-6">PRIMARY KEY</div>
            <div class="mono small">settlement_date, period, fuel_type</div>`

  Edit 2 (stats strip, Median lag → Resolution):
    old:
      `        <div class="stat-n">42<span style="font-size:18px; color:var(--ink-soft); margin-left:2px;">s</span></div>
        <div class="stat-l">Median lag</div>`
    new:
      `        <div class="stat-n">30<span style="font-size:18px; color:var(--ink-soft); margin-left:2px;">min</span></div>
        <div class="stat-l">Resolution</div>`

  Edit 3 (sidebar, Live chart → Snapshot chart):
    old: `          <a href="#live-chart">Live chart</a>`
    new: `          <a href="#live-chart">Snapshot chart</a>`

  Edit 4 (section comment, Live chart → Sample chart):
    old: `        <!-- ── Live chart ── -->`
    new: `        <!-- ── Sample chart ── -->`

  Edit 5 (chart eyebrow + heading, Live chart → Static snapshot + new heading):
    old:
      `          <div class="eyebrow mb-8">Live chart</div>
          <h2 class="display-3 mb-24">GB generation mix · last 24 h.</h2>`
    new:
      `          <div class="eyebrow mb-8">Static snapshot</div>
          <h2 class="display-3 mb-24">GB generation mix · 24-hour <span class="italic">snapshot.</span></h2>`

  Edit 6 (chart subtitle, add date):
    old: `                <div class="small">Stacked area · MW · UTC</div>`
    new: `                <div class="small">Stacked area · MW · UTC · 29 Apr 2026</div>`

  Edit 7 (insert snapshot-note line after data-chart div, before closing section's chart div):
    old: `            <div data-chart="stackedArea" data-opts='{"width":900,"height":280}'></div>
          </div>
        </section>`
    new: `            <div data-chart="stackedArea" data-opts='{"width":900,"height":280}'></div>
            <div class="snapshot-note mt-16" style="font-family: var(--mono); font-size: 10px; letter-spacing: 0.08em; color: var(--ink-faint); text-transform: uppercase;">Static snapshot · live wiring planned</div>
          </div>
        </section>`

CHUNK 4 (remaining tweaks — elexon.html + index.html + fuelhh.html viewport only):

  Per D-02 of CONTEXT.md. The chunk 4 edits are LOAD-BEARING — copy them verbatim.

  4a — fuelhh.html viewport fix (1 line):
    old: `  <meta name="viewport" content="width=1280" />`
    new: `  <meta name="viewport" content="width=device-width, initial-scale=1" />`

  4b — index.html hero copy rewrite (multi-line):
    old:
      `          <h1 class="display-1" style="margin-bottom: 28px;">
            European energy<br/>
            markets, <span class="italic">tidied.</span>
          </h1>
          <p class="lede" style="max-width: 520px; margin-bottom: 12px;">
            A pipeline, a catalogue, and a probabilistic modelling stack
            for UK &amp; European energy data.
          </p>`
    new:
      `          <h1 class="display-1" style="margin-bottom: 28px;">
            A pipeline and catalogue<br/>
            for UK &amp; European<br/>
            <span class="italic">energy data.</span>
          </h1>`
    Note: chunk 1 (typography sweep) has already converted `<span class="italic fg-accent">tidied.</span>` to `<span class="italic">tidied.</span>` in the old_string. If chunks 1-3 staged-and-committed correctly, this `old_string` matches the on-disk state at chunk 4 time.

  4c — index.html WIP-bar section removal (full <section> block):
    old:
      `  <!-- ════════════════ WIP / CURRENTLY WORKING ON ════════════════ -->
  <section style="padding: 32px 0 64px;" data-screen-label="wip">
    <div class="container">
      <div class="wip-bar">
        <div class="wip-dot"></div>
        <span class="mono tiny" style="color:var(--ink-soft);">Currently:</span>
        <span class="mono tiny">ENTSO-E balancing datasets (Phase G3) · power stack model · cleaning the demand pipeline for live use</span>
      </div>
    </div>
  </section>

  <script src="assets/charts.js"></script>`
    new:
      `  <script src="assets/charts.js"></script>`

  4d — elexon.html viewport fix:
    old: `  <meta name="viewport" content="width=1280" />`
    new: `  <meta name="viewport" content="width=device-width, initial-scale=1" />`

  4e — elexon.html LAST FETCH → TIMEZONE (in metadata grid):
    old:
      `              <div class="tiny mb-8">LAST FETCH</div>
              <div class="small"><span class="dot live"></span> 1 min 42 s ago</div>`
    new:
      `              <div class="tiny mb-8">TIMEZONE</div>
              <div class="small">UTC · settlement period · SP 1–50</div>`

  4f — elexon.html stat-card overhaul (2 stat cards replaced):
    old:
      `      <div>
        <div class="stat-n">99.7<span style="font-size:18px; color:var(--ink-soft); margin-left:2px;">%</span></div>
        <div class="stat-l">Fetch success · 30d</div>
      </div>
      <div>
        <div class="stat-n">42<span style="font-size:18px; color:var(--ink-soft); margin-left:2px;">s</span></div>
        <div class="stat-l">Median freshness</div>
      </div>`
    new:
      `      <div>
        <div class="stat-n">4</div>
        <div class="stat-l">Categories</div>
      </div>
      <div>
        <div class="stat-n">7</div>
        <div class="stat-l">Settlement runs · II → DF</div>
      </div>`

  4g — elexon.html Live · fuelhh → Snapshot · fuelhh framing:
    old:
      `              <div class="eyebrow mb-8">Live · fuelhh</div>
              <h3 style="font-family: var(--serif); font-size: 22px;">GB generation by fuel · last 24 hours</h3>`
    new:
      `              <div class="eyebrow mb-8">Snapshot · fuelhh</div>
              <h3 style="font-family: var(--serif); font-size: 22px;">GB generation by fuel · 24-hour snapshot</h3>`

  4h — elexon.html snapshot-note chip add (after data-chart, before closing chart div):
    old:
      `          <div data-chart="stackedArea" data-opts='{"width":880,"height":280}'></div>
        </div>

        <div class="card" style="padding: 0; display: flex; flex-direction: column;">`
    new:
      `          <div data-chart="stackedArea" data-opts='{"width":880,"height":280}'></div>
          <div class="snapshot-note mt-16" style="font-family: var(--mono); font-size: 10px; letter-spacing: 0.08em; color: var(--ink-faint); text-transform: uppercase;">Static snapshot · 29 Apr 2026 · live wiring planned</div>
        </div>

        <div class="card" style="padding: 0; display: flex; flex-direction: column;">`

  4i — elexon.html "Right now" → "Sample window" metric card rewrite (large multi-block edit). The full target block (final state, replaces lines from `<div style="padding: 18px 20px; border-bottom: 1px solid var(--rule);">` containing eyebrow "Right now" through closing footer with `silver.fuelhh`):

    old:
      `          <div style="padding: 18px 20px; border-bottom: 1px solid var(--rule);">
            <div class="eyebrow">Right now</div>
          </div>
          <div style="padding: 20px; display:flex; flex-direction:column; gap: 16px; flex:1;">
            <div>
              <div class="tiny mb-8">DEMAND</div>
              <div class="display-3" style="font-size: 32px;">34.6 <span style="font-size: 14px; font-family: var(--sans); color: var(--ink-soft); font-weight: 400;">GW</span></div>
              <div data-chart="sparkline" data-opts='{"seed":4,"width":280,"height":34}' class="mt-8"></div>
            </div>
            <hr class="rule" />
            <div>
              <div class="tiny mb-8">SYSTEM PRICE</div>
              <div class="display-3" style="font-size: 32px;">£82.40 <span style="font-size: 14px; font-family: var(--sans); color: var(--ink-soft); font-weight: 400;">/MWh</span></div>
              <div data-chart="priceLadder" data-opts='{"seed":3,"width":280,"height":50}' class="mt-8"></div>
            </div>
            <hr class="rule" />
            <div>
              <div class="tiny mb-8">CARBON · NESO</div>
              <div class="display-3" style="font-size: 32px;">142 <span style="font-size: 14px; font-family: var(--sans); color: var(--ink-soft); font-weight: 400;">g CO₂/kWh</span></div>
              <div class="small mt-8" style="color: var(--accent);">↓ 8% vs yesterday</div>
            </div>
          </div>
          <div style="padding: 14px 20px; border-top: 1px solid var(--rule); display:flex; justify-content: space-between; align-items: center;">
            <span class="tiny">SP 28 · 14:02 UTC</span>`
    new:
      `          <div style="padding: 18px 20px; border-bottom: 1px solid var(--rule);">
            <div class="eyebrow">Sample window</div>
            <div class="tiny mt-4">29 Apr 2026 · 48 settlement periods</div>
          </div>
          <div style="padding: 20px; display:flex; flex-direction:column; gap: 18px; flex:1;">
            <div>
              <div class="tiny mb-8">DEMAND RANGE</div>
              <div class="display-3" style="font-size: 28px;">22.1 <span style="font-size: 13px; color: var(--ink-soft); font-family: var(--sans); font-weight: 400;">→</span> 38.4 <span style="font-size: 13px; color: var(--ink-soft); font-family: var(--sans); font-weight: 400;">GW</span></div>
              <div class="small mt-8" style="color: var(--ink-soft);">Trough SP 8 · peak SP 36</div>
            </div>
            <hr class="rule" />
            <div>
              <div class="tiny mb-8">WIND SHARE</div>
              <div class="display-3" style="font-size: 28px;">8 <span style="font-size: 13px; color: var(--ink-soft); font-family: var(--sans); font-weight: 400;">→</span> 47<span style="font-size: 16px; color: var(--ink-soft); font-family: var(--sans); font-weight: 400;">%</span></div>
              <div class="small mt-8" style="color: var(--ink-soft);">26.6% mean · gas-displacing</div>
            </div>
            <hr class="rule" />
            <div>
              <div class="tiny mb-8">FUEL TYPES OBSERVED</div>
              <div class="display-3" style="font-size: 28px;">12 <span style="font-size: 13px; color: var(--ink-soft); font-family: var(--sans); font-weight: 400;">of 16</span></div>
              <div class="small mt-8" style="color: var(--ink-soft);">Gas, wind, nuclear, imports, biomass…</div>
            </div>
          </div>
          <div style="padding: 14px 20px; border-top: 1px solid var(--rule); display:flex; justify-content: space-between; align-items: center;">
            <span class="tiny mono">silver.fuelhh</span>`

  4j — elexon.html HEALTH section deletion (~50 lines, full <section data-screen-label="health"> block plus its trailing blank lines):
    old:
      `  <!-- ════════════════ HEALTH ════════════════ -->
  <section class="block" data-screen-label="health">
    <div class="container">
      <div class="row between mb-32" style="align-items: end;">
        <div>
          <div class="eyebrow mb-8">Pipeline health</div>
          <h2 class="display-3">Last 30 days, hour by hour.</h2>
        </div>
        <div class="row gap-16 small">
          <span class="row gap-8 center"><i class="dot live"></i> success</span>
          <span class="row gap-8 center"><i class="dot warn"></i> failure / retry</span>
          <span class="row gap-8 center"><i class="dot idle"></i> partial</span>
        </div>
      </div>

      <div class="card" style="padding: 22px 26px;">
        <div data-chart="heatmap" data-opts='{"width":1100,"height":220,"rows":24,"cols":30,"seed":29}'></div>
      </div>

      <div class="row mt-24" style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
        <div class="card">
          <div class="tiny mb-8">SUCCESS RATE · 30D</div>
          <div class="display-3" style="font-size: 32px; color: var(--accent);">99.7%</div>
          <div class="small mt-8">21 retries · 4 failures</div>
        </div>
        <div class="card">
          <div class="tiny mb-8">MEDIAN FRESHNESS</div>
          <div class="display-3" style="font-size: 32px;">42 <span style="font-size:14px; color:var(--ink-soft); font-family: var(--sans); font-weight: 400;">s</span></div>
          <div class="small mt-8">Target ≤ 5 min</div>
        </div>
        <div class="card">
          <div class="tiny mb-8">P95 FRESHNESS</div>
          <div class="display-3" style="font-size: 32px;">3:18</div>
          <div class="small mt-8">Slowest: <span class="mono">disbsad</span></div>
        </div>
        <div class="card">
          <div class="tiny mb-8">SCHEMA DRIFT</div>
          <div class="display-3" style="font-size: 32px;">0</div>
          <div class="small mt-8">Last drift: 2026-04-14</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ════════════════ ABOUT VENDOR ════════════════ -->`
    new:
      `  <!-- ════════════════ ABOUT VENDOR ════════════════ -->`

CHUNK 5 (.gitattributes + .gitignore — per D-05 and gitattributes_decision Approach A):

  Create `.gitattributes` at repo root with this EXACT content (final newline included):
    ```
    *.html text eol=lf
    *.css  text eol=lf
    *.js   text eol=lf
    *.json text eol=lf
    *.py   text eol=lf
    *.md   text eol=lf
    *.yml  text eol=lf
    *.yaml text eol=lf
    *.toml text eol=lf
    ```

  Append to `.gitignore` (existing 7 lines preserved verbatim — `.venv/`, `__pycache__/`, `*.pyc`, `*.egg-info/`, `dist/`, `build/`, `.idea/`). Add these 2 lines at the end:
    ```
    .claude/
    .codex-assessment-shots/
    ```

CHUNK 6 (renormalize line endings):
  After chunk 5's commit lands, run:
    `git add --renormalize .`
  Then commit whatever Git produces. If `git status` shows nothing after the renormalize command (i.e. Git's existing index already matched the new rules), make an empty commit with `--allow-empty` to preserve the documented intent. Most likely Git will renormalize all 27+ recently-modified .html files plus possibly the existing committed files (theme.css, site.js, charts.js, serve.py, etc.).
</canonical_diffs>

<environment_notes>
- `gh` CLI is authenticated as EBentham (verified at planning time via `gh auth status`).
- Current branch is `docs/codebase-map` (correct per C9 — DO NOT create a new branch).
- GitHub Pages URL: `https://ebentham.github.io/gridflow-front-end/` (derived from `.github/workflows/deploy.yml` + repo owner EBentham). Verify at runtime via `gh api repos/EBentham/gridflow-front-end/pages -q .html_url` in case a custom domain is later configured.
- Pages deploy trigger: push to `main` (per `.github/workflows/deploy.yml` line 5). PR merge into main triggers it; PR open does not.
- `gsd-sdk` CLI is NOT installed — use raw `git`, `gh`, `curl` commands only. NEVER `gsd-sdk query ...`.
- All commits MUST be on `docs/codebase-map`. NEVER commit to `main`.
- Pre-existing 9 planning commits on `docs/codebase-map` are NOT touched. Task 0 adds a 10th planning commit (the planner-record commit for `00-PLAN.md` + `ROADMAP.md`). The 6 cleanup + 1 ROADMAP reconciliation commits then stack on top.
- `/tmp` directory is verified writable on this host via Bash (Git for Windows bash provides POSIX-style /tmp).
</environment_notes>
</context>

<tasks>

<task type="auto">
  <name>Task 0: Stage and commit the planner-bookkeeping artifacts (docs: record phase 0 plan)</name>
  <files>
    .planning/ROADMAP.md,
    .planning/STATE.md,
    .planning/phases/00-commit-in-flight-refactor/00-PLAN.md
  </files>
  <read_first>
    - CLAUDE.md (Conventional Commits convention; never commit to main)
    - .planning/phases/00-commit-in-flight-refactor/00-PLAN.md (this file — the artefact being committed)
    - .planning/ROADMAP.md (planner-bookkeeping diff: Phase 0 progress-table + `**Plans**: 1 plan` line + Phase 6 stray-line restore — verify with `git diff .planning/ROADMAP.md` first)
    - .planning/STATE.md (orchestrator-bookkeeping diff: Phase 0 status flipped to "Ready to execute" + plan path recorded + last-action narrative updated — verify with `git diff .planning/STATE.md` first)
  </read_first>
  <action>
    The act of running `/gsd-plan-phase 0` mutated the working tree: it wrote `00-PLAN.md` (untracked), updated `ROADMAP.md` (Phase 0 progress-table entry + `**Plans**: 1 plan` line + Phase 6 stray-line restoration by the orchestrator), and updated `STATE.md` (orchestrator's §13b "record planning completion" step — flipped status to "Ready to execute" and updated the last-action / next-action narrative). All three edits are planner/orchestrator bookkeeping artefacts, NOT part of the cleanup chunks. Task 1's sanity check (Step 1) explicitly expects the baseline "27 M + 2 ??" — so we must commit these three artefacts BEFORE Task 1 starts.

    This task isolates the planner-bookkeeping diff into one focused `docs:` commit, leaving the working tree at exactly the baseline Task 1 expects.

    Step 1 — Verify the working tree matches the post-planning baseline:
    ```bash
    cd C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow-front-end
    git status --porcelain | sort
    ```
    Expect exactly 29 `M` lines (27 site files + `.planning/ROADMAP.md` + `.planning/STATE.md`) and 3 `??` lines (`.claude/`, `.codex-assessment-shots/`, `.planning/phases/00-commit-in-flight-refactor/00-PLAN.md`). If counts differ, STOP — the working tree has diverged from the planning-time baseline.

    Step 2 — Inspect the ROADMAP and STATE diffs to confirm they're only planner/orchestrator bookkeeping (no content drift):
    ```bash
    git diff .planning/ROADMAP.md
    git diff .planning/STATE.md
    ```
    Expect ROADMAP.md diff: small (~3-4 lines), confined to two hunks: (a) Phase 0's `**Plans**: TBD` → `**Plans**: 1 plan` transition plus the new `- [ ] 00-01-PLAN.md` line, and (b) the Progress Table row for Phase 0 (`0/?` → `0/1`, `Not started` → `Plan ready`). NO Phase 6 hunk should appear — the planner inadvertently removed Phase 6's `**Plans**: TBD` and the orchestrator restored it before this commit, so the net diff in that region is zero.
    Expect STATE.md diff: small (~8 lines): "Current Focus" line updated, "Plan:" line populated with the new file path, "Status:" flipped to "Ready to execute", and the Session Continuity block's "Last action" / "Next action" / "Resume from" lines updated to reflect planning completion.
    If you see additional unrelated edits, STOP and ask the user.

    Step 3 — Stage ONLY the three planner-bookkeeping artefacts BY LITERAL PATH (NEVER `git add -A` or `git add .`; per T-00-08 a glob would sweep in the 27 site files and corrupt the chunk-1 scope):
    ```bash
    git add .planning/ROADMAP.md .planning/STATE.md .planning/phases/00-commit-in-flight-refactor/00-PLAN.md
    ```

    Step 4 — Verify the stage matches expectations BEFORE committing:
    ```bash
    git diff --cached --stat
    ```
    Expect EXACTLY 3 files staged: `.planning/ROADMAP.md` (a few-line modification), `.planning/STATE.md` (a few-line modification), and `.planning/phases/00-commit-in-flight-refactor/00-PLAN.md` (a new file, ~1443 lines). If any site/hifi/* path appears, STOP and run `git restore --staged .` to unstage everything, then retry from Step 3.

    Step 5 — Commit:
    ```bash
    git commit -m "$(cat <<'EOF'
    docs(00): record phase 0 plan

    Capture the consolidated 11-task plan for Phase 0, the corresponding
    ROADMAP.md progress-table entry, and the STATE.md transition to
    "Ready to execute". The plan was generated via /gsd-plan-phase 0 on
    2026-05-17. See 00-PLAN.md for the full task chain (this planner-record
    commit + 6 cleanup commits + 1 ROADMAP SC#1 reconciliation + PR
    open/merge/verify).
    EOF
    )"
    ```

    Step 6 — Verify the commit landed AND the working tree now matches the baseline Task 1 expects:
    ```bash
    git log -1 --format="%h %s"
    git status --porcelain | sort
    ```
    Expect:
    - Latest commit subject = `docs(00): record phase 0 plan`
    - `git status --porcelain` shows exactly 27 `M` lines (only site files) + 2 `??` lines (`.claude/`, `.codex-assessment-shots/`)
    - `00-PLAN.md` is now TRACKED (`git ls-files .planning/phases/00-commit-in-flight-refactor/00-PLAN.md` returns the path)
  </action>
  <verify>
    <automated>git log --format=%s -1 HEAD | grep -q "^docs(00): record phase 0 plan" && test "$(git status --porcelain | grep -c '^ M ')" = "27" && test "$(git status --porcelain | grep -c '^??')" = "2" && git ls-files .planning/phases/00-commit-in-flight-refactor/00-PLAN.md | grep -q "00-PLAN.md" ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - Latest commit subject is `docs(00): record phase 0 plan`
    - `git status --porcelain | grep -c '^ M '` returns 27 (the original 27 site files only)
    - `git status --porcelain | grep -c '^??'` returns 2 (`.claude/` and `.codex-assessment-shots/` — `00-PLAN.md` is now tracked)
    - `git ls-files .planning/phases/00-commit-in-flight-refactor/00-PLAN.md` returns the path (plan file is tracked)
    - The 27 site-file modifications stay untouched in the working tree, ready for Task 1 chunk-1 staging
  </done>
</task>

<task type="auto" depends_on="Task 0">
  <name>Task 1: Chunk 1 — typography sweep (refactor: fg-accent → italic across all 27 files)</name>
  <files>
    site/hifi/architecture.html,
    site/hifi/data-sources.html,
    site/hifi/data-sources/elexon.html,
    site/hifi/data-sources/elexon/agpt.html,
    site/hifi/data-sources/elexon/agws.html,
    site/hifi/data-sources/elexon/boal.html,
    site/hifi/data-sources/elexon/disbsad.html,
    site/hifi/data-sources/elexon/fou2t14d.html,
    site/hifi/data-sources/elexon/freq.html,
    site/hifi/data-sources/elexon/fuelhh.html,
    site/hifi/data-sources/elexon/fuelinst.html,
    site/hifi/data-sources/elexon/indo.html,
    site/hifi/data-sources/elexon/indod.html,
    site/hifi/data-sources/elexon/itsdo.html,
    site/hifi/data-sources/elexon/mid.html,
    site/hifi/data-sources/elexon/ndf.html,
    site/hifi/data-sources/elexon/ndfd.html,
    site/hifi/data-sources/elexon/netbsad.html,
    site/hifi/data-sources/elexon/nonbm.html,
    site/hifi/data-sources/elexon/pn.html,
    site/hifi/data-sources/elexon/system_prices.html,
    site/hifi/data-sources/elexon/temp.html,
    site/hifi/data-sources/elexon/tsdf.html,
    site/hifi/data-sources/elexon/uou2t14d.html,
    site/hifi/data-sources/elexon/windfor.html,
    site/hifi/index.html,
    site/hifi/models/demand-forecast.html
  </files>
  <read_first>
    - CLAUDE.md (Conventional Commits convention)
    - .planning/phases/00-commit-in-flight-refactor/00-CONTEXT.md (D-01 in particular)
    - .planning/research/PITFALLS.md § Pitfall 0
    - 00-PLAN.md `<canonical_diffs>` block (above) — CHUNK 1 section
  </read_first>
  <action>
    **Phase 0 staging strategy:** The 27 modified files contain mixed concerns. To stage cleanly per chunk, we use a "checkout-and-rebuild" pattern for the 3 mixed-concern files (`index.html`, `elexon.html`, `fuelhh.html`) and direct staging for the 24 typography-only files.

    Step 1 — Sanity-check working tree matches planning-time state:
    ```bash
    cd C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow-front-end
    git status --porcelain | sort
    ```
    Expect exactly 27 `M` lines + 2 `??` lines (`.claude/`, `.codex-assessment-shots/`). If counts differ, STOP and ask the user — the working tree has diverged from the plan baseline.

    Step 2 — For the 3 mixed-concern files, save the current (final-state) content to `/tmp/phase-0-targets/`, then revert each file to HEAD. This lets each subsequent chunk re-apply only its own edits against the prior chunk's known-good state, while `/tmp/phase-0-targets/` remains the authoritative final-state reference for diff verification.
    ```bash
    mkdir -p /tmp/phase-0-targets
    cp site/hifi/index.html /tmp/phase-0-targets/index.html
    cp site/hifi/data-sources/elexon.html /tmp/phase-0-targets/elexon.html
    cp site/hifi/data-sources/elexon/fuelhh.html /tmp/phase-0-targets/fuelhh.html
    git checkout HEAD -- site/hifi/index.html site/hifi/data-sources/elexon.html site/hifi/data-sources/elexon/fuelhh.html
    ```
    The other 24 files keep their typography-only working-tree edits.

    Step 3 — Re-apply chunk 1 (typography sweep) to the 3 reverted files only. For each, do the global find/replace `<span class="italic fg-accent">` → `<span class="italic">` using the Edit tool with `replace_all=true`:
    - On `site/hifi/index.html`: 4 occurrences (per planning diff).
    - On `site/hifi/data-sources/elexon.html`: 1 occurrence.
    - On `site/hifi/data-sources/elexon/fuelhh.html`: 1 occurrence.

    Step 4 — Verify the 27 files now contain only typography-class changes (no `fg-accent` should remain anywhere):
    ```bash
    grep -rn "fg-accent" site/hifi/ || echo "OK: zero fg-accent occurrences"
    ```
    Expect "OK: zero fg-accent occurrences".

    Step 5 — Stage all 27 files and commit with the chunk-1 message:
    ```bash
    git add site/hifi/architecture.html site/hifi/data-sources.html site/hifi/data-sources/elexon.html site/hifi/data-sources/elexon/agpt.html site/hifi/data-sources/elexon/agws.html site/hifi/data-sources/elexon/boal.html site/hifi/data-sources/elexon/disbsad.html site/hifi/data-sources/elexon/fou2t14d.html site/hifi/data-sources/elexon/freq.html site/hifi/data-sources/elexon/fuelhh.html site/hifi/data-sources/elexon/fuelinst.html site/hifi/data-sources/elexon/indo.html site/hifi/data-sources/elexon/indod.html site/hifi/data-sources/elexon/itsdo.html site/hifi/data-sources/elexon/mid.html site/hifi/data-sources/elexon/ndf.html site/hifi/data-sources/elexon/ndfd.html site/hifi/data-sources/elexon/netbsad.html site/hifi/data-sources/elexon/nonbm.html site/hifi/data-sources/elexon/pn.html site/hifi/data-sources/elexon/system_prices.html site/hifi/data-sources/elexon/temp.html site/hifi/data-sources/elexon/tsdf.html site/hifi/data-sources/elexon/uou2t14d.html site/hifi/data-sources/elexon/windfor.html site/hifi/index.html site/hifi/models/demand-forecast.html

    git commit -m "$(cat <<'EOF'
    refactor(typography): drop fg-accent class from display italics

    Strip the .fg-accent decoration from <span class="italic"> elements
    across architecture, index, demand-forecast, the Elexon hub, and all
    22 Elexon dataset pages. The italic style alone now carries the
    emphasis; .fg-accent's green tint was visually overloading the
    cream/forest palette.

    Part of Phase 0 (commit in-flight refactor) per D-01 / HYG-01.
    EOF
    )"
    ```

    Step 6 — Verify the commit:
    ```bash
    git log -1 --format="%h %s"
    git show --stat HEAD
    ```
    Expect 27 files changed, ~39 insertions, ~39 deletions (each `fg-accent` removal is a 1-line edit).
  </action>
  <verify>
    <automated>git log --format=%s -1 HEAD | grep -q "^refactor(typography): drop fg-accent" && git diff HEAD~1 HEAD --name-only | wc -l | grep -q "^27$" && (grep -rn "fg-accent" site/hifi/ ; test $? -eq 1) ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - Latest commit subject starts with `refactor(typography): drop fg-accent`
    - `git diff HEAD~1 HEAD --stat` shows exactly 27 files
    - `grep -rn "fg-accent" site/hifi/` returns no matches (exit code 1)
    - The 3 mixed-concern files (`index.html`, `elexon.html`, `fuelhh.html`) match `/tmp/phase-0-targets/*` for ONLY the typography line; other edits still remain to be applied in chunks 2-4
  </done>
</task>

<task type="auto" depends_on="Task 1">
  <name>Task 2: Chunk 2 — pillar-status removal (chore: remove false pillar-status badges on index.html)</name>
  <files>site/hifi/index.html</files>
  <read_first>
    - CLAUDE.md
    - 00-PLAN.md `<canonical_diffs>` block — CHUNK 2 section
    - /tmp/phase-0-targets/index.html (target final-state reference)
  </read_first>
  <action>
    On `site/hifi/index.html` (currently committed at chunk-1 state, missing the pillar-status deletions + the chunk-4 hero/WIP-bar edits), apply the 3 pillar-status deletions per CHUNK 2 section of `<canonical_diffs>`.

    Recommended pattern — diff against the target to see which lines are still pending:
    ```bash
    diff -u site/hifi/index.html /tmp/phase-0-targets/index.html | head -80
    ```
    You should see two distinct change-classes pending: (a) the 3 pillar-status line deletions (chunk 2), and (b) the hero copy rewrite + WIP-bar deletion (chunk 4). Apply only (a) here.

    Use the Edit tool 3 times, once per deletion (A, B, C). For each, use the surrounding context (1 line above + the pillar-status line + 1 line below) as the `old_string` to guarantee uniqueness, and the same surrounding context minus the pillar-status line as the `new_string`. The exact strings to delete (verbatim, including the `<span class="pillar-status...` element) are documented in CHUNK 2 of `<canonical_diffs>`:

    - Deletion A: `<span class="pillar-status live"><span class="dot live"></span>Shipping</span>` (Pillar 1)
    - Deletion B: `<span class="pillar-status"><span class="dot live"></span><span style="color:var(--accent);">Elexon complete</span> · 6 vendors in progress</span>` (Pillar 2)
    - Deletion C: `<span class="pillar-status"><span class="dot live"></span><span style="color:var(--accent);">Demand</span> shipping · 4 more planned</span>` (Pillar 3)

    All three lines have the same 10-space indentation in the file. Each appears exactly once. Wrap each in a 1-line-above + 1-line-below context block when constructing `old_string` so the Edit tool can locate it unambiguously.

    After 3 deletions, verify:
    ```bash
    grep -c "pillar-status" site/hifi/index.html
    ```
    Expect 0 (all 3 instances removed). The class definition in theme.css can stay (not touched in this refactor; cleanup is a Phase 5 concern).

    Then stage and commit:
    ```bash
    git add site/hifi/index.html
    git commit -m "$(cat <<'EOF'
    chore(index): remove false pillar-status Shipping badges

    Drop the three <span class="pillar-status"> badges from the pillar
    tiles on index.html. The "Shipping" / "Elexon complete · 6 vendors in
    progress" / "Demand shipping · 4 more planned" claims were inflated
    self-promotion that didn't match shipped reality; honest framing
    lives in the pillar copy itself.

    Part of Phase 0 (commit in-flight refactor) per D-01 / HYG-01.
    EOF
    )"
    ```

    Verify the commit:
    ```bash
    git show --stat HEAD
    ```
    Expect exactly 1 file changed (`site/hifi/index.html`), ~0 insertions, 3 deletions.
  </action>
  <verify>
    <automated>git log --format=%s -1 HEAD | grep -q "^chore(index): remove false pillar-status" && git diff HEAD~1 HEAD --name-only | tr -d '\r' | grep -Fx "site/hifi/index.html" && test "$(grep -c 'pillar-status' site/hifi/index.html)" = "0" ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - Latest commit subject starts with `chore(index): remove false pillar-status`
    - `git diff HEAD~1 HEAD --name-only` shows only `site/hifi/index.html`
    - `grep -c "pillar-status" site/hifi/index.html` returns 0
    - The hero copy + WIP-bar edits remain pending in working tree (chunk 4)
  </done>
</task>

<task type="auto" depends_on="Task 2">
  <name>Task 3: Chunk 3 — fuelhh.html honesty edits (docs: pivot fuelhh from live-framing to static-snapshot)</name>
  <files>site/hifi/data-sources/elexon/fuelhh.html</files>
  <read_first>
    - CLAUDE.md
    - 00-PLAN.md `<canonical_diffs>` block — CHUNK 3 section (7 edits)
    - .planning/research/PITFALLS.md § Pitfall 1 (partial-honesty-pivot context)
    - /tmp/phase-0-targets/fuelhh.html (target final-state reference)
  </read_first>
  <action>
    `site/hifi/data-sources/elexon/fuelhh.html` is currently at chunk-1 state (typography sweep applied). The chunk-3 honesty edits (7 substitutions) plus the chunk-4 viewport fix are still pending.

    Apply Edits 1-7 from the CHUNK 3 section of `<canonical_diffs>` in order. Use the Edit tool with the literal `old_string`/`new_string` pairs from that block. DO NOT touch the viewport line (`<meta name="viewport" content="width=1280" />`) — that's chunk 4.

    After applying all 7 edits, verify with diff-against-target:
    ```bash
    diff site/hifi/data-sources/elexon/fuelhh.html /tmp/phase-0-targets/fuelhh.html
    ```
    Expect ONE remaining diff: the viewport line on line 6. Everything else (LAST FETCH→PRIMARY KEY, Median lag→Resolution, sidebar Live chart→Snapshot chart, section comment, eyebrow + heading, subtitle date, snapshot-note insert) should match the target.

    Spot-checks via grep:
    ```bash
    grep -c "PRIMARY KEY" site/hifi/data-sources/elexon/fuelhh.html   # expect 1
    grep -c "settlement_date, period, fuel_type" site/hifi/data-sources/elexon/fuelhh.html  # expect 1
    grep -c "Resolution" site/hifi/data-sources/elexon/fuelhh.html    # expect 1
    grep -c "Snapshot chart" site/hifi/data-sources/elexon/fuelhh.html  # expect 1 (sidebar)
    grep -c "Static snapshot" site/hifi/data-sources/elexon/fuelhh.html  # expect 2 (eyebrow + snapshot-note)
    grep -c "29 Apr 2026" site/hifi/data-sources/elexon/fuelhh.html  # expect 1 (subtitle)
    grep -c "snapshot-note mt-16" site/hifi/data-sources/elexon/fuelhh.html  # expect 1
    grep -c "LAST FETCH" site/hifi/data-sources/elexon/fuelhh.html  # expect 0
    grep -c "Median lag" site/hifi/data-sources/elexon/fuelhh.html  # expect 0
    grep -c "Live chart" site/hifi/data-sources/elexon/fuelhh.html  # expect 0
    ```

    Then stage and commit:
    ```bash
    git add site/hifi/data-sources/elexon/fuelhh.html
    git commit -m "$(cat <<'EOF'
    docs(fuelhh): pivot to honest static-snapshot framing

    Replace live-framing with snapshot-framing on fuelhh.html:
    - Stat-card hero LAST FETCH/42 s ago → PRIMARY KEY/settlement_date, period, fuel_type
    - Stats strip Median lag/42s → Resolution/30min
    - Sidebar "Live chart" → "Snapshot chart"
    - Chart eyebrow "Live chart" → "Static snapshot"
    - Chart heading "GB generation mix · last 24 h." → "...24-hour snapshot."
    - Subtitle adds the snapshot date (29 Apr 2026)
    - New snapshot-note chip: "Static snapshot · live wiring planned"

    Pre-empts Pitfall 1 on this page only; the wider honesty sweep is
    Phase 5. Viewport fix is bundled into chunk 4. Part of Phase 0 per
    D-01 / HYG-01.
    EOF
    )"
    ```

    Verify the commit:
    ```bash
    git show --stat HEAD
    ```
    Expect 1 file changed (`site/hifi/data-sources/elexon/fuelhh.html`), roughly 9 insertions, 6 deletions (the snapshot-note line is net +1).
  </action>
  <verify>
    <automated>git log --format=%s -1 HEAD | grep -q "^docs(fuelhh):" && git diff HEAD~1 HEAD --name-only | tr -d '\r' | grep -Fx "site/hifi/data-sources/elexon/fuelhh.html" && grep -q "PRIMARY KEY" site/hifi/data-sources/elexon/fuelhh.html && grep -q "snapshot-note mt-16" site/hifi/data-sources/elexon/fuelhh.html && ! grep -q "LAST FETCH" site/hifi/data-sources/elexon/fuelhh.html && ! grep -q "Median lag" site/hifi/data-sources/elexon/fuelhh.html ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - Latest commit subject starts with `docs(fuelhh):`
    - `git diff HEAD~1 HEAD --name-only` shows only `site/hifi/data-sources/elexon/fuelhh.html`
    - All 7 spot-check greps pass
    - Only the viewport line remains pending in working tree (chunk 4)
  </done>
</task>

<task type="auto" depends_on="Task 3">
  <name>Task 4: Chunk 4 — remaining tweaks (docs: viewport + honesty pivots on elexon.html + index.html + fuelhh viewport per D-02)</name>
  <files>
    site/hifi/data-sources/elexon.html,
    site/hifi/index.html,
    site/hifi/data-sources/elexon/fuelhh.html
  </files>
  <read_first>
    - CLAUDE.md
    - .planning/phases/00-commit-in-flight-refactor/00-CONTEXT.md (D-02 — load-bearing enumeration)
    - 00-PLAN.md `<canonical_diffs>` block — CHUNK 4 section (edits 4a-4j)
    - /tmp/phase-0-targets/elexon.html (target final-state reference)
    - /tmp/phase-0-targets/index.html (target final-state reference)
    - /tmp/phase-0-targets/fuelhh.html (target final-state reference)
  </read_first>
  <action>
    This chunk implements D-02 verbatim. The current state after chunks 1-3:
    - `site/hifi/index.html`: chunks 1 + 2 committed; pending = hero rewrite + WIP-bar removal.
    - `site/hifi/data-sources/elexon/fuelhh.html`: chunks 1 + 3 committed; pending = viewport.
    - `site/hifi/data-sources/elexon.html`: chunk 1 committed; pending = viewport + LAST FETCH→TIMEZONE + stat-card overhaul + Live·fuelhh→Snapshot framing + snapshot-note + Right now→Sample window + footer SP→silver + HEALTH section deletion.

    Apply edits in this order:

    Step 1 — `fuelhh.html` viewport fix (Edit 4a):
    Use the Edit tool with `old_string='  <meta name="viewport" content="width=1280" />'` and `new_string='  <meta name="viewport" content="width=device-width, initial-scale=1" />'`.

    Step 2 — `index.html` hero copy rewrite (Edit 4b):
    Use the Edit tool with the multi-line `old_string`/`new_string` from CHUNK 4 section. The `old_string` reflects the post-chunk-1 state (italic class with NO fg-accent).

    Step 3 — `index.html` WIP-bar section removal (Edit 4c):
    Use the Edit tool with the multi-line `old_string` (the full `<section data-screen-label="wip">` block plus the trailing blank line plus the `<script src="assets/charts.js"></script>` anchor for uniqueness) and `new_string='  <script src="assets/charts.js"></script>'`.

    Step 4 — `elexon.html` viewport fix (Edit 4d):
    Same find/replace pattern as 4a on the elexon.html file.

    Step 5 — `elexon.html` LAST FETCH → TIMEZONE (Edit 4e):
    Multi-line Edit per canonical_diffs.

    Step 6 — `elexon.html` stat-card overhaul (Edit 4f):
    Multi-line Edit per canonical_diffs (replaces 2 stat cards in one block).

    Step 7 — `elexon.html` Live · fuelhh → Snapshot · fuelhh (Edit 4g):
    Multi-line Edit per canonical_diffs.

    Step 8 — `elexon.html` snapshot-note chip insert (Edit 4h):
    Multi-line Edit per canonical_diffs (uses surrounding context for uniqueness).

    Step 9 — `elexon.html` Right now → Sample window metric card rewrite (Edit 4i):
    Multi-line Edit per canonical_diffs — the largest single edit in this chunk.

    Step 10 — `elexon.html` HEALTH section deletion (Edit 4j):
    Multi-line Edit per canonical_diffs — deletes ~50 lines from the `<!-- ════════════════ HEALTH ═` comment through the section close, preserving the `<!-- ════════════════ ABOUT VENDOR ═` anchor.

    Step 11 — Verify the 3 files now match the planning-time targets:
    ```bash
    diff site/hifi/index.html /tmp/phase-0-targets/index.html  # expect zero output
    diff site/hifi/data-sources/elexon.html /tmp/phase-0-targets/elexon.html  # expect zero output
    diff site/hifi/data-sources/elexon/fuelhh.html /tmp/phase-0-targets/fuelhh.html  # expect zero output
    ```
    If ANY diff is non-empty, STOP — the chunk-4 edits diverged from the captured planning baseline. Re-read the canonical_diffs block and reconcile before staging.

    Step 12 — Spot-check that pending honest-framing markers landed:
    ```bash
    grep -c "A pipeline and catalogue" site/hifi/index.html  # expect 1
    ! grep -q "wip-bar" site/hifi/index.html  # expect WIP bar gone
    grep -c "TIMEZONE" site/hifi/data-sources/elexon.html  # expect 1
    grep -c "Sample window" site/hifi/data-sources/elexon.html  # expect 1
    grep -c "silver.fuelhh" site/hifi/data-sources/elexon.html  # expect 1
    ! grep -q "Pipeline health" site/hifi/data-sources/elexon.html  # expect HEALTH section gone
    ! grep -q "width=1280" site/hifi/data-sources/elexon.html  # viewport fixed
    ! grep -q "width=1280" site/hifi/data-sources/elexon/fuelhh.html  # viewport fixed
    ```

    Step 13 — Stage and commit:
    ```bash
    git add site/hifi/index.html site/hifi/data-sources/elexon.html site/hifi/data-sources/elexon/fuelhh.html
    git commit -m "$(cat <<'EOF'
    docs(site): consolidate cross-page honesty + viewport tweaks

    Bundle the remaining in-flight edits that span 3 files (per D-02):

    site/hifi/data-sources/elexon.html:
      - Viewport fix (width=1280 -> device-width)
      - LAST FETCH/1 min 42 s ago -> TIMEZONE/UTC · settlement period · SP 1-50
      - Stat-card overhaul: Fetch success + Median freshness -> Categories + Settlement runs
      - Live · fuelhh -> Snapshot · fuelhh framing + 24-hour snapshot heading
      - Snapshot-note chip added under the stacked-area chart
      - Right now metric card -> Sample window (DEMAND -> DEMAND RANGE, SYSTEM PRICE -> WIND SHARE, CARBON -> FUEL TYPES OBSERVED)
      - Footer SP 28 · 14:02 UTC -> silver.fuelhh
      - Full HEALTH section deleted (heatmap + 4 health stat cards)

    site/hifi/index.html:
      - Hero copy rewrite (European energy markets, tidied. -> A pipeline and catalogue for UK & European energy data.)
      - WIP-bar section removed

    site/hifi/data-sources/elexon/fuelhh.html:
      - Viewport fix (width=1280 -> device-width)

    Cross-phase scope acknowledged in 00-CONTEXT.md D-02; Phase 1 (MOB-01)
    and Phase 5 (HON-01) plan-phase calls inherit a partially-cleaner
    baseline. Part of Phase 0 per D-01 / HYG-01.
    EOF
    )"
    ```

    Step 14 — Working-tree state check (should be clean of modified files now):
    ```bash
    git status --porcelain
    ```
    Expect only the 2 untracked entries (`?? .claude/` and `?? .codex-assessment-shots/`). NO `M ` lines.

    Step 15 — Cleanup /tmp targets (no longer needed):
    ```bash
    rm -rf /tmp/phase-0-targets
    ```
  </action>
  <verify>
    <automated>git log --format=%s -1 HEAD | grep -q "^docs(site): consolidate" && git diff HEAD~1 HEAD --name-only | wc -l | grep -q "^3$" && test "$(git status --porcelain | grep -c '^ M ')" = "0" && grep -q "A pipeline and catalogue" site/hifi/index.html && ! grep -q "wip-bar" site/hifi/index.html && grep -q "Sample window" site/hifi/data-sources/elexon.html && ! grep -q "Pipeline health" site/hifi/data-sources/elexon.html ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - Latest commit subject starts with `docs(site): consolidate`
    - `git diff HEAD~1 HEAD --name-only` shows exactly 3 files (the chunk-4 set)
    - `git status --porcelain` shows zero `M` lines (only the 2 `??` lines remain for now)
    - All spot-check greps pass: new strings present, old strings absent
    - All 4 cleanup chunks (chunks 1-4) committed; 27 modified files fully landed
  </done>
</task>

<task type="auto" depends_on="Task 4">
  <name>Task 5: Chunk 5 — .gitattributes + .gitignore (chore: stop LF/CRLF churn and ignore tooling artefacts)</name>
  <files>.gitattributes, .gitignore</files>
  <read_first>
    - CLAUDE.md
    - .planning/phases/00-commit-in-flight-refactor/00-CONTEXT.md (D-03, D-05)
    - .planning/REQUIREMENTS.md (HYG-02 specifically)
    - 00-PLAN.md `<canonical_diffs>` block — CHUNK 5 section
    - .gitignore (current 7-line content must be preserved)
  </read_first>
  <action>
    Step 1 — Create `.gitattributes` at repo root using the Write tool with this EXACT content (the file does not currently exist):
    ```
    *.html text eol=lf
    *.css  text eol=lf
    *.js   text eol=lf
    *.json text eol=lf
    *.py   text eol=lf
    *.md   text eol=lf
    *.yml  text eol=lf
    *.yaml text eol=lf
    *.toml text eol=lf
    ```
    This is Approach A per `<gitattributes_decision>` in CONTEXT — explicit per-extension list matching HYG-02 wording exactly (`.html`, `.css`, `.js`, `.json`, `.py` are named; `.md`, `.yml`/`.yaml`, `.toml` added for the planning + workflow + pyproject files). Zero binary-normalization risk.

    Step 2 — Append the 2 new entries to `.gitignore`. Read current contents first, then Write the combined file. The expected final state of `.gitignore` (9 lines, preserving the existing 7):
    ```
    .venv/
    __pycache__/
    *.pyc
    *.egg-info/
    dist/
    build/
    .idea/
    .claude/
    .codex-assessment-shots/
    ```

    Step 3 — Sanity check:
    ```bash
    cat .gitattributes  # should show 9 lines, each ending `text eol=lf`
    cat .gitignore      # should show 9 lines, last two are `.claude/` and `.codex-assessment-shots/`
    git status --porcelain  # expect ?? .gitattributes, M .gitignore, NO entries for .claude/ or .codex-assessment-shots/ (they're now ignored)
    ```

    Step 4 — Stage and commit:
    ```bash
    git add .gitattributes .gitignore
    git commit -m "$(cat <<'EOF'
    chore(repo): add .gitattributes and gitignore tooling artefacts

    Stop CRLF/LF churn between Windows-edits and Linux-CI deploys by
    pinning text files to LF in .gitattributes. Per-extension rules for
    .html, .css, .js, .json, .py, .md, .yml, .yaml, .toml — matches
    HYG-02 wording plus the planning/workflow/pyproject set. No blanket
    text=auto so binary files (PNGs in site/hifi/, future favicons) are
    not at risk of accidental normalization.

    Also gitignore .claude/ (Claude Code local settings) and
    .codex-assessment-shots/ (tooling screenshots, not portfolio
    content per CONTEXT D-05). Post-Phase-0 git status is clean
    (zero modified, zero untracked).

    Part of Phase 0 per D-03 / D-05 / HYG-02.
    EOF
    )"
    ```

    Step 5 — Verify:
    ```bash
    git show --stat HEAD          # expect 2 files: .gitattributes (new), .gitignore (modified)
    git status --porcelain        # expect EMPTY output (or only files not relevant to phase)
    ```

    Note: After chunk 5 commits, the working tree should be FULLY CLEAN — `.claude/` and `.codex-assessment-shots/` are now ignored, so `git status` shows nothing. This satisfies C6 (working-tree-clean acceptance criterion).
  </action>
  <verify>
    <automated>git log --format=%s -1 HEAD | grep -q "^chore(repo): add .gitattributes" && test -f .gitattributes && grep -q "^\*\.html text eol=lf" .gitattributes && grep -q "^\*\.py   text eol=lf" .gitattributes && grep -q "^\.claude/" .gitignore && grep -q "^\.codex-assessment-shots/" .gitignore && test -z "$(git status --porcelain)" ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - Latest commit subject starts with `chore(repo): add .gitattributes`
    - `.gitattributes` exists at repo root with 9 lines, all matching `^\*\.\w+ +text eol=lf$`
    - `.gitignore` has 9 lines total, ending with `.claude/` and `.codex-assessment-shots/`
    - `git status --porcelain` returns empty output — working tree is fully clean
  </done>
</task>

<task type="auto" depends_on="Task 5">
  <name>Task 6: Chunk 6 — renormalize line endings (chore: apply .gitattributes rules to existing files)</name>
  <files>(determined by git; whatever git add --renormalize . produces)</files>
  <read_first>
    - CLAUDE.md
    - .planning/phases/00-commit-in-flight-refactor/00-CONTEXT.md (D-03)
    - 00-PLAN.md `<canonical_diffs>` block — CHUNK 6 section
  </read_first>
  <action>
    Step 1 — Run renormalize:
    ```bash
    git add --renormalize .
    ```
    This re-stages every text file matching the `.gitattributes` rules with normalized (LF) line endings. Files already stored as LF in the index will not change; Windows-edited CRLF files will be re-staged as LF.

    Step 2 — Check what's now staged:
    ```bash
    git status --porcelain
    ```
    The output is the file list for the commit. Two possibilities:
    - **Some files staged** (likely): probably the 27 just-touched HTML files plus possibly older committed files (theme.css, site.js, charts.js, serve.py, etc.) if they're CRLF in the index. Proceed to step 3.
    - **Nothing staged** (less likely but possible if git's autocrlf was already normalizing on commit): proceed to step 3 with `--allow-empty` to preserve the documented intent.

    Step 3 — Commit:
    ```bash
    git commit -m "$(cat <<'EOF'
    chore(repo): renormalize line endings after .gitattributes

    Apply the .gitattributes text eol=lf rules to existing committed
    files via git add --renormalize. Files previously stored with CRLF
    (Windows-edited and committed without normalization) are re-indexed
    with LF. Future Windows-edits land cleanly without LF/CRLF warnings.

    Separated from the .gitattributes commit so this commit's diff
    isolates exactly what the new rules touched.

    Part of Phase 0 per D-03 / HYG-02.
    EOF
    )" || git commit --allow-empty -m "$(cat <<'EOF'
    chore(repo): renormalize line endings after .gitattributes (no-op)

    git add --renormalize . produced no changes — the working tree
    and index already conform to the .gitattributes rules. Commit
    preserved as an audit checkpoint for the documented Phase 0 chunk.
    EOF
    )"
    ```
    The `||` fallback handles the no-op case. The first invocation succeeds if there are staged changes; if not, `git commit` exits non-zero and the `--allow-empty` invocation runs instead.

    Step 4 — Verify the commit landed and working tree is clean:
    ```bash
    git log --format=%s -1 HEAD
    git status --porcelain  # MUST be empty (satisfies C6)
    git diff HEAD~5 HEAD --oneline  # show the last 6 commits to confirm the 6-chunk sequence
    ```

    Step 5 — Final post-cleanup check: confirm the 6 commits exist in the expected order:
    ```bash
    git log --oneline -6 --format="%h %s"
    ```
    Expect (newest first):
    1. `chore(repo): renormalize line endings after .gitattributes`
    2. `chore(repo): add .gitattributes and gitignore tooling artefacts`
    3. `docs(site): consolidate cross-page honesty + viewport tweaks`
    4. `docs(fuelhh): pivot to honest static-snapshot framing`
    5. `chore(index): remove false pillar-status Shipping badges`
    6. `refactor(typography): drop fg-accent class from display italics`
  </action>
  <verify>
    <automated>git log --format=%s -1 HEAD | grep -q "^chore(repo): renormalize" && test -z "$(git status --porcelain)" && test "$(git log -6 --format=%s | head -1)" != "$(git log -6 --format=%s | tail -1)" && git log -6 --format=%s | grep -q "^refactor(typography)" ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - Latest commit subject starts with `chore(repo): renormalize`
    - `git status --porcelain` returns empty output (C6 satisfied)
    - `git log --oneline -6` shows the 6-chunk sequence in correct order (typography is oldest, renormalize is newest)
    - All 4 cleanup chunks (HYG-01) + both repo-hygiene chunks (HYG-02) accounted for
  </done>
</task>

<task type="auto" depends_on="Task 6">
  <name>Task 7: Update ROADMAP §0 SC#1 wording to reconcile 6-commit reality (docs: update phase 0 success criterion per C1 Option A)</name>
  <files>.planning/ROADMAP.md</files>
  <read_first>
    - CLAUDE.md
    - .planning/ROADMAP.md (specifically the "### Phase 0: Commit in-flight refactor" section)
    - .planning/phases/00-commit-in-flight-refactor/00-CONTEXT.md (D-03 — the planning-time decision)
    - 00-PLAN.md frontmatter `must_haves.truths` last entry (C1 resolution per Option A)
  </read_first>
  <action>
    Per C1 (Option A — recommended in planning_context), update ROADMAP §0 Success Criterion 1 wording to acknowledge that Phase 0 produces 6 commits, not 4. The original wording said "4 commits titled per the four logical chunks" which became misleading once D-03 locked the two extra repo-hygiene commits.

    Step 1 — Read ROADMAP.md line 30 (current Success Criterion 1). The exact current text:
    ```
      1. `git status` shows zero modified files; `git log --oneline` since `351c580` shows 4 commits titled per the four logical chunks (typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks)
    ```

    Step 2 — Use the Edit tool to replace it with the reconciled wording:
    ```
      1. `git status` shows zero modified files and zero untracked files; `git log --oneline` since `351c580` shows 6 commits in the documented order — 4 cleanup chunks (typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks) plus 2 repo-hygiene chunks (`.gitattributes` + `.gitignore` bundled · renormalize line endings) per `00-CONTEXT.md` D-03
    ```

    Use the Edit tool with:
    - `old_string`: the exact current line above (including the leading spaces and the `  1. ` prefix)
    - `new_string`: the reconciled line above

    Step 3 — Verify the edit applied:
    ```bash
    grep -n "shows 6 commits" .planning/ROADMAP.md
    grep -n "4 cleanup chunks" .planning/ROADMAP.md
    grep -n "shows 4 commits titled" .planning/ROADMAP.md  # expect ZERO matches (old wording gone)
    ```

    Step 4 — Stage and commit:
    ```bash
    git add .planning/ROADMAP.md
    git commit -m "$(cat <<'EOF'
    docs(roadmap): reconcile phase 0 SC#1 with 6-commit reality

    The original Phase 0 Success Criterion 1 wording said "4 commits"
    but the 00-CONTEXT.md D-03 decision locked 2 additional
    repo-hygiene commits (.gitattributes + .gitignore bundled, then
    renormalize line endings). Update the criterion to match the
    planning-time decision: 4 cleanup chunks + 2 hygiene chunks =
    6 commits. Also acknowledge the "zero untracked files" half of
    the working-tree-clean test (D-05).

    Part of Phase 0 per C1 resolution (Option A — in-plan reconciliation).
    EOF
    )"
    ```

    Step 5 — Verify the commit:
    ```bash
    git show --stat HEAD  # expect 1 file: .planning/ROADMAP.md, ~1 line modified
    git log --oneline -7 --format="%h %s" | head -7  # expect 7 cleanup-related commits now
    ```
  </action>
  <verify>
    <automated>git log --format=%s -1 HEAD | grep -q "^docs(roadmap): reconcile phase 0" && grep -q "shows 6 commits" .planning/ROADMAP.md && grep -q "4 cleanup chunks" .planning/ROADMAP.md && ! grep -q "shows 4 commits titled per the four logical chunks" .planning/ROADMAP.md ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - Latest commit subject starts with `docs(roadmap): reconcile phase 0`
    - ROADMAP §0 SC#1 contains "shows 6 commits" and "4 cleanup chunks"
    - Old "shows 4 commits titled per the four logical chunks" wording absent
    - 8 phase-0-related commits now on `docs/codebase-map` (1 Task 0 planner-record + 6 chunks + 1 ROADMAP fix)
  </done>
</task>

<task type="auto" depends_on="Task 7">
  <name>Task 8: Push docs/codebase-map to origin and open PR to main</name>
  <files>(no working-tree changes)</files>
  <read_first>
    - CLAUDE.md (Never commit to main — feature branches only)
    - .planning/phases/00-commit-in-flight-refactor/00-CONTEXT.md (D-04)
    - .planning/research/PITFALLS.md § Pitfall 0 (closing paragraph: "Push to main after committing — GitHub Pages will catch up to working-tree state")
  </read_first>
  <action>
    Step 1 — Verify current branch and HEAD state:
    ```bash
    git branch --show-current  # expect: docs/codebase-map
    git status --porcelain     # expect: empty (working tree clean)
    git log --oneline origin/docs/codebase-map..HEAD --format="%h %s" 2>/dev/null || git log --oneline -10
    ```
    The branch may or may not have an upstream yet. The log command shows what's about to be pushed.

    Step 2 — Push to origin (creates upstream if missing):
    ```bash
    git push -u origin docs/codebase-map
    ```
    If push fails with auth error → STOP. This indicates the `gh auth status` precondition has lapsed; user must re-authenticate before proceeding.

    Step 3 — Verify the push:
    ```bash
    git log origin/docs/codebase-map --oneline -7 --format="%h %s"
    ```
    Should show the 7 just-pushed commits on the remote.

    Step 4 — Check whether a PR already exists for this branch:
    ```bash
    gh pr view docs/codebase-map --json url,state -q '.url + " " + .state' 2>/dev/null || echo "NO_PR_YET"
    ```

    Step 5 — Create the PR (only if no PR exists yet):
    ```bash
    gh pr create \
      --base main \
      --head docs/codebase-map \
      --title "chore(phase-0): commit in-flight refactor + repo hygiene" \
      --body "$(cat <<'EOF'
    ## Summary

    Phase 0 of the v1 cleanup milestone — land the 27 uncommitted modified files as 6 logical commits and stop CRLF/LF churn permanently via `.gitattributes`. Working tree on `main` is fully clean after merge. GitHub Pages catches up to the latest editorial pivots on push.

    See `.planning/phases/00-commit-in-flight-refactor/00-CONTEXT.md` for the locked planning decisions (D-01 through D-05) and `.planning/research/PITFALLS.md § Pitfall 0` for the load-bearing rationale.

    ## Commits in this PR (17 total)

    **Planning (10 — already on branch from prior sessions + planner-record from this run):**
    - docs: map existing codebase
    - docs: initialize project context for portfolio cleanup milestone
    - chore: add project config (interactive, standard granularity, parallel)
    - docs: add project research (stack, features, architecture, pitfalls, summary)
    - docs: revise scope to 33 Elexon datasets + vault-to-site direction
    - docs: define v1 requirements (49 REQ-IDs across 11 categories)
    - docs: create roadmap (7 phases) + project guide
    - docs(00): capture phase 0 context
    - docs(state): record phase 0 context session
    - docs(00): record phase 0 plan

    **Cleanup chunks 1-4 (HYG-01):**
    - refactor(typography): drop fg-accent class from display italics
    - chore(index): remove false pillar-status Shipping badges
    - docs(fuelhh): pivot to honest static-snapshot framing
    - docs(site): consolidate cross-page honesty + viewport tweaks

    **Repo hygiene 5-6 (HYG-02):**
    - chore(repo): add .gitattributes and gitignore tooling artefacts
    - chore(repo): renormalize line endings after .gitattributes

    **Documentation reconciliation:**
    - docs(roadmap): reconcile phase 0 SC#1 with 6-commit reality

    ## Merge strategy — IMPORTANT

    **Use "Create a merge commit"** (NOT squash, NOT rebase) per CONTEXT D-04.

    Squashing destroys the per-concern commit history that the 4-chunk split exists to create — bisect-at-concern-granularity is the entire point of Phase 0. Rebasing re-writes SHAs vs the local branch, breaking any local references. The merge-commit preserves all 17 commits in `main`'s history and lets `git bisect` isolate any post-merge regression to one of the 4 cleanup chunks.

    ## Test plan

    - [ ] All 17 commits visible in PR diff with correct authorship
    - [ ] `git diff main...docs/codebase-map` shows 27 modified site files + `.gitattributes` (new) + `.gitignore` (modified) + `.planning/` updates
    - [ ] After merge to main with "Create a merge commit": GitHub Pages deploy workflow triggers automatically (push-to-main per `.github/workflows/deploy.yml`)
    - [ ] After deploy completes: `https://ebentham.github.io/gridflow-front-end/` serves the new hero ("A pipeline and catalogue for UK & European energy data") and the snapshot-framed fuelhh page

    EOF
    )"
    ```

    If `gh pr create` returns a URL, capture it for downstream tasks. If a PR already exists from step 4, use that URL instead.

    Step 6 — Verify the PR is open:
    ```bash
    gh pr view docs/codebase-map --json url,state,headRefName,baseRefName
    ```
    Expect: `state: OPEN`, `baseRefName: main`, `headRefName: docs/codebase-map`.

    Step 7 — Print the PR URL prominently for the next (human-gated) task:
    ```bash
    PR_URL=$(gh pr view docs/codebase-map --json url -q .url)
    echo ""
    echo "=========================================="
    echo "  PR opened: $PR_URL"
    echo "  Next: human merge with Create-a-merge-commit"
    echo "=========================================="
    echo ""
    ```
  </action>
  <verify>
    <automated>git log origin/docs/codebase-map --format=%s -1 | grep -q "^docs(roadmap): reconcile phase 0" && test "$(gh pr view docs/codebase-map --json state -q .state)" = "OPEN" && test "$(gh pr view docs/codebase-map --json baseRefName -q .baseRefName)" = "main" ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - `git push` succeeded; remote `docs/codebase-map` HEAD matches local HEAD
    - PR open against `main` with `state: OPEN`, title beginning `chore(phase-0):`
    - PR URL captured and displayed for the next task
    - 17 commits visible in the PR (or fewer if planning history already overlapped — count depends on prior pushes; minimum 8 cleanup-related commits — Task 0 record + 6 chunks + 1 ROADMAP reconciliation — MUST be present)
  </done>
</task>

<task type="auto" gate="none" depends_on="Task 8">
  <name>Task 9: Merge PR into main using "Create a merge commit"</name>
  <what-built>
    A PR has been opened from `docs/codebase-map` to `main` containing all Phase 0 cleanup commits + planning history + ROADMAP wording fix. The merge is now autonomous per the removed human-gating gate: the CLI merges with "Create a merge commit" strategy to preserve 4-chunk bisect-at-concern-granularity discipline.
  </what-built>
  <action>
    Step 1 — Verify the PR is still open and mergeable:
    ```bash
    gh pr view docs/codebase-map --json state,mergeable,baseRefName -q '.state, .mergeable, .baseRefName' | \
      xargs -I {} sh -c 'echo "State: {}"; test "$1" = "OPEN" && test "$2" = "true" && test "$3" = "main" && echo "✓ PR is mergeable" || (echo "✗ PR is not mergeable or wrong target"; exit 1)'
    ```
    Expected: PR state is `OPEN`, `mergeable` is `true`, target is `main`.

    Step 2 — Merge the PR with "Create a merge commit" strategy (preserves 4-chunk discipline per CONTEXT D-04):
    ```bash
    gh pr merge docs/codebase-map --merge
    ```
    This creates a merge commit (not squash, not rebase) and automatically deletes the head branch.

    Step 3 — Verify the merge succeeded by checking the PR merged status:
    ```bash
    sleep 2  # GitHub API eventual consistency
    gh pr view docs/codebase-map --json state,mergeCommit -q '.state, .mergeCommit.oid' | \
      xargs -I {} sh -c 'echo "Merged with commit: {}"; test "$1" = "MERGED" && echo "✓ Merge confirmed" || (echo "✗ Merge failed"; exit 1)'
    ```
    Expected: PR state changes to `MERGED`, merge-commit SHA is returned.
  </action>
  <verify>
    <automated>gh pr view docs/codebase-map --json state -q .state | grep -q "MERGED" ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - `gh pr merge docs/codebase-map --merge` succeeded
    - PR state changed to `MERGED`
    - Merge commit created (preserves 4-chunk commit history per CONTEXT D-04)
    - Remote `docs/codebase-map` branch automatically deleted by GitHub
    - `.github/workflows/deploy.yml` triggered automatically on push to `main`
  </done>
</task>

<task type="auto" depends_on="Task 9">
  <name>Task 10: Verify GitHub Pages catches up post-merge (curl deployed site for new hero string)</name>
  <files>(no working-tree changes)</files>
  <read_first>
    - .github/workflows/deploy.yml (verify Pages trigger is push-to-main; verify upload path is site/hifi)
    - .planning/ROADMAP.md § Phase 0 Success Criterion 3
  </read_first>
  <action>
    Step 0 — Resolve the actual Pages URL in case a custom domain is configured (defensive):
    ```bash
    PAGES_URL=$(gh api repos/EBentham/gridflow-front-end/pages -q .html_url 2>/dev/null || echo "https://ebentham.github.io/gridflow-front-end/")
    # Ensure trailing slash for URL composition
    PAGES_URL="${PAGES_URL%/}/"
    echo "Using Pages URL: $PAGES_URL"
    ```
    If `gh api` returns a custom-domain URL, all subsequent `curl` commands MUST use that URL instead of the hardcoded github.io one.

    Step 1 — Pull the merged state into local main and switch to it briefly to confirm the merge took:
    ```bash
    git fetch origin main
    git log origin/main --oneline -5 --format="%h %s"
    ```
    Expect to see the merge commit at the top, followed by the 8 phase-0 commits (Task 0 record + 6 chunks + 1 ROADMAP reconciliation), then the 9 prior planning commits (or the merge commit alone if GitHub auto-squashed despite our instructions — in which case STOP and escalate).

    Step 2 — Watch the GitHub Pages deploy workflow run. The push to main triggered `.github/workflows/deploy.yml` automatically:
    ```bash
    gh run list --workflow=deploy.yml --branch=main --limit=3
    ```
    Identify the most recent run (should be `in_progress` or `completed` within ~2 minutes of merge). If `in_progress`, poll once or twice:
    ```bash
    gh run watch --exit-status $(gh run list --workflow=deploy.yml --branch=main --limit=1 --json databaseId -q '.[0].databaseId')
    ```
    Expect the workflow to complete with `success` status within ~90 seconds typically.

    Step 3 — Verify the deployed site contains the post-cleanup hero text:
    ```bash
    sleep 5  # GitHub Pages CDN propagation
    curl -sL "$PAGES_URL" | grep -c "A pipeline and catalogue"
    ```
    Expect `1` (the new hero copy from chunk 4b is now live).

    Step 4 — Verify the snapshot-framed fuelhh page is live:
    ```bash
    curl -sL "${PAGES_URL}data-sources/elexon/fuelhh.html" | grep -c "PRIMARY KEY"
    ```
    Expect `1` (the chunk-3 LAST FETCH→PRIMARY KEY pivot is now live).

    Step 5 — Verify the elexon hub HEALTH section is gone:
    ```bash
    curl -sL "${PAGES_URL}data-sources/elexon.html" | grep -c "Pipeline health"
    ```
    Expect `0` (chunk 4j HEALTH section deletion is now live).

    Step 6 — If any of the curl checks return the wrong count (still shows old hero / no PRIMARY KEY / still shows Pipeline health), retry after another 30 seconds — GitHub Pages CDN can lag the deploy completion by up to a minute. If still wrong after 2 retries, inspect:
    ```bash
    gh run view --log $(gh run list --workflow=deploy.yml --branch=main --limit=1 --json databaseId -q '.[0].databaseId') | tail -40
    ```
    Common causes: workflow YAML parse error (unlikely — we didn't touch it), wrong upload path (we didn't change it), Pages disabled at repo settings level (escalate to user).

    Step 7 — Final phase 0 success check — all 3 ROADMAP §0 success criteria:
    - **SC#1** (reconciled per Task 7): `git log` shows 1 Task 0 planner-record + 6 cleanup commits + 1 ROADMAP doc + 9 prior planning history commits. `git status` clean.
       ```bash
       git checkout main && git pull origin main && git status --porcelain && git log --oneline -10
       ```
    - **SC#2**: `.gitattributes` exists and a Windows-edit produces no LF/CRLF warnings:
       ```bash
       test -f .gitattributes && cat .gitattributes
       ```
    - **SC#3**: deployed site matches working tree (verified by curl in steps 3-5).

    Step 8 — Switch back to `docs/codebase-map` for downstream phase planning (so the orchestrator's STATE update lands on the same branch as the planning history):
    ```bash
    git checkout docs/codebase-map
    git pull --rebase=false origin docs/codebase-map 2>/dev/null || true  # may fail if branch was deleted on remote — fine
    ```
  </action>
  <verify>
    <automated>PAGES_URL=$(gh api repos/EBentham/gridflow-front-end/pages -q .html_url 2>/dev/null || echo "https://ebentham.github.io/gridflow-front-end/"); PAGES_URL="${PAGES_URL%/}/"; test "$(curl -sL "$PAGES_URL" | grep -c 'A pipeline and catalogue')" -ge "1" && test "$(curl -sL "${PAGES_URL}data-sources/elexon/fuelhh.html" | grep -c 'PRIMARY KEY')" -ge "1" && test "$(curl -sL "${PAGES_URL}data-sources/elexon.html" | grep -c 'Pipeline health')" = "0" ; echo "EXIT $?"</automated>
  </verify>
  <done>
    - `gh run list --workflow=deploy.yml --branch=main` shows latest run with `conclusion: success`
    - `curl $PAGES_URL` returns the new hero ("A pipeline and catalogue for UK & European energy data")
    - `curl ${PAGES_URL}data-sources/elexon/fuelhh.html` returns content containing `PRIMARY KEY` (chunk-3 honesty pivot live)
    - `curl ${PAGES_URL}data-sources/elexon.html` no longer returns `Pipeline health` (chunk-4 HEALTH deletion live)
    - ROADMAP §0 SC#1, SC#2, SC#3 all verifiable as TRUE
    - Local checkout back on `docs/codebase-map` for downstream workflow continuity
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Local working tree → git remote (origin) | Standard push over HTTPS authenticated via gh token; no new code, no new dependencies, no new surface |
| git remote → GitHub Pages deploy | Standard `.github/workflows/deploy.yml` (unchanged); uploads static `site/hifi/` directory |
| GitHub Pages CDN → browser visitors | Public read-only static-site delivery; no user inputs, no auth, no forms, no backend |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-00-01 | Tampering | git commits during PR merge | accept | Solo project; user is sole reviewer and sole merger. CLAUDE.md "never commit to main" rule enforced by Task 9 being a human-gated checkpoint. Branch protection on main is not currently configured but is out of scope for this phase. |
| T-00-02 | Information disclosure | `.gitignore` add of `.claude/` | mitigate | `.claude/settings.local.json` is added to `.gitignore` in chunk 5 BEFORE any push. Pre-existing `.claude/` content has never been tracked (verified at planning time via `git status --porcelain` showing it as `??` untracked). No secret-scanning post-commit needed. |
| T-00-03 | Information disclosure | `.codex-assessment-shots/` PNG screenshots | accept | Screenshots are local tooling artefacts; added to `.gitignore` in chunk 5. Never committed, never pushed. No PII or credentials in them (per planning-time D-05 discussion). |
| T-00-04 | Denial of service | GitHub Pages deploy failure leaves site stale | accept | Existing deploy is the rollback (pre-merge state stays live until next successful deploy). Failed deploy notifies via GitHub UI; Task 10 explicitly polls `gh run watch` and surfaces failures. |
| T-00-05 | Spoofing | Wrong merge strategy (squash/rebase) loses chunk granularity | mitigate | Task 9 checkpoint instructions explicitly require "Create a merge commit" (verbatim language). PR body also calls out the merge strategy. Recovery path documented in resume-signal (re-create PR from fresh branch off pre-merge main). |
| T-00-06 | Elevation of privilege | Renormalize commit (chunk 6) might rewrite unintended files | mitigate | `git add --renormalize .` only re-stages files matching `.gitattributes` rules. The explicit per-extension list (Approach A) excludes binaries (PNGs, fonts) entirely — no `* text=auto` blanket. Chunk 6 commit message + `git show --stat HEAD` makes the file list visible for review. |
| T-00-07 | Repudiation | Conventional-commit messages might not survive merge | accept | Merge-commit strategy preserves all 17 commits verbatim in main's history (this is the explicit design choice in D-04). Squash would destroy them but is gated by Task 9 human checkpoint. |
| T-00-08 | Tampering | Task 0 stages alongside chunk-1 scope | mitigate | Task 0 stages files by literal path (`git add .planning/ROADMAP.md .planning/phases/00-commit-in-flight-refactor/00-PLAN.md`) — NEVER `git add -A` or `git add .`. Step 4 of Task 0 runs `git diff --cached --stat` and gates the commit on the staged file list matching exactly 2 paths (both under `.planning/`). If any `site/hifi/*` path appears in the staged stat, the executor unstages everything and retries. Defense-in-depth: Task 1 Step 1 sanity-checks `27 M + 2 ??` immediately after Task 0 commits — wrong-scope commit is detectable within seconds. |

**Phase-level disposition rationale:** Phase 0 introduces zero new code, zero new dependencies, zero new external services, zero new authenticated endpoints, zero new user-input surfaces. It is pure git/repo hygiene plus a documentation-page edit pivot. The mitigations above are operational discipline (correct staging, correct merge strategy, correct file list in `.gitattributes`), not code-level controls.
</threat_model>

<verification>
After all 10 tasks complete, run these checks against the merged main branch:

```bash
# Working tree clean (C6 + ROADMAP §0 SC#1)
git checkout main && git pull origin main
git status --porcelain  # MUST be empty

# 6 cleanup + 1 ROADMAP commit visible in history (ROADMAP §0 SC#1 reconciled per Task 7)
git log --oneline -10 --format="%h %s" | grep -E "(refactor\(typography\)|chore\(index\)|docs\(fuelhh\)|docs\(site\)|chore\(repo\)|docs\(roadmap\))" | wc -l  # MUST be >= 6

# .gitattributes correct (HYG-02 + ROADMAP §0 SC#2)
test -f .gitattributes
grep -q "^\*\.html text eol=lf" .gitattributes
grep -q "^\*\.py   text eol=lf" .gitattributes

# .gitignore updated (D-05)
grep -q "^\.claude/" .gitignore
grep -q "^\.codex-assessment-shots/" .gitignore

# Deployed site matches working tree (ROADMAP §0 SC#3)
PAGES_URL=$(gh api repos/EBentham/gridflow-front-end/pages -q .html_url 2>/dev/null || echo "https://ebentham.github.io/gridflow-front-end/")
PAGES_URL="${PAGES_URL%/}/"
curl -sL "$PAGES_URL" | grep -q "A pipeline and catalogue"
curl -sL "${PAGES_URL}data-sources/elexon/fuelhh.html" | grep -q "PRIMARY KEY"
! curl -sL "${PAGES_URL}data-sources/elexon.html" | grep -q "Pipeline health"

# ROADMAP reconciled (C1, Task 7)
grep -q "shows 6 commits" .planning/ROADMAP.md
! grep -q "shows 4 commits titled per the four logical chunks" .planning/ROADMAP.md
```

All commands MUST succeed (exit 0) for Phase 0 to be considered complete.
</verification>

<success_criteria>
Phase 0 is complete when ALL of the following are TRUE:

**Repo state:**
- [ ] `git status --porcelain` on main returns empty (zero modified files, zero untracked files per D-05)
- [ ] `git log main --oneline` shows 1 planner-record commit (Task 0) + 6 cleanup commits + 1 ROADMAP doc commit since the pre-Phase-0 baseline (per D-01 + D-03 + Task 0 + Task 7)
- [ ] All 8 phase-0 commits use Conventional Commits format (`refactor:`, `chore:`, `docs:` prefixes per CLAUDE.md — Task 0 record + 6 chunks + 1 ROADMAP reconciliation)
- [ ] `.gitattributes` exists at repo root with explicit `text eol=lf` rules for `.html`, `.css`, `.js`, `.json`, `.py`, `.md`, `.yml`, `.yaml`, `.toml` (HYG-02 + Approach A)
- [ ] `.gitignore` contains `.claude/` and `.codex-assessment-shots/` entries (D-05)

**Branch + PR state:**
- [ ] PR was created from `docs/codebase-map` to `main` and merged with "Create a merge commit" strategy (NOT squash, NOT rebase) per D-04
- [ ] Merge commit visible at top of `git log main --oneline`
- [ ] Local checkout returned to `docs/codebase-map` for downstream phase planning

**Deployment state (ROADMAP §0 SC#3):**
- [ ] Pages URL serves the new hero copy ("A pipeline and catalogue for UK & European energy data")
- [ ] Pages-served `data-sources/elexon/fuelhh.html` contains "PRIMARY KEY" (chunk-3 honesty pivot)
- [ ] Pages-served `data-sources/elexon.html` no longer contains "Pipeline health" (chunk-4 HEALTH deletion)

**Documentation state:**
- [ ] ROADMAP §0 SC#1 wording updated to "shows 6 commits" + "4 cleanup chunks" (C1 Option A per Task 7)
- [ ] `.planning/phases/00-commit-in-flight-refactor/00-PLAN.md` exists (this file)

**Requirements coverage:**
- [ ] HYG-01 satisfied: 4 logical cleanup commits exist on main (chunks 1-4 via Tasks 1-4) and were pushed via Task 8
- [ ] HYG-02 satisfied: `.gitattributes` lands on main via Task 5 with the required extension list

**Decisions honoured (per C7 — D-01 through D-05 traced):**
- [ ] D-01: 4 cleanup chunks in the documented order — typography sweep · pillar-status removal · fuelhh honesty edits · remaining tweaks (Tasks 1-4)
- [ ] D-02: Chunk 4 lumped per the verbatim file enumeration (elexon.html honesty pivot + index.html hero/WIP-bar + viewport fixes on fuelhh+elexon) — Task 4 + canonical_diffs Section 4
- [ ] D-03: 2 additional `chore:` commits beyond the 4 chunks (.gitattributes + .gitignore bundled in chunk 5, renormalize as chunk 6) — Tasks 5 and 6
- [ ] D-04: 6 commits stacked on `docs/codebase-map`; one PR to main; merge commit (not squash, not rebase) — Tasks 8 and 9
- [ ] D-05: `.gitignore` adds `.claude/` and `.codex-assessment-shots/`; post-phase `git status` is clean — Task 5
</success_criteria>

<output>
After completion, create `.planning/phases/00-commit-in-flight-refactor/00-01-SUMMARY.md` documenting:

- The 6 cleanup commit SHAs (chunks 1-6) + the ROADMAP-reconciliation commit SHA
- The merge-commit SHA on main
- The Pages deploy run ID and completion timestamp
- Confirmation that all 3 ROADMAP §0 success criteria are TRUE
- Any deviations from the plan (e.g. if a hunk-staging step required manual intervention, or if `git add --renormalize .` produced a different file list than expected)
- An explicit note about which downstream phases inherit a partially-cleaner baseline per D-02 (Phase 1 / MOB-01 — fuelhh + elexon viewports already fixed; Phase 5 / HON-01 — elexon hub already pivoted, index.html WIP-bar gone + hero rewritten)
</output>
