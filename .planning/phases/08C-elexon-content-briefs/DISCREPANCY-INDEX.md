# Phase 8C — DISCREPANCY-INDEX.md

**Generated:** 2026-05-20 (autonomous closure of Phase 8C-01)
**Purpose:** User-facing triage doc for the 45 discrepancies surfaced across 32 of 33 Elexon content briefs. Each section groups discrepancies of the same shape; per-dataset details point to the brief's frontmatter for the verbatim entry.
**Scope:** Elexon datasets only (Phase 8C scope). ENTSO-E and four-vendor batches are deferred to Phase 9 + Phase 10.
**Convention:** "Trust gridflow" follows PROJECT.md SoT hierarchy (gridflow code > live API > vault > on-site rendered pages). Where gridflow itself is missing or under-documented, the recommendation flags Phase-7-style mini-recon.

---

## Category 1 — No dedicated Pydantic class (21 occurrences) · BLAST RADIUS: HIGH

**Pattern:** `schemas/elexon.py` declares only 12 Pydantic classes (`ElexonSystemPrice`, `ElexonGenerationByFuel`, `ElexonFuelHH`, `ElexonBOAL`, `ElexonBOD`, `ElexonMID`, `ElexonFrequency`, `ElexonDemandForecast`, `ElexonWindForecast`, `ElexonPN`, `ElexonDISBSAD`, `ElexonBMUnit`). The other 21 active Elexon datasets have no Pydantic class — their silver-layer shape is defined by `<Transformer>.output_cols` lists alone. Any downstream code that imports a non-existent `ElexonAGPT` / `ElexonAGWS` / etc. will fail at import.

**Affected datasets** (21): `agpt`, `agws`, `atl`, `disbsad` (has class but discrepancy here is unrelated — list it under category 2), `fou2t14d`, `fuelinst`, `imbalngc`, `inddem`, `indgen`, `indo`, `indod`, `itsdo`, `lolpdrm`, `market_depth`, `melngc`, `netbsad`, `nonbm`, `soso`, `temp`, `tsdf`, `tsdfd`, `uou2t14d`.

**Per-occurrence template** (consistent across all 21):
- source_a: `gridflow schemas/elexon.py`
- source_a_says: `No Elexon<Slug> class declared`
- source_b: `gridflow silver/elexon/<slug>.py::<Transformer>`
- source_b_says: `Transformer outputs <N> columns: <list>`
- orchestrator_recommendation: `trust silver transformer; same shape gap as other indicated/aggregate datasets`

**Recommendation (Phase 7-style mini-recon — TRIGGER MET, CONTEXT Q-C):**
- **Option A (codify the policy):** Document `silver/elexon/<slug>.py output_cols` as the authoritative schema for the 21 absent datasets. Add a top-level note in `schemas/elexon.py` explaining the split: "Pydantic classes exist for load-bearing schemas with multi-source ingestion or non-trivial validators. Other silver transformers are self-describing via `output_cols`." Update vault Implementation-Delta sections to reference this policy by name.
- **Option B (close the gap):** Add 21 mechanical Pydantic classes mirroring each transformer's `output_cols`. Higher consistency cost in gridflow, but enables typed downstream consumers.
- **Recommend Option A** unless gridflow_models repo (or another downstream) actually needs the typed classes; the existing patterns suggest the absence is a *design choice* not an omission.

**Blast radius beyond Elexon:** likely affects ENTSO-E (49 datasets, Phase 9) and the four-vendor batch (81 datasets, Phase 10) too — confirm via grep for `class Entsoe` / `class Entsog` / `class Gie` / `class Neso` / `class OpenMeteo` in the corresponding `schemas/*.py` files during Phase 9/10 brief production.

---

## Category 2 — Vendor API field-name drift vs transformer column mapping (4 occurrences) · BLAST RADIUS: MEDIUM

**Pattern:** the transformer's column-rename mapping references field names that no longer match the live API response. Fresh bronze captured from the current vendor API produces silver rows where the target columns are silent-null because the rename rule never fires.

**Per-occurrence details:**

### 2.1 `netbsad` — 4 columns vs 8 finer-grained API fields
- source_a: `vault Silver schema: 4 columns (net_buy_price_adjustment, ...)`
- source_a_says: `Transformer renames netBuyPriceAdjustment / netSellPriceAdjustment / netBuyVolumeAdjustment / netSellVolumeAdjustment`
- source_b: `Live API 2026-05-08 returns: netBuyPriceCostAdjustmentEnergy, netBuyPriceVolumeAdjustmentEnergy, netBuyPriceVolumeAdjustmentSystem, buyPricePriceAdjustment, netSellPriceCostAdjustmentEnergy, netSellPriceVolumeAdjustmentEnergy, netSellPriceVolumeAdjustmentSystem, sellPricePriceAdjustment`
- orchestrator_recommendation: **Phase-7 mini-recon candidate** — extend column mapping to cover the 8 actual fields, or document the gap explicitly. Current behaviour: all four NETBSAD adjustment columns are null in fresh silver.

### 2.2 `mid` — `dataProvider` / `price` vs transformer's `dataProviderId` / `midPrice`
- source_a: `vault Silver schema (dataProviderId, midPrice mapping)`
- source_b: `Live API 2026-05-08 returns dataProvider and price (not dataProviderId, not midPrice)`
- orchestrator_recommendation: **Phase-7 mini-recon candidate** — update `silver/elexon/mid.py L55-61` to include `"dataProvider": "data_provider_id"` and `"price": "market_index_price"` in the rename map. Current behaviour: `data_provider_id` and `market_index_price` are null in fresh silver.

### 2.3 `disbsad` — `component` vs `service`
- source_a: `vault Silver schema sources component`
- source_b: `Live API 2026-05-08 returns service field (component absent in sample)`
- orchestrator_recommendation: **Phase-7 mini-recon candidate** — extend mapping to handle both `component` (legacy) and `service` (current). Document which API version emits which.

### 2.4 `temp` — `measurement_date` renamed-then-dropped
- source_a: `vault Implementation Delta — API measurementDate not currently mapped`
- source_b: `gridflow silver/elexon/temp.py L57 renames measurementDate → measurement_date but output_cols L95-99 does NOT include it`
- orchestrator_recommendation: **non-blocking** — add `measurement_date` to `output_cols` if downstream needs the original measurement date (vs derived `timestamp_utc`).

**Recommendation:** Bundle 2.1 + 2.2 + 2.3 into a single Phase-7-style mini-recon PR against `gridflow`. Each fix is < 5 lines of column-mapping update. Add regression tests that fail if the mapping ever drifts again (e.g., assert that a freshly-captured live-API JSON round-trips through the transformer with no null columns).

---

## Category 3 — Schema declares fields the transformer does not emit (3 occurrences) · BLAST RADIUS: LOW

**Pattern:** the Pydantic class declares a field that does not appear in the transformer's `output_cols` list. Code that imports the class and accesses the field receives `None` for every row.

### 3.1 `boal` — `bid_offer_acceptance_number` reserved-but-unpopulated
- source_a: `vault Silver schema includes bid_offer_acceptance_number as distinct column`
- source_b: `schemas/elexon.py L114 declares bid_offer_acceptance_number: int | None; silver/elexon/boal.py output_cols L113-119 does NOT include it`
- orchestrator_recommendation: **trust gridflow** — `bid_offer_acceptance_number` is reserved for a future per-pair column. Either populate it in the transformer or remove it from the schema. Currently it always returns null.

### 3.2 `fuelhh` — `published_at` declared but not emitted
- source_a: `schemas/elexon.py L87 declares ElexonFuelHH.published_at`
- source_b: `silver/elexon/fuelhh.py L103-106 output_cols does NOT include published_at`
- orchestrator_recommendation: **trust gridflow silver** — `published_at` is documented as the PIT field but the transformer drops it. The reference page `authored-pages/elexon/fuelhh.html` treats it as the PIT field anyway. Recommendation: add `"published_at"` to `output_cols` to make the schema honest, or remove from `ElexonFuelHH` and document the column drop.

### 3.3 `uou2t14d` — `fuel_type` and `national_grid_bm_unit` renamed but dropped
- source_a: `vault Silver schema lists 7 columns`
- source_b: `silver/elexon/uou2t14d.py L63-65 renames fuelType and nationalGridBmUnit but output_cols L114-117 does NOT include them`
- orchestrator_recommendation: **trust gridflow output_cols** — fuel_type and national_grid_bm_unit are dropped. Joins for fuel context must use `bmunits_reference`, not UOU2T14D's own fuel column. Either restore them to `output_cols` (simpler downstream) or update vault to mark them dropped.

**Recommendation:** small PR to either align schema with `output_cols` or vice-versa. Low priority.

---

## Category 4 — Connector param-style doc-vs-code mismatches (3 occurrences) · BLAST RADIUS: LOW

**Pattern:** vault notes a documented API parameter (from docs) that the gridflow connector does not pass. The API accepts the alternate (default) param style and returns data anyway, so this is a working-but-undocumented state.

### 4.1 `nonbm` — docs say `from`/`to`; connector uses default `publishDateTimeFrom`/`To`
- source_a: `vault Implementation Delta`
- source_b: `connectors/elexon/endpoints.py L200-204 uses default PUBLISH_DATETIME style`
- orchestrator_recommendation: live test 2026-05-08 confirmed both work. Choose one as canonical and update either docs or code for consistency with REMIT/SOSO patterns.

### 4.2 `melngc` — `boundary` filter supported by API but not used by connector AND transformer drops boundary
- source_a: `vault API endpoint table accepts boundary`
- source_b: `connectors/elexon/endpoints.py L140-144 + silver/elexon/melngc.py output_cols`
- orchestrator_recommendation: connector doesn't send boundary; transformer additionally drops it from silver output despite the API returning it — internal inconsistency with `inddem`/`indgen` which preserve boundary. Recommend aligning with siblings (preserve boundary in silver).

### 4.3 `imbalngc` — `boundary` filter supported by API but not used by connector
- source_a: `vault API endpoint table includes boundary`
- source_b: `connectors/elexon/endpoints.py L125-129 omits boundary from param style`
- orchestrator_recommendation: trust gridflow as the active default — `boundary` left unfiltered (returns all boundaries). Extend the connector if downstream needs boundary filtering.

**Recommendation:** small consistency-pass PR. Decide whether to expose `boundary` filtering across the indicated suite (inddem, indgen, imbalngc, melngc, tsdf) or document that all of them ignore the param and return mixed boundaries.

---

## Category 5 — Vendor identifier/header inconsistencies (2 occurrences) · BLAST RADIUS: LOW

**Pattern:** the vendor's record header field (`dataset:`) or path naming carries a different value than the documented endpoint name.

### 5.1 `lolpdrm` — `dataset: LOLPDM` (no trailing R) in record headers
- source_a: `vault Bronze Sample uses dataset: LOLPDM`
- source_b: `connectors/elexon/endpoints.py L229 registers path as /datasets/LOLPDRM`
- orchestrator_recommendation: documented vendor inconsistency. Connector path is correct; the `dataset` field in bronze is metadata only. Don't filter bronze on `dataset == 'LOLPDRM'` — you'll find zero rows.

### 5.2 `boal` — slug `boal` ≠ API path `BOALF`
- source_a: vault Overview heading
- source_b: `connectors/elexon/endpoints.py L67-73 path=/datasets/BOALF; old BOAL also in EXCLUDED_ENDPOINTS`
- orchestrator_recommendation: documented and consistent. Gridflow slug retains `boal` for backward compat while the API path tracks BOALF. Surface in editorial layer for clarity.

**Recommendation:** no code action needed; both already documented. Captured here for the user's reference.

---

## Category 6 — Cosmetic / documentation drift (12 occurrences) · BLAST RADIUS: NONE

These are documented in the per-brief frontmatter but require no immediate code or vault action. Listed here for completeness:

- **agpt, agws, atl, fou2t14d, uou2t14d**: vault schema documentation marks columns as required that the silver layer treats as optional (e.g. `settlement_period` is conditional for forecast-only payloads in fou2t14d/uou2t14d).
- **agpt, freq**: vault sample placeholder strings (`"..."`) where the actual gridflow output would have a typed value.
- **disbsad, netbsad**: vault placeholder `stor_flag: "..."` strings where the actual value is a `bool`.
- **freq (V2-FIX-01), system_prices (V2-FIX-04), remit + soso (V2-FIX-03)**: documented and resolved schema/connector fixes. Listed in frontmatter for traceability; no further action needed.
- **system_prices**: cosmetic registry-path-omits-{date}-placeholder (actual URL is correct via DATE_PATH style).
- **bmunits_reference**: implementation-defined order-of-preference between `bmUnit` vs `elexonBmUnit` field names; both supported.
- **ndf, ndfd, windfor**: vault Silver Sample placeholders for derived fields (`issue_time`, `transmission_demand_mw`, etc.) that the actual transformer derives correctly.
- **indod**: vault sparse-cadence note is documented but not enforced (connector returns whatever the window contains).

**Recommendation:** refresh during the next vault drift-check pass; not blocking for Phase 9 / Phase 10 execution.

---

## Summary recommendation for the user

1. **Approve Phase-7 mini-recon for Category 1 (21 missing Pydantic classes)** — choose Option A (codify the policy) or Option B (mechanical class additions). My pick: Option A unless gridflow_models specifically needs typed classes.
2. **Bundle Category 2 (4 silent-null column mappings) into a single PR** — small, targeted, with regression tests to prevent future drift.
3. **Defer Categories 3-6** — useful background for the next vault drift-check or Phase 9/10 vendor-doc refresh; not blocking.
4. **Phase 9 / Phase 10 brief production** should grep the corresponding `schemas/<vendor>.py` files for class-coverage gaps and adopt the same "trust silver transformer; document absent class" pattern this phase used for Elexon.

If you accept the Category 1 recommendation, you can spin off the mini-recon as a separate background task; if you reject (or want more discussion), no action is needed and the briefs remain as-is — they explicitly flag every absence so downstream Claude Design has full context regardless.
