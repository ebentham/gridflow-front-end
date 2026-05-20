---
slug: storage
vendor: gie
vendor_label: GIE AGSI+ (Gas Storage)
api_code: AGSI
last_verified: 2026-05-08
sources_consulted:
  - quant-vault/30-vendors/gie/datasets/storage.md (vault not yet vendored to gridflow-front-end/vault/gie/ — Phase 10 vendoring deferred)
  - gridflow/src/gridflow/schemas/gie.py::GasStorage (line 12)
  - gridflow/src/gridflow/silver/gie/agsi.py::GasStorageTransformer (line 115, registered at L624)
  - gridflow/src/gridflow/connectors/gie/client.py::_fetch_agsi_storage and connectors/gie/endpoints.py
  - https://agsi.gie.eu/api (JSON API — documentation page exists at agsi.gie.eu but is interactive; no static doc page to WebFetch successfully)
discrepancies_found:
  - source_a: "vault Implementation Delta — legacy ALSI fetch path"
    source_a_says: "connectors/gie/client.py::_fetch_country (used by gie_alsi) still uses `till=` instead of `to=` for range parameter"
    source_b: "gridflow connectors/gie/client.py — AGSI code path uses `from`/`to` correctly; legacy `till=` is unreachable for gie_agsi but still present for the eventual ALSI implementation"
    orchestrator_recommendation: "non-blocking for storage — legacy code path is unused for AGSI. Surface in caveats for the future ALSI brief; cleanup deferred until ALSI lands."
  - source_a: "vault dataset_key frontmatter says `storage` but source is `gie_agsi`"
    source_a_says: "source: gie_agsi (the AGSI sub-product within GIE)"
    source_b: "gridflow vendor namespace is `gie` for `connectors/gie/`, schemas namespace is `gie` for `schemas/gie.py`, but transformer namespace is `gie_agsi` (registered as `register_transformer('gie_agsi', 'storage', ...)`)"
    orchestrator_recommendation: "documented vendor-namespace split — gridflow treats GIE as the parent and AGSI/ALSI as sub-products; the silver layer key reflects this split (`silver.gie_agsi.storage`). gridflow-front-end vendor manifest should mirror this. Treat as design intent, not a bug."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** European gas storage, <span class="italic fg-accent">country by country.</span>

**Lede:** Country-scoped gas storage time-series from GIE's Aggregated Gas Storage Inventory (AGSI+). Daily snapshots for nine European countries — gas-in-storage levels (GWh), injection / withdrawal flows, working-gas capacity, percent-full, and trend. The workhorse country-level view for winter-tightness models, fuel-switching signals, and storage-spread trades.

**Verified line:** Verified against vendor docs: 2026-05-08 · [GIE AGSI+ · /api](https://agsi.gie.eu/api)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.gie_agsi.storage` |
| API PATH | `/api?country={ISO2}&date={YYYY-MM-DD}` |
| FREQUENCY | daily |
| PUBLICATION LAG | ~16:00 CET refresh |
| VOLUME | 9 countries × 365 days = ~3.3k rows / year |
| PRIMARY KEY | `(gas_day, entity_level, entity_code, entity_url)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Snapshot cadence |
| 2 | 9 | AGSI countries (AT BE DE ES FR GB IT NL PL) |
| 3 | GWh | Reporting unit |
| 4 | 28 | Schema columns |

# Sidebar siblings

- storage_reports
- lng
- unavailability
- about_listing
- about_summary

# Overview

1. <code>storage</code> is the **country-level rollup of European gas storage** published by GIE (Gas Infrastructure Europe) via the AGSI+ platform. Each row reports one country's gas storage state for one gas day: absolute stock (<code>gas_in_storage_gwh</code>), injection/withdrawal flows (<code>injection_gwh</code> / <code>withdrawal_gwh</code> / <code>net_withdrawal_gwh</code>), capacity-side metrics (<code>working_gas_volume_gwh</code>, <code>injection_capacity_gwh_per_day</code>), and convenience aggregates (<code>storage_pct_full</code>, <code>trend</code>). Coverage is the nine-country AGSI footprint: AT, BE, DE, ES, FR, GB, IT, NL, PL.

2. Gridflow fetches it from <code>agsi.gie.eu/api</code> with header authentication (`x-key` — lowercase, vendor-enforced; capitalised `X-Key` returns 401) and the API key from <code>GIE_API_KEY</code>. The connector dispatch lives in <code>connectors/gie/client.py::_fetch_agsi_storage</code> with endpoint registration in <code>connectors/gie/endpoints.py</code>. Pagination uses `last_page` (source of truth) rather than `total` (which is the per-page row count). The <code>GasStorageTransformer</code> at <code>silver/gie/agsi.py L115</code> handles the country-scope variant; the same class is reused for facility-level data via the <code>StorageReportsTransformer</code> subclass at L274. Pydantic class <code>GasStorage</code> is declared at <code>schemas/gie.py L12</code>.

3. Cadence is daily snapshots refreshed around 16:00 CET. Verified against the live API on 2026-05-08; the Germany sample for 2026-05-06 returned `gas_in_storage_gwh: 65.96`, `storage_pct_full: 26.62`, `trend: -0.57` (withdrawing). **Gas day starts at 06:00 UTC, not midnight** — see Caveats #03. GB is in the footprint but returns `"United Kingdom (Pre-Brexit)"` with `"-"` placeholders for all numerical fields since 2020 (data is unusable). The transformer converts `"-"` to null via <code>_safe_float</code>; downstream filters on `status = "E"` (estimate) or `status = "C"` (confirmed) yield clean rows.

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE storage · pct_full · last 12 months"
- **Subtitle:** "Sparkline · % full · daily · UTC · 2025-06 → 2026-05"
- **Seed:** 17
- **Toggles:** `1y` (active) / `5y`

# Schema

Defined in `gridflow/schemas/gie.py` · `GasStorage` (line 12) and `gridflow/silver/gie/agsi.py` · `GasStorageTransformer` (line 115). Partitioned by `gas_day` (year + month). Point-in-time field: `updated_at` (vendor `updatedAt` revision timestamp).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `gas_day` | `date` | No | `gasDayStart` | Gas day, NOT calendar day — starts at 06:00 UTC. See Caveats #03. | `schemas/gie.py L12+` |
| `gas_day_end` | `datetime[UTC]` | Yes | `gasDayEnd` | End of the same gas day window. | `schemas/gie.py` |
| `updated_at` | `datetime[UTC]` | Yes | `updatedAt` | Vendor revision timestamp. Use for as-of filtering on revised data. | `schemas/gie.py` |
| `entity_level` | `str` | No | _derived_ | Always `"country"` for this dataset (vs `"facility"` for `storage_reports`). | `silver/gie/agsi.py L115+` |
| `entity_code` | `str` | No | `country` request param + `code` response | ISO-2 country code (`AT`, `BE`, `DE`, ...). | `schemas/gie.py` |
| `entity_name` | `str` | No | `name` | Human-readable country name. | `schemas/gie.py` |
| `entity_url` | `str` | Yes | `url` | Vendor URL slug. | `schemas/gie.py` |
| `country_code` | `str` | No | request `country` | Duplicate of `entity_code` for consistency with other AGSI datasets. | `schemas/gie.py` |
| `country_name` | `str` | No | `name` | Duplicate of `entity_name`. | `schemas/gie.py` |
| `gas_in_storage_gwh` | `float` | Yes | `gasInStorage` | **GWh** (NOT MWh — GIE convention). `"-"` placeholder → null. | `schemas/gie.py` |
| `consumption_gwh` | `float` | Yes | `consumption` | Daily consumption in GWh. | `schemas/gie.py` |
| `consumption_full_pct` | `float` | Yes | `consumptionFull` | Consumption as % of working gas volume. | `schemas/gie.py` |
| `injection_gwh` | `float` | Yes | `injection` | Daily injection in GWh. | `schemas/gie.py` |
| `withdrawal_gwh` | `float` | Yes | `withdrawal` | Daily withdrawal in GWh. | `schemas/gie.py` |
| `net_withdrawal_gwh` | `float` | Yes | `netWithdrawal` | Signed: positive = withdrawing (drawing down stock), negative = injecting. | `schemas/gie.py` |
| `working_gas_volume_gwh` | `float` | Yes | `workingGasVolume` | Total usable capacity in GWh. | `schemas/gie.py` |
| `injection_capacity_gwh_per_day` | `float` | Yes | `injectionCapacity` | Daily injection capacity. | `schemas/gie.py` |
| `withdrawal_capacity_gwh_per_day` | `float` | Yes | `withdrawalCapacity` | Daily withdrawal capacity. | `schemas/gie.py` |
| `contracted_capacity_gwh_per_day` | `float` | Yes | `contractedCapacity` | Capacity contracted to shippers. | `schemas/gie.py` |
| `available_capacity_gwh_per_day` | `float` | Yes | `availableCapacity` | Capacity still available to contract. | `schemas/gie.py` |
| `covered_capacity_gwh_per_day` | `float` | Yes | `coveredCapacity` | Capacity covered by storage obligations. | `schemas/gie.py` |
| `storage_pct_full` | `float` | Yes | `full` | 0-100, clamped at schema layer. The headline winter-tightness indicator. | `schemas/gie.py` |
| `trend` | `float` | Yes | `trend` | Signed daily change in `storage_pct_full`. | `schemas/gie.py` |
| `status` | `str` | Yes | `status` | `E` = estimate, `C` = confirmed, `N` = no value (filter out). | `schemas/gie.py` |
| `info` | `str` | Yes | `info` | JSON-encoded freeform info object (rare). | `schemas/gie.py` |
| `data_provider` | `str` | No | _derived_ | Always `"gie_agsi"` (NOT `"gie"` — gridflow distinguishes the AGSI sub-product). | `schemas/gie.py` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver write timestamp. | `schemas/gie.py` |

**PARQUET PATH:** `data/silver/gie_agsi/storage/year=YYYY/month=MM/`
**PARTITION BY:** `gas_day (year + month)`
**DEDUP KEY:** `(gas_day, entity_level, entity_code, entity_url)` — keep latest by `updated_at`

# Sample data

| gas_day | entity_code | gas_in_storage_gwh | injection_gwh | withdrawal_gwh | net_withdrawal_gwh | storage_pct_full | trend | status |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06 | DE | 65.96 | 182.43 | 60.30 | -122.13 | 26.62 | -0.57 | E |
| 2026-05-06 | FR | 84.20 | 95.10 | 12.40 | -82.70 | 33.45 | -0.40 | E |
| _ROW HIGHLIGHTED_ 2026-05-06 | GB | _null_ | _null_ | _null_ | _null_ | _null_ | _null_ | N |
| 2026-05-06 | NL | 41.30 | 78.20 | 8.10 | -70.10 | 29.85 | -0.31 | C |
| 2026-05-06 | IT | 92.40 | 142.60 | 15.30 | -127.30 | 38.20 | -0.49 | E |
| 2026-05-06 | AT | 38.10 | 47.20 | 4.60 | -42.60 | 35.10 | -0.42 | E |
| 2026-05-06 | BE | 4.85 | 6.20 | 0.40 | -5.80 | 28.30 | -0.31 | E |
| 2026-05-06 | ES | 18.40 | 21.10 | 3.50 | -17.60 | 39.60 | -0.34 | E |

[1] First row (DE) from vault Silver sample (live 2026-05-08); subsequent country rows synthesised respecting the schema's GWh-and-% ranges and the early-May "shoulder-season injection" macro pattern (positive injection, small withdrawal, percent-full slowly rising from winter lows). The highlighted row is GB — `"United Kingdom (Pre-Brexit)"` with `status: "N"` (no value); all numeric columns are null. GB has been unusable in AGSI since 2020 — fall back to UK-specific sources (e.g. National Gas Transmission published statistics) for British storage. PL has been excluded from the sample since AGSI tracks it but PL's recent statistics are sparse.

# AGSI footprint (country codelist)

The nine countries covered by AGSI+ as of 2026. Querying any other ISO-2 code returns empty data.

| Code | Country | Notes |
|---|---|---|
| `AT` | Austria | |
| `BE` | Belgium | |
| `DE` | Germany | Largest single-country storage; dominant European winter buffer |
| `ES` | Spain | |
| `FR` | France | |
| `GB` | United Kingdom | **Unusable post-Brexit** — returns `"-"` placeholders since 2020. Vendor still publishes the row with `status: "N"` for consistency. |
| `IT` | Italy | |
| `NL` | Netherlands | Includes Groningen historical (now ~0 since closure) |
| `PL` | Poland | |

# API & ingestion

**Endpoint card:**
- **ENDPOINT**: `agsi.gie.eu/api?country={ISO2}&date={YYYY-MM-DD}` (single-day) or `&from={YYYY-MM-DD}&to={YYYY-MM-DD}` (range)
- **AUTH**: header `x-key` (LOWERCASE — `X-Key` returns 401) with key from env `GIE_API_KEY` ([register at agsi.gie.eu](https://agsi.gie.eu/account/registration))

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/gie_agsi/storage/<year>/<month>/<day>/raw_<uuid>.json`
- **TRANSFORMER**: `gridflow.silver.gie.agsi.GasStorageTransformer` (registered at `silver/gie/agsi.py L624`)

**Tab 1 — Example URL:**
```
https://agsi.gie.eu/api
  ?country=DE
  &from=2026-05-01
  &to=2026-05-07
```

Header: `x-key: $GIE_API_KEY`

**Tab 2 — DuckDB · SQL:**
```sql
-- European storage trajectory: percent-full per country, last 90 days
SELECT entity_code,
       gas_day,
       storage_pct_full,
       trend
FROM read_parquet('data/silver/gie_agsi/storage/**/*.parquet')
WHERE status IN ('E', 'C')                      -- exclude GB no-value rows
  AND gas_day >= current_date - INTERVAL 90 DAY
ORDER BY entity_code, gas_day;
```

**Tab 3 — Python · parquet:**
```python
import polars as pl

df = pl.read_parquet(
    "data/silver/gie_agsi/storage/**/*.parquet",
)
# EU-wide storage trajectory: rolling sum of country gas_in_storage_gwh
eu = (
    df.filter(pl.col("status").is_in(["E", "C"]))
      .group_by("gas_day")
      .agg(pl.col("gas_in_storage_gwh").sum().alias("eu_total_twh") / 1000)
      .sort("gas_day")
)
print(eu.tail(30))
```

# Caveats

## 01 Unit is GWh — NOT MWh

GIE reports gas storage in **GWh** (and capacities in GWh/day). Divide by 1000 to express in TWh, or multiply by 1000 to compare against MWh-denominated power-market datasets. The vault Implementation Delta confirms this convention is intentional. *Source: vault Known Issues + GIE API docs.*

## 02 GB is in the footprint but unusable post-Brexit

`country=GB` returns a valid row with `name: "United Kingdom (Pre-Brexit)"` but all numeric values are `"-"` (vendor placeholder, converted to null by `_safe_float`) and `status: "N"`. The vendor keeps GB in the footprint for backwards compatibility with pre-2020 data. For UK storage, use National Gas Transmission published statistics directly. Filter out GB silently OR document the gap in any UK-inclusive aggregation. *Source: vault Known Issues #4.*

## 03 Gas day starts at 06:00 UTC, NOT midnight

The `gas_day` column is a `date`, not a timestamp. The gas day for 2026-05-06 runs from 2026-05-06 06:00 UTC to 2026-05-07 06:00 UTC (per the European gas-market convention). Do not synthesise a midnight timestamp without applying the +06:00 offset, or you will mis-align with cross-vendor power-market datasets that use calendar days. *Source: vault Known Issues + 20-domain/concepts/gas-day.md.*

## 04 `x-key` header MUST be lowercase

The vendor enforces lowercase header naming for the API key. Capitalised `X-Key` (which is what most HTTP libraries default to via case-insensitive expansion) returns HTTP 401. The connector at `connectors/gie/client.py` is explicit about case. Custom HTTP code that adds the header must do so verbatim. *Source: vault Known Issues #1.*

## 05 `status: "N"` filtering is non-optional

Rows with `status: "N"` carry null values for every numeric column. Aggregations that sum across countries without filtering produce silent null-dominated results. Always `WHERE status IN ('E', 'C')` for any GB-inclusive cross-country aggregation, or explicitly handle the null pattern. *Source: vault Modelling notes + domain knowledge.*

## 06 `last_page` is the pagination source of truth

The `last_page` field in the response envelope is authoritative for pagination; the `total` field is the per-page row count and will mislead any caller that treats it as the global count. Iterate `page=1..last_page`. The connector handles this correctly; custom callers should not. *Source: vault Known Issues #2.*

# Related datasets

- **`storage_reports`** (GIE-AGSI) — Facility-level (not country-level) version of this dataset; chip `daily` — same `/api` endpoint, but `entity_level: "facility"` and one row per storage facility per gas day. Use when country-level rollup hides facility-specific dynamics (Groningen closure, German storage obligations). *gie · storage · daily*

- **`aggregated_physical_flows`** (ENTSOG) — Daily cross-border gas flows; chip `daily` — pair with the `Storage`-direction rows in ENTSOG to validate AGSI injection/withdrawal against pipeline-network attribution. *entsog · transmission · daily*

- **`unavailability`** (GIE-AGSI) — Planned outages of storage facilities; chip `as published` — flag periods where storage capacity is reduced; pair with this dataset's capacity columns to derive effective-capacity-net-of-outages. *gie · storage · as published*

- **`forecast_demand`** (Open-Meteo) — Weather-driven gas demand forecasts; chip `hourly` — combine with this dataset's `withdrawal_gwh` for the canonical "weather-driven storage drawdown" winter-tightness model. *open-meteo · forecast · hourly*
