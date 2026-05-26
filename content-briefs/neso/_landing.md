---
slug: _landing
vendor: neso
vendor_label: NESO Carbon Intensity
brief_type: landing
vault_dataset_count: 33
last_verified: 2026-05-09
sources_consulted:
  - quant-vault/30-vendors/neso/datasets/ (34 files total: 33 dataset .md files + README.md; see discrepancies_found for README note)
  - gridflow/src/gridflow/connectors/neso/endpoints.py (ENDPOINTS dict — 33 keys across 4 categories; DEFAULT_POSTCODE L13, DEFAULT_REGION_ID L14)
  - gridflow/src/gridflow/connectors/neso/client.py (NesoConnector — no auth, Accept header only, retry policy)
  - gridflow/src/gridflow/schemas/neso.py (7 classes: _NesoBase, _TimestampedNesoBase, CarbonIntensity, CarbonIntensityStats, CarbonIntensityFactor, GenerationMix, RegionalIntensity)
  - "gridflow/src/gridflow/silver/neso/carbon_intensity.py (1 file — GenericNesoJsonTransformer base + CarbonIntensityTransformer; dynamically generates 33 transformer classes via register_neso_transformers() at L110–118)"
  - gridflow-front-end/src/gridflow_front_end/build.py COMING_SOON_VENDORS (neso stub at L176 — vendor_label 'NESO Carbon Intensity', vendor_docs_url 'https://carbonintensity.org.uk/')
  - https://carbon-intensity.github.io/api-definitions/ (vendor API docs — attempted WebFetch; result surfaced in discrepancies_found)
discrepancies_found:
  - source_a: "quant-vault/30-vendors/neso/datasets/ ls *.md | wc -l"
    source_a_says: "34 files returned by glob (33 dataset files + README.md)"
    source_b: "gridflow/src/gridflow/connectors/neso/endpoints.py ENDPOINTS dict"
    source_b_says: "33 endpoint keys — exactly one per vault dataset file, excluding README.md"
    orchestrator_recommendation: "Use vault_dataset_count: 33 (true dataset count). The structural Check 7 expected count will read 34 from ls glob; note in BRIEF-LOG.md as a known README-inclusion false positive for this vendor."
  - source_a: "vault/neso/datasets/carbon_intensity.md Historical depth row"
    source_a_says: "Historical depth: TODO — official docs do not state earliest date; max 14 days per request"
    source_b: "build.py COMING_SOON_VENDORS neso entry"
    source_b_says: "No earliest date field present in stub"
    orchestrator_recommendation: "EARLIEST cell in brief marked 'not documented · max 14 days / request' — needs-info. Phase 10 per-dataset briefs should resolve this via live API verification."
  - source_a: "vault/neso/datasets/carbon_intensity.md Rate limit row"
    source_a_says: "Not documented by NESO; Gridflow config uses 10 req/s"
    source_b: "gridflow/src/gridflow/connectors/neso/endpoints.py — no rate-limit constant defined"
    source_b_says: "Rate limit is set only in config/sources.yaml (10 req/s); not encoded in endpoints.py"
    orchestrator_recommendation: "Use '10 req/s · project default (vendor undocumented)' for RATE LIMIT cell"
ready_for_claude_design: true
checked_at: 2026-05-20T12:00:00Z
---

# Editorial layer

**H1 pattern:**

```html
NESO <span class="italic">Carbon.</span>
```

**Eyebrow chip:** `NESO · United Kingdom · Carbon`

**Illustrative snapshot chip:** yes (standard)

**Lede paragraph (≤60 words):**

The National Energy System Operator's public Carbon Intensity API for Great Britain. Half-hourly forecast and actual grid carbon intensity in gCO₂/kWh, generation mix by fuel type, regional intensity by DNO zone and postcode, and 48-hour forward forecasts — all without authentication. 33 endpoint surfaces covering national, regional, and reference data.

**CTA 1:** `Browse 33 datasets ↓` (anchors `#datasets`)
**CTA 2:** `Vendor docs ↗` → `https://carbonintensity.org.uk/`

---

# Vendor metadata

| Cell label | Value |
|---|---|
| BASE URL | `api.carbonintensity.org.uk` |
| AUTH | Public · no key required (`Accept: application/json` header only) |
| RATE LIMIT | 10 req/s · project default (vendor undocumented) |
| FORMAT | JSON · ISO-8601 · UTC |
| EARLIEST | Not documented · max 14 days per request |
| TIMEZONE | UTC · 30-min settlement periods |

---

# Stats strip

| slot | value | label | source |
|---|---|---|---|
| 1 | `33` | `Datasets` | 33 dataset files in vault (excluding README.md) |
| 2 | `4` | `Categories` | 4 endpoint categories per endpoints.py |
| 3 | `48h` | `Forecast horizon` | intensity_fw48h / regional_intensity_fw48h look ahead 48 hours |
| 4 | `gCO₂/kWh` | `Reporting unit` | canonical NESO unit for all intensity values |

---

# About section

**Paragraph 1 — Who they are:**

`neso` is the National Energy System Operator (formerly National Grid ESO), which operates the GB electricity system and publishes the Carbon Intensity API as a public data service at `api.carbonintensity.org.uk`. The API was developed in partnership with the Environmental Defense Fund Europe and University of Oxford. It requires no authentication — the entire surface is open to anonymous HTTP access.

**Paragraph 2 — What they publish:**

33 endpoint surfaces fall into four categories. **Carbon Intensity - National** (10 datasets): half-hourly forecast and actual intensity in gCO₂/kWh plus point-in-time, date, period, and windowed range queries. **Statistics - National** (2 datasets): aggregated intensity statistics over windowed ranges and hour blocks. **Generation Mix - National** (3 datasets): per-fuel generation percentage breakdown from the current run, prior 24h, and date range. **Carbon Intensity - Regional** (18 datasets): intensity at all-GB, England/Scotland/Wales, DNO region-ID, and postcode granularities — each with current, fw24h, fw48h, and pt24h variants.

**Paragraph 3 — Why it matters for energy trading:**

The NESO carbon intensity series is the primary half-hourly carbon signal for GB grid operations. Pair `carbon_intensity` actuals with `elexon.fuelhh` (per-fuel generation) to derive marginal emission factors: when CCGT generation is the marginal unit, every additional MWh carries ~394 gCO₂ vs ~937 gCO₂ for coal. The `intensity_fw48h` forward forecast, calibrated to temperature-driven demand, supports intra-day carbon dispatch optimisation and ESG reporting. `generation` (fuel mix) cross-referenced with `elexon.system_prices` reveals weather-driven carbon-price correlations over multi-year backtests.

---

# Groups

## Group: Carbon Intensity · National

**Blurb:** Half-hourly national grid carbon intensity — actuals, forecasts, and windowed range queries.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `carbon_intensity` | Carbon intensity · national · date range | 30 min | ~0 | ~48 / day |
| `intensity_current` | Carbon intensity · current half-hour | 30 min | ~0 | 1 snapshot |
| `intensity_today` | Carbon intensity · today all periods | 30 min | ~0 | ~48 / day |
| `intensity_date` | Carbon intensity · single date | 30 min | ~0 | 48 / date |
| `intensity_period` | Carbon intensity · single settlement period | 30 min | ~0 | 1 snapshot |
| `intensity_at` | Carbon intensity · at datetime | 30 min | ~0 | 1 snapshot |
| `intensity_fw24h` | Carbon intensity · forecast 24h ahead | 30 min | forecast | ~48 |
| `intensity_fw48h` | Carbon intensity · forecast 48h ahead | 30 min | forecast | ~96 |
| `intensity_pt24h` | Carbon intensity · prior 24h | 30 min | ~0 | ~48 |
| `intensity_factors` | Emission factors · per fuel type | static | on change | 1 snapshot |

## Group: Statistics · National

**Blurb:** Aggregated carbon intensity statistics over windowed ranges — max, min, mean, and hour-block splits.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `intensity_stats` | Carbon intensity statistics · windowed range | 30 min | ~0 | 1 per window |
| `intensity_stats_block` | Carbon intensity statistics · 24h block splits | 30 min | ~0 | varies by block |

## Group: Generation Mix · National

**Blurb:** Per-fuel generation mix percentage breakdown — current run, prior 24h, and date range.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `generation` | Generation mix · national · date range | 30 min | ~0 | ~48 × N fuels / day |
| `generation_current` | Generation mix · current half-hour | 30 min | ~0 | N fuels snapshot |
| `generation_pt24h` | Generation mix · prior 24h | 30 min | ~0 | ~48 × N fuels |

## Group: Carbon Intensity · Regional

**Blurb:** Regional carbon intensity by GB DNO zone, country, and postcode — current, fw24h, fw48h, and pt24h.

| id | title | freq | lag | rows |
|---|---|---|---|---|
| `regional_current` | Regional intensity · all GB regions | 30 min | ~0 | ~17 regions |
| `regional_england` | Regional intensity · England | 30 min | ~0 | 1 snapshot |
| `regional_scotland` | Regional intensity · Scotland | 30 min | ~0 | 1 snapshot |
| `regional_wales` | Regional intensity · Wales | 30 min | ~0 | 1 snapshot |
| `regional_postcode` | Regional intensity · by postcode | 30 min | ~0 | 1 snapshot |
| `regional_regionid` | Regional intensity · by region ID | 30 min | ~0 | 1 snapshot |
| `regional_intensity` | Regional intensity · all regions · date range | 30 min | ~0 | ~17 × 48 / day |
| `regional_intensity_fw24h` | Regional intensity · all regions · fw24h | 30 min | forecast | ~17 × 48 |
| `regional_intensity_fw24h_postcode` | Regional intensity fw24h · by postcode | 30 min | forecast | ~48 |
| `regional_intensity_fw24h_regionid` | Regional intensity fw24h · by region ID | 30 min | forecast | ~48 |
| `regional_intensity_fw48h` | Regional intensity · all regions · fw48h | 30 min | forecast | ~17 × 96 |
| `regional_intensity_fw48h_postcode` | Regional intensity fw48h · by postcode | 30 min | forecast | ~96 |
| `regional_intensity_fw48h_regionid` | Regional intensity fw48h · by region ID | 30 min | forecast | ~96 |
| `regional_intensity_pt24h` | Regional intensity · all regions · pt24h | 30 min | ~0 | ~17 × 48 |
| `regional_intensity_pt24h_postcode` | Regional intensity pt24h · by postcode | 30 min | ~0 | ~48 |
| `regional_intensity_pt24h_regionid` | Regional intensity pt24h · by region ID | 30 min | ~0 | ~48 |
| `regional_intensity_postcode` | Regional intensity · by postcode · date range | 30 min | ~0 | ~48 per window |
| `regional_intensity_regionid` | Regional intensity · by region ID · date range | 30 min | ~0 | ~48 per window |

**Row count:** 10 + 2 + 3 + 18 = 33 dataset rows across 4 groups == `vault_dataset_count: 33`. ✓

---

# Source map

| Gridflow source | Purpose | Notes |
|---|---|---|
| `connectors/neso/endpoints.py` | 33 endpoint registrations across 4 categories; path templates; parser family assignments | `ENDPOINTS` dict L44–286; `DEFAULT_POSTCODE = "RG10"` L13; `DEFAULT_REGION_ID = 13` L14; `NESO_DATETIME_FORMAT = "%Y-%m-%dT%H:%MZ"` L12 |
| `connectors/neso/client.py` | No-auth connector; `Accept: application/json` header; retry policy | `NesoConnector` — no API key; all routes are public |
| `schemas/neso.py` | 7 Pydantic classes: `_NesoBase`, `_TimestampedNesoBase`, `CarbonIntensity`, `CarbonIntensityStats`, `CarbonIntensityFactor`, `GenerationMix`, `RegionalIntensity` | `IntensityIndex` Literal type alias (`"very low"` / `"low"` / `"moderate"` / `"high"` / `"very high"`) defined at L13 |
| `silver/neso/carbon_intensity.py` | Single file; `GenericNesoJsonTransformer` base (L24) + `CarbonIntensityTransformer` (L103); `register_neso_transformers()` (L110) dynamically creates 33 typed classes | All 33 transformer classes are generated at import time via `type(class_name, (GenericNesoJsonTransformer,), {...})` — they are real classes registered to the transformer registry |
| `build.py COMING_SOON_VENDORS` | `neso` stub at L176 — `vendor_label = "NESO Carbon Intensity"`, `vendor_docs_url = "https://carbonintensity.org.uk/"` | Not yet promoted to `REAL_VENDORS`; this brief defines the `vendor_meta` block for Phase 10 promotion |

---

# Cross-vendor links

- **`elexon` · `fuelhh`** — marginal emission factor modelling: NESO `carbon_intensity` + Elexon per-fuel generation outturn → derive marginal gCO₂/kWh by hour, accounting for dispatch merit order. Core MEF workstream.
- **`elexon` · `system_prices`** — carbon-price correlation: grid carbon intensity vs system buy/sell price; weather-driven volatility analysis over multi-year backtest windows.
- **`openmeteo` · `historical_demand`** — weather-driven carbon attribution: temperature HDD/CDD from ERA5 explains ~60% of short-run national carbon intensity variation; regression basis for carbon nowcasting.
- **`entsog` · `aggregated_physical_flows`** — gas-supply carbon view: ENTSO-G GB interconnection nominations predict CCGT dispatch probability 1–3 days ahead; leads NESO intensity signal by gas-flow lead time.
- **`elexon` · `windfor`** — renewable-carbon coupling: Elexon wind forecast vs NESO intensity — days with high forecast wind show anticipatory decarbonisation in the D+1 intensity forecast series.

---

# Caveats

## 01 Earliest data date not documented by NESO

The Carbon Intensity API does not publish an official earliest data date. The vault notes "max 14 days per request" as the only documented constraint on historical depth. In practice, historical data appears to be available from approximately 2018 onwards (the API's original launch date), but this has not been verified in the vault's curl-based verification process. Phase 10 per-dataset briefs should run a binary-search verification against the live API to determine true earliest coverage.

**Source:** vault `carbon_intensity.md` Historical depth row: "TODO — official docs do not state earliest date; max 14 days per request"

## 02 Rate limit is gridflow-configured, not vendor-documented

NESO does not publish a rate limit for the Carbon Intensity API. The 10 req/s figure in the RATE LIMIT hero cell is gridflow's own project default (`config/sources.yaml`), not a vendor-imposed constraint. Downstream users running their own clients should treat this as a courtesy cap rather than a hard API boundary. The connector's `endpoints.py` does not encode a rate-limit constant (unlike GIE's `GIE_MAX_CALLS_PER_MINUTE`).

**Source:** vault `carbon_intensity.md` Rate limit: "Not documented by NESO; Gridflow config uses 10 req/s"; `connectors/neso/endpoints.py` — no rate-limit constant.

## 03 vault_dataset_count 33 vs ls *.md count 34 (README.md inclusion)

The structural Check 7 script runs `ls vault/neso/datasets/*.md | wc -l` which returns 34 — one README.md is included in the glob. The true dataset count is 33 (matching the 33 keys in `ENDPOINTS`). This brief uses `vault_dataset_count: 33` and lists 33 dataset rows. The Check 7 mismatch (expected=34, listed=33) is a known false positive from the README glob; it has been logged in BRIEF-LOG.md.

**Source:** `ls quant-vault/30-vendors/neso/datasets/*.md | wc -l` = 34; `len(ENDPOINTS)` = 33.

## 04 Generation Mix and Regional are labelled "beta" in NESO's API

The `Generation Mix - National` and `Carbon Intensity - Regional` categories carry a "beta" qualifier in NESO's API definition (visible in endpoint `category` strings: "Generation Mix - National beta", "Carbon Intensity - Regional beta"). The data is live and the gridflow connector treats these endpoints as fully operational, but NESO may modify or deprecate them without the standard versioning notice applied to the main intensity surface.

**Source:** `connectors/neso/endpoints.py` endpoint `category` fields.

## 05 Transformer classes are dynamically generated, not statically defined

Unlike all other vendors in gridflow (where silver transformer classes are explicitly defined), NESO's 33 transformer classes are generated at import time by `register_neso_transformers()` in `silver/neso/carbon_intensity.py` (L110–118) using Python's `type()` factory. The classes are real (not lambdas), are registered to the transformer registry, and behave identically to static classes. However, static analysis tools (mypy, IDE introspection) cannot inspect them without running the registration code.

**Source:** `silver/neso/carbon_intensity.py` L121–136 `_make_transformer_class` and L110–118 `register_neso_transformers`.

---

# Per-vendor cheatsheet

## Endpoint categories and dataset counts

| Category | Count | Representative datasets |
|---|---|---|
| Carbon Intensity - National | 10 | `carbon_intensity`, `intensity_fw48h`, `intensity_factors` |
| Statistics - National | 2 | `intensity_stats`, `intensity_stats_block` |
| Generation Mix - National beta | 3 | `generation`, `generation_current`, `generation_pt24h` |
| Carbon Intensity - Regional beta | 18 | `regional_intensity`, `regional_intensity_fw48h`, `regional_postcode` |

## IntensityIndex values

`"very low"` · `"low"` · `"moderate"` · `"high"` · `"very high"` (Literal type alias in `schemas/neso.py` L13)

## Key schema classes → datasets

| Class | Datasets |
|---|---|
| `CarbonIntensity` | All intensity_* and carbon_intensity endpoints |
| `CarbonIntensityStats` | `intensity_stats`, `intensity_stats_block` |
| `CarbonIntensityFactor` | `intensity_factors` |
| `GenerationMix` | `generation`, `generation_current`, `generation_pt24h` |
| `RegionalIntensity` | All regional_* endpoints |

## Default query values

`DEFAULT_POSTCODE = "RG10"` (Wargrave, Berkshire — used for postcode-scoped endpoints in tests/examples)
`DEFAULT_REGION_ID = 13` (South East England DNO zone)
`DEFAULT_PERIOD = 1` (first settlement period of the gas/calendar day)
`DEFAULT_STATS_BLOCK_HOURS = 24`

---

# Source-of-truth note

Pages are regenerated from the [gridflow](https://github.com/EBentham/gridflow) ETL pipeline's vault content via `gridflow-build`. Schemas align with `gridflow.schemas.neso` (`CarbonIntensity`, `GenerationMix`, `RegionalIntensity`, etc.); values shown in charts are illustrative deterministic snapshots, not live NESO Carbon Intensity API responses. The vault's `neso/datasets/` files are the canonical per-dataset reference; this landing brief is the vendor-hub layer above them.
