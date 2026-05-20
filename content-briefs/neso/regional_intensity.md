---
slug: regional_intensity
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity
last_verified: 2026-05-09
sources_consulted:
  - vault/neso/regional_intensity.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::_rows_from_region_period (lines 252-286 — V2-FIX-02 dual-shape handling)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity"] (lines 263-269, path /regional/intensity/{from_dt}/{to_dt})
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** All GB regions, <span class="italic fg-accent">range query.</span>

**Lede:** Regional carbon intensity and generation mix for all ~17 GB DNO regions over a datetime range — the canonical historical series for spatial carbon backtests.

**Verified line:** Verified against vendor docs: 2026-05-09 · [NESO Carbon Intensity · /regional/intensity/{from}/{to}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity` |
| API PATH | `/regional/intensity/{from}/{to}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | per period · actual rarely populated |
| VOLUME | ~17 × 48 / day × N fuels |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 14 d | Max range per request |
| 3 | 17 | GB DNO regions per call |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_postcode
- regional_intensity_regionid
- regional_intensity_fw24h
- regional_intensity_pt24h
- regional_current

# Sample chart

- **Type:** `heatmap`
- **Title:** "Regional GB carbon intensity · 24h × 17 regions"
- **Subtitle:** "Heatmap · gCO2/kWh · UTC · 6 May 2026"
- **Seed:** 45
- **Toggles:** `24h` (active) / `7d` / `30d`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via the shared `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc` (year + month). Uses the **period-keyed envelope** — `_rows_from_region_period` reads `intensity` / `generationmix` from whichever level holds the data (V2-FIX-02, see Caveats #01).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | NESO region identifier (1..17). | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Blank for all-regions calls. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Regional forecast carbon intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Often null on regional endpoints. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_intensity/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last (`silver/neso/carbon_intensity.py L425-428`)

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| 2026-05-08T17:30:00+00:00 | 1 | North Scotland | 0.0 | very low | wind | 78.3 |
| **2026-05-08T17:30:00+00:00** | **13** | **London** | **185.0** | **high** | **gas** | **42.4** |
| 2026-05-08T17:30:00+00:00 | 16 | Scotland | 12.0 | very low | wind | 78.5 |
| 2026-05-08T17:30:00+00:00 | 17 | Wales | 347.0 | very high | gas | 88.0 |
| 2026-05-08T18:00:00+00:00 | 1 | North Scotland | 0.0 | very low | wind | 80.1 |
| 2026-05-08T18:00:00+00:00 | 13 | London | 195.0 | high | gas | 44.2 |

**Sources:** Six rows showing 4 contrasting regions across 2 SPs (vault Bronze sample at L61 supplies the regions[]-list shape; per-region fuel mix synthesised from siblings). The full call returns ~17 regions × N fuels per SP × N SPs in the requested range. Highlighted London row at 185 gCO2/kWh — the canonical inter-region spread (North Scotland at 0, London at 185, Wales at 347 in the same SP) is the dataset's defining feature.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/{to}` (path segments; max 14-day range)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-08T00:00Z/2026-05-09T00:00Z
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Inter-region spread per SP: cleanest minus dirtiest region
WITH summary AS (
  SELECT timestamp_utc,
         min(forecast_gco2_kwh) AS min_g,
         max(forecast_gco2_kwh) AS max_g
  FROM read_parquet('data/silver/neso/regional_intensity/**/*.parquet')
  WHERE fuel = ''
  GROUP BY 1
)
SELECT timestamp_utc, max_g - min_g AS spread_g
FROM summary
ORDER BY spread_g DESC
LIMIT 10;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_intensity/**/*.parquet")
# Region rankings: cleanest day on record per region
cleanest = (
    df.filter(pl.col("fuel") == "")
      .with_columns(pl.col("timestamp_utc").dt.date().alias("day"))
      .group_by(["shortname", "day"]).agg(pl.col("forecast_gco2_kwh").mean().alias("mean_g"))
      .sort("mean_g")
      .group_by("shortname").first()
)
print(cleanest)
```

# Caveats

## 01 Period-keyed envelope — V2-FIX-02 handles it correctly

Live API returns `data[].regions[]` (period-keyed). `_rows_from_region_period` (`silver/neso/carbon_intensity.py L252-286`) reads from whichever level holds the data. Pre-V2 silver carried null carbon/mix; re-run silver from bronze if your tables predate 2026-05-09. *(Source: vault Implementation Delta L119; vault Changelog L125.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L265`). *(Source: `endpoints.py L265`.)*

## 03 14-day max window per request

Connector chunks longer spans (`_MAX_DAYS_PER_REQUEST=14`). High row counts — plan storage accordingly (~17 regions × 48 SPs × N fuels × N days). *(Source: `connectors/neso/carbon_intensity.py L21`.)*

## 04 Path placeholder `{from_dt}` / `{to_dt}` internally

Docs document `/regional/intensity/{from}/{to}`; connector templates as `{from_dt}` / `{to_dt}`. *(Source: vault Implementation Delta L117.)*

## 05 Transformer is dynamically generated

`RegionalIntensityTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_current`** — Live snapshot · all regions. `30 min`. Live companion to this dataset's historical / range. *neso · regional intensity · 30 min*
- **`regional_intensity_postcode`** — Range query · single postcode. `30 min`. Postcode-scoped version of this dataset. *neso · regional intensity · 30 min*
- **`regional_intensity_regionid`** — Range query · single regionid. `30 min`. Regionid-scoped version. *neso · regional intensity · 30 min*
- **`carbon_intensity`** — National range query. `30 min`. National counterpart — pair to attribute national intensity to regions. *neso · national intensity · 30 min*
