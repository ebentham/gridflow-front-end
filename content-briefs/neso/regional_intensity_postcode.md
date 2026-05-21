---
slug: regional_intensity_postcode
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity/postcode
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_intensity_postcode.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityPostcodeTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity_postcode"] (lines 270-277, path /regional/intensity/{from_dt}/{to_dt}/postcode/{postcode})
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Postcode carbon intensity, <span class="italic fg-accent">range query.</span>

**Lede:** Postcode-scoped regional carbon intensity over a datetime range — the canonical historical series for one UK postcode and its serving DNO region.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/intensity/{from}/{to}/postcode/{postcode}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity_postcode` |
| API PATH | `/regional/intensity/{from}/{to}/postcode/{postcode}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | per period · actual rarely populated |
| VOLUME | 1 region × 48 SPs / day × N fuels |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 14 d | Max range per request |
| 3 | 1 / call | Region per request |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_postcode
- regional_intensity_fw24h_postcode
- regional_intensity_pt24h_postcode
- regional_intensity
- regional_intensity_regionid

# Sample chart

- **Type:** `sparkline`
- **Title:** "Postcode carbon intensity · 7-day history"
- **Subtitle:** "Sparkline · gCO2/kWh · postcode RG10 · UTC · last 7 days"
- **Seed:** 46
- **Toggles:** `7d` (active) / `30d`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via the shared `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc` (year + month). Region-keyed envelope — region object echoes the requested `postcode`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | DNO region serving this postcode. | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | The requested outward postcode. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Regional forecast carbon intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Often null on regional endpoints. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_intensity_postcode/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | postcode | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|---|
| 2026-05-08T00:00:00+00:00 | 12 | South England | RG41 | 235.0 | high | gas | 54.5 |
| 2026-05-08T06:00:00+00:00 | 12 | South England | RG41 | 198.0 | moderate | gas | 48.1 |
| **2026-05-08T12:00:00+00:00** | **12** | **South England** | **RG41** | **82.0** | **low** | **solar** | **24.8** |
| 2026-05-08T18:00:00+00:00 | 12 | South England | RG41 | 245.0 | high | gas | 58.3 |
| 2026-05-08T23:30:00+00:00 | 12 | South England | RG41 | 225.0 | moderate | gas | 52.1 |

**Sources:** Five SPs across one day for postcode RG41 (SSE South / South England, regionid=12). Vault Silver sample shape supplies the row layout; values plausible for southern-England DNO (gas-heavy with sunny solar peak). Highlighted 12:00 row — postcode-level solar peak shows the consumer-relevant clean window for "when to run the dishwasher" applications.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/{to}/postcode/{postcode}` (path segments; max 14-day range; outward postcode only)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity_postcode/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityPostcodeTransformer` (dynamically generated; default postcode `RG10`)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-08T00:00Z/2026-05-09T00:00Z/postcode/RG10
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Postcode rolling 7d cleanest hour
SELECT date_trunc('day', timestamp_utc) AS day,
       postcode,
       min(forecast_gco2_kwh) AS min_g,
       arg_min(timestamp_utc, forecast_gco2_kwh) AS cleanest_sp
FROM read_parquet('data/silver/neso/regional_intensity_postcode/**/*.parquet')
WHERE fuel = ''
  AND timestamp_utc >= current_date - INTERVAL 7 DAY
GROUP BY 1, 2
ORDER BY 1 DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_intensity_postcode/**/*.parquet")
# Postcode-level fuel-share trend
fuel_trend = (
    df.filter(pl.col("fuel") == "solar")
      .with_columns(pl.col("timestamp_utc").dt.date().alias("day"))
      .group_by("day").agg(pl.col("generation_percentage").max().alias("peak_solar"))
      .sort("day")
)
print(fuel_trend.tail(7))
```

# Caveats

## 01 Outward postcode only

`{postcode}` accepts the outward part only (e.g. `RG10`, not `RG10 8AA`). *(Source: NESO docs — postcode segment semantics.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L272`). *(Source: `endpoints.py L272`.)*

## 03 14-day max window per request

Connector chunks longer spans (`_MAX_DAYS_PER_REQUEST=14`). *(Source: `connectors/neso/carbon_intensity.py L21`.)*

## 04 Path placeholders `{from_dt}` / `{to_dt}` internally

Docs document `/regional/intensity/{from}/{to}/postcode/{postcode}`; connector templates as `{from_dt}` / `{to_dt}`. *(Source: vault Implementation Delta L106.)*

## 05 Transformer is dynamically generated

`RegionalIntensityPostcodeTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_postcode`** — Live snapshot · same postcode. `30 min`. Live companion to this dataset's historical / range. *neso · regional intensity · 30 min*
- **`regional_intensity_fw24h_postcode`** — 24h forecast · same postcode. `30 min`. Day-ahead carbon for the same postcode. *neso · regional forecast · 30 min*
- **`regional_intensity_pt24h_postcode`** — Past-24h actuals · same postcode. `30 min`. Rolling look-back companion. *neso · regional intensity · 30 min*
- **`regional_intensity`** — All-regions range query. `30 min`. Returns the postcode's DNO region embedded in 17-region output. *neso · regional intensity · 30 min*
