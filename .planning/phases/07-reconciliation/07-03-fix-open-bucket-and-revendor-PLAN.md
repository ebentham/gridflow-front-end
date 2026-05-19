---
id: 07-03-fix-open-bucket-and-revendor
phase: 07-reconciliation
plan: 03
type: execute
wave: 2
depends_on:
  - 07-02-run-verification-and-triage
files_modified:
  # Upstream Vault edits (the source-of-truth changes):
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndf.md"
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndfd.md"
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/fuelhh.md"
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsoe/datasets/"        # 18 files for `resolution` nullability
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/hydrogen_content.md"
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/interruptions.md"
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/methane_content.md"
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/oxygen_content.md"
  - "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md"
  # Vendored snapshot in gridflow-front-end (the consumer-side mirror):
  - "vault/elexon/ndf.md"
  - "vault/elexon/ndfd.md"
  - "vault/elexon/fuelhh.md"
  - "vault/entsoe/"                                                                              # 18 ENTSO-E files re-vendored
  - "vault/entsog/hydrogen_content.md"
  - "vault/entsog/interruptions.md"
  - "vault/entsog/methane_content.md"
  - "vault/entsog/oxygen_content.md"
  - "vault/entsog/physical_flows.md"
  # Finding-file closure notes:
  - ".planning/reconciliation/elexon/01-ndf-schema-table-missing-published-at.md"                # appended `## Comments` with closed-at
  - ".planning/reconciliation/elexon/02-ndfd-schema-table-missing-published-at.md"
  - ".planning/reconciliation/elexon/04-fuelhh-schema-table-missing-published-at.md"
  - ".planning/reconciliation/elexon/03-ndf-national-demand-nullability-mismatch.md"
  - ".planning/reconciliation/entsoe/"                                                            # 18 resolution-nullability findings closed
  - ".planning/reconciliation/entsog/01-hydrogen-content-http-404.md"
  - ".planning/reconciliation/entsog/02-interruptions-http-404.md"
  - ".planning/reconciliation/entsog/03-methane-content-http-404.md"
  - ".planning/reconciliation/entsog/04-oxygen-content-http-404.md"
  - ".planning/reconciliation/entsog/05-physical-flows-schema-table-rewrite.md"
requirements:
  - RECON-03
  - RECON-05
autonomous: false   # contains a checkpoint:human-verify gate for the CI re-run sanity check
must_haves:
  truths:
    - "Every `status: open` finding in `.planning/reconciliation/*/` has had its acceptance Vault edit landed; the finding file is updated with `status: closed` + a `closed-at:` date + a comment recording the fix"
    - "The 5 load-bearing fixes are concrete and visible in the upstream Vault: `published_at` row added to ndf/ndfd/fuelhh schema tables; 18 ENTSO-E `resolution` rows marked Nullable=Yes; 4 ENTSO-G 404 endpoints handled (delete OR `removed:` frontmatter flag); `physical_flows.md` schema table rewritten to `flow_gwh_per_day` + `timestamp_utc`"
    - "The vendored snapshot under `gridflow-front-end/vault/<vendor>/` matches the upstream Vault byte-equivalently for every edited file"
    - "`gridflow-drift-check` re-runs and produces zero new `Missing in docs:` / `Nullable mismatch:` / HTTP 404 findings beyond the documented `wontfix-v3` / `needs-info` bucket"
    - "v1 CI gates pass on `gridflow-front-end` after the re-vendor: `htmlhint`, `lychee --offline --include-fragments`, `gridflow-build --check` all exit 0"
  artifacts:
    - path: "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndf.md"
      provides: "`published_at` row added to schema table; metadata `Point-in-time field` updated from `issue_time` to `published_at`"
      contains: "published_at"
    - path: "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md"
      provides: "Schema table rewritten to `flow_gwh_per_day` + `timestamp_utc`; raw response keys (if useful) preserved in a `## Bronze response keys` prose section"
      contains: "flow_gwh_per_day"
    - path: "vault/elexon/ndf.md"
      provides: "Vendored snapshot byte-equivalent to upstream after re-vendor"
      contains: "published_at"
  key_links:
    - from: "Upstream Vault edits in `quant-vault/30-vendors/<vendor>/datasets/`"
      to: "Vendored snapshot in `gridflow-front-end/vault/<vendor>/`"
      via: "manual `cp` per file (inertia per ADR-0002: 'vendoring pattern preserved'; v1 used manual copy)"
      pattern: "diff -q vault/<vendor>/<dataset>.md C:/Users/.../quant-vault/30-vendors/<vendor>/datasets/<dataset>.md"
    - from: "Each `open` finding file"
      to: "Its closure record in `## Comments`"
      via: "`closed-at: YYYY-MM-DD` + commit hash + status change to `closed`"
      pattern: "^closed-at:"
    - from: "Re-run `gridflow-drift-check` output"
      to: "07-02 baseline (pre-fix) report"
      via: "Verify the `Missing in docs: published_at` / 404 / 35-field-mismatch findings are GONE"
      pattern: "grep -c 'Missing in docs: published_at' vault-curl-schema-validation.md"
---

<objective>
Land the Vault edits for every `status: open` finding produced by 07-02; re-vendor the edited files into `gridflow-front-end/vault/<vendor>/` byte-equivalently; re-run `gridflow-drift-check` to confirm only documented `wontfix-v3` / `needs-info` Drift remains; verify v1 CI gates (`htmlhint`, `lychee --offline --include-fragments`, `gridflow-build --check`) stay green on the regenerated set.

Purpose: close the `open` triage bucket and prove the Vault layer is trustworthy as the input for content phases 9 and 10. RECON-03 + RECON-05 are the dual acceptance gates.

Output: Edits committed to BOTH the upstream `quant-vault` (which 07-04 will push to private GitHub) AND the vendored snapshot at `gridflow-front-end/vault/<vendor>/` (which the build pipeline consumes); finding files updated to `status: closed` with closure metadata; a re-run drift-check report showing zero new Drift; passing CI gates.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@CLAUDE.md
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/07-reconciliation/07-CONTEXT.md
@.planning/phases/07-reconciliation/07-02-SUMMARY.md
@.planning/research/post-v1/drift-detection/DRIFT-SURFACES.md
@CONTEXT.md

<canonical_field_definitions>
<!-- These are the source-of-truth Pydantic declarations the Vault edits must    -->
<!-- mirror. Read the actual files in gridflow before editing the Vault — line   -->
<!-- numbers may have shifted.                                                   -->

From `C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/elexon.py`:

```python
# ElexonFuelHH — line ~79 onwards (read the file to confirm)
class ElexonFuelHH(BaseModel):
    settlement_date: date
    settlement_period: int
    fuel_type: str
    generation_mw: float
    published_at: datetime | None = None       # L87 — this is the field the Vault is missing on fuelhh.md

# ElexonDemandForecast — line ~185 onwards (covers both NDF and NDFD via forecast_type discriminator)
class ElexonDemandForecast(BaseModel):
    settlement_date: date
    settlement_period: int
    forecast_type: str                         # L191 — "ndf" or "ndfd"
    national_demand_mw: float                  # L192 — NON-NULLABLE in canonical (not `float | None`)
    published_at: datetime | None              # L194 — this is the field the Vault names `issue_time` and omits
```

(Confirm the actual canonical declarations in `gridflow/src/gridflow/schemas/elexon.py` before editing the Vault — line numbers above are from drift research and may have shifted.)
</canonical_field_definitions>

<vault_edit_specifications>
<!-- The exact text changes 07-03 lands in the upstream Vault. These are mechanical.  -->

### Fix 1 — `ndf.md` and `ndfd.md` (DRIFT-SURFACES § 4.1)

**File:** `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndf.md`

- Around line 99 (metadata block; confirm line by reading first): replace `**Point-in-time field**: issue_time` with `**Point-in-time field**: published_at`.
- Around line 111 (schema table; confirm line by reading first): the table currently has a row `| \`issue_time\` | \`datetime\` | Yes | \`issueTime\` | ... |`. Two options:
  - Option A (preferred): replace `issue_time` with `published_at` and source `issueTime` → `publishTime` (the canonical's source field per `elexon.py:194`).
  - Option B: if the Vault author has stylistic preference, KEEP the `issue_time` row AND add a new `published_at` row — but then verifier still flags `Extra in docs: issue_time`. Default to Option A unless evidence in `vault-amendment-plan.md` says otherwise.

  Concrete inserted row:
  ```
  | `published_at` | `datetime` | Yes | `publishTime` | Publication time of the forecast (Canonical: ElexonDemandForecast.published_at, elexon.py:194) |
  ```

- Same file, the `national_demand_mw` row (around line 109): change Nullable from `Yes` to `No` to match the Canonical's `float` (not `float | None`) declaration at `elexon.py:192`. This closes the Semantic part of § 4.1.

**File:** `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndfd.md`

- Same `published_at` / `issue_time` swap and `national_demand_mw` nullability change. The fix is structurally identical because `ElexonDemandForecast` covers both via `forecast_type`.

### Fix 2 — `fuelhh.md` (DRIFT-SURFACES § 4.2)

**File:** `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/fuelhh.md`

- Around line 103 (metadata block): the line `**Point-in-time field**: published_at` is ALREADY correct — the metadata claim matches the canonical. NO change here.
- Around lines 107-115 (schema table): the table currently omits the `published_at` row. ADD this row (at the bottom of the schema table, or in the position matching canonical field order — preserve readability):
  ```
  | `published_at` | `datetime` | Yes | `publishTime` | Publication time (Canonical: ElexonFuelHH.published_at, elexon.py:87; metadata claim at line 103 now matches table) |
  ```

  This closes the intra-file Drift documented in § 4.2 ("metadata says `published_at` but schema table omits it").

### Fix 3 — 18 ENTSO-E `resolution` field nullability flags (DRIFT-SURFACES § 4.1 Semantic equivalent, ENTSO-E scope)

**Files:** the 18 ENTSO-E dataset files under `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsoe/datasets/`. The exact list is enumerated in `quant-vault/30-vendors/vault-amendment-plan.md:147-170` — READ that file first to get the canonical list of 18 file paths.

Each file's schema table has a `resolution` row with Nullable currently EITHER blank or `No`. The canonical declares `Field(default=None, ...)` (nullable). Change every one to `Nullable: Yes`. Mechanical edit per file.

### Fix 4 — 4 ENTSO-G 404 endpoints (DRIFT-SURFACES § 4.5)

**Files:** `entsog/datasets/hydrogen_content.md`, `interruptions.md`, `methane_content.md`, `oxygen_content.md`.

**Decision the planner makes here (in plain text in finding-file closure notes):** delete the .md files OR mark them with a `removed:` frontmatter flag.

Recommended: **mark with `removed:` frontmatter flag**, NOT delete. Rationale: deletion loses the audit trail; a `removed:` flag lets the template/build script render distinctly (in a future Phase, not 07-03) and preserves the historical fact that these endpoints existed. The flag is non-load-bearing for v2 (the build script in v1 doesn't read it) but it's the lighter footprint.

Add to each file's frontmatter:
```yaml
removed: 2026-05-19
removed_reason: Vendor took the endpoint down; HTTP 404 from current API. See `.planning/reconciliation/entsog/<NN>-<slug>-http-404.md` for the Verification finding.
```

Do NOT delete the files. Future Vendor changes (a vendor un-removes an endpoint) would lose the audit context.

### Fix 5 — `physical_flows.md` schema-table rewrite (DRIFT-SURFACES § 4.6)

**File:** `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md`

Read the file first. The current schema table has ~29 "extra" fields (raw bronze response keys) and is missing the 2 derived silver columns. Per the verifier finding from § 4.6:
```
Missing in docs: flow_gwh_per_day, timestamp_utc
Extra in docs: booking_platform_key, booking_platform_label, ... (29 extras)
Nullable mismatch: direction_key, operator_key, operator_label, point_key, point_label, unit
```

Replace the existing schema table with:
```
| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `flow_gwh_per_day` | `float` | No | (derived from `value` × unit-conversion) | Daily physical flow in GWh, silver-layer derived |
| `timestamp_utc` | `datetime` | No | `periodFrom` | UTC-aware, derived in silver |
| `direction_key` | `str` | Yes | `directionKey` | (canonical name; nullable per silver schema) |
| `operator_key` | `str` | Yes | `operatorKey` | |
| `operator_label` | `str` | Yes | `operatorLabel` | |
| `point_key` | `str` | Yes | `pointKey` | |
| `point_label` | `str` | Yes | `pointLabel` | |
| `unit` | `str` | Yes | `unit` | |
```

Read the canonical at `gridflow/src/gridflow/schemas/entsog.py` (or wherever `EntsogPhysicalFlow` lives — confirm by `grep -rn 'physical_flow' gridflow/src/gridflow/schemas/`) to verify the exact field list and nullability. The above is the planner's best guess; the canonical wins.

Preserve the existing prose. Move the raw response keys discussion (the 29 "extras") into a new `## Bronze response keys` section at the bottom of the file IF the prose is useful for site narrative. The format:
```markdown
## Bronze response keys

The ENTSO-G physical-flows endpoint returns these raw keys in each bronze record. The silver layer consolidates them into the schema table above; raw keys are preserved here for reference only.

<paste the previous "29 extras" prose into this section>
```

This was the worst single-file Drift in the ecosystem per § 4.6 — the rewrite is load-bearing.
</vault_edit_specifications>

<revendor_mechanism>
<!-- ADR-0002 preserves the v1 vendoring pattern (manual copy). Use `cp` per file. -->
<!-- Do NOT introduce submodules, symlinks, or a Python helper in 07-03 — that's a -->
<!-- separate change that the user hasn't approved.                                -->

For each edited file in the upstream Vault, copy it to the corresponding location under `gridflow-front-end/vault/<vendor>/`. Map:

| Upstream                                                                                              | Vendored snapshot                              |
|-------------------------------------------------------------------------------------------------------|------------------------------------------------|
| `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndf.md`           | `vault/elexon/ndf.md`                          |
| `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndfd.md`          | `vault/elexon/ndfd.md`                         |
| `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/fuelhh.md`        | `vault/elexon/fuelhh.md`                       |
| `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsoe/datasets/<slug>.md`        | `vault/entsoe/<slug>.md` (18 files)            |
| `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/<slug>.md`        | `vault/entsog/<slug>.md` (4 × 404 + physical_flows = 5 files) |

Note: today's `gridflow-front-end/vault/entsoe/` contains ONLY `actual_generation.md` (the v1 cross-vendor proof). The 18 ENTSO-E nullability findings affect files that may not yet be vendored. For each such upstream file, ALSO vendor it (this is preparatory work for Phase 9; explicitly within scope per RECON-03 acceptance "vendored snapshot matches upstream byte-equivalently for the reconciled set"). If any of the 18 file paths don't yet have a vendored equivalent, create it via `cp`.

Verification per file:
```bash
diff -q "vault/<vendor>/<slug>.md" "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/<vendor>/datasets/<slug>.md"
# Expected output: nothing (silent success means byte-equivalent)
```

The build script (`gridflow-build`) reads from `gridflow-front-end/vault/<vendor>/` — verified by `cat src/gridflow_front_end/build.py | grep -nE 'vault/|VAULT_DIR'`. The re-vendor step is what propagates the Reconciliation fix to the rendered Site.
</revendor_mechanism>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Land the 5 load-bearing Vault edits in the upstream `quant-vault` (Elexon: ndf, ndfd, fuelhh; ENTSO-E: 18 resolution-nullability files; ENTSO-G: 4 × 404 + physical_flows)</name>
  <files>
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndf.md
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndfd.md
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/fuelhh.md
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsoe/datasets/<18 files per vault-amendment-plan.md:147-170>
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/hydrogen_content.md
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/interruptions.md
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/methane_content.md
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/oxygen_content.md
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md
  </files>
  <read_first>
    - C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/elexon.py (canonical for `ElexonFuelHH.published_at` line ~87 and `ElexonDemandForecast.published_at` line ~194; CONFIRM line numbers and exact type annotations before editing the Vault)
    - C:/Users/Bobbo/OneDrive/Desktop/Python/gridflow/src/gridflow/schemas/entsog.py OR equivalent (canonical for `physical_flows` schema; confirm field names + nullability — use `grep -rn physical_flow gridflow/src/gridflow/schemas/`)
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-amendment-plan.md:147-170 (the 18 ENTSO-E `resolution` files — exact list)
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndf.md (full file before editing)
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndfd.md (full file before editing)
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/fuelhh.md (full file before editing)
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md (full file before editing — this is the worst single-file rewrite)
    - .planning/research/post-v1/drift-detection/DRIFT-SURFACES.md §§ 4.1, 4.2, 4.5, 4.6 (the Drift specifications)
  </read_first>
  <action>
    Implement the 5 fixes per `<vault_edit_specifications>` in the context block above. Each fix is mechanical — no design questions, no scope reduction.

    **Cadence:** one commit per fix (5 commits total in the upstream `quant-vault`). Conventional Commits, one concern per commit, per CLAUDE.md.

    1. **`fix(07-03): add published_at to ndf/ndfd schema tables and fix national_demand_mw nullability`**
       - Edit `ndf.md` and `ndfd.md` per `<vault_edit_specifications>` Fix 1.
       - Replace `**Point-in-time field**: issue_time` with `**Point-in-time field**: published_at` (both files).
       - In the schema table: replace the `issue_time` row with a `published_at` row (Option A — confirm in `vault-amendment-plan.md` if Vault author has stated preference; otherwise default Option A).
       - Change `national_demand_mw` Nullable column from `Yes` to `No`.

    2. **`fix(07-03): add published_at row to fuelhh schema table`**
       - Edit `fuelhh.md` per `<vault_edit_specifications>` Fix 2.
       - Add a `published_at` row to the schema table at lines 107-115. Metadata at line 103 is already correct; this commit closes the intra-file Drift.

    3. **`fix(07-03): mark resolution field Nullable=Yes across 18 ENTSO-E vault tables`**
       - Edit the 18 files enumerated in `vault-amendment-plan.md:147-170`. Each file's `resolution` row in the schema table gets `Nullable: Yes`.
       - This is mechanical; consider a brief loop reading each file, regex-replacing the resolution row. If unsure of exact format, edit one file by hand first to confirm the table pattern, then mechanically apply to the other 17.

    4. **`fix(07-03): mark 4 ENTSO-G 404 endpoints removed`**
       - Add `removed: 2026-05-19` + `removed_reason:` frontmatter to `hydrogen_content.md`, `interruptions.md`, `methane_content.md`, `oxygen_content.md` per `<vault_edit_specifications>` Fix 4.
       - Do NOT delete the files (preserves audit trail).

    5. **`fix(07-03): rewrite physical_flows schema table to silver shape and preserve raw keys`**
       - Rewrite `physical_flows.md` schema table per `<vault_edit_specifications>` Fix 5.
       - Read `gridflow/src/gridflow/schemas/entsog.py` (or wherever `EntsogPhysicalFlow` lives) FIRST to get the canonical field list. The planner's snippet is best-guess; defer to code.
       - Preserve the existing 29 raw response keys in a new `## Bronze response keys` section at the bottom of the file (per § 4.6 fix specification).

    **Note on ENTSO-G 18 nullability findings:** if 07-02 produced any `open` findings for ENTSO-G/GIE/NESO/Open-Meteo beyond the 5 load-bearing examples, land those too in separate commits. Default: only the 5 load-bearing fixes are explicitly enumerated in this plan. If 07-02 surfaced more `open` findings, add commits 6+ for them, scoping to one finding per commit.

    **Working directory note:** all edits in this task happen in `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/`, NOT in `gridflow-front-end/`. The `quant-vault` directory may not yet be a git repo (07-04 initialises it as a private GitHub repo). If it's not yet a git repo, `git init` it locally first (the user has likely done this; check `test -d .git` before assuming) so the per-fix commits land as the initial history that 07-04 pushes.
  </action>
  <verify>
    <automated>cd "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors" && grep -c 'published_at' elexon/datasets/ndf.md ; grep -c 'published_at' elexon/datasets/ndfd.md ; grep -c 'published_at' elexon/datasets/fuelhh.md ; grep -l 'Nullable.*Yes' entsoe/datasets/*.md 2>/dev/null | wc -l ; grep -l 'removed:' entsog/datasets/{hydrogen_content,interruptions,methane_content,oxygen_content}.md | wc -l ; grep -c 'flow_gwh_per_day' entsog/datasets/physical_flows.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c 'published_at' C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndf.md` returns >= 2 (one in metadata block, one in schema table; the count may be higher if mentioned in prose).
    - Same check returns >= 2 for `ndfd.md` and >= 2 for `fuelhh.md`.
    - `grep 'issue_time' C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/{ndf,ndfd}.md | grep -v 'Implementation delta\\|prose\\|historical'` returns zero lines under the schema table heading (i.e. `issue_time` is gone from the structural metadata/table, but may remain in narrative prose as historical context — that's fine).
    - For each of the 18 files in `vault-amendment-plan.md:147-170`: `grep -c 'resolution.*Yes' <file>` returns >= 1 in the schema-table region of the file.
    - Each of `hydrogen_content.md`, `interruptions.md`, `methane_content.md`, `oxygen_content.md` contains `removed: 2026-05-19` in frontmatter — verify: `for f in hydrogen_content interruptions methane_content oxygen_content ; do head -10 "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/$f.md" | grep -c 'removed:' ; done` returns 4 lines, each `1`.
    - `grep -c 'flow_gwh_per_day' C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md` returns >= 1.
    - `grep -c 'timestamp_utc' C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md` returns >= 1.
    - `grep -c '## Bronze response keys' C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md` returns 1.
    - `git -C "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault" log --oneline | wc -l` returns at least 5 (5 fix commits; 07-04 picks these up for the initial push).
  </acceptance_criteria>
  <done>
    The 5 load-bearing fixes are landed in the upstream Vault as 5 Conventional Commits. The `published_at` row exists on ndf/ndfd/fuelhh schema tables. 18 ENTSO-E `resolution` fields are Nullable=Yes. 4 ENTSO-G 404 endpoints carry `removed:` frontmatter. `physical_flows.md` has a `flow_gwh_per_day` + `timestamp_utc` schema table and a `## Bronze response keys` section.
  </done>
</task>

<task type="auto">
  <name>Task 2: Re-vendor edited files into `gridflow-front-end/vault/<vendor>/` byte-equivalently; close finding files</name>
  <files>
    - vault/elexon/ndf.md
    - vault/elexon/ndfd.md
    - vault/elexon/fuelhh.md
    - vault/entsoe/<18 ENTSO-E files; create the directory targets that don't yet exist>
    - vault/entsog/hydrogen_content.md
    - vault/entsog/interruptions.md
    - vault/entsog/methane_content.md
    - vault/entsog/oxygen_content.md
    - vault/entsog/physical_flows.md
    - .planning/reconciliation/elexon/01-ndf-schema-table-missing-published-at.md (status: open → closed)
    - .planning/reconciliation/elexon/02-ndfd-schema-table-missing-published-at.md
    - .planning/reconciliation/elexon/04-fuelhh-schema-table-missing-published-at.md
    - .planning/reconciliation/elexon/03-ndf-national-demand-nullability-mismatch.md
    - .planning/reconciliation/entsoe/<18 files for resolution nullability>
    - .planning/reconciliation/entsog/01-hydrogen-content-http-404.md
    - .planning/reconciliation/entsog/02-interruptions-http-404.md
    - .planning/reconciliation/entsog/03-methane-content-http-404.md
    - .planning/reconciliation/entsog/04-oxygen-content-http-404.md
    - .planning/reconciliation/entsog/05-physical-flows-schema-table-rewrite.md
  </files>
  <read_first>
    - .planning/phases/07-reconciliation/07-02-SUMMARY.md (the per-Vendor finding counts)
    - .planning/reconciliation/ (every directory; identify all `status: open` findings)
    - vault/ (the current vendored snapshot — confirm vault/entsoe/ contains only actual_generation.md today; the 18 ENTSO-E files may need to be newly-vendored)
    - docs/agents/issue-tracker.md (the `## Comments` append convention)
    - docs/adr/0002-vault-hosted-private-github-repo.md (vendoring pattern preserved)
  </read_first>
  <action>
    Step 1 — Copy each edited upstream file to the vendored snapshot. Use `cp` (or `Copy-Item` if running PowerShell explicitly), preserving content byte-for-byte. Do NOT introduce transforms; the vendored snapshot is a mirror.

    ```bash
    # The 3 Elexon files:
    cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndf.md" "vault/elexon/ndf.md"
    cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndfd.md" "vault/elexon/ndfd.md"
    cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/fuelhh.md" "vault/elexon/fuelhh.md"

    # The 18 ENTSO-E files (loop over the slugs in vault-amendment-plan.md:147-170):
    for slug in <enumerate from vault-amendment-plan.md>; do
      cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsoe/datasets/$slug.md" "vault/entsoe/$slug.md"
    done

    # The 5 ENTSO-G files:
    cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/hydrogen_content.md" "vault/entsog/hydrogen_content.md"
    cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/interruptions.md" "vault/entsog/interruptions.md"
    cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/methane_content.md" "vault/entsog/methane_content.md"
    cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/oxygen_content.md" "vault/entsog/oxygen_content.md"
    cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md" "vault/entsog/physical_flows.md"
    ```

    Create `vault/entsoe/` if it doesn't have all 18 target slugs yet (today only `actual_generation.md` is vendored). The 18 entsoe files going to the snapshot is preparatory work for Phase 9 explicitly within RECON-03's "vendored snapshot matches reconciled upstream byte-equivalently" — Phase 9 then doesn't need to re-vendor these.

    Step 2 — Verify byte-equivalence per file. For each pair:
    ```bash
    diff -q "vault/<vendor>/<slug>.md" "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/<vendor>/datasets/<slug>.md"
    ```
    Empty output = success. Any output = the cp failed or the line endings drifted (CRLF/LF). If line-ending drift appears, the project's `.gitattributes` with `text eol=lf` should handle it; verify by running `diff` on Unix-normalised content via `git diff --no-index --text -- "vault/..." "C:/...quant-vault/.../...md"`.

    Step 3 — Close each finding file. For every `status: open` finding that this task addresses:

    Edit the YAML frontmatter: change `status: open` → `status: closed`. Add a `closed-at: 2026-05-19` line.

    Append to the file body, under `## Comments`:
    ```markdown
    ### 2026-05-19: Closed in 07-03

    Vault edit landed upstream at `C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/<vendor>/datasets/<slug>.md`. Re-vendored byte-equivalently into `vault/<vendor>/<slug>.md`. Commit: `<the conventional-commit hash from Task 1>`.
    ```

    Step 4 — Commit cadence. Two commits in `gridflow-front-end`:
    - `feat(07-03): re-vendor reconciled Elexon + ENTSO-E + ENTSO-G files`
    - `docs(07-03): close <N> reconciliation findings`
  </action>
  <verify>
    <automated>diff -q vault/elexon/ndf.md "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndf.md" ; diff -q vault/elexon/fuelhh.md "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/fuelhh.md" ; diff -q vault/entsog/physical_flows.md "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md" ; grep -l 'status: closed' .planning/reconciliation/*/*.md | wc -l ; grep -l 'closed-at: 2026-05-19' .planning/reconciliation/*/*.md | wc -l</automated>
  </verify>
  <acceptance_criteria>
    - For each edited upstream file, `diff -q "vault/<vendor>/<slug>.md" "C:/Users/...quant-vault/30-vendors/<vendor>/datasets/<slug>.md"` produces empty output (byte-equivalent).
    - `ls vault/entsoe/*.md | wc -l` returns >= 19 (1 actual_generation pre-existed + 18 newly-vendored for the resolution-nullability fix) — confirms the snapshot is now expanded.
    - `grep -l 'status: closed' .planning/reconciliation/*/*.md | wc -l` returns at least 27 (3 elexon load-bearing + 22 elexon wontfix-v3 do NOT close in 07-03 — they stay `wontfix` per D-01 — but the 18 entsoe resolution + 5 entsog open findings DO close; total `closed` count: 3 elexon-published_at + 1 ndf-nullability + 18 entsoe-resolution + 5 entsog = 27. Higher acceptable.).
    - For every closed finding, the frontmatter contains `closed-at: 2026-05-19` (verify: `grep -L 'closed-at:' $(grep -l 'status: closed' .planning/reconciliation/*/*.md)` returns no files — i.e. every closed file has a closed-at date).
    - `grep -l 'wontfix' .planning/reconciliation/elexon/*.md | wc -l` returns 22 (the manual_transformer_schema findings STAY wontfix-v3, NOT closed — they're not actionable in v2 per D-01).
    - `grep -l 'needs-info' .planning/reconciliation/entsoe/*.md | wc -l` returns >= 33 (the entitlement findings STAY needs-info, NOT closed — Phase 9 owns the decision per D-06).
  </acceptance_criteria>
  <done>
    Edited upstream files re-vendored byte-equivalently into `gridflow-front-end/vault/<vendor>/`. Every `open` finding in `.planning/reconciliation/` is closed with `status: closed` + `closed-at: 2026-05-19` + a `## Comments` entry recording the upstream commit. `wontfix-v3` and `needs-info` findings stay in their respective non-closed states (those are not 07-03's problem).
  </done>
</task>

<task type="auto">
  <name>Task 3: Re-run `gridflow-drift-check` to confirm only documented Drift remains; capture the regenerated report</name>
  <files>
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.{json,md} (regenerated for the second time in this phase)
    - .planning/phases/07-reconciliation/07-03-RERUN-REPORT.md
  </files>
  <read_first>
    - .planning/phases/07-reconciliation/07-02-VERIFICATION-REPORT.md (the baseline)
    - C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.md (current state after 07-02 — the snapshot to diff against)
  </read_first>
  <action>
    Step 1 — Save a copy of the post-07-02 baseline before re-running:
    ```bash
    cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.md" /tmp/drift-check-baseline-07-02.md
    cp "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.json" /tmp/drift-check-baseline-07-02.json
    ```

    Step 2 — Re-run the verifier:
    ```bash
    cd "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors"
    gridflow-drift-check 2>&1 | tee /tmp/drift-check-rerun.log
    ```

    Step 3 — Compare the two reports:
    ```bash
    diff /tmp/drift-check-baseline-07-02.md "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.md" > /tmp/drift-check-delta.diff
    ```

    Step 4 — Write `.planning/phases/07-reconciliation/07-03-RERUN-REPORT.md`. Required sections:
    ```markdown
    # 07-03 Re-run Drift-Check Report

    **Re-ran:** <ISO timestamp from new vault-curl-schema-validation.md line 3>
    **Baseline:** <ISO timestamp from /tmp/drift-check-baseline-07-02.md>

    ## Resolved findings (expected DELTA — these should be GONE in the re-run)

    | Finding (from 07-02 baseline)                                       | DRIFT-SURFACES § | Re-run status |
    |---------------------------------------------------------------------|------------------|---------------|
    | `Missing in docs: published_at` on elexon\datasets\ndf.md           | § 4.1            | <gone / still present> |
    | `Missing in docs: published_at` on elexon\datasets\ndfd.md          | § 4.1            | <gone / still present> |
    | `Missing in docs: published_at` on elexon\datasets\fuelhh.md        | § 4.2            | <gone / still present> |
    | `Nullable mismatch: national_demand_mw` on ndf                      | § 4.1 Semantic   | <gone / still present> |
    | 18 × `Nullable mismatch: resolution` on entsoe\datasets\*           | § 4.1 ENTSO-E    | <count remaining; expected 0> |
    | 4 × HTTP 404 on entsog\datasets\{hydrogen,interruptions,methane,oxygen}_content.md | § 4.5 | <count remaining; expected 0 — but the files now carry `removed:` frontmatter, so they may be re-tested or skipped depending on verifier behaviour> |
    | `Missing in docs: flow_gwh_per_day, timestamp_utc` on physical_flows | § 4.6           | <gone / still present> |

    **Acceptance gate:** Every "Re-run status" cell must read either "gone" OR be explained (e.g. the HTTP 404 cells: if the verifier still re-tests removed endpoints, the 404 still surfaces but the Reconciliation finding is closed because the Vault now documents the removal — annotate this nuance).

    ## Persistent expected findings (these should STILL be present — they're not closed in 07-03)

    | Finding                                                              | Status        | Reason                  |
    |----------------------------------------------------------------------|---------------|-------------------------|
    | 22 × `manual_transformer_schema` on Elexon datasets                  | wontfix       | v3-candidate (D-01)     |
    | 33 × HTTP 401 on ENTSO-E datasets                                    | needs-info    | defer-entitlement (D-06)|

    These two counts should NOT decrease between baseline and re-run. If either decreases, the verifier's behaviour shifted unexpectedly; investigate.

    ## New findings (regressions or unexpected discoveries)

    <List any Drift instances in the re-run that did NOT appear in the 07-02 baseline. There should be very few or none. If anything is here, it is a regression that needs a new finding file under `.planning/reconciliation/<vendor>/` and likely a follow-up commit.>

    ## Conclusion

    - [ ] All 5 load-bearing fix categories closed (cells in the "Resolved findings" table read "gone" or "documented")
    - [ ] No regressions (the "New findings" section is empty or all entries are pre-explained)
    - [ ] `wontfix-v3` and `needs-info` counts unchanged

    Tick boxes; if any unticked, do NOT proceed to Task 4.
    ```

    Conventional Commit: `chore(07-03): re-run drift-check and confirm open bucket closed`
  </action>
  <verify>
    <automated>diff -q /tmp/drift-check-baseline-07-02.md "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.md" ; grep -c 'Missing in docs: published_at' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.md" ; grep -c 'flow_gwh_per_day' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.md" ; grep -c '- \\[ \\]' .planning/phases/07-reconciliation/07-03-RERUN-REPORT.md</automated>
  </verify>
  <acceptance_criteria>
    - `grep -c 'Missing in docs: published_at' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.md"` returns 0 (the 3 baseline hits — ndf, ndfd, fuelhh — are gone after Task 1's edits).
    - `grep -nE 'Missing in docs: flow_gwh_per_day|Missing in docs: timestamp_utc' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.md"` returns zero hits (the physical_flows schema-table rewrite closed this).
    - `grep -c 'failed_auth' vault-curl-schema-validation.md` returns at least 33 (the ENTSO-E entitlement findings STAY — D-06).
    - `grep -c 'manual_transformer_schema' vault-curl-schema-validation.md` returns at least 58 (the wontfix-v3 findings STAY — D-01).
    - `.planning/phases/07-reconciliation/07-03-RERUN-REPORT.md` exists; every box under "Conclusion" is ticked (`grep -c '- \\[ \\]' ... = 0`, `grep -c '- \\[x\\]' ... = 3`).
  </acceptance_criteria>
  <done>
    Re-running `gridflow-drift-check` produces zero new `Missing in docs:` / nullability findings in the `open` bucket categories. The 22 wontfix-v3 and 33 needs-info findings remain (correctly, per D-01 and D-06). RECON-03 success criterion 3 is satisfied.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 4 (CHECKPOINT): Verify v1 CI gates remain green on `gridflow-front-end` after re-vendor (RECON-05)</name>
  <what-built>
    Tasks 1-3 landed 5 Vault edits in upstream, re-vendored them into `gridflow-front-end/vault/`, closed the corresponding `open` reconciliation findings, and confirmed the verifier reports zero remaining open-bucket Drift. Now the v1 CI gates (`htmlhint`, `lychee --offline --include-fragments`, `gridflow-build --check`) need to verify ON the regenerated set — Phase 7 must not change the deploy contract.
  </what-built>
  <how-to-verify>
    Run the three v1 CI gates locally before relying on the GitHub Actions run. The deploy contract is from `.github/workflows/deploy.yml`; the same three commands run there.

    **Step 1 — Rebuild the Site from the freshly-vendored Vault:**
    ```bash
    uv pip install -e ".[build]" --quiet
    gridflow-build
    # Then re-run to test idempotence:
    gridflow-build --check
    # Expected: exits 0 (idempotence holds — no diff between two consecutive builds)
    ```

    Expected behaviour: the rendered HTML under `site/hifi/data-sources/elexon/{ndf,ndfd,fuelhh}.html` now shows `Point-in-time field: published_at` (was `issue_time` on ndf/ndfd; was already `published_at` on fuelhh) and the rendered schema table now includes the `published_at` row on all three.

    The 18 newly-vendored ENTSO-E files cause `gridflow-build` to attempt to render them. If `entsoe.json` manifest doesn't yet list them (Phase 9's work), the build either skips them or renders them as orphans — investigate which and document.

    **Step 2 — htmlhint:**
    ```bash
    npx htmlhint --config .htmlhintrc 'site/hifi/**/*.html'
    # Expected: exit 0, no errors
    ```

    **Step 3 — lychee:**
    ```bash
    lychee --offline --include-fragments 'site/hifi/**/*.html'
    # Expected: exit 0, no broken internal links / dead anchors
    ```

    Step 4 — Visit the freshly-built `fuelhh.html` and `ndf.html` in a browser via `gridflow-serve` (or `python -m http.server` from `site/hifi/`):
    ```bash
    gridflow-serve &
    # Open http://localhost:8000/data-sources/elexon/fuelhh.html
    # Scroll to the schema table — confirm `published_at` row is present
    # Open http://localhost:8000/data-sources/elexon/ndf.html
    # Confirm "Point-in-time field: published_at" near the metadata block + `published_at` row in the schema table
    # Confirm `national_demand_mw` row shows "No" in the Nullable column
    ```

    **Sign off with one of:**
    - "approved" — all three CI gates exit 0; browser spot-check confirms `published_at` rendering on ndf.html and fuelhh.html.
    - "blocked: <what failed>" — describe which gate failed and which file. The blocker becomes a follow-up task within 07-03 (or escalates if it implies a build-script change, which would be Phase 8 / out of scope for 07-03).
  </how-to-verify>
  <resume-signal>Type "approved" or describe the blocker.</resume-signal>
</task>

</tasks>

<threat_model>

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Upstream Vault edits → vendored snapshot | The `cp` operation is the trust handoff; any transform here breaks "vendored snapshot byte-equivalent to upstream" |
| Vendored snapshot → `gridflow-build` rendering | The build reads vault/<vendor>/ markdown; misrendered markdown breaks `gridflow-build --check` |
| `physical_flows.md` schema-table rewrite | The largest single rewrite in this plan; risk of introducing a new field-name mismatch |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-07-03-01 | T (Tampering) | The `cp` operation upstream → vendored | mitigate | Acceptance check via `diff -q` for every copied file confirms byte-equivalence. Any non-empty diff output blocks the task. |
| T-07-03-02 | I (Information disclosure) | Closure `## Comments` entries in finding files | mitigate | The acceptance criteria's grep for API-key patterns in `.planning/reconciliation/` (from 07-02) carries forward; do not paste vendor secrets into closure notes. |
| T-07-03-03 | D (Denial of service) | `gridflow-build` build step in checkpoint | mitigate | If `gridflow-build` errors on a newly-vendored ENTSO-E file (e.g. orphan: present in vault but not in manifest), it could fail the deploy contract. The checkpoint's expected behaviour explicitly checks this; if it triggers, the resolution is to document in 07-03-SUMMARY.md and either (a) add the orphan to `entsoe.json` (Phase 9 work; defer) or (b) confirm `gridflow-build` skips unlisted files (current v1 behaviour per `build.py:104-105`; the orphan is silent). |
| T-07-03-04 | R (Repudiation) | The `closed-at:` date on closed findings | accept | A user with commit access can backdate; this is a low-stakes audit field, not a security boundary. |

</threat_model>

<verification>

Plan-level verification — run after all 4 tasks land:

```bash
# 1. The 5 load-bearing fixes are landed upstream:
grep -c 'published_at' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndf.md"    # >= 2
grep -c 'published_at' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/ndfd.md"   # >= 2
grep -c 'published_at' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/elexon/datasets/fuelhh.md" # >= 2
ls C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/{hydrogen_content,interruptions,methane_content,oxygen_content}.md | wc -l   # = 4
grep -c 'flow_gwh_per_day' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/entsog/datasets/physical_flows.md"  # >= 1

# 2. Byte-equivalent vendored snapshot:
for f in elexon/ndf.md elexon/ndfd.md elexon/fuelhh.md entsog/hydrogen_content.md entsog/interruptions.md entsog/methane_content.md entsog/oxygen_content.md entsog/physical_flows.md ; do
  diff -q "vault/$f" "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/${f%/*}/datasets/${f##*/}" || echo "DRIFT on $f"
done

# 3. Re-run verifier shows zero `open` bucket Drift:
grep -c 'Missing in docs: published_at' "C:/Users/Bobbo/OneDrive/Desktop/Learning/AI/quant-vault/30-vendors/vault-curl-schema-validation.md"   # = 0

# 4. Finding closure:
grep -l 'status: closed' .planning/reconciliation/*/*.md | wc -l                       # >= 27 (3+1+18+5)
grep -L 'closed-at:' $(grep -l 'status: closed' .planning/reconciliation/*/*.md)        # empty list
grep -l 'wontfix' .planning/reconciliation/elexon/*.md | wc -l                          # = 22 (unchanged)
grep -l 'needs-info' .planning/reconciliation/entsoe/*.md | wc -l                       # >= 33 (unchanged)

# 5. CI gates pass:
gridflow-build --check        # exit 0
npx htmlhint --config .htmlhintrc 'site/hifi/**/*.html'   # exit 0
lychee --offline --include-fragments 'site/hifi/**/*.html'  # exit 0
```

</verification>

<success_criteria>

RECON-03 from REQUIREMENTS.md is satisfied:
- The `open` bucket is closed: Vault edits land in the upstream `quant-vault` (5 load-bearing fixes + any other surfaced `open` findings)
- Re-vendored into `gridflow-front-end/vault/<vendor>/` byte-equivalently (verified by per-file `diff -q`)
- Re-running `gridflow-drift-check` returns "no new Drift" (the `Missing in docs: published_at` count is 0; the physical_flows 35-field mismatch is gone; the 4 × 404 cases now carry `removed:` frontmatter; the 18 ENTSO-E nullability mismatches are gone). Documented `wontfix-v3` (22 elexon manual_transformer_schema) and `needs-info` (33 entsoe HTTP 401) remain — that's correct, per D-01 and D-06.

RECON-05 from REQUIREMENTS.md is satisfied:
- v1 CI gates remain green on `gridflow-front-end`: `htmlhint`, `lychee --offline --include-fragments`, and `gridflow-build --check` idempotence all pass on the regenerated set (verified by the checkpoint).

</success_criteria>

<output>
After all 4 tasks complete, create `.planning/phases/07-reconciliation/07-03-SUMMARY.md` per the standard summary template. Capture:
- The 5 conventional-commit hashes for the upstream Vault edits (Task 1)
- The 2 conventional-commit hashes for the re-vendor + finding-closure commits (Task 2)
- Output of the re-run drift-check report (Task 3) — specifically the per-row "Resolved findings" table
- The checkpoint sign-off (Task 4) — "approved" or the blocker description
- Per-Vendor stats:
  - Elexon: <N> open findings closed; 22 wontfix-v3 remain
  - ENTSO-E: <N> open findings closed (the 18 resolution-nullability set); 33 needs-info remain
  - ENTSO-G: 5 open findings closed (4 × 404 marked `removed:` + 1 × physical_flows rewrite)
  - Other vendors: counts as they materialise from 07-02 surfacing
- Pointer for 07-04: "Upstream Vault now has <N> commits ready to push to `EBentham/quant-vault`"
</output>
