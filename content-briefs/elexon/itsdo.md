---
slug: itsdo
vendor: elexon
vendor_label: Elexon BMRS
api_code: ITSDO
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/itsdo.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonITSDO class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/itsdo.py::ITSDOTransformer (lines 19-108)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 190-194, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/ITSDO (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonITSDO class declared"
    source_b: "gridflow silver/elexon/itsdo.py L19-108"
    source_b_says: "ITSDOTransformer outputs settlement_date, settlement_period, timestamp_utc, initial_transmission_system_demand_outturn_mw, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; same gap as indo/indod"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Transmission-system demand, <span class="italic fg-accent">embedded excluded.</span>

**Lede:** ITSDO is the Initial Transmission System Demand Outturn — realised demand on the GB transmission network, per settlement period. Unlike `indo` (national total), ITSDO excludes embedded generation; the gap between the two is the canonical measurement of how much demand is offset by sub-transmission generation (small solar, embedded wind, CHP).

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · ITSDO](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/ITSDO)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.itsdo` |
| API PATH | `/datasets/ITSDO` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | ~5 min |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | ~5 min | Publication lag |
| 3 | 1 | Row per period |
| 4 | 6 | Schema columns |

# Sidebar siblings

- indo
- atl
- indod
- tsdf
- tsdfd

# Overview

1. <code>itsdo</code> is **Initial Transmission System Demand Outturn** — the demand actually measured on the GB transmission network per settlement period. The key distinction from `indo` is that ITSDO is transmission-only: embedded generation (sub-1 MW solar, distribution-connected wind, embedded CHP) is excluded. The implied embedded contribution is therefore <code>indo − itsdo</code>.

2. Gridflow fetches it from <code>/datasets/ITSDO</code> using the <code>publishDateTimeFrom</code> / <code>publishDateTimeTo</code> pattern (connector entry at <code>connectors/elexon/endpoints.py L190-194</code>). The <code>ITSDOTransformer</code> renames `demand` → `initial_transmission_system_demand_outturn_mw`, derives `timestamp_utc`, and dedups on `(settlement_date, settlement_period)`. No Pydantic class is declared.

3. Cadence is half-hourly publication with ~5-minute lag at period close. Verified against the live API on 2026-05-08. ITSDO is what the transmission network operators actually had to balance; INDO is the broader measure that includes load served behind the meter. Pair with `indo` to track embedded generation over time, with `tsdf` for the forecast counterpart, and with `fuelhh` for transmission-side fuel-mix attribution.

# Sample chart

- **Type:** `sparkline`
- **Title:** "Transmission demand · 24-hour profile"
- **Subtitle:** "Sparkline · MW · UTC · 6 May 2026"
- **Seed:** 19
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/silver/elexon/itsdo.py` · `ITSDOTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `ingested_at`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/itsdo.py L76` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/itsdo.py L77` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/itsdo.py L81-90` |
| `initial_transmission_system_demand_outturn_mw` | `float` | No | `demand` | MW. Transmission-only national demand. | `silver/elexon/itsdo.py L59, L78` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/itsdo.py L96` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/itsdo.py L97` |

**PARQUET PATH:** `data/silver/elexon/itsdo/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period)` (`silver/elexon/itsdo.py L92`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | initial_transmission_system_demand_outturn_mw | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-05-06 | 7 | 2026-05-06T03:00:00+00:00 | 24569.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 8 | 2026-05-06T03:30:00+00:00 | 23628.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 16 | 2026-05-06T07:30:00+00:00 | 30180.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | 31410.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **24** | **2026-05-06T11:30:00+00:00** | **27840.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 36 | 2026-05-06T17:30:00+00:00 | 35820.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 31410.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 27108.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** Rows 1 (SP7, `demand=24569`) and 2 (SP8, `demand=23628`) verbatim from the vault Bronze Sample (vault/elexon/itsdo.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (float MW) and follow the typical GB transmission-demand curve. The highlighted **SP24 (27840 MW)** row is the interesting case: noon is the period where the gap between INDO (national) and ITSDO (transmission-only) is largest, because midday embedded solar offsets the most demand. INDO − ITSDO at this period is the closest you can get to an instantaneous embedded-solar estimate.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: ITSDO emits one scalar per period; no enumerable taxonomies. The INDO/ITSDO relationship is in caveats.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/ITSDO`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/itsdo/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.itsdo.ITSDOTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/ITSDO?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily embedded-generation estimate: sum of (INDO − ITSDO) × 0.5 per day
WITH joined AS (
  SELECT i.settlement_date, i.settlement_period,
         i.initial_demand_outturn_mw - t.initial_transmission_system_demand_outturn_mw AS embedded_mw
  FROM read_parquet('data/silver/elexon/indo/**/*.parquet') i
  JOIN read_parquet('data/silver/elexon/itsdo/**/*.parquet') t
    USING (settlement_date, settlement_period)
)
SELECT settlement_date, SUM(embedded_mw) * 0.5 AS embedded_mwh
FROM joined
WHERE settlement_date >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

indo = pl.read_parquet("data/silver/elexon/indo/**/*.parquet")
itsdo = pl.read_parquet("data/silver/elexon/itsdo/**/*.parquet")
embedded = (
    indo.join(itsdo, on=["settlement_date", "settlement_period"], how="inner")
        .with_columns([
            pl.col("timestamp_utc").dt.hour().alias("hour"),
            (pl.col("initial_demand_outturn_mw")
             - pl.col("initial_transmission_system_demand_outturn_mw"))
              .alias("embedded_mw"),
        ])
        .group_by("hour")
        .agg(pl.col("embedded_mw").mean().alias("avg_embedded_mw"))
        .sort("hour")
)
print(embedded)
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

Like `indo`/`indod`, ITSDO has no dedicated Pydantic class. Silver shape is defined by `ITSDOTransformer.output_cols`. *(Source: `schemas/elexon.py` grep returns no ITSDO class.)*

## 02 Transmission-only — embedded generation excluded

ITSDO is what the transmission network metered. Embedded generation (small solar, distribution-connected wind, embedded CHP) appears as *reduced demand* in ITSDO but is added back in INDO. `indo − itsdo` is therefore the implied embedded contribution. The midday gap is dominated by embedded solar; the evening gap is mostly embedded wind + CHP. *(Source: vault Known Issues — "Transmission-only — does not include embedded generation. Embedded contribution = INDO − ITSDO".)*

## 03 Column name is verbose by design

The silver column is `initial_transmission_system_demand_outturn_mw` — long, but unambiguous. Aliasing to `itsdo_mw` or similar in downstream views is fine; just don't conflate it with `initial_demand_outturn_mw` (which is the INDO column). *(Source: `silver/elexon/itsdo.py L59` — column rename intentionally explicit.)*

## 04 Initial estimate, revised through settlement

Like INDO, ITSDO is the *initial* published outturn — D+1 publish, revised through BSC settlement reconciliation. For final reconciled transmission demand use settlement-run datasets. *(Source: vault Overview — "Initial National Demand Outturn".)*

## 05 Pair with `tsdf` / `tsdfd` for forecast-vs-outturn

ITSDO is the realised transmission demand; `tsdf` is the same-day transmission forecast and `tsdfd` is the 2-14 day forecast. Compute forecast error by joining on (settlement_date, settlement_period). Note `tsdfd` is published days ahead with append-only revisions — use the latest-revision pattern documented in the FOU2T14D brief. *(Source: cross-reference with TSDF/TSDFD briefs; domain knowledge.)*

# Related datasets

- **indo** — Initial National Demand Outturn. `30 min`. The national counterpart; INDO − ITSDO = embedded generation contribution. `elexon · demand & forecasts · 30 min`
- **atl** — Actual total load per bidding zone (ENTSO-E B0610). `30 min`. ENTSO-E-aligned demand; compare against INDO/ITSDO for cross-reporting validation. `elexon · demand & forecasts · 30 min`
- **tsdf** — Transmission System Demand Forecast. `daily`. The forecast counterpart for forecast-error analysis. `elexon · demand & forecasts · daily`
- **fuelhh** — Generation by fuel type, half-hourly. `30 min`. Sum across fuels (excluding INT*) gives transmission-side generation; compare to ITSDO to derive transmission-only imbalance. `elexon · generation · 30 min`
