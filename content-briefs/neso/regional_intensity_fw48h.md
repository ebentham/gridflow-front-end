---
slug: regional_intensity_fw48h
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity/fw48h
last_verified: 2026-05-09
sources_consulted:
  - vault/neso/regional_intensity_fw48h.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityFw48HTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::_rows_from_region_period (lines 252-286 — V2-FIX-02 dual-shape handling)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity_fw48h"] (lines 217-223, path /regional/intensity/{from_dt}/fw48h)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Regional intensity, <span class="italic fg-accent">48h forecast.</span>

**Lede:** Regional carbon-intensity forecast for all ~17 GB DNO regions, 48 hours ahead — the canonical two-day spatial outlook for multi-day flexible-load planning.

**Verified line:** Verified against vendor docs: 2026-05-09 · [NESO Carbon Intensity · /regional/intensity/{from}/fw48h](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity_fw48h` |
| API PATH | `/regional/intensity/{from}/fw48h` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast horizon |
| VOLUME | ~17 × 96 × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 48 h | Forecast horizon |
| 3 | 17 | GB DNO regions per call |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_fw48h_postcode
- regional_intensity_fw48h_regionid
- regional_intensity_fw24h
- regional_intensity_pt24h
- intensity_fw48h

# Sample chart

- **Type:** `heatmap`
- **Title:** "Regional 48h forecast · 17 regions"
- **Subtitle:** "Heatmap · gCO2/kWh · from 6 May 2026 00:00 · forward 48h"
- **Seed:** 51
- **Toggles:** `48h` (active) / `24h` / `vs actuals`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc`. Uses the **period-keyed envelope** — `_rows_from_region_period` handles dual-shape (V2-FIX-02). `actual_gco2_kwh` always null (forecast-only).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | NESO region identifier (1..17). | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Blank for all-regions calls. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | 48h-horizon forecast intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Always null. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_intensity_fw48h/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| 2026-05-07T12:00:00+00:00 | 1 | North Scotland | 8.0 | very low | wind | 76.4 |
| 2026-05-07T12:00:00+00:00 | 13 | London | 78.0 | low | solar | 23.5 |
| 2026-05-08T00:00:00+00:00 | 13 | London | 198.0 | moderate | gas | 46.2 |
| **2026-05-08T12:30:00+00:00** | **1** | **North Scotland** | **2.0** | **very low** | **wind** | **82.1** |
| 2026-05-08T12:30:00+00:00 | 17 | Wales | 312.0 | very high | gas | 78.9 |
| 2026-05-08T18:00:00+00:00 | 13 | London | 248.0 | high | gas | 55.1 |

**Sources:** Six rows across the 48h horizon for 4 contrasting regions (vault Silver sample shape). Highlighted day-2 North Scotland at 2 gCO2/kWh / 82% wind — the dataset's value: longer horizon lets schedulers see when persistent wind weather windows hit; multi-day clean-energy planning.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/fw48h`
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity_fw48h/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityFw48HTransformer` (dynamically generated)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-07T00:00Z/fw48h
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Tomorrow vs day-after: per-region 24h-mean carbon forecast
SELECT regionid, shortname,
       avg(case when timestamp_utc::date = current_date + 1 then forecast_gco2_kwh end) AS day1_mean,
       avg(case when timestamp_utc::date = current_date + 2 then forecast_gco2_kwh end) AS day2_mean
FROM read_parquet('data/silver/neso/regional_intensity_fw48h/**/*.parquet')
WHERE fuel = ''
GROUP BY 1, 2
ORDER BY day1_mean - day2_mean DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_intensity_fw48h/**/*.parquet")
# Multi-day spread evolution — does carbon variation widen or narrow?
ws = (
    df.filter(pl.col("fuel") == "")
      .group_by("timestamp_utc")
      .agg(
          (pl.col("forecast_gco2_kwh").max() - pl.col("forecast_gco2_kwh").min()).alias("spread_g")
      )
      .sort("timestamp_utc")
)
print(ws.tail(20))
```

# Caveats

## 01 Period-keyed envelope — V2-FIX-02 handles it correctly

Live API returns `data[].regions[]`. `_rows_from_region_period` reads from whichever level holds the data. *(Source: vault Implementation Delta L118-119.)*

## 02 `actual_gco2_kwh` always null

Forecast horizon only. *(Source: `endpoints.py L221`.)*

## 03 Skill degrades with horizon

+48h skill is meaningfully worse than +24h — weather-driven renewable forecast attenuates. *(Source: domain knowledge — meteorology.)*

## 04 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L219`). *(Source: `endpoints.py L219`.)*

## 05 Transformer is dynamically generated

`RegionalIntensityFw48HTransformer` is created at import time via `type()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_intensity_fw24h`** — All-regions 24h forecast. `30 min`. Shorter horizon — compare for skill attenuation. *neso · regional forecast · 30 min*
- **`regional_intensity_pt24h`** — Past-24h actuals · all-regions. `30 min`. Mirror window for forecast-skill calculation. *neso · regional intensity · 30 min*
- **`regional_intensity_fw48h_postcode`** — Single-postcode 48h forecast. `30 min`. Postcode-scoped version. *neso · regional forecast · 30 min*
- **`intensity_fw48h`** — National 48h forecast. `30 min`. National counterpart — pair to attribute the national forecast to regions. *neso · national forecast · 30 min*
