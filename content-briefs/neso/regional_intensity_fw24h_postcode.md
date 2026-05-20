---
slug: regional_intensity_fw24h_postcode
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity/fw24h/postcode
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_intensity_fw24h_postcode.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityFw24HPostcodeTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity_fw24h_postcode"] (lines 201-208, path /regional/intensity/{from_dt}/fw24h/postcode/{postcode})
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Postcode intensity, <span class="italic fg-accent">24h forecast.</span>

**Lede:** Postcode-scoped carbon-intensity forecast 24 hours ahead — the canonical day-ahead carbon outlook for one UK outward postcode.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/intensity/{from}/fw24h/postcode/{postcode}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity_fw24h_postcode` |
| API PATH | `/regional/intensity/{from}/fw24h/postcode/{postcode}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast horizon |
| VOLUME | ~48 SPs × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 24 h | Forecast horizon |
| 3 | 1 / call | Region per request |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_fw24h
- regional_intensity_fw24h_regionid
- regional_postcode
- regional_intensity_fw48h_postcode
- regional_intensity_pt24h_postcode

# Sample chart

- **Type:** `sparkline`
- **Title:** "Postcode 24h forecast"
- **Subtitle:** "Sparkline · gCO2/kWh · postcode RG10 · from 6 May 2026 00:00"
- **Seed:** 49
- **Toggles:** `24h` (active) / `vs national fw24h`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc`. Region-keyed envelope — region object echoes the requested `postcode`. `actual_gco2_kwh` always null (forecast-only).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | DNO region serving this postcode. | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | The requested outward postcode. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | 24h-horizon forecast intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Always null. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_intensity_fw24h_postcode/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | postcode | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|---|
| 2026-05-07T00:00:00+00:00 | 12 | South England | RG41 | 192.0 | moderate | gas | 44.3 |
| 2026-05-07T06:00:00+00:00 | 12 | South England | RG41 | 145.0 | moderate | gas | 36.8 |
| **2026-05-07T12:00:00+00:00** | **12** | **South England** | **RG41** | **78.0** | **low** | **solar** | **24.2** |
| 2026-05-07T18:00:00+00:00 | 12 | South England | RG41 | 232.0 | high | gas | 51.2 |
| 2026-05-07T23:30:00+00:00 | 12 | South England | RG41 | 205.0 | moderate | gas | 47.4 |

**Sources:** Five SPs across the 24h forecast window for postcode `RG41` (SSE South / regionid=12). Vault Silver sample shape; values plausible for southern-England DNO day-ahead. Highlighted 12:00 row at 78 gCO2/kWh — the postcode's clean window for tomorrow; the consumer-facing "when to plug in the EV" answer.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/fw24h/postcode/{postcode}` (outward postcode only)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity_fw24h_postcode/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityFw24HPostcodeTransformer` (dynamically generated; default postcode `RG10`)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-07T00:00Z/fw24h/postcode/RG10
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Tomorrow's cleanest 4 SPs for one postcode
SELECT timestamp_utc, forecast_gco2_kwh, intensity_index
FROM read_parquet('data/silver/neso/regional_intensity_fw24h_postcode/**/*.parquet')
WHERE fuel = ''
ORDER BY forecast_gco2_kwh
LIMIT 4;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_intensity_fw24h_postcode/**/*.parquet")
# Postcode 24h fuel-mix forecast — pair with intensity_factors for MEF outlook
factors = pl.read_parquet("data/silver/neso/intensity_factors/intensity_factors.parquet")
attribution = (
    df.filter(pl.col("fuel") != "")
      .join(factors, on="fuel", how="left")
      .with_columns(
          (pl.col("generation_percentage") * pl.col("factor_gco2_kwh") / 100).alias("contrib_g")
      )
)
print(attribution.head())
```

# Caveats

## 01 Outward postcode only

`{postcode}` accepts the outward part only (e.g. `RG10`, not `RG10 8AA`). *(Source: NESO docs — postcode segment semantics.)*

## 02 `actual_gco2_kwh` always null

Forecast horizon only. *(Source: `endpoints.py L205`.)*

## 03 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L203`). *(Source: `endpoints.py L203`.)*

## 04 Default postcode `RG10`

Connector default if no override (`endpoints.py L207`). Change for production. *(Source: `endpoints.py L13, L207`.)*

## 05 Transformer is dynamically generated

`RegionalIntensityFw24HPostcodeTransformer` is created at import time via `type()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_intensity_fw24h`** — All-regions 24h forecast. `30 min`. Returns this postcode's DNO embedded in 17-region output. *neso · regional forecast · 30 min*
- **`regional_intensity_fw24h_regionid`** — Same 24h forecast keyed by regionid. `30 min`. Numeric-ID equivalent — use whichever join key you have. *neso · regional forecast · 30 min*
- **`regional_intensity_fw48h_postcode`** — Same postcode · 48h horizon. `30 min`. Longer outlook for the same postcode. *neso · regional forecast · 30 min*
- **`regional_postcode`** — Live snapshot · same postcode. `30 min`. Companion for "right now" alongside this forecast. *neso · regional intensity · 30 min*
