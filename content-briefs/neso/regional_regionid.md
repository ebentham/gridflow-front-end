---
slug: regional_regionid
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/regionid
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_regionid.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalRegionidTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_regionid"] (lines 187-193, path /regional/regionid/{regionid}, default regionid=13)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** DNO region carbon intensity, <span class="italic fg-accent">live half-hour.</span>

**Lede:** Current carbon intensity and generation mix for a single GB DNO region by ID — the canonical numeric-keyed regional snapshot for stable region joins.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/regionid/{regionid}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_regionid` |
| API PATH | `/regional/regionid/{regionid}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast ahead · actual rarely populated |
| VOLUME | 1 region × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 1 / call | Region per request |
| 3 | 1..17 | Region ID range |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_regionid
- regional_postcode
- regional_current
- regional_intensity_fw24h_regionid
- regional_intensity_pt24h_regionid

# Sample chart

- **Type:** `donut`
- **Title:** "DNO region · generation mix · live"
- **Subtitle:** "Donut · percent share · regionid 13 (London) · UTC · 6 May 2026"
- **Seed:** 44
- **Toggles:** `now` (active) / `regionid 1 (N Scot)`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via the shared `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc` (year + month). Region-keyed envelope.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | NESO region identifier (1..17). Path-parameter echo. | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | Blank for regionid routes. | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Regional forecast carbon intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Often null on regional endpoints. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_regionid/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|
| **2026-05-08T17:30:00+00:00** | **13** | **London** | **185.0** | **high** | **gas** | **42.4** |
| 2026-05-08T17:30:00+00:00 | 13 | London | 185.0 | high | imports | 23.2 |
| 2026-05-08T17:30:00+00:00 | 13 | London | 185.0 | high | nuclear | 11.8 |
| 2026-05-08T17:30:00+00:00 | 13 | London | 185.0 | high | wind | 9.4 |
| 2026-05-08T17:30:00+00:00 | 13 | London | 185.0 | high | solar | 6.5 |
| 2026-05-08T17:30:00+00:00 | 13 | London | 185.0 | high | biomass | 4.2 |

**Sources:** Six fuel rows for regionid=13 (UKPN London) at 17:30 UTC. Vault Bronze sample L59 supplies `gas=42.4`, `imports=23.2`; remaining fuels synthesised. Highlighted `gas=42.4%` row — London's gas dependency drives moderate-to-high intensity at evening peak. Compare regionid=1 (North Scotland, see `regional_scotland`) which would show wind-dominated `very low` at the same SP.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/regionid/{regionid}` (path param `{regionid}` = 1..17, e.g. `13` for London)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_regionid/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalRegionidTransformer` (dynamically generated via `register_neso_transformers()` at L110-118; default regionid `13`)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/regionid/13
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Region 13 (London) hour-of-day intensity profile
SELECT extract('hour' FROM timestamp_utc) AS hod,
       avg(forecast_gco2_kwh) AS mean_g
FROM read_parquet('data/silver/neso/regional_regionid/**/*.parquet')
WHERE regionid = 13
  AND fuel = ''
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_regionid/**/*.parquet")
# Per-region fuel-share latest snapshot
latest = (
    df.sort("timestamp_utc", descending=True)
      .group_by(["regionid", "fuel"]).first()
      .filter(pl.col("fuel") != "")
      .pivot(index="regionid", on="fuel", values="generation_percentage", aggregate_function="sum")
)
print(latest)
```

# Caveats

## 01 `regionid` range is 1..17

Valid IDs: 1 (North Scotland) … 17 (Wales). Out-of-range IDs return a vendor error. *(Source: vault Query parameters L35; `endpoints.py L14 DEFAULT_REGION_ID=13`.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L189`). *(Source: `endpoints.py L189`.)*

## 03 Default regionid `13` (UKPN London)

If the connector is called without a `regionid` override, it uses `DEFAULT_REGION_ID = 13` (`endpoints.py L14`). *(Source: `endpoints.py L14, L192`.)*

## 04 Numeric ID preferred over postcode for stable joins

Postcode → regionid mapping is vendor-managed and may change at DNO boundary revisions. Use `regional_regionid` for long-term backtests; `regional_postcode` for consumer UI. *(Source: NESO methodology.)*

## 05 Transformer is dynamically generated

`RegionalRegionidTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_postcode`** — Same single-region snapshot keyed by outward postcode. `30 min`. Equivalent — use whichever join key you have. *neso · regional intensity · 30 min*
- **`regional_intensity_regionid`** — Range query · same regionid shape. `30 min`. Historical analysis for one DNO region. *neso · regional intensity · 30 min*
- **`regional_intensity_fw24h_regionid`** — 24h forecast · same regionid shape. `30 min`. Day-ahead carbon for one DNO region. *neso · regional forecast · 30 min*
- **`regional_current`** — All ~17 regions · same SP. `30 min`. Pre-fetched all-regions view if you query many regionids in sequence. *neso · regional intensity · 30 min*
