---
slug: regional_intensity_fw24h
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity/fw24h
last_verified: 2026-05-09
sources_consulted:
  - vault/neso/regional_intensity_fw24h.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityFw24HTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::_rows_from_region_period (lines 252-286 — V2-FIX-02 dual-shape handling)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity_fw24h"] (lines 194-200, path /regional/intensity/{from_dt}/fw24h)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Regional intensity, <span class="italic fg-accent">24h forecast.</span>

**Lede:** Regional carbon-intensity forecast for all ~17 GB DNO regions, 24 hours ahead — the canonical day-ahead spatial forecast for inter-region carbon arbitrage.

**Verified line:** Verified against vendor docs: 2026-05-09 · [NESO Carbon Intensity · /regional/intensity/{from}/fw24h](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity_fw24h` |
| API PATH | `/regional/intensity/{from}/fw24h` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast horizon |
| VOLUME | ~17 × 48 × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 24 h | Forecast horizon |
| 3 | 17 | GB DNO regions per call |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_fw24h_postcode
- regional_intensity_fw24h_regionid
- regional_intensity_fw48h
- regional_intensity
- intensity_fw24h

# Sample chart

- **Type:** `heatmap`
- **Title:** "Regional 24h forecast · 17 regions"
- **Subtitle:** "Heatmap · gCO2/kWh · from 6 May 2026 00:00 · forward 24h"
- **Seed:** 48
- **Toggles:** `24h` (active) / `vs actuals`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc`. Uses the **period-keyed envelope** — `_rows_from_region_period` reads from whichever level holds the data (V2-FIX-02, see Caveats #01). `actual_gco2_kwh` always null (forecast-only).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | NESO region identifier (1..17). | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Blank for all-regions calls. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | 24h-horizon forecast intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Always null (forecast horizon). | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_intensity_fw24h/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | actual_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|---|
| 2026-05-07T00:00:00+00:00 | 1 | North Scotland | 5.0 | _null_ | very low | wind | 76.2 |
| **2026-05-07T12:00:00+00:00** | **13** | **London** | **78.0** | **_null_** | **low** | **solar** | **23.1** |
| 2026-05-07T12:00:00+00:00 | 16 | Scotland | 8.0 | _null_ | very low | wind | 75.4 |
| 2026-05-07T12:00:00+00:00 | 17 | Wales | 295.0 | _null_ | very high | gas | 78.5 |
| 2026-05-07T18:00:00+00:00 | 13 | London | 245.0 | _null_ | high | gas | 52.4 |

**Sources:** Five rows across the 24h forecast window for 4 contrasting regions (vault Silver sample shape; values consistent with V2-validated 7938 silver rows from `/regional/intensity/2026-05-09T00:00Z/fw24h`). Highlighted London 12:00 row at `low` (78 gCO2/kWh) — the dataset's value-proposition: identifies tomorrow's cleanest hours per region for inter-region load shifting.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/fw24h` (path param `{from}` in ISO-8601 `YYYY-MM-DDThh:mmZ`)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity_fw24h/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityFw24HTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-07T00:00Z/fw24h
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Day-ahead cleanest region per SP — inter-region carbon arbitrage
SELECT timestamp_utc,
       arg_min(shortname, forecast_gco2_kwh) AS cleanest_region,
       min(forecast_gco2_kwh) AS min_g
FROM read_parquet('data/silver/neso/regional_intensity_fw24h/**/*.parquet')
WHERE fuel = ''
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_intensity_fw24h/**/*.parquet")
# Forecast inter-region spread evolution
spread = (
    df.filter(pl.col("fuel") == "")
      .group_by("timestamp_utc")
      .agg(
          (pl.col("forecast_gco2_kwh").max() - pl.col("forecast_gco2_kwh").min())
          .alias("spread_g")
      )
      .sort("timestamp_utc")
)
print(spread.tail(10))
```

# Caveats

## 01 Period-keyed envelope — V2-FIX-02 handles it correctly

Live API returns `data[].regions[]` (period-keyed). `_rows_from_region_period` (`silver/neso/carbon_intensity.py L252-286`) reads from whichever level holds the data. Pre-V2 silver had null carbon/mix. *(Source: vault Changelog L124-125 (live re-validated 2026-05-09 with 7938 rows, 0% null).)*

## 02 `actual_gco2_kwh` always null

Forecast horizon only. Pair with `regional_intensity_pt24h` for after-the-fact actuals. *(Source: `endpoints.py L198`.)*

## 03 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L196`). *(Source: `endpoints.py L196`.)*

## 04 High row count — plan storage

~17 regions × 48 SPs × ~10 fuels ≈ 8000 rows per call. *(Source: live verification 2026-05-09: 7938 silver rows.)*

## 05 Transformer is dynamically generated

`RegionalIntensityFw24HTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_intensity_fw48h`** — 48h horizon · all-regions · same schema. `30 min`. Longer outlook at the same cadence. *neso · regional forecast · 30 min*
- **`regional_intensity_pt24h`** — Past-24h actuals · all-regions. `30 min`. Mirror window for forecast-skill calculation. *neso · regional intensity · 30 min*
- **`regional_intensity_fw24h_postcode`** — Single-postcode 24h forecast. `30 min`. Postcode-scoped version of this dataset. *neso · regional forecast · 30 min*
- **`intensity_fw24h`** — National 24h forecast. `30 min`. National counterpart — pair to attribute national forecast to regions. *neso · national forecast · 30 min*
