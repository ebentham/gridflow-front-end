---
slug: windfor
vendor: elexon
vendor_label: Elexon BMRS
api_code: WINDFOR
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/windfor.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonWindForecast (lines 206-223)
  - gridflow/src/gridflow/silver/elexon/wind_forecast.py::WindForecastTransformer (lines 19-140)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 156-160, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vault Silver Sample uses `issue_time` field"
    source_a_says: "Silver row includes `issue_time` placeholder"
    source_b: "gridflow silver/elexon/wind_forecast.py L110-115"
    source_b_says: "Transformer derives `issue_time` from `published_at` (renamed from publishTime) — UTC-cast — and includes it in output_cols L134"
    orchestrator_recommendation: "trust gridflow — issue_time is the UTC-cast version of publishTime used as bitemporal dedup tiebreaker"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB wind forecast, <span class="italic fg-accent">per period.</span>

**Lede:** WINDFOR is the GB wind generation forecast — published per settlement period with `initial_forecast_mw` (first issue) and `latest_forecast_mw` (most recent revision). Used as the wind-output forecast benchmark for forecast-error analysis (against `fuelhh` WIND or `agws` Wind Onshore/Offshore actuals) and as a regressor for short-term load-net-wind models.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · WINDFOR](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.windfor` |
| API PATH | `/datasets/WINDFOR` |
| FREQUENCY | hourly |
| PUBLICATION LAG | 0 (forward-looking) |
| VOLUME | 0.5M / mo |
| PRIMARY KEY | `(settlement_date, settlement_period, issue_time)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | hourly | Publication frequency |
| 2 | 0 | Lag (forward-looking) |
| 3 | initial + latest | Forecast revisions per period |
| 4 | 8 | Schema columns |

# Sidebar siblings

- fuelhh
- agws
- agpt
- fou2t14d
- uou2t14d

# Overview

1. <code>windfor</code> is **Wind Generation Forecast** — Elexon's published GB-total wind output forecast per settlement period. Each row may carry `initial_forecast_mw` (the first issued forecast for that period) and `latest_forecast_mw` (the most recent revision). On the live API, only `generation` (mapped to `latest_forecast_mw`) is consistently populated; `initialForecast` appears in some payload variants.

2. Gridflow fetches it from <code>/datasets/WINDFOR</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern (connector entry at <code>connectors/elexon/endpoints.py L156-160</code>). The <code>WindForecastTransformer</code> renames camelCase to snake_case, derives `timestamp_utc` from settlement-period pair preferentially (or from `startTime` if periods absent), parses `publishTime` → `issue_time`, and dedups on `(settlement_date, settlement_period, issue_time)` so revisions coexist. Pydantic schema <code>ElexonWindForecast</code> is declared with `settlement_date` and `settlement_period` both nullable.

3. Cadence is multiple publishes per day with zero lag. Verified against the live API on 2026-05-08; the sample returned hourly-cadence `generation` values (2983 MW, 3046 MW) from a publishTime of 2026-05-05T23:30:00Z without `settlementDate`/`settlementPeriod` fields — the transformer falls back to `startTime` parsing for `timestamp_utc`. Pair with `fuelhh` (WIND) or `agws` (Wind Onshore + Offshore actuals) for forecast-error analysis.

# Sample chart

- **Type:** `sparkline`
- **Title:** "GB wind forecast vs actual · 24-hour overlay"
- **Subtitle:** "Sparkline · MW · UTC · forecast for 6 May 2026"
- **Seed:** 24
- **Toggles:** `latest` (active) / `initial`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonWindForecast` (lines 206-223) and `gridflow/silver/elexon/wind_forecast.py` · `WindForecastTransformer.output_cols`. Partitioned by `settlement_date` (year + month, derived from `timestamp_utc`). Point-in-time field: `issue_time` (derived from `publishTime`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `Optional[date]` | Yes | `settlementDate` | Settlement date (BST/GMT calendar). Nullable in `ElexonWindForecast` (`schemas/elexon.py L209`) because some payload variants omit it; transformer falls back to `start_time` for `timestamp_utc`. | `schemas/elexon.py L209` |
| `settlement_period` | `Optional[int]` | Yes | `settlementPeriod` | 1..50 when present. Validator `ge=1, le=50`. Often absent — see caveat 02. | `schemas/elexon.py L210` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Period-derived if both date+period present, else from `startTime` parse. | `silver/elexon/wind_forecast.py L82-104` |
| `initial_forecast_mw` | `Optional[float]` | Yes | `initialForecast` | MW. First-issue forecast for the period; not always populated. | `schemas/elexon.py L212`; `silver/elexon/wind_forecast.py L59` |
| `latest_forecast_mw` | `Optional[float]` | Yes | `latestForecast` / `generation` | MW. Most-recent forecast. Live API returns this as `generation`. | `schemas/elexon.py L213`; `silver/elexon/wind_forecast.py L60-61` |
| `issue_time` | `Optional[datetime[UTC]]` | Yes | `publishTime` (renamed `published_at`) | Publication time. Bitemporal dedup tiebreaker. | `silver/elexon/wind_forecast.py L110-115` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `schemas/elexon.py L215` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `schemas/elexon.py L216` |

**PARQUET PATH:** `data/silver/elexon/windfor/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)` — derived from `timestamp_utc` when settlement_date is null
**DEDUP KEY:** `(settlement_date, settlement_period, issue_time)` when periods present, else `(timestamp_utc, issue_time)` (`silver/elexon/wind_forecast.py L118-123`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | initial_forecast_mw | latest_forecast_mw | issue_time | data_provider | ingested_at |
|---|---|---|---|---|---|---|---|
| _null_ | _null_ | 2026-05-04T20:00:00+00:00 | _null_ | 2983.0 | 2026-05-05T23:30:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| _null_ | _null_ | 2026-05-04T21:00:00+00:00 | _null_ | 3046.0 | 2026-05-05T23:30:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | 9180.0 | 9220.0 | 2026-05-06T02:30:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | 6520.0 | 6420.0 | 2026-05-06T02:30:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **24** | **2026-05-06T11:30:00+00:00** | **5180.0** | **5340.0** | **2026-05-06T02:30:00+00:00** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | 5810.0 | 5910.0 | 2026-05-06T02:30:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 7220.0 | 7180.0 | 2026-05-06T02:30:00+00:00 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 8410.0 | 8520.0 | 2026-05-06T02:30:00+00:00 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (`generation=2983`) and 2 (`generation=3046`) verbatim from the vault Bronze Sample (vault/elexon/windfor.md, live 2026-05-08; both lack `settlementDate`/`settlementPeriod` so timestamp_utc is derived from `startTime`). Remaining rows synthesised — respect schema constraints (Optional float MW, optional period) and represent typical GB wind forecast with both initial and latest values populated. The highlighted **SP24 (initial 5180, latest 5340)** row is the interesting case: midday revision UP — the kind of intra-day correction wind-forecast updates make, exactly what the issue_time bitemporal column exists to track.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: WINDFOR is a single forecast time series with no enumerable taxonomy. The initial-vs-latest distinction is in schema rows; the wind onshore/offshore split is provided by agws, not windfor.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/windfor/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.wind_forecast.WindForecastTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR?publishDateTimeFrom=2026-05-05T00:00Z&publishDateTimeTo=2026-05-06T00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Latest-issue wind forecast vs FUELHH WIND actual (forecast error per period)
WITH latest AS (
  SELECT settlement_date, settlement_period, latest_forecast_mw,
         ROW_NUMBER() OVER (
           PARTITION BY settlement_date, settlement_period
           ORDER BY issue_time DESC
         ) AS rn
  FROM read_parquet('data/silver/elexon/windfor/**/*.parquet')
  WHERE settlement_date IS NOT NULL
), actual AS (
  SELECT settlement_date, settlement_period, generation_mw AS wind_mw
  FROM read_parquet('data/silver/elexon/fuelhh/**/*.parquet')
  WHERE fuel_type = 'WIND'
)
SELECT l.settlement_date, l.settlement_period,
       l.latest_forecast_mw, a.wind_mw,
       (l.latest_forecast_mw - a.wind_mw) AS error_mw
FROM latest l JOIN actual a USING (settlement_date, settlement_period)
WHERE l.rn = 1
  AND l.settlement_date >= current_date - INTERVAL 7 DAY
ORDER BY l.settlement_date, l.settlement_period;
```

**Tab 3 — Python · polars**
```python
import polars as pl

wf = pl.read_parquet("data/silver/elexon/windfor/**/*.parquet")
# Forecast revision delta — how much does each publish change vs the prior?
revisions = (
    wf.filter(pl.col("settlement_date").is_not_null())
      .sort(["settlement_date", "settlement_period", "issue_time"])
      .with_columns(
          pl.col("latest_forecast_mw").diff().over(["settlement_date", "settlement_period"])
            .alias("revision_delta_mw")
      )
      .filter(pl.col("revision_delta_mw").is_not_null())
)
print(revisions.tail(20))
```

# Caveats

## 01 Settlement date/period are nullable in the schema

`ElexonWindForecast.settlement_date` and `settlement_period` are `Optional` (`schemas/elexon.py L209-210`) because some payload variants omit them. The transformer falls back to `start_time` for `timestamp_utc` when missing (`silver/elexon/wind_forecast.py L97-104`). Filter `WHERE settlement_date IS NOT NULL` when joining to per-period datasets. *(Source: vault Implementation Delta; `schemas/elexon.py L209-210`.)*

## 02 Sparse cadence — empty within 3-hour windows

Despite the `hourly` frequency tag, WINDFOR's actual publication pattern is irregular — multiple publishes per day but not strictly hourly. Use 1-day query windows minimum for backfills. *(Source: vault Implementation Delta — "Sparse publication cadence — empty within 3-hour windows; required at-least-1-day window in V1 validation".)*

## 03 `latest_forecast_mw` vs `initial_forecast_mw`

`latest_forecast_mw` is the most-recent revision; `initial_forecast_mw` is the first published value. Live API on 2026-05-08 returned only `generation` (which maps to `latest_forecast_mw`); `initialForecast` payload appears in older bronze. For pure "what the operator most recently thinks" analytics use `latest_forecast_mw`; for forecast-stability metrics compare initial vs latest. *(Source: vault Known Issues; `silver/elexon/wind_forecast.py L59-61`.)*

## 04 No onshore/offshore split — use `agws`

WINDFOR is a single GB total. For the onshore/offshore split, use `agws` (Wind Onshore vs Wind Offshore PSR types). Wind forecast models that need technology splits should join WINDFOR (total) with `agws` ratios to reconstruct. *(Source: domain knowledge — Elexon's GB wind forecasting only emits aggregate; ENTSO-E B-series provides the split.)*

## 05 Forecast revisions preserved via `issue_time`

The dedup key includes `issue_time`, so multiple revisions of the same period coexist. The latest-revision-per-period SQL pattern is the canonical "what's the operator's current view" query; older revisions are retained for forecast-stability analytics. *(Source: `silver/elexon/wind_forecast.py L118-123`.)*

# Related datasets

- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. Outturn `fuel_type='WIND'` is the canonical realised wind series — pair with WINDFOR for forecast-error per period. `elexon · generation · 30 min`
- **agws** — Wind & solar actual generation. `30 min`. Provides onshore/offshore split that WINDFOR collapses into a single total — combine for technology-aware forecast-error analysis. `elexon · generation · 30 min`
- **agpt** — Aggregated generation per PSR type. `30 min`. Broader PSR-level outturn; includes Wind Onshore + Wind Offshore among others. `elexon · generation · 30 min`
- **fou2t14d** — 2-14 day generation availability by fuel. `daily`. Medium-horizon wind availability declaration; WINDFOR is intra-day, FOU2T14D extends days ahead. `elexon · demand & forecasts · daily`
