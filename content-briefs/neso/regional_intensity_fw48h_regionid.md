---
slug: regional_intensity_fw48h_regionid
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity/fw48h/regionid
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_intensity_fw48h_regionid.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityFw48HRegionidTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity_fw48h_regionid"] (lines 232-239, path /regional/intensity/{from_dt}/fw48h/regionid/{regionid})
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** DNO region intensity, <span class="italic fg-accent">48h forecast.</span>

**Lede:** Regionid-scoped carbon-intensity forecast 48 hours ahead — the canonical two-day carbon outlook for one numeric-keyed GB DNO region.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/intensity/{from}/fw48h/regionid/{regionid}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity_fw48h_regionid` |
| API PATH | `/regional/intensity/{from}/fw48h/regionid/{regionid}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast horizon |
| VOLUME | ~96 SPs × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 48 h | Forecast horizon |
| 3 | 1..17 | Region ID range |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_fw48h
- regional_intensity_fw48h_postcode
- regional_intensity_fw24h_regionid
- regional_intensity_pt24h_regionid
- regional_regionid

# Sample chart

- **Type:** `sparkline`
- **Title:** "Regionid 48h forecast"
- **Subtitle:** "Sparkline · gCO2/kWh · regionid 13 (London) · from 6 May 2026 00:00"
- **Seed:** 53
- **Toggles:** `48h` (active) / `24h`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc`. Region-keyed envelope. `actual_gco2_kwh` always null.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | NESO region identifier (1..17). | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Blank for regionid routes. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | 48h-horizon forecast intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Always null. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_intensity_fw48h_regionid/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| 2026-05-07T12:00:00+00:00 | 13 | London | 88.0 | low | solar | 22.4 |
| 2026-05-07T18:00:00+00:00 | 13 | London | 248.0 | high | gas | 53.4 |
| **2026-05-08T12:30:00+00:00** | **13** | **London** | **70.0** | **very low** | **solar** | **26.8** |
| 2026-05-08T18:00:00+00:00 | 13 | London | 252.0 | high | gas | 54.2 |
| 2026-05-08T23:30:00+00:00 | 13 | London | 218.0 | moderate | gas | 49.6 |

**Sources:** Five SPs across the 48h horizon for regionid=13 (London). Vault Silver sample shape; values plausible for London DNO multi-day. Highlighted day-2 12:30 row at 70 gCO2/kWh / `very low` — day-after-tomorrow's clean window in London.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/fw48h/regionid/{regionid}` (regionid 1..17)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity_fw48h_regionid/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityFw48HRegionidTransformer` (dynamically generated; default regionid `13`)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-07T00:00Z/fw48h/regionid/13
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- 48h forecast: hour-of-day distribution per region
SELECT extract('hour' FROM timestamp_utc) AS hod,
       median(forecast_gco2_kwh) AS median_g
FROM read_parquet('data/silver/neso/regional_intensity_fw48h_regionid/**/*.parquet')
WHERE regionid = 13
  AND fuel = ''
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_intensity_fw48h_regionid/**/*.parquet")
# Multi-day cleanest 4h windows per region
windows = (
    df.filter(pl.col("fuel") == "")
      .sort("timestamp_utc")
      .with_columns(
          pl.col("forecast_gco2_kwh").rolling_mean(window_size=8).alias("mean_4h")
      )
      .group_by("regionid").agg(pl.col("mean_4h").min().alias("cleanest_4h_g"))
      .sort("cleanest_4h_g")
)
print(windows.head())
```

# Caveats

## 01 `regionid` range is 1..17

Valid IDs: 1..17. *(Source: `endpoints.py L14`.)*

## 02 `actual_gco2_kwh` always null

Forecast horizon only. *(Source: `endpoints.py L236`.)*

## 03 Skill degrades with horizon

+48h skill is meaningfully worse than +24h. *(Source: domain knowledge.)*

## 04 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L234`). *(Source: `endpoints.py L234`.)*

## 05 Transformer is dynamically generated

`RegionalIntensityFw48HRegionidTransformer` is created at import time via `type()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_intensity_fw48h`** — All-regions 48h forecast. `30 min`. Returns this regionid embedded in 17-region output. *neso · regional forecast · 30 min*
- **`regional_intensity_fw48h_postcode`** — Same forecast keyed by postcode. `30 min`. Equivalent — use whichever join key. *neso · regional forecast · 30 min*
- **`regional_intensity_fw24h_regionid`** — Same regionid · 24h horizon. `30 min`. Shorter horizon for skill comparison. *neso · regional forecast · 30 min*
- **`regional_regionid`** — Live snapshot · same regionid. `30 min`. Companion for "right now". *neso · regional intensity · 30 min*
