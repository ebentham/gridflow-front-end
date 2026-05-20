---
slug: regional_england
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/england
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_england.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalEnglandTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_england"] (lines 162-167, path /regional/england)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** England carbon intensity, <span class="italic fg-accent">live half-hour.</span>

**Lede:** Current carbon intensity and generation mix for England (regionid 15) — the canonical live country-level snapshot for England-vs-rest-of-GB carbon comparisons.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/england](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_england` |
| API PATH | `/regional/england` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast ahead · actual rarely populated |
| VOLUME | 1 region × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 15 | NESO regionid (England) |
| 3 | beta | NESO API status |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_scotland
- regional_wales
- regional_current
- regional_postcode
- regional_intensity

# Sample chart

- **Type:** `donut`
- **Title:** "England generation mix · live"
- **Subtitle:** "Donut · percent share · regionid 15 · UTC · 6 May 2026"
- **Seed:** 40
- **Toggles:** `now` (active) / `vs Scotland`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via the shared `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc` (year + month). Uses the **region-keyed envelope** — `regions[]` carries the region object with nested `data[]` of period rows.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | Always `15` for this endpoint. | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | Always `England`. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Always `England`. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Blank for country routes. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Regional forecast carbon intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Often null on regional endpoints. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_england/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| 2026-05-08T17:30:00+00:00 | 15 | England | 182.0 | high | biomass | 9.0 |
| 2026-05-08T17:30:00+00:00 | 15 | England | 182.0 | high | gas | 48.2 |
| **2026-05-08T17:30:00+00:00** | **15** | **England** | **182.0** | **high** | **nuclear** | **12.1** |
| 2026-05-08T17:30:00+00:00 | 15 | England | 182.0 | high | solar | 5.4 |
| 2026-05-08T17:30:00+00:00 | 15 | England | 182.0 | high | wind | 16.8 |
| 2026-05-08T17:30:00+00:00 | 15 | England | 182.0 | high | imports | 8.5 |

**Sources:** Six fuel rows for the single SP at 17:30 UTC (vault Bronze sample L59 supplies `biomass=9`, `coal=0`; remaining fuels synthesised to fill the mix). Highlighted `nuclear` row at 12.1% — England's nuclear fleet (Hinkley Point B / Heysham / Sizewell B) contributes baseload share absent from Scotland (which has no operational nuclear) and Wales (gas-dominated).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/england` (no path params — single-country route)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_england/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalEnglandTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/england
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Country-spread: England vs Scotland vs Wales at the latest SP
WITH e AS (SELECT * FROM read_parquet('data/silver/neso/regional_england/**/*.parquet')),
     s AS (SELECT * FROM read_parquet('data/silver/neso/regional_scotland/**/*.parquet')),
     w AS (SELECT * FROM read_parquet('data/silver/neso/regional_wales/**/*.parquet'))
SELECT shortname, forecast_gco2_kwh, intensity_index
FROM (SELECT * FROM e UNION ALL SELECT * FROM s UNION ALL SELECT * FROM w)
WHERE timestamp_utc = (SELECT max(timestamp_utc) FROM e)
  AND fuel = ''
ORDER BY forecast_gco2_kwh;
```

**Tab 3 — Python · polars**
```python
import polars as pl

en = pl.read_parquet("data/silver/neso/regional_england/**/*.parquet")
# Nuclear share trend for England — baseload feature
nuke = (
    en.filter(pl.col("fuel") == "nuclear")
      .select(["timestamp_utc", "generation_percentage"])
      .sort("timestamp_utc")
)
print(nuke.tail(48))
```

# Caveats

## 01 Region-keyed envelope (not period-keyed)

Country routes return `data[]` of region objects with nested `data[]` of period rows. `_rows_from_region_period` handles both shapes; the dual-shape V2-FIX-02 applies to all-regions siblings, not this single-region route. *(Source: vault Bronze Sample L55-57.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L164`). *(Source: `endpoints.py L164`.)*

## 03 `regionid` always 15

England carries `regionid=15`. Useful for joining to a multi-region table where you need to disambiguate. *(Source: vault Bronze Sample L59.)*

## 04 Transformer is dynamically generated

`RegionalEnglandTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_scotland`** — Scotland country snapshot (regionid 16). `30 min`. Companion country view; contrasts wind-dominated Scotland vs gas-heavy England. *neso · regional intensity · 30 min*
- **`regional_wales`** — Wales country snapshot (regionid 17). `30 min`. Third country view; complete the country triad. *neso · regional intensity · 30 min*
- **`regional_current`** — All ~17 regions at once. `30 min`. Returns England embedded in the full DNO list. *neso · regional intensity · 30 min*
- **`regional_intensity`** — Range query · all regions. `30 min`. Use for historical analysis; this dataset for live snapshots. *neso · regional intensity · 30 min*
