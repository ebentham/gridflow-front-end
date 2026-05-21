---
slug: regional_scotland
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/scotland
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_scotland.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalScotlandTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_scotland"] (lines 168-173, path /regional/scotland)
  - .planning/reconciliation/neso/01-regional-scotland-transient-curl-failure.md (closed 2026-05-19 — transient DNS, not dataset behavior)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Scotland carbon intensity, <span class="italic fg-accent">live half-hour.</span>

**Lede:** Current carbon intensity and generation mix for Scotland (regionid 16) — the canonical live country-level snapshot for Scotland's wind-dominated low-carbon grid.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/scotland](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_scotland` |
| API PATH | `/regional/scotland` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast ahead · actual rarely populated |
| VOLUME | 1 region × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 16 | NESO regionid (Scotland) |
| 3 | beta | NESO API status |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_england
- regional_wales
- regional_current
- regional_postcode
- regional_intensity

# Sample chart

- **Type:** `donut`
- **Title:** "Scotland generation mix · live"
- **Subtitle:** "Donut · percent share · regionid 16 · UTC · 6 May 2026"
- **Seed:** 41
- **Toggles:** `now` (active) / `vs England`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via the shared `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc` (year + month). Region-keyed envelope.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | Always `16` for this endpoint. | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | Always `Scotland`. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Always `Scotland`. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Blank for country routes. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Regional forecast carbon intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Often null on regional endpoints. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_scotland/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| 2026-05-08T17:30:00+00:00 | 16 | Scotland | 0.0 | very low | nuclear | 17.5 |
| **2026-05-08T17:30:00+00:00** | **16** | **Scotland** | **0.0** | **very low** | **wind** | **78.5** |
| 2026-05-08T17:30:00+00:00 | 16 | Scotland | 0.0 | very low | hydro | 3.2 |
| 2026-05-08T17:30:00+00:00 | 16 | Scotland | 0.0 | very low | gas | 0.8 |
| 2026-05-08T17:30:00+00:00 | 16 | Scotland | 0.0 | very low | imports | 0.0 |

**Sources:** Five rows for the single SP at 17:30 UTC. Vault Bronze sample L59 supplies `nuclear=17.5`, `wind=78.5`; remaining fuels synthesised to fill the mix (small gas / hydro / no imports — typical for a windy Scotland evening). Highlighted `wind=78.5%` row illustrates Scotland's defining renewable profile — at peak wind, intensity collapses to 0 gCO2/kWh (`very low`), exporting clean power south.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/scotland` (no path params — single-country route)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_scotland/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalScotlandTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/scotland
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Scotland wind dominance: hours with wind share >= 70% over the last 7 days
SELECT timestamp_utc, generation_percentage, forecast_gco2_kwh, intensity_index
FROM read_parquet('data/silver/neso/regional_scotland/**/*.parquet')
WHERE fuel = 'wind'
  AND generation_percentage >= 70
  AND timestamp_utc >= current_date - INTERVAL 7 DAY
ORDER BY timestamp_utc DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

sc = pl.read_parquet("data/silver/neso/regional_scotland/**/*.parquet")
# Hour-of-day mean wind share — diurnal wind feature
diurnal = (
    sc.filter(pl.col("fuel") == "wind")
      .with_columns(pl.col("timestamp_utc").dt.hour().alias("hod"))
      .group_by("hod").agg(pl.col("generation_percentage").mean().alias("mean_wind"))
      .sort("hod")
)
print(diurnal)
```

# Caveats

## 01 Region-keyed envelope (shared transformer with regional_wales)

Functionally identical to `regional_wales` — same `RegionalIntensity` schema, same `_transform_regional` path, only `regionid` differs (Scotland=16, Wales=17). *(Source: `endpoints.py L168-173`, L174-179; `silver/neso/carbon_intensity.py L400-445`.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L170`). *(Source: `endpoints.py L170`.)*

## 03 `regionid` always 16

Scotland carries `regionid=16`. *(Source: vault Bronze Sample L59.)*

## 04 Transformer is dynamically generated

`RegionalScotlandTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_wales`** — Wales country snapshot (regionid 17). `30 min`. Sibling country — same shape, gas-dominated vs Scotland's wind. *neso · regional intensity · 30 min*
- **`regional_england`** — England country snapshot (regionid 15). `30 min`. Third country view; nuclear-baseload contrast. *neso · regional intensity · 30 min*
- **`regional_current`** — All ~17 DNO regions at once. `30 min`. Returns Scotland embedded as one of 17 regions. *neso · regional intensity · 30 min*
- **`regional_intensity`** — Range query · all regions. `30 min`. Historical analysis at the same regionid=16 grain. *neso · regional intensity · 30 min*
