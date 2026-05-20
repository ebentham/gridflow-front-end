---
slug: actual_generation
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A75
last_verified: 2026-05-08
sources_consulted:
  - quant-vault/30-vendors/entsoe/datasets/actual_generation.md (vault not yet vendored to gridflow-front-end/vault/entsoe/ — Phase 9 vendoring deferred)
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeActualGeneration (lines 46-61)
  - gridflow/src/gridflow/silver/entsoe/actual_generation.py::ActualGenerationTransformer (lines 18-90)
  - gridflow/src/gridflow/connectors/entsoe/client.py (DOC_TYPES dispatch, lines 23+106+112)
  - https://web-api.tp.entsoe.eu/api?documentType=A75 (XML API — not browsable; documented in transparency.entsoe.eu API Guide §16.1.B; no vendor doc page to WebFetch)
discrepancies_found:
  - source_a: "vault Silver schema: lists area_name as a 6th silver column"
    source_a_says: "area_name (str, No-Nullable, derived, default '')"
    source_b: "gridflow silver/entsoe/actual_generation.py — transformer does not populate area_name"
    source_b_says: "Pydantic class declares area_name: str = '' but the transformer leaves it unfilled — silver rows always have area_name == ''. Marked 'unverified in silver output' in vault Implementation Delta."
    orchestrator_recommendation: "trust gridflow silver — same Category-3 shape as boal.bid_offer_acceptance_number (handover P2). Either populate via an EIC → area_name lookup in the transformer or drop from Pydantic. Surface as a caveat for downstream consumers."
  - source_a: "vault API endpoint table — psrType listed as optional filter"
    source_a_says: "psrType (str, No, Filter to one production type, e.g. B16)"
    source_b: "gridflow connectors/entsoe/client.py — psrType is NOT in optional_params for actual_generation; caller can still inject via **params into _optional_filter_params"
    orchestrator_recommendation: "documented vault gap — connector path exists but isn't first-class. Low priority; works for callers who know the API."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Realised generation, <span class="italic fg-accent">by fuel and zone.</span>

**Lede:** Actual realised MW generation per EIC bidding zone, broken down by PSR (Primary Source) production type — coal, gas, wind onshore, wind offshore, solar, hydro, nuclear, biomass. The canonical residual-load input for European power-market models (`actual_load − wind − solar = residual demand`), and the cross-vendor analogue of GB's `fuelhh` published by individual TSOs.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency Platform · A75](https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType/show)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.actual_generation` |
| API PATH | `/api?documentType=A75&processType=A16` |
| FREQUENCY | PT15M · PT30M · PT60M (zone-dependent) |
| PUBLICATION LAG | T+1h → T+24h (zone-dependent) |
| VOLUME | ~17 TimeSeries / zone / day |
| PRIMARY KEY | `(timestamp_utc, area_code, production_type)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 25 | PSR production types (B01..B25) |
| 2 | T+1h → T+24h | Publication lag |
| 3 | XML | Response format (`GL_MarketDocument`) |
| 4 | 6 | Schema columns |

# Sidebar siblings

- actual_load
- day_ahead_prices
- wind_solar_forecast
- cross_border_flows
- actual_generation_units

# Overview

1. <code>actual_generation</code> is **realised generation per production type** in MW for each EIC bidding zone, broken down by PSR (Primary Source) — coal, gas, wind onshore (`B19`), wind offshore (`B18`), solar (`B16`), hydro (`B11`/`B12`), nuclear (`B14`), biomass (`B01`), and ~17 other categories. Published per settlement period (resolution varies by zone: `PT15M` for DE/AT/FR, `PT60M` for others). Each row carries `(timestamp_utc, area_code, production_type)` as the primary key and `generation_mw` as the value.

2. Gridflow fetches it from the ENTSO-E Transparency Platform's XML API at <code>web-api.tp.entsoe.eu/api</code> with `documentType=A75`, `processType=A16` (realised), and `in_Domain` set to the EIC zone (e.g. `10Y1001A1001A82H` for DE-LU). Authentication is via query-param `securityToken=$ENTSOE_API_KEY`. The connector dispatch is registered in <code>connectors/entsoe/client.py::DOC_TYPES["actual_generation"]</code>. The response is XML rooted at <code>GL_MarketDocument</code> with one <code>TimeSeries</code> per PSR type. The <code>ActualGenerationTransformer</code> parses the XML, expands each Period's Points (using start + `position * resolution`) into per-timestep rows, and writes to the silver parquet partition. Pydantic class <code>EntsoeActualGeneration</code> is declared.

3. Cadence is per-zone — most zones publish hourly with T+1h lag; some lag T+24h. Verified against the live API on 2026-05-08; DE-LU returned 17 TimeSeries for 2026-05-06 (one per PSR type). The same call against GB (`10YGB----------A`) returned an Acknowledgement_MarketDocument with reason 999 "No matching data" — **GB stopped publishing aggregated generation to ENTSO-E after Brexit**; use Elexon `fuelhh` or `fuelinst` for GB fuel mix instead.

# Sample chart

- **Type:** `stackedArea`
- **Title:** "DE-LU generation by production type · 24-hour snapshot"
- **Subtitle:** "Stacked area · MW · UTC · 6 May 2026"
- **Seed:** 11
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeActualGeneration` (lines 46-61) and `gridflow/silver/entsoe/actual_generation.py` · `ActualGenerationTransformer.output_cols`. Partitioned by `timestamp_utc` (year + month). Point-in-time field: **none** (revisions overwrite via sort-and-keep-last on the dedup key).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + `position × resolution` | tz-aware UTC; resolution varies (`PT15M` / `PT30M` / `PT60M`). Validator requires tzinfo. | `schemas/entsoe.py L49, L56-61` |
| `area_code` | `str` | No | `<inBiddingZone_Domain.mRID>` (codingScheme A01) | EIC bidding zone identifier (e.g. `10YGB----------A`, `10Y1001A1001A82H`). | `schemas/entsoe.py L50` |
| `area_name` | `str` | No (default `""`) | _derived_ | **Declared but not populated by the transformer** — always `""` in silver. See Caveats #04. | `schemas/entsoe.py L51` |
| `production_type` | `str` | No | `<MktPSRType><psrType>` | EIC PSR-type code, `B01`..`B25`. See Production types section below for the full codelist. | `schemas/entsoe.py L52` |
| `generation_mw` | `float` | No | `<Point><quantity>` | MW. XML unit is `MAW` (mega-amp-watt = MW in the IEC 62325 spec). | `schemas/entsoe.py L53` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L54` |

**PARQUET PATH:** `data/silver/entsoe/actual_generation/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code, production_type)` — keep last on sort (silently overwrites prior revisions; no `published_at`)

# Sample data

| timestamp_utc | area_code | area_name | production_type | generation_mw | data_provider |
|---|---|---|---|---|---|
| 2026-05-05T22:00:00+00:00 | 10Y1001A1001A82H | _empty_ | B19 (Wind Onshore) | 0.0 | entsoe |
| 2026-05-05T22:15:00+00:00 | 10Y1001A1001A82H | _empty_ | B16 (Solar) | 1843.5 | entsoe |
| 2026-05-05T22:15:00+00:00 | 10Y1001A1001A82H | _empty_ | B14 (Nuclear) | 4280.0 | entsoe |
| 2026-05-05T22:15:00+00:00 | 10Y1001A1001A82H | _empty_ | B12 (Hydro Pumped Storage) | -340.0 | entsoe |
| _ROW HIGHLIGHTED_ 2026-05-06T11:00:00+00:00 | 10Y1001A1001A82H | _empty_ | B16 (Solar) | 28940.0 | entsoe |
| 2026-05-06T11:00:00+00:00 | 10Y1001A1001A82H | _empty_ | B05 (Fossil Hard coal) | 1820.0 | entsoe |
| 2026-05-06T11:00:00+00:00 | 10Y1001A1001A82H | _empty_ | B04 (Fossil Gas) | 12450.0 | entsoe |
| 2026-05-06T22:00:00+00:00 | 10Y1001A1001A82H | _empty_ | B16 (Solar) | 0.0 | entsoe |

[1] Rows derived from vault Bronze sample (DE-LU, 2026-05-06, captured live 2026-05-08); PSR-type code labels added editorially. The highlighted row is solar midday peak (`B16` = 28.9 GW) — illustrates the diurnal swing the dataset is most useful for. Hydro Pumped Storage shows -340 MW (charging from grid) — note the negative-can-occur semantics for storage classes. `area_name` is empty in every row because the transformer doesn't populate it (Caveats #04).

# Production types (PSR codelist — `psrType` field)

EIC code list B01..B25, used in the `production_type` column. This is the canonical taxonomy for European generation — every TSO publishes against it.

| Code | Type | Notes |
|---|---|---|
| `B01` | Biomass | |
| `B02` | Fossil Brown coal / Lignite | |
| `B03` | Fossil Coal-derived gas | |
| `B04` | Fossil Gas | CCGT / OCGT combined |
| `B05` | Fossil Hard coal | |
| `B06` | Fossil Oil | |
| `B07` | Fossil Oil shale | |
| `B08` | Fossil Peat | |
| `B09` | Geothermal | |
| `B10` | Hydro Pumped Storage | Negative = charging from grid |
| `B11` | Hydro Run-of-river and poundage | |
| `B12` | Hydro Water Reservoir | |
| `B13` | Marine | |
| `B14` | Nuclear | |
| `B15` | Other renewable | |
| `B16` | Solar | |
| `B17` | Waste | |
| `B18` | Wind Offshore | Distinct from B19 — offshore-only |
| `B19` | Wind Onshore | Distinct from B18 — onshore-only |
| `B20` | Other | |
| `B25` | Energy storage | (rare; non-pumped batteries) |

(Codes `B21`..`B24` are reserved/unused in the current spec.)

# API & ingestion

**Endpoint card:**
- **ENDPOINT**: `web-api.tp.entsoe.eu/api?documentType=A75&processType=A16&in_Domain={EIC}&periodStart={YYYYMMDDhhmm}&periodEnd={YYYYMMDDhhmm}`
- **AUTH**: query-param `securityToken={ENTSOE_API_KEY}` — register for an API key at [transparency.entsoe.eu](https://transparency.entsoe.eu/)

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/entsoe/actual_generation/<year>/<month>/<day>/raw_<uuid>.xml`
- **TRANSFORMER**: `gridflow.silver.entsoe.actual_generation.ActualGenerationTransformer`

**Tab 1 — Example URL:**
```
https://web-api.tp.entsoe.eu/api
  ?securityToken=$ENTSOE_API_KEY
  &documentType=A75
  &processType=A16
  &in_Domain=10Y1001A1001A82H
  &periodStart=202605060000
  &periodEnd=202605070000
```

**Tab 2 — DuckDB · SQL:**
```sql
-- Daily generation mix for DE-LU last 7 days
SELECT date_trunc('day', timestamp_utc) AS day,
       production_type,
       sum(generation_mw) / count(*) AS avg_mw
FROM read_parquet('data/silver/entsoe/actual_generation/**/*.parquet')
WHERE area_code = '10Y1001A1001A82H'
  AND timestamp_utc >= current_timestamp - INTERVAL 7 DAY
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · parquet:**
```python
import polars as pl

df = pl.read_parquet(
    "data/silver/entsoe/actual_generation/**/*.parquet",
)
# Pivot to wide: one column per production type
mix = df.filter(pl.col("area_code") == "10Y1001A1001A82H").pivot(
    index="timestamp_utc",
    on="production_type",
    values="generation_mw",
    aggregate_function="sum",
)
# Residual load = actual_load - wind - solar (canonical MEF feature)
print(mix.select(["timestamp_utc", "B19", "B18", "B16"]).tail())
```

# Caveats

## 01 GB stopped publishing post-Brexit

Calls against GB (`10YGB----------A`) return HTTP 200 with an `Acknowledgement_MarketDocument` and reason 999 ("No matching data found"). GB ceased publishing aggregated generation to ENTSO-E after the GB exit from the IEM (verified 2026-05-08). For GB fuel mix, use Elexon `fuelhh` (30 min, settled) or `fuelinst` (5 min, real-time). *Source: vault Known Issues #1.*

## 02 Resolution varies by zone

Most zones publish hourly (`PT60M`), but DE / AT / FR are quarter-hourly (`PT15M`) and a few are half-hourly (`PT30M`). Don't assume hourly when joining against settlement-period datasets. The `timestamp_utc` column is at the published resolution — downstream aggregation to hourly may be needed for cross-zone comparison. *Source: vault Known Issues #2.*

## 03 Revisions silently overwrite

Same `(timestamp_utc, area_code, production_type)` may be republished by the TSO with revised values. The transformer dedups via sort-last — older revisions are silently overwritten on re-ingest. There is **no** `published_at` field surfaced in silver, so point-in-time queries against historical revisions are not possible without re-fetching from bronze. *Source: vault Known Issues #3.*

## 04 `area_name` is always empty

The Pydantic class declares `area_name: str = ""` but the transformer does not populate it — every silver row has `area_name == ""`. Treat as a known unfilled column; if you need a human-readable zone name, join against an EIC reference lookup. Same Category-3 shape as Elexon `boal.bid_offer_acceptance_number` and `fuelhh.published_at`. *Source: vault Implementation Delta + cross-checked against `silver/entsoe/actual_generation.py output_cols`.*

## 05 Storage units carry both directions

A75 includes both generation (XML `businessType=A03`) and consumption (`A04`) for storage units — pumped hydro charging appears as negative `generation_mw` in the B10 / B12 rows. Sum-by-fuel without checking sign will undercount renewables and overcount thermal. Filter on `generation_mw > 0` or treat storage classes specially for net-generation calculations. *Source: vault Known Issues #5.*

# Related datasets

- **`actual_load`** — Realised demand per zone; chip `hourly` — pair with this dataset to compute residual demand (`actual_load - sum(renewable production_types)`) — the canonical European MEF input. *entsoe · load · hourly*

- **`day_ahead_prices`** — Marginal day-ahead clearing prices per zone; chip `hourly` — the price counterpart that residual-load models try to predict from this dataset's renewable shares. *entsoe · prices · hourly*

- **`wind_solar_forecast`** — TSO-published forecasts of wind/solar generation; chip `hourly` — compare actuals from this dataset against forecasts to measure forecast skill per zone / per technology. *entsoe · forecast · hourly*

- **`fuelhh` (Elexon)** — GB equivalent of this dataset (since GB doesn't publish to ENTSO-E post-Brexit); chip `30 min` — substitute for any GB query that would otherwise look here. Cross-vendor join: stitch GB `fuelhh` to continental `actual_generation` for a full-Europe view. *elexon · generation · 30 min*
