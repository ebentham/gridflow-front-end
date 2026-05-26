---
slug: regional_intensity_pt24h_postcode
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity/pt24h/postcode
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_intensity_pt24h_postcode.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityPt24HPostcodeTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity_pt24h_postcode"] (lines 247-254, path /regional/intensity/{from_dt}/pt24h/postcode/{postcode})
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Postcode intensity, <span class="italic fg-accent">past 24 hours.</span>

**Lede:** Postcode-scoped regional carbon intensity for the prior 24 hours — the canonical look-back series for one UK outward postcode for skill scoring and recent-history analysis.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/intensity/{from}/pt24h/postcode/{postcode}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity_pt24h_postcode` |
| API PATH | `/regional/intensity/{from}/pt24h/postcode/{postcode}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | post-period (look-back) |
| VOLUME | ~48 SPs × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 24 h | Look-back horizon |
| 3 | 1 / call | Region per request |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_pt24h
- regional_intensity_pt24h_regionid
- regional_intensity_fw24h_postcode
- regional_intensity_postcode
- regional_postcode

# Sample chart

- **Type:** `sparkline`
- **Title:** "Postcode past-24h intensity"
- **Subtitle:** "Sparkline · gCO2/kWh · postcode RG10 · ending 6 May 2026 00:00"
- **Seed:** 55
- **Toggles:** `24h` (active) / `vs fw24h`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc`. Region-keyed envelope.

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

**PARQUET PATH:** `data/silver/neso/regional_intensity_pt24h_postcode/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | postcode | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|---|
| 2026-05-05T00:00:00+00:00 | 12 | South England | RG41 | 218.0 | moderate | gas | 49.4 |
| 2026-05-05T06:00:00+00:00 | 12 | South England | RG41 | 165.0 | moderate | gas | 38.8 |
| **2026-05-05T12:00:00+00:00** | **12** | **South England** | **RG41** | **85.0** | **low** | **solar** | **23.4** |
| 2026-05-05T18:00:00+00:00 | 12 | South England | RG41 | 232.0 | high | gas | 51.5 |
| 2026-05-05T23:30:00+00:00 | 12 | South England | RG41 | 218.0 | moderate | gas | 49.6 |

**Sources:** Five SPs across the 24h look-back ending 2026-05-06 00:00Z for postcode RG41. Vault Silver sample shape; values plausible for southern-England DNO. Highlighted 12:00 row — yesterday's actual cleanest hour for that postcode.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/pt24h/postcode/{postcode}` (outward postcode only)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity_pt24h_postcode/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityPt24HPostcodeTransformer` (dynamically generated; default postcode `RG10`)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-06T00:00Z/pt24h/postcode/RG10
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Yesterday's cleanest postcode SP (intensity-only rows)
SELECT timestamp_utc, forecast_gco2_kwh, intensity_index
FROM read_parquet('data/silver/neso/regional_intensity_pt24h_postcode/**/*.parquet')
WHERE fuel = ''
ORDER BY forecast_gco2_kwh
LIMIT 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_intensity_pt24h_postcode/**/*.parquet")
# Postcode pt24h fuel-mix evolution — yesterday's solar curve
solar = (
    df.filter(pl.col("fuel") == "solar")
      .select(["timestamp_utc", "generation_percentage"])
      .sort("timestamp_utc")
)
print(solar)
```

# Caveats

## 01 Outward postcode only

`{postcode}` accepts the outward part only (e.g. `RG10`). *(Source: NESO docs.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L249`). *(Source: `endpoints.py L249`.)*

## 03 `actual_gco2_kwh` often absent

Regional endpoints rarely publish actuals. *(Source: vault Implementation Delta L116.)*

## 04 Window anchored to SP enclosing `{from}`

The 24h look-back ends at the SP containing `{from}`. *(Source: NESO docs.)*

## 05 Transformer is dynamically generated

`RegionalIntensityPt24HPostcodeTransformer` is created at import time via `type()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_intensity_pt24h`** — All-regions past-24h. `30 min`. Returns this postcode's DNO embedded in 17-region output. *neso · regional intensity · 30 min*
- **`regional_intensity_pt24h_regionid`** — Same look-back keyed by regionid. `30 min`. Numeric-ID equivalent. *neso · regional intensity · 30 min*
- **`regional_intensity_fw24h_postcode`** — Same postcode · 24h forecast. `30 min`. Mirror window for forecast-skill calculation. *neso · regional forecast · 30 min*
- **`regional_postcode`** — Live snapshot · same postcode. `30 min`. Companion for "right now". *neso · regional intensity · 30 min*
