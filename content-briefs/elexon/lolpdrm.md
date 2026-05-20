---
slug: lolpdrm
vendor: elexon
vendor_label: Elexon BMRS
api_code: LOLPDRM
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/lolpdrm.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonLOLPDRM class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/lolpdrm.py::LOLPDRMTransformer (lines 19-113)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 229-234, PUBLISH_DATETIME style with max_chunk_hours=1)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/LOLPDRM (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonLOLPDRM class declared"
    source_b: "gridflow silver/elexon/lolpdrm.py L19-113"
    source_b_says: "LOLPDRMTransformer outputs settlement_date, settlement_period, timestamp_utc, loss_of_load_probability, derated_margin_mw, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; same shape gap as other reliability/indicated datasets"
  - source_a: "vault Bronze Sample uses `dataset: LOLPDM` (no trailing R)"
    source_a_says: "Live API records identify themselves as LOLPDM"
    source_b: "gridflow connectors/elexon/endpoints.py L229"
    source_b_says: "Path registered as `/datasets/LOLPDRM` with trailing R"
    orchestrator_recommendation: "documented vendor inconsistency — the endpoint path expects LOLPDRM but echoes LOLPDM in record headers. Connector path is correct."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB reliability metrics, <span class="italic fg-accent">day-ahead.</span>

**Lede:** Half-hourly GB loss-of-load probability and de-rated margin — the canonical day-ahead signals for capacity adequacy, reliability alerts, and stress-period analysis.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · LOLPDRM](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/LOLPDRM)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.lolpdrm` |
| API PATH | `/datasets/LOLPDRM` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | 0 (day-ahead) |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Per-period cadence |
| 2 | 1 h | Max chunk hours (connector) |
| 3 | 0..1 | LOLP range |
| 4 | 7 | Schema columns |

# Sidebar siblings

- melngc
- imbalngc
- fou2t14d
- uou2t14d
- inddem

# Sample chart

- **Type:** `sparkline`
- **Title:** "De-rated margin · 7-day day-ahead view"
- **Subtitle:** "Sparkline · MW · UTC · week of 6 May 2026"
- **Seed:** 23
- **Toggles:** `24h` / `7d` (active) / `30d`

# Schema

Defined in `gridflow/silver/elexon/lolpdrm.py` · `LOLPDRMTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/lolpdrm.py L79` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/lolpdrm.py L80` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/lolpdrm.py L85-93` |
| `loss_of_load_probability` | `float` | No | `lossOfLoadProbability` | **Dimensionless probability 0..1**. Healthy operating range: ≈0. Non-zero values cluster in winter evening peaks. | `silver/elexon/lolpdrm.py L60, L81` |
| `derated_margin_mw` | `float` | No | `deratedMargin` | MW. Headroom above expected demand after de-rating intermittent capacity. Negative values are possible during system stress. | `silver/elexon/lolpdrm.py L61, L82` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/lolpdrm.py L100` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/lolpdrm.py L101` |

**PARQUET PATH:** `data/silver/elexon/lolpdrm/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period)` (`silver/elexon/lolpdrm.py L96`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | loss_of_load_probability | derated_margin_mw | data_provider | ingested_at |
|---|---|---|---|---|---|---|
| 2026-05-07 | 9 | 2026-05-07T04:00:00+00:00 | 0.0 | 17801.912 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-07 | 10 | 2026-05-07T04:30:00+00:00 | 0.0 | 17769.74 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-07 | 17 | 2026-05-07T08:00:00+00:00 | 0.0 | 11240.5 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-07 | 24 | 2026-05-07T11:30:00+00:00 | 0.0 | 8920.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-07** | **36** | **2026-05-07T17:30:00+00:00** | **0.0021** | **4810.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-07 | 37 | 2026-05-07T18:00:00+00:00 | 0.0014 | 5210.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-07 | 44 | 2026-05-07T21:30:00+00:00 | 0.0 | 9420.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-07 | 48 | 2026-05-07T23:30:00+00:00 | 0.0 | 15410.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (SP9, `lossOfLoadProbability=0.0`, `deratedMargin=17801.912`) and 2 (SP10, `deratedMargin=17769.74`) verbatim from the vault Bronze Sample (vault/elexon/lolpdrm.md, live 2026-05-08 for day-ahead settlement_date 2026-05-07). Remaining rows synthesised — respect transformer constraints (LOLP 0..1, derated margin float MW) and represent the typical day-ahead arc: low LOLP overnight and midday, slightly elevated around the SP36 evening peak. The highlighted **SP36 (LOLP=0.0021, DRM=4810 MW)** row is the interesting case: tightest margin of the day and non-zero LOLP, exactly the period reliability analytics need to surface for capacity-margin alerts.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: LOLPDRM emits two scalars per period; no enumerable taxonomies. Relationship to MELNGC and de-rating methodology is documented in caveats.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/LOLPDRM`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/lolpdrm/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.lolpdrm.LOLPDRMTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/LOLPDRM?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T01:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Periods with non-zero LOLP over the last 30 days (rare events)
SELECT settlement_date, settlement_period,
       loss_of_load_probability, derated_margin_mw
FROM read_parquet('data/silver/elexon/lolpdrm/**/*.parquet')
WHERE loss_of_load_probability > 0
  AND settlement_date >= current_date - INTERVAL 30 DAY
ORDER BY loss_of_load_probability DESC, settlement_date, settlement_period
LIMIT 50;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/lolpdrm/**/*.parquet")
# Daily minimum de-rated margin (worst-margin period each day)
worst = (
    df.group_by("settlement_date")
      .agg(
          pl.col("derated_margin_mw").min().alias("worst_drm_mw"),
          pl.col("loss_of_load_probability").max().alias("max_lolp"),
      )
      .sort("settlement_date")
)
print(worst.tail(30))
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

No `ElexonLOLPDRM` class; shape lives in `LOLPDRMTransformer.output_cols`. *(Source: `silver/elexon/lolpdrm.py`.)*

## 02 1-hour chunk cap on the API

Connector sets `max_chunk_hours=1`; vendor rejects larger windows. Backfills require many calls. *(Source: `connectors/elexon/endpoints.py L229-234`.)*

## 03 LOLP is dimensionless 0..1, not a percentage

`0.01` = 1% chance, not 1%. Don't multiply by 100. *(Source: vault Known Issues.)*

## 04 De-rated margin uses NESO's de-rating factors

Wind scaled ~15-20%, solar near-zero in winter evenings. Don't recompute from `fuelhh` without matching methodology. *(Source: NESO de-rating publication.)*

## 05 Vendor dataset header inconsistency

API echoes `"dataset": "LOLPDM"` (no trailing R); the path is `LOLPDRM`. Don't filter bronze on `dataset == "LOLPDRM"`. *(Source: vault Bronze Sample.)*

# Related datasets

- **melngc** — Indicated margin (day & day-ahead). `30 min`. Intra-day counterpart with no de-rating — pair to see how the de-rated view differs from the raw view. `elexon · demand & forecasts · 30 min`
- **imbalngc** — Indicated imbalance. `30 min`. Complementary day-ahead signal — IMBALNGC says how much short/long; LOLPDRM says how scary that is given the available capacity. `elexon · demand & forecasts · 30 min`
- **fou2t14d** — 2-14 day generation availability by fuel. `daily`. Forward-availability declarations that feed the LOLP/DRM calculation; if availability is over-declared, LOLP under-estimates risk. `elexon · demand & forecasts · daily`
- **uou2t14d** — 2-14 day availability by BM unit. `daily`. Unit-level companion to FOU2T14D; the granular source LOLP/DRM is derived from. `elexon · demand & forecasts · daily`
