---
slug: regional_current
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional
last_verified: 2026-05-09
sources_consulted:
  - vault/neso/regional_current.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalCurrentTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::_rows_from_region_period (lines 252-286 — V2-FIX-02 dual-shape handling)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_current"] (lines 156-161, path /regional)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** All GB regions, <span class="italic fg-accent">live half-hour.</span>

**Lede:** Current regional carbon intensity and generation mix for all ~17 GB DNO regions — the canonical live snapshot for spatial carbon dashboards and per-region carbon-aware UI.

**Verified line:** Verified against vendor docs: 2026-05-09 · [NESO Carbon Intensity · /regional](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_current` |
| API PATH | `/regional` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast ahead · actual rarely populated |
| VOLUME | ~17 regions × N fuels |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 17 | GB DNO regions per call |
| 3 | beta | NESO API status |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity
- regional_england
- regional_scotland
- regional_wales
- regional_postcode

# Sample chart

- **Type:** `barsH`
- **Title:** "Regional GB carbon intensity · live"
- **Subtitle:** "Horizontal bars · gCO2/kWh · ~17 DNO regions · UTC · 6 May 2026"
- **Seed:** 39
- **Toggles:** `now` (active) / `24h ago`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73, subclass of `_TimestampedNesoBase`). Transformed via the shared `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc` (year + month). This dataset uses the **period-keyed envelope** — `_rows_from_region_period` reads `intensity` / `generationmix` from whichever level (region or period) holds the data (V2-FIX-02, see Caveats #01).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | NESO region identifier (1..17). | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name (e.g. `Scottish Hydro Electric Power Distribution`). | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short label (e.g. `North Scotland`, `London`). | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Outward postcode if requested; blank for all-regions calls. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Regional forecast carbon intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Often absent from regional examples; nullable. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_current/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last (`silver/neso/carbon_intensity.py L425-428`)

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| 2026-05-08T17:30:00+00:00 | 1 | North Scotland | 0.0 | very low | wind | 78.3 |
| 2026-05-08T17:30:00+00:00 | 1 | North Scotland | 0.0 | very low | hydro | 12.1 |
| 2026-05-08T17:30:00+00:00 | 13 | London | 185.0 | high | gas | 42.4 |
| **2026-05-08T17:30:00+00:00** | **13** | **London** | **185.0** | **high** | **imports** | **23.2** |
| 2026-05-08T17:30:00+00:00 | 16 | Scotland | 12.0 | very low | wind | 78.5 |
| 2026-05-08T17:30:00+00:00 | 17 | Wales | 347.0 | very high | gas | 88.0 |

**Sources:** Six rows showing four contrasting regions for the same SP (vault Bronze sample at L60 — North Scotland, supplementary Scotland / Wales / London synthesised from sibling vaults: `regional_scotland.md` L59 regionid=16, `regional_wales.md` L59 regionid=17, `regional_regionid.md` L59 regionid=13). Highlighted London `imports` row at 23.2% illustrates the inter-region carbon spread — North Scotland is `very low` (wind-dominated) while Wales is `very high` (gas-dominated) at the same instant.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional` (no path params — returns all ~17 DNO regions)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_current/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalCurrentTransformer` (dynamically generated via `register_neso_transformers()` at L110-118)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Latest snapshot: per-region intensity, cleanest first
SELECT regionid, shortname, forecast_gco2_kwh, intensity_index
FROM read_parquet('data/silver/neso/regional_current/**/*.parquet')
WHERE timestamp_utc = (
  SELECT max(timestamp_utc) FROM read_parquet('data/silver/neso/regional_current/**/*.parquet')
)
GROUP BY 1, 2, 3, 4
ORDER BY forecast_gco2_kwh;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_current/**/*.parquet")
# Regional spread: latest cleanest vs dirtiest region
latest = (
    df.sort("timestamp_utc", descending=True)
      .group_by(["regionid", "shortname"]).first()
      .sort("forecast_gco2_kwh")
)
print(latest.head(3))   # cleanest
print(latest.tail(3))   # dirtiest
```

# Caveats

## 01 Period-keyed envelope — V2-FIX-02 handles it correctly

The live API returns `data[].regions[]` (period-keyed), with `intensity` / `generationmix` on each region. `_rows_from_region_period` (`silver/neso/carbon_intensity.py L252-286`) reads from whichever level holds the data — region-keyed siblings continue to work unchanged. Pre-V2 silver tables for this dataset carried null carbon/mix and required re-running silver from bronze. *(Source: vault Implementation Delta L118-119; vault Changelog L124.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L158`); subject to vendor changes without notice. *(Source: `endpoints.py L158`.)*

## 03 `actual_gco2_kwh` often absent

Regional API examples publish forecast and index but rarely actual. Treat null as expected, not a publishing delay. *(Source: vault Implementation Delta L117.)*

## 04 One row per (region × fuel) — long shape

Each region contributes `~N fuel rows` to silver. ~17 regions × ~10 fuels ≈ 170 rows per call. *(Source: `silver/neso/carbon_intensity.py L425-428`.)*

## 05 Transformer is dynamically generated

`RegionalCurrentTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_intensity`** — Range query · same schema. `30 min`. Use for historical / multi-period; this dataset for "right now". *neso · regional intensity · 30 min*
- **`regional_england`** — Single-region snapshot for England. `30 min`. Equivalent shape, narrower scope (one region per call). *neso · regional intensity · 30 min*
- **`regional_postcode`** — Single-region snapshot by postcode. `30 min`. Postcode-scoped version of this all-regions dataset. *neso · regional intensity · 30 min*
- **`intensity_current`** — National live snapshot · gCO2/kWh. `30 min`. National counterpart — pair to show "GB-wide vs per-region". *neso · national intensity · 30 min*
