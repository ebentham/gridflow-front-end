---
slug: regional_intensity_pt24h
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity/pt24h
last_verified: 2026-05-09
sources_consulted:
  - vault/neso/regional_intensity_pt24h.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityPt24HTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::_rows_from_region_period (lines 252-286 — V2-FIX-02 dual-shape handling)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity_pt24h"] (lines 240-246, path /regional/intensity/{from_dt}/pt24h)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** All GB regions, <span class="italic fg-accent">past 24 hours.</span>

**Lede:** Regional carbon intensity for all ~17 GB DNO regions over the prior 24 hours — the canonical spatial look-back series for forecast-skill scoring and recent-history backtests.

**Verified line:** Verified against vendor docs: 2026-05-09 · [NESO Carbon Intensity · /regional/intensity/{from}/pt24h](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity_pt24h` |
| API PATH | `/regional/intensity/{from}/pt24h` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | post-period (look-back) |
| VOLUME | ~17 × 48 × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 24 h | Look-back horizon |
| 3 | 17 | GB DNO regions per call |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_pt24h_postcode
- regional_intensity_pt24h_regionid
- regional_intensity_fw24h
- regional_intensity
- regional_current

# Sample chart

- **Type:** `heatmap`
- **Title:** "Regional past-24h intensity · 17 regions"
- **Subtitle:** "Heatmap · gCO2/kWh · ending 6 May 2026 00:00"
- **Seed:** 54
- **Toggles:** `24h` (active) / `vs fw24h`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc`. Uses the **period-keyed envelope** — `_rows_from_region_period` handles dual-shape (V2-FIX-02).

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

**PARQUET PATH:** `data/silver/neso/regional_intensity_pt24h/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| 2026-05-05T00:00:00+00:00 | 1 | North Scotland | 0.0 | very low | wind | 79.4 |
| 2026-05-05T00:00:00+00:00 | 13 | London | 195.0 | moderate | gas | 45.4 |
| **2026-05-05T12:00:00+00:00** | **13** | **London** | **88.0** | **low** | **solar** | **22.8** |
| 2026-05-05T12:00:00+00:00 | 17 | Wales | 295.0 | very high | gas | 78.2 |
| 2026-05-05T18:00:00+00:00 | 1 | North Scotland | 5.0 | very low | wind | 80.2 |
| 2026-05-05T23:30:00+00:00 | 13 | London | 215.0 | moderate | gas | 49.4 |

**Sources:** Six rows across the 24h look-back ending 2026-05-06 00:00Z for 4 contrasting regions (vault Silver sample shape). Highlighted London 12:00 row at 88 gCO2/kWh — paired with `regional_intensity_fw24h` from the prior day's forecast, this is the canonical input to a per-region forecast-skill calculation.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/pt24h`
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity_pt24h/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityPt24HTransformer` (dynamically generated)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-06T00:00Z/pt24h
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Per-region forecast skill over the past 24h (where actuals populated)
WITH a AS (
  SELECT regionid, timestamp_utc, forecast_gco2_kwh AS actual_g
  FROM read_parquet('data/silver/neso/regional_intensity_pt24h/**/*.parquet')
  WHERE fuel = ''
),
f AS (
  SELECT regionid, timestamp_utc, forecast_gco2_kwh AS forecast_g
  FROM read_parquet('data/silver/neso/regional_intensity_fw24h/**/*.parquet')
  WHERE fuel = ''
)
SELECT a.regionid, avg(abs(f.forecast_g - a.actual_g)) AS mae_g
FROM a JOIN f USING (regionid, timestamp_utc)
GROUP BY 1
ORDER BY mae_g;
```

**Tab 3 — Python · polars**
```python
import polars as pl

pt = pl.read_parquet("data/silver/neso/regional_intensity_pt24h/**/*.parquet")
# Per-region cleanest 4h window over the past 24h
clean = (
    pt.filter(pl.col("fuel") == "")
      .sort("timestamp_utc")
      .with_columns(
          pl.col("forecast_gco2_kwh").rolling_mean(window_size=8).over("regionid").alias("mean_4h")
      )
      .group_by("regionid").agg(pl.col("mean_4h").min().alias("cleanest_4h_g"))
      .sort("cleanest_4h_g")
)
print(clean.head())
```

# Caveats

## 01 Period-keyed envelope — V2-FIX-02 handles it correctly

Live API returns `data[].regions[]`. `_rows_from_region_period` reads from whichever level holds the data. *(Source: vault Implementation Delta L118-119.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L242`). *(Source: `endpoints.py L242`.)*

## 03 `actual_gco2_kwh` often absent

Regional endpoints rarely publish actuals — forecast field is the primary read. *(Source: vault Implementation Delta L117.)*

## 04 High row count — plan storage

~17 regions × 48 SPs × ~10 fuels ≈ 8000 rows per call. *(Source: live verification — `regional_intensity` family parity.)*

## 05 Transformer is dynamically generated

`RegionalIntensityPt24HTransformer` is created at import time via `type()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_intensity_fw24h`** — All-regions 24h forecast. `30 min`. Mirror window for forecast-skill calculation. *neso · regional forecast · 30 min*
- **`regional_intensity`** — Range query · all regions. `30 min`. Use for arbitrary spans; this dataset for a fixed-24h tail. *neso · regional intensity · 30 min*
- **`regional_intensity_pt24h_postcode`** — Single-postcode past-24h. `30 min`. Postcode-scoped version. *neso · regional intensity · 30 min*
- **`intensity_pt24h`** — National past-24h actuals. `30 min`. National counterpart — pair to attribute national actual to regions. *neso · national intensity · 30 min*
