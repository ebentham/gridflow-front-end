---
slug: regional_intensity_regionid
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity/regionid
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_intensity_regionid.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityRegionidTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity_regionid"] (lines 278-285, path /regional/intensity/{from_dt}/{to_dt}/regionid/{regionid})
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** DNO region carbon intensity, <span class="italic fg-accent">range query.</span>

**Lede:** Regionid-scoped regional carbon intensity over a datetime range — the canonical historical series for one numeric-keyed DNO region.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/intensity/{from}/{to}/regionid/{regionid}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity_regionid` |
| API PATH | `/regional/intensity/{from}/{to}/regionid/{regionid}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | per period · actual rarely populated |
| VOLUME | 1 region × 48 SPs / day × N fuels |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 14 d | Max range per request |
| 3 | 1..17 | Region ID range |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_regionid
- regional_intensity_fw24h_regionid
- regional_intensity_pt24h_regionid
- regional_intensity
- regional_intensity_postcode

# Sample chart

- **Type:** `sparkline`
- **Title:** "DNO region carbon intensity · 7-day history"
- **Subtitle:** "Sparkline · gCO2/kWh · regionid 13 (London) · last 7 days"
- **Seed:** 47
- **Toggles:** `7d` (active) / `30d`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via the shared `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc` (year + month). Region-keyed envelope.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | NESO region identifier (1..17). | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Blank for regionid routes. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Regional forecast carbon intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Often null on regional endpoints. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_intensity_regionid/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| 2026-05-08T00:00:00+00:00 | 13 | London | 215.0 | moderate | gas | 48.4 |
| 2026-05-08T06:00:00+00:00 | 13 | London | 178.0 | moderate | gas | 41.2 |
| **2026-05-08T12:00:00+00:00** | **13** | **London** | **95.0** | **low** | **solar** | **22.1** |
| 2026-05-08T18:00:00+00:00 | 13 | London | 245.0 | high | gas | 55.8 |
| 2026-05-08T23:30:00+00:00 | 13 | London | 218.0 | moderate | gas | 49.2 |

**Sources:** Five SPs across one day for regionid=13 (UKPN London). Vault Silver sample shape; values plausible for London DNO with mid-day solar peak. Highlighted 12:00 row at 95 gCO2/kWh / `low` — London's diurnal carbon arc; midday solar drops intensity even in a gas-heavy region.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/{to}/regionid/{regionid}` (path segments; max 14-day range; regionid 1..17)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity_regionid/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityRegionidTransformer` (dynamically generated; default regionid `13`)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-08T00:00Z/2026-05-09T00:00Z/regionid/13
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Regionid-13 (London) day-of-week carbon profile
SELECT extract('dow' FROM timestamp_utc) AS dow,
       avg(forecast_gco2_kwh) AS mean_g
FROM read_parquet('data/silver/neso/regional_intensity_regionid/**/*.parquet')
WHERE regionid = 13
  AND fuel = ''
  AND timestamp_utc >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_intensity_regionid/**/*.parquet")
# Region-by-region cleanest 4h windows
wide = (
    df.filter(pl.col("fuel") == "")
      .sort("timestamp_utc")
      .with_columns(
          pl.col("forecast_gco2_kwh").rolling_mean(window_size=8).alias("mean_4h")
      )
      .group_by("regionid").agg(pl.col("mean_4h").min().alias("cleanest_4h_g"))
)
print(wide.sort("cleanest_4h_g"))
```

# Caveats

## 01 `regionid` range is 1..17

Valid IDs: 1..17. Out-of-range returns a vendor error. *(Source: `endpoints.py L14 DEFAULT_REGION_ID=13`.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L280`). *(Source: `endpoints.py L280`.)*

## 03 14-day max window per request

Connector chunks longer spans (`_MAX_DAYS_PER_REQUEST=14`). *(Source: `connectors/neso/carbon_intensity.py L21`.)*

## 04 Path placeholders `{from_dt}` / `{to_dt}` internally

Docs document `/regional/intensity/{from}/{to}/regionid/{regionid}`; connector templates as `{from_dt}` / `{to_dt}`. *(Source: vault Implementation Delta L106.)*

## 05 Transformer is dynamically generated

`RegionalIntensityRegionidTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_regionid`** — Live snapshot · same regionid. `30 min`. Live companion to this dataset's historical / range. *neso · regional intensity · 30 min*
- **`regional_intensity_fw24h_regionid`** — 24h forecast · same regionid. `30 min`. Day-ahead carbon for one DNO region. *neso · regional forecast · 30 min*
- **`regional_intensity_pt24h_regionid`** — Past-24h actuals · same regionid. `30 min`. Rolling look-back companion. *neso · regional intensity · 30 min*
- **`regional_intensity`** — All-regions range query. `30 min`. Returns regionid embedded in 17-region output. *neso · regional intensity · 30 min*
