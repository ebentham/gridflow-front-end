---
slug: regional_postcode
vendor: neso
vendor_label: NESO Carbon Intensity
api_code: regional/postcode
last_verified: 2026-05-08
sources_consulted:
  - vault/neso/regional_postcode.md
  - gridflow/src/gridflow/schemas/neso.py::RegionalIntensity (lines 62-73)
  - gridflow/src/gridflow/silver/neso/carbon_intensity.py::RegionalPostcodeTransformer (dynamically generated via register_neso_transformers L110-118; parser_family=REGIONAL)
  - gridflow/src/gridflow/connectors/neso/endpoints.py::ENDPOINTS["regional_postcode"] (lines 180-186, path /regional/postcode/{postcode}, default postcode=RG10)
  - https://carbon-intensity.github.io/api-definitions/ (official NESO API docs — Carbon Intensity - Regional **beta**)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Postcode carbon intensity, <span class="italic fg-accent">live half-hour.</span>

**Lede:** Current carbon intensity and generation mix for the DNO region serving a UK outward postcode — the canonical postcode-scoped snapshot for consumer-facing carbon-aware UI.

**Verified line:** Verified against vendor docs: 2026-05-08 · [NESO Carbon Intensity · /regional/postcode/{postcode}](https://carbon-intensity.github.io/api-definitions/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.regional_postcode` |
| API PATH | `/regional/postcode/{postcode}` |
| FREQUENCY | 30 min (settlement period) |
| PUBLICATION LAG | forecast ahead · actual rarely populated |
| VOLUME | 1 region × N fuels per call |
| PRIMARY KEY | `(timestamp_utc, regionid, shortname, postcode, fuel)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 30 min | Settlement period cadence |
| 2 | 1 / call | Region per request |
| 3 | outward | Postcode granularity (e.g. `RG10`) |
| 4 | 13 | Schema columns |

# Sidebar siblings

- regional_intensity_postcode
- regional_regionid
- regional_current
- regional_intensity_fw24h_postcode
- regional_intensity_pt24h_postcode

# Sample chart

- **Type:** `donut`
- **Title:** "Postcode generation mix · live"
- **Subtitle:** "Donut · percent share · postcode RG10 · UTC · 6 May 2026"
- **Seed:** 43
- **Toggles:** `now` (active) / `vs national`

# Schema

Defined in `gridflow/schemas/neso.py` · `RegionalIntensity` (lines 62-73). Transformed via the shared `_transform_regional` (`silver/neso/carbon_intensity.py L400-445`). Partitioned by `timestamp_utc` (year + month). Region-keyed envelope — the region object echoes the requested `postcode` field.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `from` | Half-hour period start. UTC enforced. | `schemas/neso.py L20, L23-28` |
| `period_end_utc` | `datetime[UTC]` | Yes | `to` | Half-hour period end. | `schemas/neso.py L21` |
| `regionid` | `int \| None` | Yes | `regionid` | DNO region serving this postcode. | `schemas/neso.py L65` |
| `dnoregion` | `str` | No (default `""`) | `dnoregion` | DNO region name. | `schemas/neso.py L66` |
| `shortname` | `str` | No (default `""`) | `shortname` | Short region label. | `schemas/neso.py L67` |
| `postcode` | `str` | No (default `""`) | `postcode` | The requested outward postcode (echoed from path). | `schemas/neso.py L68` |
| `forecast_gco2_kwh` | `float \| None` | Yes | `intensity.forecast` | Regional forecast carbon intensity. | `schemas/neso.py L69` |
| `actual_gco2_kwh` | `float \| None` | Yes | `intensity.actual` | Often null on regional endpoints. | `schemas/neso.py L70` |
| `intensity_index` | `str` | No (default `""`) | `intensity.index` | Categorical: `very low` … `very high`. | `schemas/neso.py L71` |
| `fuel` | `str` | No (default `""`) | `generationmix.fuel` | Regional generation mix fuel. | `schemas/neso.py L72` |
| `generation_percentage` | `float \| None` | Yes | `generationmix.perc` | Regional fuel share in percent. | `schemas/neso.py L73` |
| `data_provider` | `str` | No (default `"neso"`) | _derived_ | Always `"neso"`. | `schemas/neso.py L16` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Silver transform timestamp. | `silver/neso/carbon_intensity.py L469-474` |

**PARQUET PATH:** `data/silver/neso/regional_postcode/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, regionid, shortname, postcode, fuel)` — keep last

# Sample data

| timestamp_utc | regionid | shortname | postcode | forecast_gco2_kwh | intensity_index | fuel | generation_percentage |
|---|---|---|---|---|---|---|---|
| 2026-05-08T17:30:00+00:00 | 12 | South England | RG41 | 220.0 | high | gas | 52.1 |
| **2026-05-08T17:30:00+00:00** | **12** | **South England** | **RG41** | **220.0** | **high** | **imports** | **17.8** |
| 2026-05-08T17:30:00+00:00 | 12 | South England | RG41 | 220.0 | high | nuclear | 13.2 |
| 2026-05-08T17:30:00+00:00 | 12 | South England | RG41 | 220.0 | high | solar | 8.1 |
| 2026-05-08T17:30:00+00:00 | 12 | South England | RG41 | 220.0 | high | wind | 5.6 |
| 2026-05-08T17:30:00+00:00 | 12 | South England | RG41 | 220.0 | high | biomass | 3.2 |

**Sources:** Six fuel rows for postcode `RG41` (SSE South / South England DNO, regionid=12) at 17:30 UTC. Vault Bronze sample L60 supplies `gas=52.1`, `imports=17.8`; remaining fuels synthesised to complete the mix. Highlighted `imports=17.8%` row illustrates the southern DNO's reliance on interconnector flows — the canonical "near the coast" carbon signature different from inland regions.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `api.carbonintensity.org.uk/regional/postcode/{postcode}` (path param = outward postcode only, e.g. `RG10`, not full `RG10 8AA`)
- AUTH: None (public). Send `Accept: application/json`. Gridflow throttles to 10 req/s.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/neso/regional_postcode/<year>/<month>/<day>/raw_<timestamp>_<hash>.json`
- TRANSFORMER: `gridflow.silver.neso.carbon_intensity.RegionalPostcodeTransformer` (dynamically generated via `register_neso_transformers()` at L110-118; default postcode `RG10`)

**Tab 1 — Example URL**
```
https://api.carbonintensity.org.uk/regional/postcode/RG10
```

Header: `Accept: application/json`

**Tab 2 — DuckDB · SQL**
```sql
-- Multi-postcode comparison: cleanest postcode at the latest SP
SELECT postcode, regionid, shortname, forecast_gco2_kwh, intensity_index
FROM read_parquet('data/silver/neso/regional_postcode/**/*.parquet')
WHERE timestamp_utc = (
  SELECT max(timestamp_utc) FROM read_parquet('data/silver/neso/regional_postcode/**/*.parquet')
)
  AND fuel = ''
ORDER BY forecast_gco2_kwh;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/neso/regional_postcode/**/*.parquet")
# Latest by postcode — consumer-facing "is my area clean right now?" lookup
latest = (
    df.sort("timestamp_utc", descending=True)
      .group_by("postcode").first()
      .select(["postcode", "shortname", "forecast_gco2_kwh", "intensity_index"])
      .sort("forecast_gco2_kwh")
)
print(latest)
```

# Caveats

## 01 Outward postcode only — not full postcode

The `{postcode}` segment accepts the outward part only (e.g. `RG10`, not `RG10 8AA`). Sending the full postcode returns a vendor error. *(Source: vault Query parameters L35.)*

## 02 NESO API status: beta

`Carbon Intensity - Regional` is beta (`endpoints.py L183`). *(Source: `endpoints.py L183`.)*

## 03 Default postcode `RG10` (Wargrave, Berkshire)

If the connector is called without a `postcode` override, it uses `DEFAULT_POSTCODE = "RG10"` (`endpoints.py L13`). This is the gridflow test/example default — change it for production use. *(Source: `endpoints.py L13, L185`.)*

## 04 Region-keyed envelope with postcode echo

The region object includes `postcode` echoed from the request. Always populated for this endpoint; blank on all-regions calls. *(Source: vault Bronze Sample L55-60.)*

## 05 Transformer is dynamically generated

`RegionalPostcodeTransformer` is created at import time via `type()` in `register_neso_transformers()`. *(Source: `silver/neso/carbon_intensity.py L110-136`.)*

# Related datasets

- **`regional_regionid`** — Same single-region snapshot keyed by regionid (1..17). `30 min`. Equivalent — use whichever join key you have. *neso · regional intensity · 30 min*
- **`regional_intensity_postcode`** — Range query · same postcode shape. `30 min`. Use for historical postcode-scoped analysis. *neso · regional intensity · 30 min*
- **`regional_intensity_fw24h_postcode`** — 24h forecast · same postcode shape. `30 min`. Day-ahead carbon for a specific postcode. *neso · regional forecast · 30 min*
- **`regional_current`** — All ~17 regions · same SP. `30 min`. Returns the requested postcode's DNO region embedded in the full list. *neso · regional intensity · 30 min*
