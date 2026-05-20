---
slug: imbalngc
vendor: elexon
vendor_label: Elexon BMRS
api_code: IMBALNGC
last_verified: 2026-05-08
sources_consulted:
  - vault/elexon/imbalngc.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonIMBALNGC class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/imbalngc.py::ImbalNGCTransformer (lines 19-106)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 125-129, PUBLISH_DATETIME style)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/IMBALNGC (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonIMBALNGC Pydantic class declared"
    source_b: "gridflow silver/elexon/imbalngc.py L19-106"
    source_b_says: "ImbalNGCTransformer outputs settlement_date, settlement_period, timestamp_utc, indicated_imbalance, data_provider, ingested_at"
    orchestrator_recommendation: "trust silver transformer; same shape gap as other indicated/demand datasets (melngc, inddem, indgen)"
  - source_a: "vault API endpoint query params include `boundary`"
    source_a_says: "The vendor accepts a `boundary` filter (e.g. `N`)"
    source_b: "gridflow connectors/elexon/endpoints.py L125-129"
    source_b_says: "Connector registration omits `boundary` from the param style — only `publishDateTimeFrom/To` are sent"
    orchestrator_recommendation: "trust gridflow as the active default — boundary is left unfiltered (returns all boundaries). The vault note is the API option; if downstream needs boundary filtering, extend the connector."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** National Grid's indicated imbalance, <span class="italic fg-accent">half-hour by half-hour.</span>

**Lede:** Half-hourly GB indicated imbalance forecast — the canonical day-ahead signal for gate-closure trading, forecast-error analysis, and cash-out attribution.

**Verified line:** Verified against vendor docs: 2026-05-08 · [Elexon BMRS · IMBALNGC](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/IMBALNGC)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.imbalngc` |
| API PATH | `/datasets/IMBALNGC` |
| FREQUENCY | 30 min |
| PUBLICATION LAG | 0 (forward-looking) |
| VOLUME | 44k / mo |
| PRIMARY KEY | `(settlement_date, settlement_period)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Frequency |
| 2 | 0 | Lag (day-ahead) |
| 3 | 1 | Row per period |
| 4 | 6 | Schema columns |

# Sidebar siblings

- melngc
- inddem
- indgen
- ndf
- system_prices

# Sample chart

- **Type:** `sparkline`
- **Title:** "Indicated imbalance · 24-hour forecast"
- **Subtitle:** "Sparkline · MWh · UTC · forecast for 6 May 2026"
- **Seed:** 41
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/silver/elexon/imbalngc.py` · `ImbalNGCTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month). Point-in-time field: `published_at` (silver currently drops it — see caveat 03).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `settlement_date` | `date` | No | `settlementDate` | Settlement date (BST/GMT calendar). Partition key. | `silver/elexon/imbalngc.py L74` |
| `settlement_period` | `int` | No | `settlementPeriod` | 1..50 (DST: 46 spring, 50 autumn). | `silver/elexon/imbalngc.py L75` |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. | `silver/elexon/imbalngc.py L79-88` |
| `indicated_imbalance` | `Optional[float]` | Yes | `indicatedImbalance` / `imbalance` | **MWh**. Positive = expected long (generation > demand); negative = expected short. | `silver/elexon/imbalngc.py L60-61, L76` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/imbalngc.py L94` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/imbalngc.py L95` |

**PARQUET PATH:** `data/silver/elexon/imbalngc/year=YYYY/month=MM/`
**PARTITION BY:** `settlement_date (year + month)`
**DEDUP KEY:** `(settlement_date, settlement_period)` (`silver/elexon/imbalngc.py L90`)

# Sample data

| settlement_date | settlement_period | timestamp_utc | indicated_imbalance | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-05-06 | 9 | 2026-05-06T04:00:00+00:00 | 77.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 10 | 2026-05-06T04:30:00+00:00 | 66.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 16 | 2026-05-06T07:30:00+00:00 | -45.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 17 | 2026-05-06T08:00:00+00:00 | -120.0 | elexon | 2026-05-08T12:00:00Z |
| **2026-05-06** | **36** | **2026-05-06T17:30:00+00:00** | **-188.0** | **elexon** | **2026-05-08T12:00:00Z** |
| 2026-05-06 | 37 | 2026-05-06T18:00:00+00:00 | -161.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 44 | 2026-05-06T21:30:00+00:00 | 28.0 | elexon | 2026-05-08T12:00:00Z |
| 2026-05-06 | 48 | 2026-05-06T23:30:00+00:00 | 51.0 | elexon | 2026-05-08T12:00:00Z |

**Sources:** SP9 (`imbalance=77`) and SP10 (`imbalance=66`) rows verbatim from the vault Bronze Sample (vault/elexon/imbalngc.md, live 2026-05-08). Remaining rows synthesised — respect transformer constraints (float MWh, signed) and follow the typical GB daily imbalance arc: positive (long) overnight, negative (short) at morning and evening peaks. The highlighted **SP36 (-188 MWh)** row is the interesting case: evening-peak system short of nearly 200 MWh — the kind of period where SBP spikes and BOAL volume jumps, exactly the forecast signal trading desks want before gate closure.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: IMBALNGC emits one scalar per period; no enumerable taxonomies. The boundary code is API-side input rather than output structure.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/IMBALNGC`
- AUTH: None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/imbalngc/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.imbalngc.ImbalNGCTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/IMBALNGC?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-06T03:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Average indicated imbalance by hour-of-day over the last 30 days
SELECT date_part('hour', timestamp_utc) AS hour,
       AVG(indicated_imbalance) AS avg_imbalance_mwh,
       MIN(indicated_imbalance) AS min_imbalance_mwh
FROM read_parquet('data/silver/elexon/imbalngc/**/*.parquet')
WHERE settlement_date >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/elexon/imbalngc/**/*.parquet")
# Periods forecast to be short (negative imbalance), sorted by depth
short = (
    df.filter(pl.col("indicated_imbalance") < 0)
      .sort("indicated_imbalance")
      .select(["settlement_date", "settlement_period", "indicated_imbalance"])
      .head(20)
)
print(short)
```

# Caveats

## 01 No Pydantic schema in `schemas/elexon.py`

No `ElexonIMBALNGC` class; shape lives in `ImbalNGCTransformer.output_cols`. Importing will fail. *(Source: `silver/elexon/imbalngc.py L98-101`.)*

## 02 Sign convention — positive = long, negative = short

`indicated_imbalance = generation − demand`; positive = long (SSP falls), negative = short (SBP rises). Matches the NIV convention in `system_prices`. *(Source: GB imbalance settlement framework.)*

## 03 Forecast revisions are not preserved

Silver dedup `keep="last"` collapses revisions to latest. Forecast-error studies need bronze with `published_at`. *(Source: `silver/elexon/imbalngc.py L90`.)*

## 04 `boundary` filter is supported by API but not used by connector

Connector omits the `boundary` param; all boundaries collapse in silver dedup. Extend the connector for boundary-specific imbalance. *(Source: `connectors/elexon/endpoints.py L125-129`.)*

## 05 Pair with `melngc` for the full margin picture

IMBALNGC is generation−demand; MELNGC is headroom above peak demand. Models need both to catch tight-margin periods with small imbalance. *(Source: GB capacity-margin framework.)*

# Related datasets

- **melngc** — Indicated margin (day & day-ahead). `30 min`. The complementary headroom-above-demand signal; same publish cadence and key. `elexon · demand & forecasts · 30 min`
- **inddem** — Indicated demand (day & day-ahead). `30 min`. The demand input to IMBALNGC; subtract `indgen` from this to reproduce IMBALNGC. `elexon · demand & forecasts · 30 min`
- **indgen** — Indicated generation (day & day-ahead). `30 min`. The generation input; IMBALNGC = `indgen` − `inddem`. Useful for understanding which side of the equation is driving the imbalance. `elexon · demand & forecasts · 30 min`
- **system_prices** — System buy / sell prices. `30 min`. The post-settlement outturn; compute forecast error by joining IMBALNGC to system_prices' `net_imbalance_volume` on (date, period). `elexon · prices & balancing · 30 min`
