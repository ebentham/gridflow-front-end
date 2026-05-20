---
slug: carbon_intensity
vendor: neso
vendor_label: National Energy System Operator (NESO)
api_code: intensity
last_verified: 2026-05-08
sources_consulted:
  - quant-vault/30-vendors/neso/datasets/carbon_intensity.md (vault not yet vendored to gridflow-front-end/vault/neso/ — Phase 10 vendoring deferred)
  - gridflow/src/gridflow/schemas/neso.py::CarbonIntensity (line 31, subclass of _TimestampedNesoBase)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::CarbonIntensityTransformer (line 103, registered at L118)
  - gridflow/src/gridflow/connectors/neso/carbon_intensity.py and connectors/neso/endpoints.py (ENDPOINTS["carbon_intensity"] = range route /intensity/{from_dt}/{to_dt})
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs page)
discrepancies_found:
  - source_a: "vault Implementation Delta L111"
    source_a_says: "official docs and config/sources.yaml use {from} and {to}; src/gridflow/connectors/neso/endpoints.py uses {from_dt} and {to_dt} internally before formatting the same path"
    source_b: "gridflow connectors/neso/endpoints.py"
    source_b_says: "Path template uses {from_dt} / {to_dt} placeholders; formats to /intensity/{from}/{to} at request time"
    orchestrator_recommendation: "cosmetic — internal placeholder naming differs from vendor's documented placeholders but the final URL is identical. No fix needed."
  - source_a: "vault Implementation Delta L113 — distinct from intensity_current"
    source_a_says: "carbon_intensity and intensity_current share the same /intensity path in config/sources.yaml but ENDPOINTS distinguishes them: carbon_intensity is /intensity/{from_dt}/{to_dt} (range, max 14 days); intensity_current is /intensity (no-arg, current single record)"
    source_b: "gridflow connectors/neso/endpoints.py::ENDPOINTS"
    source_b_says: "Two separate endpoint entries with the same /intensity prefix; both produce CarbonIntensity silver schema but answer different questions"
    orchestrator_recommendation: "documented design intent — same schema, different query semantics. Surface as caveat so users know to pick the right dataset for their query shape."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB carbon intensity, <span class="italic fg-accent">half-hourly.</span>

**Lede:** The canonical National Grid carbon-intensity series — gCO2 per kWh of GB electricity consumed, published per settlement period as both forecast and post-period actual. The reference dataset for carbon-aware scheduling, MEF (Marginal Emissions Factor) modelling, and "is it a clean hour to charge?" consumer applications across the UK.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity API · /intensity](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.carbon_intensity` |
| API PATH | `/intensity/{from}/{to}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast ahead · actual after each SP |
| VOLUME | 48 / day · ~1.4k / mo |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 14 d | Max range per request |
| 3 | gCO2/kWh | Reporting unit |
| 4 | 7 | Schema columns |

# Sidebar siblings

- intensity_current
- intensity_factors
- intensity_at
- intensity_date
- intensity_fw24h

# Overview

1. <code>carbon_intensity</code> is the **GB grid carbon intensity time-series** — `forecast_gco2_kwh` and `actual_gco2_kwh` per half-hour settlement period, plus a categorical `intensity_index` (`very low` / `low` / `moderate` / `high` / `very high`). It answers "how carbon-heavy is GB electricity right now, and what's predicted next?" — the canonical input for carbon-aware load shifting, MEF (Marginal Emissions Factor) modelling, and emissions-reporting baselines.

2. Gridflow fetches it from <code>api.carbonintensity.org.uk/intensity/{from}/{to}</code> with no authentication (public API; just send `Accept: application/json`). The connector dispatch lives in <code>connectors/neso/carbon_intensity.py</code> with endpoint metadata in <code>connectors/neso/endpoints.py::ENDPOINTS["carbon_intensity"]</code> — a range route with maximum 14-day window per request (`max_days_per_request=14`). The <code>CarbonIntensityTransformer</code> at <code>silver/neso/carbon_intensity.py L103</code> parses the JSON `data[]` array, flattens the nested `intensity.{forecast,actual,index}` object into top-level columns, and writes to the silver parquet partition. Pydantic class <code>CarbonIntensity</code> at <code>schemas/neso.py L31</code> inherits from `_TimestampedNesoBase`. The dataset is part of a NESO carbon-intensity family — see Caveats #02 for distinguishing from `intensity_current`.

3. Cadence is half-hourly. Forecasts are published ahead of the period; estimated actuals are populated shortly after the period closes. Verified against the live API on 2026-05-08; a 30-day range request for 2026-04-08 → 2026-05-07 returned 1,440 rows (no missing periods). The dataset feeds <code>gold_uk_imbalance_context</code> (SQL view at <code>gold/views/uk_imbalance_context.sql</code>) which joins it against Elexon `system_prices` on `timestamp_utc` — the most-load-bearing NESO downstream.

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB carbon intensity · forecast vs actual · last 24h"
- **Subtitle:** "Sparkline · gCO2/kWh · 30 min SP · UTC · 6 May 2026"
- **Seed:** 23
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/neso.py` · `CarbonIntensity` (line 31, subclass of `_TimestampedNesoBase`) and `gridflow/silver/neso/carbon_intensity.py` · `CarbonIntensityTransformer` (line 103). Partitioned by `timestamp_utc` (year + month). Point-in-time field: `timestamp_utc` (no separate revision timestamp — actuals are post-period estimates, not revised once published).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period START. Period END is `period_end_utc`. UTC always (vendor sends `Z` suffix). | `schemas/neso.py L31`, inherits `_TimestampedNesoBase` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end (`timestamp_utc + 30 min`). | `schemas/neso.py L31+` |
| `forecast_gco2_kwh` | `float` | Yes | `intensity.forecast` | Forecast carbon intensity in gCO2/kWh. Populated ahead of the period. | `schemas/neso.py L34` |
| `actual_gco2_kwh` | `float` | Yes | `intensity.actual` | Post-period estimated actual; **often null before actuals publish**. Treat null as "actual not yet available" not "zero carbon". | `schemas/neso.py L35` |
| `intensity_index` | `str` | No | `intensity.index` | Categorical: `very low` / `low` / `moderate` / `high` / `very high`. Vendor-managed value list; no regex constraint. | `schemas/neso.py L36` |
| `data_provider` | `str` | No | _derived_ | Always `"neso"`. | `schemas/neso.py` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `schemas/neso.py` |

**PARQUET PATH:** `data/silver/neso/carbon_intensity/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc)` — keep last (forecast → actual replaces forecast row in place once available)

# Sample data

| timestamp_utc | period_end_utc | forecast_gco2_kwh | actual_gco2_kwh | intensity_index |
|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | 2026-05-06T00:30:00+00:00 | 245.0 | 239.0 | moderate |
| 2026-05-06T00:30:00+00:00 | 2026-05-06T01:00:00+00:00 | 250.0 | 248.0 | moderate |
| 2026-05-06T11:00:00+00:00 | 2026-05-06T11:30:00+00:00 | 92.0 | 88.0 | low |
| _ROW HIGHLIGHTED_ 2026-05-06T12:00:00+00:00 | 2026-05-06T12:30:00+00:00 | 68.0 | 64.0 | very low |
| 2026-05-06T13:00:00+00:00 | 2026-05-06T13:30:00+00:00 | 71.0 | 70.0 | very low |
| 2026-05-06T18:00:00+00:00 | 2026-05-06T18:30:00+00:00 | 218.0 | 224.0 | moderate |
| 2026-05-06T19:00:00+00:00 | 2026-05-06T19:30:00+00:00 | 285.0 | 293.0 | high |
| 2026-05-06T23:30:00+00:00 | 2026-05-07T00:00:00+00:00 | 198.0 | _null_ | moderate |

[1] First two rows from vault Silver sample (live 2026-05-08); subsequent rows synthesised respecting the published 24-hour arc on a sunny May day — solar peak at midday drives intensity into "very low" (highlighted row at 12:00, 64 gCO2/kWh — the lowest-emissions hour of the day, dominated by solar + wind), then ramps up through evening peak (19:00, 285 forecast / 293 actual, "high"), with overnight settling around moderate. The final row (23:30) shows the publication lag pattern: forecast is present but actual is null because the post-period estimate hasn't been published yet at the moment of query.

# Intensity index (categorical codelist)

The `intensity_index` column is NESO's qualitative carbon-intensity bucket. Bucket boundaries shift over time as the GB grid decarbonises (the 2024 "moderate" threshold is lower than 2018's); the categorical is more stable than the gCO2/kWh value for user-facing displays.

| Value | Typical 2026 range (gCO2/kWh) | UX framing |
|---|---|---|
| `very low` | < 90 | Optimal for delayed loads (EV charging, water heaters) |
| `low` | 90–130 | Good window |
| `moderate` | 130–230 | Default state |
| `high` | 230–330 | Defer flexible loads if possible |
| `very high` | > 330 | Peak fossil dispatch (oil / OCGT) |

# API & ingestion

**Endpoint card:**
- **ENDPOINT**: `api.carbonintensity.org.uk/intensity/{from}/{to}` (path segments, NOT query params; max 14-day range)
- **AUTH**: None (public). Send `Accept: application/json`. Rate limit not vendor-documented; gridflow throttles to 10 req/s.

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/neso/carbon_intensity/<year>/<month>/<day>/raw_<timestamp>_<hash>.json` (with `.meta.json` provenance sidecar)
- **TRANSFORMER**: `gridflow.silver.neso.carbon_intensity.CarbonIntensityTransformer` (registered at `silver/neso/carbon_intensity.py L118`)

**Tab 1 — Example URL:**
```
https://api.carbonintensity.org.uk/intensity/2026-05-06T00:00Z/2026-05-07T00:00Z
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL:**
```sql
-- Cleanest hours per day (lowest actual carbon intensity) last 30 days
SELECT date_trunc('day', timestamp_utc) AS day,
       min(actual_gco2_kwh) AS min_actual,
       arg_min(timestamp_utc, actual_gco2_kwh) AS cleanest_sp
FROM read_parquet('data/silver/neso/carbon_intensity/**/*.parquet')
WHERE actual_gco2_kwh IS NOT NULL
  AND timestamp_utc >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1 DESC;
```

**Tab 3 — Python · parquet:**
```python
import polars as pl

df = pl.read_parquet(
    "data/silver/neso/carbon_intensity/**/*.parquet",
)
# Forecast skill: mean absolute error between forecast and actual
skill = (
    df.filter(pl.col("actual_gco2_kwh").is_not_null())
      .with_columns(
          (pl.col("forecast_gco2_kwh") - pl.col("actual_gco2_kwh")).abs().alias("abs_err")
      )
      .group_by(pl.col("timestamp_utc").dt.date().alias("day"))
      .agg(pl.col("abs_err").mean().alias("mae_gco2_kwh"))
      .sort("day")
)
print(skill.tail(7))
```

# Caveats

## 01 Actuals lag — null is "not yet published"

`actual_gco2_kwh` is null for periods whose post-period estimate hasn't been computed yet (typically the most recent 1–2 hours, plus any backfill gaps). Filter `actual_gco2_kwh IS NOT NULL` for any back-fitted modelling; use `forecast_gco2_kwh` as the ex-ante feature when actuals aren't yet available. Do NOT treat null actual as "zero carbon". *Source: vault Known Issues #3.*

## 02 Distinct from `intensity_current` despite same `/intensity` path prefix

`carbon_intensity` (this dataset) is a **range** query — `/intensity/{from}/{to}` with `max_days_per_request=14` — and produces a multi-row time series. `intensity_current` (separate dataset, same vendor) is a no-arg query against `/intensity` and returns the single current half-hour record. Both produce the same `CarbonIntensity` silver schema, but they are NOT aliases. Pick `carbon_intensity` for historical / back-fill / range queries; pick `intensity_current` for live "what is it right now" displays. *Source: vault Implementation Delta L113.*

## 03 14-day max window per request

Single requests cannot span more than 14 days. The connector auto-chunks longer windows into 14-day sub-requests with rate-limited iteration. Custom callers issuing raw HTTP must respect this — exceeding the window returns a vendor error rather than truncating silently. *Source: vault API endpoint table + connector dispatch logic.*

## 04 GB clock-change days = 46 or 50 settlement periods (sometimes)

Despite official docs describing periods 1-48 per day, GB clock-change days (DST transitions) carry 46 (spring forward) or 50 (autumn back) settlement periods. The connector handles this via `timestamp_utc` directly (no period-number arithmetic), but custom callers using `intensity_period` for slot accounting must account for the 46/50 cases. *Source: vault Known Issues #4.*

## 05 Path placeholders use `{from_dt}` / `{to_dt}` internally

Official docs and `config/sources.yaml` describe the path as `/intensity/{from}/{to}`. The gridflow connector internally templates as `/intensity/{from_dt}/{to_dt}` to disambiguate from the Python `from` keyword in connector code. The final URL is identical to the documented form. Cosmetic divergence in source-reading; no behavior difference. *Source: vault Implementation Delta L111.*

# Related datasets

- **`intensity_current`** (NESO) — Single-record current carbon intensity; chip `current` — companion to this dataset for live displays. Same schema (`CarbonIntensity`), different query semantics (no-arg vs range). *neso · carbon · current*

- **`intensity_factors`** (NESO) — Per-fuel emissions factors used to compute the intensity; chip `static` — the underlying gCO2/kWh per fuel type that, when weighted by fuelhh-style fuel mix, produces this dataset's value. Use for MEF (Marginal Emissions Factor) attribution. *neso · carbon · static*

- **`fuelhh`** (Elexon) — GB generation by fuel type at 30-min resolution; chip `30 min` — pair with this dataset to attribute carbon intensity to individual fuel categories. Standard MEF derivation: `sum(generation_mw[fuel] × intensity_factor[fuel]) / sum(generation_mw)`. *elexon · generation · 30 min*

- **`system_prices`** (Elexon) — GB cash-out prices per settlement period; chip `30 min` — the most-load-bearing downstream join (gold view `uk_imbalance_context` joins these two datasets on `timestamp_utc` for carbon-aware price analysis). *elexon · prices · 30 min*
