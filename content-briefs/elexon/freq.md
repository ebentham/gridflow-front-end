---
slug: freq
vendor: elexon
vendor_label: Elexon BMRS
api_code: FREQ
last_verified: 2026-05-09
sources_consulted:
  - vault/elexon/freq.md
  - gridflow/src/gridflow/schemas/elexon.py::ElexonFrequency (lines 169-182)
  - gridflow/src/gridflow/silver/elexon/freq.py::FreqTransformer (lines 18-91)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 107-114, PUBLISH_DATETIME style with measurementDateTimeFrom/To override)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FREQ (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "vault Implementation Delta + Changelog"
    source_a_says: "V2-FIX-01 (2026-05-09) corrected the connector to send measurementDateTimeFrom/To instead of publishDateTimeFrom/To. Historical bronze captured pre-fix holds 'latest 5761 samples' rather than the requested window."
    source_b: "gridflow connectors/elexon/endpoints.py L107-114"
    source_b_says: "ENDPOINTS['freq'] uses from_param='measurementDateTimeFrom', to_param='measurementDateTimeTo' (post V2-FIX-01)"
    orchestrator_recommendation: "documented and resolved — surface in caveats so users know historical bronze may be mis-windowed"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** 50 Hz, sampled <span class="italic fg-accent">every second.</span>

**Lede:** Second-by-second GB system frequency — the canonical telemetry for frequency-response models, RoCoF estimation, and ancillary-services validation.

**Verified line:** Verified against vendor docs: 2026-05-09 · [Elexon BMRS · FREQ](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FREQ)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.freq` |
| API PATH | `/datasets/FREQ` |
| FREQUENCY | hourly (publication) |
| PUBLICATION LAG | ~1 min |
| VOLUME | 2.6M / mo |
| PRIMARY KEY | `(timestamp_utc)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | ~2 s | Sample interval |
| 2 | ~1 min | Publication lag |
| 3 | 49.0–51.0 | Hz validation range |
| 4 | 4 | Schema columns |

# Sidebar siblings

- system_prices
- netbsad
- disbsad
- nonbm
- fuelinst

# Sample chart

- **Type:** `sparkline`
- **Title:** "System frequency · 24-hour snapshot"
- **Subtitle:** "Sparkline · Hz · UTC · 6 May 2026"
- **Seed:** 50
- **Toggles:** `1h` / `24h` (active) / `7d`

# Schema

Defined in `gridflow/schemas/elexon.py` · `ElexonFrequency` (lines 169-182) and `gridflow/silver/elexon/freq.py` · `FreqTransformer.output_cols`. Partitioned by `settlement_date` (year + month) — derived from `timestamp_utc`. Point-in-time field: `ingested_at` (no native PIT field).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `reportDateTime` / `measurementTime` | Sample time. ISO-8601 UTC (e.g. `2026-05-08T00:00:00Z`). Validator requires tzinfo. | `schemas/elexon.py L172, L177-182`; `silver/elexon/freq.py L55-56, L71-74` |
| `frequency_hz` | `float` | No | `frequency` | Hz. Validated `ge=49.0, le=51.0` — the schema admits transient excursions outside the statutory 49.5–50.5 band so genuine system events are not rejected as data errors. | `schemas/elexon.py L173` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `schemas/elexon.py L174` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `schemas/elexon.py L175` |

**PARQUET PATH:** `data/silver/elexon/freq/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)` — derived from `timestamp_utc`
**DEDUP KEY:** `(timestamp_utc)` (`silver/elexon/freq.py L78`)

# Sample data

| timestamp_utc | frequency_hz | data_provider | ingested_at |
|---|---|---|---|
| 2026-05-07T23:59:45Z | 50.017 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-08T00:00:00Z | 49.97 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-08T00:00:15Z | 49.985 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-08T00:00:30Z | 50.012 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-08T00:00:45Z | 50.024 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-08T00:01:00Z | 50.030 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-08T08:17:22Z** | **49.612** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-08T08:17:24Z | 49.640 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (50.017) and 2 (49.97) verbatim from the vault Bronze Sample (vault/elexon/freq.md, live 2026-05-08; `measurementTime` 2026-05-07T23:59:45Z and 2026-05-08T00:00:00Z). Remaining rows synthesised — respect schema constraints (`frequency_hz ge=49.0 le=51.0`, ~2-second cadence) and represent normal stable operation plus a frequency dip. The highlighted **08:17:22Z** row is the interesting case: 49.612 Hz is a real-world dip below the statutory 49.5 lower bound that the schema deliberately admits — losing a major generator can drop the frequency this far before frequency-response services arrest it. This is the kind of moment a frequency-response model is trained to predict.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: FREQ is a single-series scalar telemetry; there are no codelists, settlement runs, or PSR taxonomies to surface. The validation range and time semantics are documented in schema notes.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/FREQ`
- AUTH: None required for tested endpoints (2026-05-08/09). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/freq/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.freq.FreqTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/FREQ?measurementDateTimeFrom=2026-05-09T00:00Z&measurementDateTimeTo=2026-05-09T01:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Time spent outside the statutory operating range (49.5–50.5 Hz) per day
SELECT date_trunc('day', timestamp_utc) AS day,
       SUM(CASE WHEN frequency_hz < 49.5 OR frequency_hz > 50.5
                THEN 1 ELSE 0 END) AS n_excursion_samples,
       MIN(frequency_hz) AS min_hz,
       MAX(frequency_hz) AS max_hz
FROM read_parquet('data/silver/elexon/freq/**/*.parquet')
WHERE timestamp_utc >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/freq/**/*.parquet")
# Rolling 1-minute mean + max deviation from 50 Hz
roll = (
    df.sort("timestamp_utc")
      .with_columns(
          pl.col("frequency_hz").rolling_mean(window_size=30).alias("freq_60s"),
          (pl.col("frequency_hz") - 50.0).abs().rolling_max(window_size=30).alias("dev_60s"),
      )
)
print(roll.tail(20))
```

# Caveats

## 01 Use `measurementDateTimeFrom`/`To`, NOT `publishDateTimeFrom`/`To`

`/datasets/FREQ` requires `measurementDateTime*` params; wrong names silently return the latest ~5,761 samples. *(Source: V2-FIX-01; `connectors/elexon/endpoints.py L107-114`.)*

## 02 Historical bronze may be mis-windowed

Bronze captured pre-2026-05-09 holds the latest-N fallback, not the requested window. Re-ingest to repair. *(Source: V2-FIX-01.)*

## 03 Validation range admits transient excursions

Validator `ge=49.0, le=51.0` is deliberately wider than the statutory 49.5–50.5 band so real events aren't rejected. *(Source: `schemas/elexon.py L173`.)*

## 04 High-volume — partition tightly when querying long windows

~2.6M rows/month; queries must use `WHERE timestamp_utc BETWEEN ...` for partition pruning. *(Source: manifest `rows: "2.6M / mo"`.)*

## 05 Dedup on `timestamp_utc` only — duplicate-second samples lose precision

API timestamps are whole-second; sub-second samples colliding on `timestamp_utc` are deduped to last-arrived. RoCoF needs bronze. *(Source: `silver/elexon/freq.py L78`.)*

# Related datasets

- **system_prices** — System buy / sell prices. `30 min`. Frequency excursions correlate with NIV and price spikes — pair to predict cash-out cost during system events. `elexon · prices & balancing · 30 min`
- **netbsad** — Net balancing services adjustment data. `30 min`. Frequency-response actions feed into BSAD; FREQ is the upstream signal. `elexon · prices & balancing · daily`
- **fuelinst** — Instantaneous generation by fuel. `~5 min`. Coarser-cadence companion; correlate FREQ dips with sudden fuel-mix changes (loss of a CCGT or interconnector). `elexon · generation · ~5 min`
- **nonbm** — Non-BM STOR generation. `30 min`. STOR units are dispatched on frequency response; FREQ excursions trigger NONBM volume. `elexon · generation · 30 min`
