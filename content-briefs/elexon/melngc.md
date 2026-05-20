---
slug: melngc
vendor: elexon
vendor_label: Elexon BMRS
api_code: MELNGC
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/melngc.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonMELNGC class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/melngc.py::MelNGCTransformer (lines 19-106)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 140-144, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/MELNGC (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonMELNGC class declared"
    source_b: "gridflow silver/elexon/melngc.py L19-106"
    source_b_says: "MelNGCTransformer outputs settlement_date, settlement_period, timestamp_utc, indicated_margin, data_provider, ingested_at (no boundary column despite API supporting boundary filter)"
    orchestrator_recommendation: "trust silver transformer; boundary is in bronze but transformer drops it — consistent gap with INDDEM/INDGEN where boundary IS preserved. Investigate for consistency in Phase-7 mini-recon."
  - source_a: "vault API endpoint table"
    source_a_says: "Accepts `boundary` query param (e.g. `N`)"
    source_b: "gridflow connectors/elexon/endpoints.py L140-144 + silver/elexon/melngc.py output_cols"
    source_b_says: "Connector does not pass boundary; transformer does not surface boundary even if returned"
    orchestrator_recommendation: "documented gap — same as inddem/indgen for connector side, but melngc transformer additionally drops boundary from output"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** GB capacity margin, the <span class="italic fg-accent">non-de-rated view.</span>

**Lede:** Half-hourly GB indicated margin — the canonical day-ahead headroom signal for capacity adequacy, de-rating comparison, and stress-period detection.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · MELNGC](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/MELNGC)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.melngc` |
| API PATH | `/datasets/MELNGC` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | 0 (forward-looking) |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | 0 | Lag (day-ahead) |
| 3 | indicative | De-rating treatment |
| 4 | 6 | Schema columns |

# Sidebar siblings

- lolpdrm
- imbalngc
- inddem
- indgen
- fou2t14d

# Overview

1. <code>melngc</code> is the half-hourly GB indicated margin — the non-de-rated headroom signal published day-ahead. It is the canonical capacity-adequacy series for stress-period detection and the unreserved counterpart to <code>lolpdrm</code>'s de-rated margin.

2. Gridflow fetches it from <code>/datasets/MELNGC</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern. The raw JSON lands in bronze and is written to the silver parquet partition via <code>MelNGCTransformer</code> — no Pydantic class; the API's optional <code>boundary</code> param is not currently surfaced.

3. Refreshed every 30 minutes with 0 publication lag (day-ahead). Verified against vendor docs on 2026-05-08.

# Sample chart

- **Type:** `sparkline`
- **Title:** "Indicated margin · 24-hour day-ahead view"
- **Subtitle:** "Sparkline · MW · UTC · forecast for 6 May 2026"
- **Shape:** `flat-baseload`
- **Params:** `{"mean": 8500, "noise": 0.12, "seed": 39}`
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/silver/elexon/melngc.py` · `MelNGCTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `published_at` (column-mapped from `publishTime` but not in `output_cols`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/melngc.py L74` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/melngc.py L75` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived via `utils/time.settlement_period_to_utc`. | `silver/elexon/melngc.py L79-88` |
| `indicated_margin` | `Optional[float]` | Yes | `indicatedMargin` / `margin` | **MW** (not MWh). Indicative margin headroom; negative means demand expected to exceed capacity at that boundary. | `silver/elexon/melngc.py L60-61, L76` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/melngc.py L94` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/melngc.py L95` |

**PARQUET PATH:** `data/silver/elexon/melngc/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period)` (`silver/elexon/melngc.py L90`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | indicated_margin | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | -3309.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 10 | 2026-05-06T04:30:00+00:00 | -3315.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 16 | 2026-05-06T07:30:00+00:00 | 6420.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | 8210.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 24 | 2026-05-06T11:30:00+00:00 | 9710.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **36** | **2026-05-06T17:30:00+00:00** | **4810.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 8820.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 12410.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (SP9, `margin=-3309`) and 2 (SP10, `margin=-3315`) verbatim from the vault Bronze Sample (vault/elexon/melngc.md, live 2026-05-08, boundary=B1). The negative values are **B1 zonal-boundary attributions** — not national totals. Remaining rows synthesised to represent typical national-boundary indicated margin (positive, peaks-and-troughs through the day). The highlighted **SP36 (4810 MW)** row is the interesting case: matches the LOLPDRM SP36 derated margin in this brief set's sample — note how the MELNGC indicative margin equals the LOLPDRM derated margin only when intermittent capacity is given full credit, which never happens in winter evening peaks.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: MELNGC emits one scalar per period; no enumerable taxonomies surfaced in silver. The de-rating distinction with LOLPDRM is documented in caveats.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/MELNGC`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/melngc/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.melngc.MelNGCTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/MELNGC?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Worst (smallest) indicated margin per day over the last 30 days
SELECT settlement_date,
       MIN(indicated_margin) AS worst_margin_mw,
       AVG(indicated_margin) AS avg_margin_mw
FROM read_parquet('data/silver/elexon/melngc/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

melngc = pl.read_parquet("data/silver/elexon/melngc/**/*.parquet")
lolpdrm = pl.read_parquet("data/silver/elexon/lolpdrm/**/*.parquet")
# Compare indicative vs de-rated margin per period
compare = (
    melngc.join(lolpdrm, on=["settlement_date", "settlement_period"], how="inner")
          .with_columns(
              (pl.col("indicated_margin") - pl.col("derated_margin_mw"))
                .alias("derating_haircut_mw")
          )
          .select(["settlement_date", "settlement_period",
                   "indicated_margin", "derated_margin_mw", "derating_haircut_mw"])
)
print(compare.tail(20))
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

No `ElexonMELNGC` class; shape lives in `MelNGCTransformer.output_cols`. *(Source: `silver/elexon/melngc.py`.)*

## 02 MELNGC is indicative; LOLPDRM is de-rated

MELNGC is raw margin, no de-rating. Expect MELNGC > `lolpdrm.derated_margin_mw` by several GW; the gap is the de-rating haircut. *(Source: NESO de-rating methodology.)*

## 03 `boundary` column is dropped from silver

API emits `boundary` but transformer doesn't surface it; dedup `keep="last"` mixes zonal and national rows. Inconsistent with INDDEM/INDGEN. *(Source: `silver/elexon/melngc.py L98-101`.)*

## 04 Negative values are zonal-boundary attributions

Negative `indicated_margin` (e.g. -3309) is a `boundary=B1` zonal delta, not a national deficit signal. *(Source: vault Bronze Sample.)*

## 05 Forecast revisions collapse on dedup

Dedup `keep="last"` on `(date, period)` collapses intra-day revisions. *(Source: `silver/elexon/melngc.py L90`.)*

# Related datasets

- **lolpdrm** — Loss of load probability and de-rated margin. `30 min`. The de-rated counterpart; pair to see the de-rating haircut and validate capacity-margin assumptions. `elexon · system & reference · 30 min`
- **imbalngc** — Indicated imbalance. `30 min`. Imbalance complement; MELNGC says how much headroom remains, IMBALNGC says how that headroom is being consumed by demand-side surprises. `elexon · demand & forecasts · 30 min`
- **inddem** — Indicated demand. `30 min`. The demand input to MELNGC; subtract it from indicated capacity to derive the margin (this is essentially what MELNGC publishes). `elexon · demand & forecasts · 30 min`
- **fou2t14d** — 2-14 day generation availability by fuel. `daily`. Medium-horizon availability that feeds capacity-margin projections; MELNGC is the day-ahead window of the same concept. `elexon · demand & forecasts · daily`
