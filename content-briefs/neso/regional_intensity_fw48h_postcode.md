---
slug: regional_intensity_fw48h_postcode
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/intensity/fw48h/postcode
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_intensity_fw48h_postcode.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalIntensityFw48HPostcodeTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_intensity_fw48h_postcode"] (lines 224-231, path /regional/intensity/{from_dt}/fw48h/postcode/{postcode})
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Postcode intensity, <span class="italic fg-accent">48h forecast.</span>

**Lede:** Postcode-scoped carbon-intensity forecast 48 hours ahead — the canonical two-day carbon outlook for one UK outward postcode.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/intensity/{from}/fw48h/postcode/{postcode}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_intensity_fw48h_postcode` |
| API PATH | `/regional/intensity/{from}/fw48h/postcode/{postcode}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast horizon |
| VOLUME | ~96 SPs × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 48 h | Forecast horizon |
| 3 | 1 / call | Region per request |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_fw48h
- regional_intensity_fw48h_regionid
- regional_intensity_fw24h_postcode
- regional_intensity_pt24h_postcode
- regional_postcode

# Sample chart

- **Type:** `sparkline`
- **Title:** "Postcode 48h forecast"
- **Subtitle:** "Sparkline · gCO2/kWh · postcode RG10 · from 6 May 2026 00:00"
- **Seed:** 52
- **Toggles:** `48h` (active) / `24h`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc`. Region-keyed envelope. `actual_gco2_kwh` always null.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | DNO region serving this postcode. | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | The requested outward postcode. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | 48h-horizon forecast intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Always null. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_intensity_fw48h_postcode/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | postcode | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|---|
| 2026-05-07T12:00:00+00:00 | 12 | South England | RG41 | 82.0 | low | solar | 24.5 |
| 2026-05-07T18:00:00+00:00 | 12 | South England | RG41 | 235.0 | high | gas | 51.8 |
| **2026-05-08T12:30:00+00:00** | **12** | **South England** | **RG41** | **65.0** | **very low** | **solar** | **28.2** |
| 2026-05-08T18:00:00+00:00 | 12 | South England | RG41 | 245.0 | high | gas | 52.5 |
| 2026-05-08T23:30:00+00:00 | 12 | South England | RG41 | 218.0 | moderate | gas | 49.8 |

**Sources:** Five SPs across the 48h horizon for postcode `RG41`. Vault Silver sample shape; values plausible for southern-England DNO multi-day. Highlighted day-2 12:30 row at 65 gCO2/kWh / `very low` — the day-after-tomorrow's projected clean window; multi-day flexible-load planning (e.g. weekend EV charging).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/intensity/{from}/fw48h/postcode/{postcode}` (outward postcode only)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_intensity_fw48h_postcode/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalIntensityFw48HPostcodeTransformer` (dynamically generated; default postcode `RG10`)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/intensity/2026-05-07T00:00Z/fw48h/postcode/RG10
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Postcode 48h: weekend (Sat / Sun) cleanest forecast hour
SELECT extract('dow' FROM timestamp_utc) AS dow,
       min(forecast_gco2_kwh) AS min_g,
       arg_min(timestamp_utc, forecast_gco2_kwh) AS cleanest_sp
FROM read_parquet('data/silver/neso/regional_intensity_fw48h_postcode/**/*.parquet')
WHERE fuel = ''
  AND extract('dow' FROM timestamp_utc) IN (6, 0)
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_intensity_fw48h_postcode/**/*.parquet")
# Postcode 48h fuel-mix evolution
solar = (
    df.filter(pl.col("fuel") == "solar")
      .select(["timestamp_utc", "generation_percentage"])
      .sort("timestamp_utc")
)
print(solar.tail(20))
```

# Caveats

## 01 Outward postcode only

`{postcode}` accepts the outward part only (e.g. `RG10`). *(Source: NESO docs — postcode segment semantics.)*

## 02 `actual_gco2_kwh` always null

Forecast horizon only. *(Source: `endpoints.py L228`.)*

## 03 Skill degrades with horizon

+48h skill is meaningfully worse than +24h. *(Source: domain knowledge.)*

## 04 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L226`). *(Source: `endpoints.py L226`.)*

## 05 Transformer is dynamically generated

`RegionalIntensityFw48HPostcodeTransformer` is created at import time via `type()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_intensity_fw48h`** — All-regions 48h forecast. `30 min`. Returns this postcode's DNO embedded in 17-region output. *neso · regional forecast · 30 min*
- **`regional_intensity_fw48h_regionid`** — Same forecast keyed by regionid. `30 min`. Numeric-ID equivalent. *neso · regional forecast · 30 min*
- **`regional_intensity_fw24h_postcode`** — Same postcode · 24h horizon. `30 min`. Shorter horizon. *neso · regional forecast · 30 min*
- **`regional_postcode`** — Live snapshot · same postcode. `30 min`. Companion for "right now". *neso · regional intensity · 30 min*
