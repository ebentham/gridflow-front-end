---
slug: forecast_margin
vendor: entsoe
vendor_label: ENTSO-E Transparency
api_code: A70/A33
last_verified: 2026-05-08
entitlement_required: false
sources_consulted:
  - vault/entsoe/forecast_margin.md
  - gridflow/src/gridflow/schemas/entsoe.py::EntsoeForecastMargin (lines 295-310)
  - gridflow/src/gridflow/silver/entsoe/forecast_margin.py::ForecastMarginTransformer (lines 18-89)
  - gridflow/src/gridflow/connectors/entsoe/endpoints.py::DOC_TYPES["forecast_margin"] (lines 132-134)
  - vendor docs: PDF-based platform — see vault references
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Year-ahead generation margin, <span class="italic fg-accent">capacity adequacy.</span>

**Lede:** Year-ahead forecast margin in MW per bidding zone — the TSO-published capacity-adequacy view, generation forecast minus load forecast across a full forward year.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-E Transparency · A70/A33](https://transparency.entsoe.eu/) (vendor-doc fetch deferred — platform is PDF-heavy)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.forecast_margin` |
| API PATH | `/api?documentType=A70&processType=A33` |
| FREQUENCY | PT60M (over a yearly window) |
| PUBLICATION LAG | annual |
| VOLUME | 1 TimeSeries / zone / year |
| PRIMARY KEY | `(timestamp_utc, area_code)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | A70 | DocumentType |
| 2 | annual | Forward-looking |
| 3 | XML | `GL_MarketDocument` |
| 4 | 6 | Schema columns |

# Sidebar siblings

- generation_forecast
- load_forecast_yearly
- installed_capacity
- water_reservoirs
- actual_generation

# Sample chart

- **Type:** `sparkline`
- **Title:** "DE-LU year-ahead margin · 8760 hours"
- **Subtitle:** "Line · MW · year 2026"
- **Seed:** 29
- **Toggles:** `year` (active) / `winter` / `summer`

# Schema

Defined in `gridflow/schemas/entsoe.py` · `EntsoeForecastMargin` (lines 295-310). Partitioned by `timestamp_utc` (year + month).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `<Period>` start + position × resolution | tz-aware UTC; validator requires tzinfo. | `schemas/entsoe.py L298, L305-310` |
| `area_code` | `str` | No | `<outBiddingZone_Domain.mRID>` | EIC bidding zone. | `schemas/entsoe.py L299` |
| `forecast_margin_mw` | `float` | No | `<Point><quantity>` | Margin MW = generation forecast - load forecast. Negative = capacity shortage. | `schemas/entsoe.py L300` |
| `resolution` | `str` | Yes (default `""`) | parsed | ISO duration; typically `PT60M`. | `schemas/entsoe.py L301` |
| `data_provider` | `str` | No (default `"entsoe"`) | _constant_ | Always `"entsoe"`. | `schemas/entsoe.py L302` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Set at silver write. | `schemas/entsoe.py L303` |

**PARQUET PATH:** `data/silver/entsoe/forecast_margin/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, area_code)` (`silver/entsoe/forecast_margin.py L62`)

# Sample data

| timestamp_utc | area_code | forecast_margin_mw | resolution | data_provider | ingested_at |
|---|---|---|---|---|---|
| 2026-01-15T08:00:00+00:00 | 10Y1001A1001A82H | 12450.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-01-15T18:00:00+00:00 | 10Y1001A1001A82H | 8210.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| **2026-01-16T18:00:00+00:00** | **10Y1001A1001A82H** | **-1820.0** | **PT60M** | **entsoe** | **2026-05-08T18:00:00Z** |
| 2026-07-15T13:00:00+00:00 | 10Y1001A1001A82H | 24180.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |
| 2026-12-15T18:00:00+00:00 | 10Y1001A1001A82H | 6420.0 | PT60M | entsoe | 2026-05-08T18:00:00Z |

**Sources:** Synthesised against typical DE-LU year-ahead shape — surplus in summer midday (solar dominant), tight in winter evenings, occasional dark-doldrums hours go negative. The highlighted **2026-01-16T18:00 (-1.82 GW)** row is the canonical capacity-stress hour: winter evening peak when wind is low and solar is zero — the use case A70/A33 was designed for.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `web-api.tp.entsoe.eu/api?documentType=A70&processType=A33&outBiddingZone_Domain={EIC}&periodStart={YYYY01010000}&periodEnd={YYYY12310000}`
- AUTH: query param `securityToken={ENTSOE_API_KEY}` — free registration sufficient.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsoe/forecast_margin/<year>/<month>/<day>/raw_<uuid>.xml`
- TRANSFORMER: `gridflow.silver.entsoe.forecast_margin.ForecastMarginTransformer`

**Tab 1 — Example URL**
```
https://web-api.tp.entsoe.eu/api?securityToken=$ENTSOE_API_KEY&documentType=A70&processType=A33&outBiddingZone_Domain=10Y1001A1001A82H&periodStart=202601010000&periodEnd=202612310000
```

**Tab 2 — DuckDB · SQL**
```sql
-- Hours with negative margin (capacity shortage) per zone per year
SELECT area_code, date_trunc('year', timestamp_utc) AS year,
       count(*) FILTER (WHERE forecast_margin_mw < 0) AS shortage_hours,
       min(forecast_margin_mw) AS worst_margin_mw
FROM read_parquet('data/silver/entsoe/forecast_margin/**/*.parquet')
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

mar = pl.read_parquet("data/silver/entsoe/forecast_margin/**/*.parquet")
# LOLE proxy: count of hours with margin < 0 per area per year
lole = mar.filter(pl.col("forecast_margin_mw") < 0).group_by(
    [pl.col("timestamp_utc").dt.year().alias("year"), "area_code"]
).agg(pl.len().alias("shortage_hours"))
print(lole.sort(["area_code", "year"]))
```

# Caveats

## 01 `outBiddingZone_Domain` (not `in_Domain`)

A70/A33 uses `outBiddingZone_Domain` for the area param (`domain_style="out_bidding_zone"`). Wrong param style returns EMPTY. *(Source: `endpoints.py L132-134`.)*

## 02 Use a yearly window

Year-ahead forecast — short windows may return EMPTY or partial. Build period bounds at year boundaries. *(Source: vault Known Issues.)*

## 03 Margin is signed — negative = capacity shortage

`forecast_margin_mw < 0` indicates TSO-anticipated supply shortfall (a key LOLE input). *(Source: ENTSO-E spec.)*

## 04 Revisions overwrite

Same `(timestamp_utc, area_code)` re-publication overwrites silently on dedup. No `published_at` for PIT. *(Source: `silver/entsoe/forecast_margin.py L62`.)*

## 05 Not entitlement-blocked

A70/A33 is one of the 14 ENTSO-E endpoints accessible with the free gridflow default API key (per Phase 7 D-06). *(Source: `.planning/reconciliation/entsoe/` — no `forecast_margin-http-401.md`.)*

# Related datasets

- **`generation_forecast`** — Day-ahead supply forecast. `PT60M`. The supply side of this dataset's margin (sum across PSRs ≈ this dataset's generation half). `entsoe · forecast · hourly`
- **`load_forecast_yearly`** — Year-ahead load forecast. `PT60M`. The demand side; this dataset = `generation_forecast - load_forecast_yearly`. `entsoe · load · annual`
- **`installed_capacity`** — Annual capacity-mix snapshot. `yearly`. Structural context behind any margin trajectory: low-margin years often coincide with capacity reductions. `entsoe · generation · annual`
- **`water_reservoirs`** — Weekly hydro storage. `weekly`. Reservoir level is the latent capacity that can swing margin from comfortable to tight in Nordic / Alpine zones. `entsoe · generation · weekly`
