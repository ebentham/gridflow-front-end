---
slug: regional_wales
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/wales
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_wales.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalWalesTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_wales"] (lines 174-179, path /regional/wales)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Wales carbon intensity, <span class="italic fg-accent">live half-hour.</span>

**Lede:** Current carbon intensity and generation mix for Wales (regionid 17) — the canonical live country-level snapshot for Wales's gas-dominated grid.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/wales](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_wales` |
| API PATH | `/regional/wales` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast ahead · actual rarely populated |
| VOLUME | 1 region × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 17 | NESO regionid (Wales) |
| 3 | beta | NESO API status |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_england
- regional_scotland
- regional_current
- regional_postcode
- regional_intensity

# Sample chart

- **Type:** `donut`
- **Title:** "Wales generation mix · live"
- **Subtitle:** "Donut · percent share · regionid 17 · UTC · 6 May 2026"
- **Seed:** 42
- **Toggles:** `now` (active) / `vs Scotland`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via the shared `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc` (year + month). Region-keyed envelope.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | Always `17` for this endpoint. | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | Always `Wales`. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Always `Wales`. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Blank for country routes. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Regional forecast carbon intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Often null on regional endpoints. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_wales/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| **2026-05-08T17:30:00+00:00** | **17** | **Wales** | **347.0** | **very high** | **gas** | **88.0** |
| 2026-05-08T17:30:00+00:00 | 17 | Wales | 347.0 | very high | solar | 7.4 |
| 2026-05-08T17:30:00+00:00 | 17 | Wales | 347.0 | very high | wind | 3.2 |
| 2026-05-08T17:30:00+00:00 | 17 | Wales | 347.0 | very high | imports | 1.0 |
| 2026-05-08T17:30:00+00:00 | 17 | Wales | 347.0 | very high | hydro | 0.4 |

**Sources:** Five fuel rows for the single SP at 17:30 UTC. Vault Bronze sample L59 supplies `gas=88`, `solar=7.4`; remaining fuels synthesised to complete a 100% mix. Highlighted `gas=88%` row illustrates Wales's defining gas dependency — Pembroke CCGT, Connah's Quay, and South Hook drive evening intensity to `very high` (347 gCO2/kWh) — the inverse of Scotland's wind-dominated profile.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/wales` (no path params — single-country route)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_wales/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalWalesTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/wales
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Wales gas share trend over 30 days
SELECT timestamp_utc::date AS day, avg(generation_percentage) AS mean_gas_pct
FROM read_parquet('data/silver/neso/regional_wales/**/*.parquet')
WHERE fuel = 'gas'
  AND timestamp_utc >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1 DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

w = pl.read_parquet("data/silver/neso/regional_wales/**/*.parquet")
s = pl.read_parquet("data/silver/neso/regional_scotland/**/*.parquet")
# Cross-country intensity spread: Wales vs Scotland same SP
spread = (
    w.filter(pl.col("fuel") == "").select(["timestamp_utc", "forecast_gco2_kwh"])
     .rename({"forecast_gco2_kwh": "wales_g"})
     .join(s.filter(pl.col("fuel") == "").select(["timestamp_utc", "forecast_gco2_kwh"])
              .rename({"forecast_gco2_kwh": "scot_g"}),
           on="timestamp_utc")
     .with_columns((pl.col("wales_g") - pl.col("scot_g")).alias("spread_g"))
)
print(spread.sort("spread_g", descending=True).head(5))
```

# Caveats

## 01 Region-keyed envelope (shared transformer with regional_scotland)

Functionally identical to `regional_scotland` — same `RegionalIntensity` schema, same `_transform_regional` path, only `regionid` differs (Wales=17, Scotland=16). *(Source: `endpoints.py L168-179`; `silver/neso/carbon_intensity.py L400-445`.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L176`). *(Source: `endpoints.py L176`.)*

## 03 `regionid` always 17

Wales carries `regionid=17`. *(Source: vault Bronze Sample L59.)*

## 04 Transformer is dynamically generated

`RegionalWalesTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_scotland`** — Scotland country snapshot (regionid 16). `30 min`. Sibling country — same shape, wind-dominated vs Wales's gas. *neso · regional intensity · 30 min*
- **`regional_england`** — England country snapshot (regionid 15). `30 min`. Third country view; nuclear-baseload contrast. *neso · regional intensity · 30 min*
- **`regional_current`** — All ~17 DNO regions at once. `30 min`. Returns Wales embedded as one of 17 regions. *neso · regional intensity · 30 min*
- **`regional_intensity`** — Range query · all regions. `30 min`. Historical analysis at the same regionid=17 grain. *neso · regional intensity · 30 min*
