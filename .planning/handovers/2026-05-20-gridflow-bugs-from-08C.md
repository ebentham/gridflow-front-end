---
handover_from: gridflow-front-end · Phase 8C-01 closure (2026-05-20)
handover_to: gridflow main repo · GSD agent / equivalent manager
priority: P1 (silent-null silver columns) + P2 (schema/output drift) + P3 (Pydantic coverage policy)
expected_phase_shape: G-series candidate (existing G-series is "schema corrections" — G2/G3/G4 already shipped)
artifact_dependencies:
  - gridflow/src/gridflow/silver/elexon/*.py (transformer modules)
  - gridflow/src/gridflow/schemas/elexon.py (Pydantic class declarations)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (endpoint registrations)
  - quant-vault upstream (vault/elexon/<slug>.md — schema sections need updates)
  - gridflow-front-end vendored vault (gridflow-front-end/vault/elexon/<slug>.md — synced from quant-vault)
  - gridflow-front-end content briefs (gridflow-front-end/content-briefs/elexon/<slug>.md — 4 affected briefs need refresh)
cross_repo_workflow_required: yes (gridflow code → quant-vault docs → vendored snapshot → content briefs)
---

# Handover: Elexon silver-layer drift surfaced by gridflow-front-end Phase 8C

## Provenance

Phase 8C of the gridflow-front-end (documentation portfolio) project produced 33 triangulated content briefs for Elexon datasets by cross-referencing three sources of truth:

1. The vault (`vault/elexon/<slug>.md`, vendored from quant-vault)
2. **The gridflow codebase** (schemas, silver transformers, connector registrations)
3. Live vendor docs (intended; Elexon BMRS Swagger UI is JS-rendered and unfetchable — vault Bronze samples compensate)

When the three sources disagreed, the brief recorded the discrepancy in its YAML frontmatter. **45 discrepancies surfaced across 32 of 33 briefs.** Categories 4–6 are cosmetic / documentation drift and need no gridflow action. **Categories 1, 2, 3 are gridflow-source-layer issues and motivate this handover.**

Full original triage: [`.planning/phases/08C-elexon-content-briefs/DISCREPANCY-INDEX.md`](../phases/08C-elexon-content-briefs/DISCREPANCY-INDEX.md) in the gridflow-front-end repo. This handover distills it for the gridflow workflow.

## TL;DR

| # | What | Severity | Effort | Action |
|---|---|---|---|---|
| **P1** | 4 silver columns are silently `null` because the transformer's rename map doesn't match the live API's field names (netbsad, mid, disbsad, temp) | Bug — silent data loss | ~5 LoC each + regression test | Fix transformer mappings; verify with fresh bronze capture |
| **P2** | 3 datasets declare schema fields the transformer doesn't emit (boal, fuelhh, uou2t14d) | Bug — `None` for every row | ~3 LoC each | Either populate or remove the schema field; align declarations with reality |
| **P3** | 21 of 33 Elexon datasets have **no Pydantic class** declared in `schemas/elexon.py`. Pattern is so uniform it reads as a design choice, not 21 omissions | Policy decision pending | ADR (Option A) or 10-15h (Option B) | Codify the pattern (recommended) OR add the 21 missing classes |
| **VAULT** | Any schema/transformer change must propagate to `quant-vault/30-vendors/elexon/datasets/<slug>.md` → re-vendor to `gridflow-front-end/vault/elexon/<slug>.md` → trigger brief-refresh in `gridflow-front-end/content-briefs/elexon/<slug>.md` | Cross-repo invariant | Per-fix overhead ~5min | Workflow described below |

Aim: bundle P1 + P2 as one PR (each fix is small, regression tests are similar shape). Open P3 as a separate ADR discussion. Treat the vault propagation as a per-change requirement, not a separate phase.

---

## P1 — Silent-null silver columns (Category 2 · 4 occurrences)

**Pattern.** The transformer's column-rename mapping references field names that no longer match the live API response. Fresh bronze captured from the current vendor API produces silver rows where the target columns are silent-null because the rename rule never fires. **No exception raised — the bug is invisible without column-content validation.**

### P1.1 — `netbsad` (Net Bid-Offer Settlement Adjustment Data)

- **Transformer**: `gridflow/src/gridflow/silver/elexon/netbsad.py`
- **Current mapping (broken)**: renames 4 fields:
  ```
  netBuyPriceAdjustment / netSellPriceAdjustment /
  netBuyVolumeAdjustment / netSellVolumeAdjustment
  ```
- **Live API (verified 2026-05-08)** returns **8 finer-grained fields**:
  ```
  netBuyPriceCostAdjustmentEnergy, netBuyPriceVolumeAdjustmentEnergy,
  netBuyPriceVolumeAdjustmentSystem, buyPricePriceAdjustment,
  netSellPriceCostAdjustmentEnergy, netSellPriceVolumeAdjustmentEnergy,
  netSellPriceVolumeAdjustmentSystem, sellPricePriceAdjustment
  ```
- **Current behavior**: all 4 NETBSAD adjustment columns are `null` in fresh silver.
- **Fix**: extend rename map to cover the 8 actual fields (4 original schema columns become 8 in silver, OR map the 8 to the existing 4 with summing/picking rules). Decide which is right based on downstream BM modelling — the 8 fields are not aggregations of the 4; they are finer-grained categorisations (cost vs volume × energy vs system × buy vs sell).
- **Vault impact**: `quant-vault/30-vendors/elexon/datasets/netbsad.md` Silver schema table needs the column count + names refreshed.

### P1.2 — `mid` (Market Index Price)

- **Transformer**: `gridflow/src/gridflow/silver/elexon/mid.py` (L55-61 — rename map)
- **Current mapping**: expects `dataProviderId` → `data_provider_id` and `midPrice` → `market_index_price`
- **Live API (verified 2026-05-08)** returns `dataProvider` and `price` (not `dataProviderId`, not `midPrice`)
- **Current behavior**: `data_provider_id` and `market_index_price` are `null` in fresh silver. Two of the most semantically important columns in the dataset are unpopulated.
- **Fix**: update `mid.py` L55-61 rename map:
  ```python
  # add:
  "dataProvider": "data_provider_id",
  "price":        "market_index_price",
  # consider keeping the old keys as fallback for historical bronze
  ```
- **Vault impact**: `quant-vault/30-vendors/elexon/datasets/mid.md` Silver schema table — update Source field column.

### P1.3 — `disbsad` (Disaggregated Settlement Bid-Offer Acceptances)

- **Transformer**: `gridflow/src/gridflow/silver/elexon/disbsad.py`
- **Current mapping**: sources a `component` field
- **Live API (verified 2026-05-08)** returns `service` field; `component` is absent from current samples
- **Current behavior**: the equivalent silver column is `null`.
- **Fix**: extend mapping to handle both keys for backward compatibility:
  ```python
  # pseudocode — adapt to actual transformer shape:
  source_value = record.get("service") or record.get("component")
  ```
- Document which API version emits which (vault should note the transition).
- **Vault impact**: `quant-vault/30-vendors/elexon/datasets/disbsad.md` Silver schema table — note the `service` (current) / `component` (legacy) duality.

### P1.4 — `temp` (System temperature)

- **Transformer**: `gridflow/src/gridflow/silver/elexon/temp.py` (L57 renames; L95-99 output_cols)
- **Issue**: `measurementDate` is renamed to `measurement_date` at L57 but `measurement_date` is NOT in `output_cols` at L95-99 — the rename happens, then the column is dropped before write.
- **Current behavior**: vendor's original measurement date is not available in silver; only the derived `timestamp_utc` survives.
- **Fix**: add `"measurement_date"` to `output_cols` if downstream needs the original (vs. derived) measurement date. **Non-blocking** if downstream consumers are satisfied with `timestamp_utc`.
- **Vault impact**: `quant-vault/30-vendors/elexon/datasets/temp.md` — decide whether vault should list `measurement_date` as a silver column (matching fix) or document it as deliberately dropped.

### P1 — Recommended PR shape

One PR against `gridflow` with:
- 4 column-mapping fixes (one commit each, or bundled depending on test pattern)
- Regression tests per fix: assert that a captured live-API fixture round-trips through the transformer with no null columns for the expected fields
- Vault PRs against `quant-vault` (4 datasets edited) — coordinate timing so vault and code merge together
- Re-vendor commit in `gridflow-front-end` to sync `vault/elexon/{netbsad,mid,disbsad,temp}.md`
- Brief-refresh commits in `gridflow-front-end/content-briefs/elexon/{netbsad,mid,disbsad,temp}.md` — remove the discrepancy from frontmatter, regenerate the schema section

---

## P2 — Schema declares fields the transformer doesn't emit (Category 3 · 3 occurrences)

**Pattern.** The Pydantic class declares a field that does not appear in the transformer's `output_cols` list. Code that imports the class and accesses the field receives `None` for every row. Class users are misled about data availability.

### P2.1 — `boal.bid_offer_acceptance_number`

- **Schema**: `schemas/elexon.py L114` declares `bid_offer_acceptance_number: int | None`
- **Transformer**: `silver/elexon/boal.py` `output_cols` (around L113-119) does NOT include `bid_offer_acceptance_number`
- **Recommendation**: per the brief, `bid_offer_acceptance_number` is reserved for a future per-pair column. Either populate it in the transformer NOW, or remove from `ElexonBOAL` until the implementation lands.

### P2.2 — `fuelhh.published_at`

- **Schema**: `schemas/elexon.py L87` declares `ElexonFuelHH.published_at`
- **Transformer**: `silver/elexon/fuelhh.py L103-106` `output_cols` does NOT include `published_at`
- **Tension**: `published_at` is documented as the point-in-time field for fuelhh. The downstream Claude-Design reference page at `gridflow-front-end/authored-pages/elexon/fuelhh.html` treats it as the PIT field. The schema declares it. The transformer drops it.
- **Recommendation**: add `"published_at"` to `output_cols` to make the schema honest. If the field is genuinely unavailable from the BMRS API, remove from `ElexonFuelHH` and document the column drop in the vault.

### P2.3 — `uou2t14d` (`fuel_type` and `national_grid_bm_unit`)

- **Transformer**: `silver/elexon/uou2t14d.py L63-65` renames `fuelType` and `nationalGridBmUnit` — then `output_cols` (L114-117) drops both before write.
- **Current behavior**: fuel context for UOU2T14D records must come from a join against `bmunits_reference`; you can't read it from UOU2T14D's own output.
- **Recommendation**: restore both to `output_cols` (simpler downstream — UOU2T14D is self-describing), OR update vault to mark them as deliberately-dropped and steer users to the join pattern.

### P2 — Recommended PR shape

Small consistency PR. One commit per fix (3 commits). Either align schema with `output_cols` or `output_cols` with schema, per the recommendation above. Test pattern: assert that every declared schema field appears as a non-null in at least one row of a representative fixture, OR is documented as `# nullable by design` in the schema.

Vault impact mirrors P1 — for each of `boal`, `fuelhh`, `uou2t14d`, the vault Silver schema table needs the resolved field list.

---

## P3 — Pydantic class coverage policy (Category 1 · 21 occurrences)

**Pattern.** `schemas/elexon.py` declares only 12 Pydantic classes (`ElexonSystemPrice`, `ElexonGenerationByFuel`, `ElexonFuelHH`, `ElexonBOAL`, `ElexonBOD`, `ElexonMID`, `ElexonFrequency`, `ElexonDemandForecast`, `ElexonWindForecast`, `ElexonPN`, `ElexonDISBSAD`, `ElexonBMUnit`). **21 of 33 active Elexon datasets have no Pydantic class** — their silver-layer shape is defined by the transformer's `output_cols` list alone.

**Affected datasets (21)**: `agpt, agws, atl, fou2t14d, imbalngc, inddem, indgen, indo, indod, itsdo, lolpdrm, market_depth, melngc, netbsad, nonbm, remit, soso, temp, tsdf, tsdfd, uou2t14d`.

**This is a policy decision, not a bug.** The pattern is so consistent (every absence applies to indicated/aggregate/wide-reference data; every present class corresponds to a load-bearing schema with multi-source ingestion or non-trivial validators) that it reads as deliberate. Two options:

### P3 Option A — Codify the policy (recommended)

Write a gridflow ADR documenting the split. Suggested ADR shape:

> **ADR-GXX: Pydantic class coverage for silver schemas**
>
> Status: Accepted
>
> Context: Of 33 Elexon silver transformers, 12 have dedicated Pydantic classes in `schemas/elexon.py`; 21 do not. This was previously implicit.
>
> Decision: A silver dataset gets a dedicated Pydantic class when AT LEAST ONE of the following criteria holds:
> 1. Multi-source ingestion (the transformer combines multiple API endpoints into one schema)
> 2. Non-trivial validators required (range constraints, enum validation, conditional null rules)
> 3. Downstream typed-consumer requirement (e.g., gridflow_models imports it as a Pydantic class)
> 4. Load-bearing for cross-dataset joins (e.g., `ElexonBMUnit` is the reference table everything joins against)
>
> Otherwise, the silver shape is **self-describing via `output_cols`** — sufficient for parquet schema declaration and DuckDB query without the Pydantic overhead.
>
> Update top of `schemas/elexon.py` with a docstring naming this ADR. Update each absent dataset's vault Implementation-Delta to reference the ADR by name (auto-generates a discoverable trail when documenters cross-reference).

### P3 Option B — Close the gap

Add 21 mechanical Pydantic classes mirroring each transformer's `output_cols`. ~30 min each × 21 = 10–15h of gridflow work. Higher consistency, but the criteria-based recommendation above suggests most of these classes would add no validation value over `output_cols`.

### P3 Option C — Mixed

Add Pydantic for 5 highest-volume / highest-risk datasets (`pn`-style per-unit feeds, settlement series); defer wide-reference (`bmunits_reference`-style) and append-only (`remit`-style). ~3–4h work.

**Pick A unless `gridflow_models` repo (or another downstream) specifically needs the typed classes.**

---

## Cross-repo workflow — VAULT PROPAGATION (mandatory for any P1 / P2 fix)

Every fix in gridflow's silver/schemas layer **must** propagate downstream. Skipping vault propagation means the next vault-drift-check (Phase 7-style) will re-surface the same discrepancy — and the gridflow-front-end content briefs and rendered pages will lag the truth.

**Per-fix workflow** (apply to each silver-layer fix individually):

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Fix in gridflow                                         │
│   - Edit gridflow/src/gridflow/silver/elexon/<slug>.py          │
│   - Edit gridflow/src/gridflow/schemas/elexon.py (if applicable)│
│   - Add regression test (assert no silent-null columns)         │
│   - Commit: fix(silver-elexon): <slug> mapping aligns with API  │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Vault edit in quant-vault upstream                      │
│   - Edit quant-vault/30-vendors/elexon/datasets/<slug>.md       │
│     · Silver schema table — refresh column list                 │
│     · Implementation Delta — update field-mapping note          │
│     · Changelog — add V2-FIX-XX entry with date + gridflow PR   │
│   - Commit: docs(elexon-<slug>): refresh after silver fix V2-XX │
│   - Push upstream                                               │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Re-vendor to gridflow-front-end                         │
│   - cd C:\Users\Bobbo\OneDrive\Desktop\Python\gridflow-front-end│
│   - cp quant-vault/30-vendors/elexon/datasets/<slug>.md         │
│        vault/elexon/<slug>.md                                   │
│   - diff -q <upstream> <vendored>  # must be byte-equal         │
│   - Follow .planning/phases/07-reconciliation/07-04-VAULT-      │
│       WORKFLOW.md (the cadence documented in Phase 7)           │
│   - Commit: chore(vault): re-vendor elexon-<slug> after gridflow│
│     V2-FIX-XX                                                   │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Refresh content brief in gridflow-front-end             │
│   - Edit content-briefs/elexon/<slug>.md                        │
│     · Remove the discrepancy entry from frontmatter             │
│       OR update orchestrator_recommendation to "resolved by     │
│       gridflow V2-FIX-XX"                                       │
│     · Refresh Schema section if column count changed            │
│     · Refresh Caveats section if a caveat was the bug-as-       │
│       known-issue                                               │
│     · Update sources_consulted last-fetched timestamp           │
│   - Commit: docs(08C-update): refresh <slug> brief after        │
│     gridflow V2-FIX-XX                                          │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Verification                                            │
│   - Re-run gridflow-drift-check on the affected dataset         │
│   - Confirm no new Drift surfaced                               │
│   - If a Claude-Designed authored-pages/elexon/<slug>.html      │
│     exists, regenerate via Claude Design + redrop into          │
│     authored-pages/                                             │
└─────────────────────────────────────────────────────────────────┘
```

The first fix lands all 5 steps to validate the workflow; subsequent fixes (3 more for P1, 3 for P2) can batch steps 2-4 across PRs.

---

## Reference materials

In the gridflow-front-end repo, available for the gridflow agent to consult:

- **The 4 P1-affected briefs** (full triangulated detail):
  - `gridflow-front-end/content-briefs/elexon/netbsad.md`
  - `gridflow-front-end/content-briefs/elexon/mid.md`
  - `gridflow-front-end/content-briefs/elexon/disbsad.md`
  - `gridflow-front-end/content-briefs/elexon/temp.md`
- **The 3 P2-affected briefs**:
  - `gridflow-front-end/content-briefs/elexon/boal.md`
  - `gridflow-front-end/content-briefs/elexon/fuelhh.md`
  - `gridflow-front-end/content-briefs/elexon/uou2t14d.md`
- **Full discrepancy index** (Categories 1–6, all 45 items): `gridflow-front-end/.planning/phases/08C-elexon-content-briefs/DISCREPANCY-INDEX.md`
- **Phase 8C closure summary**: `gridflow-front-end/.planning/phases/08C-elexon-content-briefs/08C-01-SUMMARY.md`
- **The reference Claude-Design page** (visual gold-standard): `gridflow-front-end/authored-pages/elexon/fuelhh.html`
- **Phase 7 vault workflow** (Step 3 reference): `gridflow-front-end/.planning/phases/07-reconciliation/07-04-VAULT-WORKFLOW.md`

---

## Suggested gridflow GSD phase shape

If the gridflow GSD manager adopts this as a phase, suggested structure:

- **Phase name** (G-series convention, schema corrections): `G5-elexon-silver-mapping-cleanup` or `G5-elexon-schema-drift-fix`
- **Sub-plans**:
  - `G5-01-p1-silent-null-columns.md` — Categories 2 (4 transformer mapping fixes + regression tests)
  - `G5-02-p2-schema-output-alignment.md` — Categories 3 (3 schema-vs-output_cols fixes)
  - `G5-03-pydantic-coverage-adr.md` — Category 1 ADR (Option A) OR mechanical class additions (Option B/C)
- **Cross-repo coordination plan**: per-fix vault propagation (5-step workflow above) is acceptance criterion
- **Verification gate**: re-run `gridflow-drift-check` (Phase 7's tool — already on path) after fixes; confirm Categories 2 + 3 close; if P3 Option A chosen, confirm the new ADR is referenced from each absent dataset's vault Implementation-Delta

---

## Acceptance for the originating workflow (gridflow-front-end Phase 8C)

When the gridflow agent reports back:

- P1 fixes landed + vault propagated → I refresh the 4 affected content briefs (`netbsad, mid, disbsad, temp`), drop discrepancies from frontmatter, re-commit
- P2 fixes landed + vault propagated → same for 3 briefs (`boal, fuelhh, uou2t14d`)
- P3 ADR landed → I refresh the 21 affected briefs' discrepancy frontmatter to reference the ADR by name (becomes "documented design intent", not "discrepancy")

After all three, the gridflow-front-end content briefs are clean (zero open discrepancies), Phase 9 (ENTSO-E briefs) and Phase 10 (four-vendor briefs) can proceed with the same triangulated pattern, and the vault drift surface for Elexon is at its post-Phase-7 baseline plus zero new Drift.

---

**End of handover. Phase 8C-01 (gridflow-front-end) is closed; this document is the bridge to the gridflow-side work.**
