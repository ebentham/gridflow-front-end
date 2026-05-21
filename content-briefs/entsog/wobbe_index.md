---
slug: wobbe_index
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/WobbeIndex
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/wobbe_index.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["wobbe_index"] (line 107) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/33-wobbe-index-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Wobbe index of delivered gas, <span class="italic fg-accent">per point.</span>

**Lede:** Wobbe index per operator-point-direction — the canonical interchangeability indicator that determines whether two gases can substitute in burner equipment.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.wobbe_index` |
| API PATH | `/api/v1/operationalData?indicator=Wobbe%20Index` |
| FREQUENCY | daily (gas day) |
| PUBLICATION LAG | same-day (Provisional) |
| VOLUME | ~9 GB points/day (default filter) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/Nm³ | Reporting unit |
| 3 | gas-quality | Indicator family |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- gcv
- hydrogen_content
- methane_content
- oxygen_content
- physical_flows

# Sample chart

- **Type:** `sparkline`
- **Title:** "Bacton (IUK) · daily Wobbe index"
- **Subtitle:** "Sparkline · kWh/Nm³ · 30-day window"
- **Seed:** 61
- **Toggles:** `30d` (active) / `1y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same operational-data shape as `gcv`; differentiators are `indicator="Wobbe Index"` and `value` unit (typically `"kWh/Nm³"` — energy/sqrt(specific-gravity)).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Gas-day window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Wobbe Index"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/Nm³"` typically. | dynamic |
| `value` | `float` | Yes | `value` | Wobbe index value (typically 13.5-15.7 kWh/Nm³ for natural gas H-type). | `silver/entsog/generic.py L122-124` |
| `flow_status` | `str` | Yes | `flowStatus` | `"Provisional"` / `"Confirmed"`. | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/wobbe_index/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | point_key | point_label | direction_key | unit | value | flow_status |
|---|---|---|---|---|---|---|
| 2026-05-06T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | kWh/Nm³ | 14.85 | Provisional |
| **2026-05-06T04:00:00+00:00** | **ITP-00207** | **Bacton (BBL)** | **exit** | **kWh/Nm³** | **14.78** | **Provisional** |
| 2026-05-06T04:00:00+00:00 | ITP-00495 | Moffat (IE) | entry | kWh/Nm³ | 14.92 | Provisional |
| 2026-05-06T04:00:00+00:00 | ITP-00090 | Moffat | entry | kWh/Nm³ | 14.88 | Provisional |
| 2026-05-05T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | kWh/Nm³ | 14.86 | Confirmed |
| 2026-05-05T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | exit | kWh/Nm³ | 14.79 | Confirmed |
| 2026-05-04T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | exit | kWh/Nm³ | 14.84 | Confirmed |
| 2026-05-04T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | exit | kWh/Nm³ | 14.77 | Confirmed |

**Sources:** Synthesised — Wobbe index for North Sea H-type natural gas typically clusters 14.7-15.0 kWh/Nm³ (interchangeability with continental high-calorific gas). Highlighted row is BBL exit Wobbe — slightly lower than IUK reflects the BBL pipeline's blend composition. Use Wobbe to verify gas interchangeability between supply sources for downstream burner equipment.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Wobbe Index&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/wobbe_index/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `WobbeIndexTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Wobbe%20Index&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Wobbe index spread across GB points (interchangeability check)
SELECT point_key, point_label,
       AVG(value) AS avg_wobbe,
       MIN(value) AS min_wobbe,
       MAX(value) AS max_wobbe
FROM read_parquet('data/silver/entsog/wobbe_index/**/*.parquet')
WHERE timestamp_utc >= current_date - INTERVAL 30 DAY
  AND operator_key LIKE 'UK-TSO%'
GROUP BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/wobbe_index/**/*.parquet")
# Check Wobbe spread to verify interchangeability (typically <0.5 kWh/Nm³ variation)
spread = (
    df.group_by("timestamp_utc")
      .agg((pl.col("value").max() - pl.col("value").min()).alias("daily_spread_kwh_nm3"))
      .sort("timestamp_utc")
      .tail(30)
)
print(spread)
```

# Caveats

## 01 Indicator string is exact-case

Vendor rejects `wobbe index` / `wobbeIndex`; connector sends literal `"Wobbe Index"`. *(Source: `OPERATIONAL_INDICATORS["wobbe_index"] = "Wobbe Index"` `connectors/entsog/endpoints.py L107`.)*

## 02 Wobbe = GCV / sqrt(specific gravity)

Two gases are interchangeable when their Wobbe values differ by <5%. The value is the energy-per-volume divided by the square-root of the specific gravity relative to air. *(Source: gas-physics convention.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Sister gas-quality indicators are withdrawn

`hydrogen_content`, `methane_content`, `oxygen_content` were withdrawn by vendor on 2026-05-19 (return HTTP 404). `gcv` and `wobbe_index` remain live and are the surviving gas-quality surfaces. *(Source: `.planning/reconciliation/entsog/0[1-4]-*-http-404.md`.)*

# Related datasets

- **`gcv`** — Gross calorific value. `daily`. Pair with Wobbe to derive specific gravity. *entsog · gas-quality · daily*
- **`hydrogen_content`** — Hydrogen fraction (endpoint withdrawn 2026-05-19). `daily`. Historic-only. *entsog · gas-quality · historic*
- **`methane_content`** — Methane fraction (endpoint withdrawn 2026-05-19). `daily`. Historic-only. *entsog · gas-quality · historic*
- **`physical_flows`** — Operational flow. `daily`. Wobbe applies to delivered gas at the same points. *entsog · operational · daily*
