---
slug: regional_intensity_fw24h_regionid
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity/fw24h/regionid
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_intensity_fw24h_regionid.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityFw24HRegionidTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity_fw24h_regionid"] (lines 209-216, path /regional/intensity/{from_dt}/fw24h/regionid/{regionid})
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** DNO region intensity, <span class="italic fg-accent">24h forecast.</span>

**Lede:** Regionid-scoped carbon-intensity forecast 24 hours ahead — the canonical day-ahead carbon outlook for one numeric-keyed GB DNO region.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/intensity/{from}/fw24h/regionid/{regionid}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity_fw24h_regionid` |
| API PATH | `/regional/intensity/{from}/fw24h/regionid/{regionid}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast horizon |
| VOLUME | ~48 SPs × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 24 h | Forecast horizon |
| 3 | 1..17 | Region ID range |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_fw24h
- regional_intensity_fw24h_postcode
- regional_regionid
- regional_intensity_fw48h_regionid
- regional_intensity_pt24h_regionid

# Sample chart

- **Type:** `sparkline`
- **Title:** "Regionid 24h forecast"
- **Subtitle:** "Sparkline · gCO2/kWh · regionid 13 (London) · from 6 May 2026 00:00"
- **Seed:** 50
- **Toggles:** `24h` (active) / `vs all-regions`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc`. Region-keyed envelope. `actual_gco2_kwh` always null (forecast-only).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | NESO region identifier (1..17). | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Blank for regionid routes. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | 24h-horizon forecast intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Always null. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_intensity_fw24h_regionid/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| 2026-05-07T00:00:00+00:00 | 13 | London | 198.0 | moderate | gas | 45.8 |
| 2026-05-07T06:00:00+00:00 | 13 | London | 162.0 | moderate | gas | 39.2 |
| **2026-05-07T12:00:00+00:00** | **13** | **London** | **88.0** | **low** | **solar** | **21.4** |
| 2026-05-07T18:00:00+00:00 | 13 | London | 248.0 | high | gas | 53.1 |
| 2026-05-07T23:30:00+00:00 | 13 | London | 215.0 | moderate | gas | 48.8 |

**Sources:** Five SPs across the 24h forecast window for regionid=13 (UKPN London). Vault Silver sample shape; values plausible for London DNO day-ahead. Highlighted 12:00 row at 88 gCO2/kWh — tomorrow's cleanest hour for London; differs from `regional_intensity_fw24h_postcode` by the join key (numeric ID rather than postcode).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/fw24h/regionid/{regionid}` (regionid 1..17)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity_fw24h_regionid/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityFw24HRegionidTransformer` (dynamically generated; default regionid `13`)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-07T00:00Z/fw24h/regionid/13
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Multi-region day-ahead comparison: cleanest forecast SP per region
SELECT regionid, shortname,
       min(forecast_gco2_kwh) AS min_g,
       arg_min(timestamp_utc, forecast_gco2_kwh) AS cleanest_sp
FROM read_parquet('data/silver/neso/regional_intensity_fw24h_regionid/**/*.parquet')
WHERE fuel = ''
GROUP BY 1, 2
ORDER BY min_g;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_intensity_fw24h_regionid/**/*.parquet")
# Per-regionid: peak-renewable forecast share over tomorrow
renewables = (
    df.filter(pl.col("fuel").is_in(["wind", "solar", "hydro"]))
      .group_by(["regionid", "timestamp_utc"])
      .agg(pl.col("generation_percentage").sum().alias("renewable_pct"))
      .group_by("regionid").agg(pl.col("renewable_pct").max().alias("peak_renew"))
      .sort("peak_renew", descending=True)
)
print(renewables.head())
```

# Caveats

## 01 `regionid` range is 1..17

Valid IDs: 1..17. *(Source: `endpoints.py L14 DEFAULT_REGION_ID=13`.)*

## 02 `actual_gco2_kwh` always null

Forecast horizon only. *(Source: `endpoints.py L214`.)*

## 03 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L211`). *(Source: `endpoints.py L211`.)*

## 04 Default regionid `13`

Connector default (`endpoints.py L215`). *(Source: `endpoints.py L14, L215`.)*

## 05 Transformer is dynamically generated

`RegionalIntensityFw24HRegionidTransformer` is created at import time via `type()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_intensity_fw24h`** — All-regions 24h forecast. `30 min`. Returns this regionid embedded in 17-region output. *neso · regional forecast · 30 min*
- **`regional_intensity_fw24h_postcode`** — Same forecast keyed by postcode. `30 min`. Equivalent — use whichever join key you have. *neso · regional forecast · 30 min*
- **`regional_intensity_fw48h_regionid`** — Same regionid · 48h horizon. `30 min`. Longer outlook for the same DNO. *neso · regional forecast · 30 min*
- **`regional_regionid`** — Live snapshot · same regionid. `30 min`. Companion for "right now". *neso · regional intensity · 30 min*
