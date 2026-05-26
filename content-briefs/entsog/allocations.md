---
slug: allocations
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/Allocation
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/allocations.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — registered via `_make_transformer_class` at L223-238
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["allocations"] (line 98) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/08-allocations-manual-transformer-schema.md (wontfix v3-candidate — confirms dynamic-schema is by design)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Settled gas allocations, <span class="italic fg-accent">post-flow.</span>

**Lede:** Final allocated quantities per operator-point-direction — the canonical settlement-grade flow record used downstream of nominations and physical-flow data.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.allocations` |
| API PATH | `/api/v1/operationalData?indicator=Allocation` |
| FREQUENCY | daily (gas day) |
| PUBLICATION LAG | ~1 day after gas-day end (post-flow allocation) |
| VOLUME | ~9 GB points/day (default filter) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | post-flow | Cadence relative to delivery |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- nominations
- renominations
- physical_flows
- firm_booked
- interruptible_booked

# Sample chart

- **Type:** `sparkline`
- **Title:** "Bacton (IUK) exit · daily allocation"
- **Subtitle:** "Sparkline · GWh/day · 30-day window"
- **Seed:** 19
- **Toggles:** `30d` (active) / `1y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same column set as `nominations` and other operational indicators; the differentiator is `indicator="Allocation"`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set from `periodFrom`. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Gas-day window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Allocation"`. | dynamic |
| `operator_key` / `operator_label` | `str` | Yes | `operatorKey` / `operatorLabel` | TSO. | dynamic |
| `point_key` / `point_label` | `str` | Yes | `pointKey` / `pointLabel` | Connection-point. | dynamic |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` / `"exit"`. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"` typically. | dynamic |
| `value` | `float` | Yes | `value` | Allocated quantity. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `is_cam_relevant` / `is_cmp_relevant` | `bool` | Yes | `isCamRelevant` / `isCmpRelevant` | Regulatory flags. | dynamic |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/allocations/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | point_key | point_label | operator_key | direction_key | unit | value | last_update_date_time |
|---|---|---|---|---|---|---|---|
| 2026-05-05T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | UK-TSO-0001 | exit | kWh/d | 19,150,000 | 2026-05-06T11:02:18+00:00 |
| 2026-05-05T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | UK-TSO-0003 | entry | kWh/d | 18,900,000 | 2026-05-06T11:02:18+00:00 |
| **2026-05-05T04:00:00+00:00** | **ITP-00207** | **Bacton (BBL)** | **UK-TSO-0001** | **exit** | **kWh/d** | **156,200,000** | **2026-05-06T11:02:18+00:00** |
| 2026-05-05T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | UK-TSO-0004 | entry | kWh/d | 154,700,000 | 2026-05-06T11:02:18+00:00 |
| 2026-05-05T04:00:00+00:00 | ITP-00495 | Moffat (IE) | IE-TSO-0002 | entry | kWh/d | 89,300,000 | 2026-05-06T11:02:18+00:00 |
| 2026-05-04T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | UK-TSO-0001 | exit | kWh/d | 17,800,000 | 2026-05-05T11:02:18+00:00 |
| 2026-05-04T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | UK-TSO-0001 | exit | kWh/d | 152,800,000 | 2026-05-06T11:02:18+00:00 |
| 2026-05-04T04:00:00+00:00 | ITP-00495 | Moffat (IE) | IE-TSO-0002 | entry | kWh/d | 87,100,000 | 2026-05-05T11:02:18+00:00 |

**Sources:** Synthesised to plausible Bacton/Moffat allocations, calibrated against vault's documented kWh/d magnitudes. Highlighted row is BBL exit allocation = 156 GWh/d for gas day 2026-05-05, settled the following day. Note `last_update_date_time` is in 11:02 UTC the day after the gas day — the documented ~1-day post-flow allocation cadence.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Allocation&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/allocations/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `AllocationsTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Allocation&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Nomination vs allocation error per point (last 30 days)
SELECT n.period_from::date AS gas_day,
       n.point_key, n.direction_key,
       n.value AS nominated_kwh,
       a.value AS allocated_kwh,
       (a.value - n.value) AS delta_kwh
FROM read_parquet('data/silver/entsog/nominations/**/*.parquet') n
JOIN read_parquet('data/silver/entsog/allocations/**/*.parquet') a
  ON  n.period_from  = a.period_from
  AND n.point_key    = a.point_key
  AND n.operator_key = a.operator_key
  AND n.direction_key= a.direction_key
WHERE n.period_from >= current_date - INTERVAL 30 DAY
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/allocations/**/*.parquet")
# Total GB allocations per direction per day
gb = (
    df.filter(pl.col("operator_key").str.starts_with("UK-TSO-"))
      .group_by(["period_from", "direction_key"])
      .agg((pl.col("value").sum() / 1e6).alias("gwh"))
      .sort("period_from")
)
print(gb.tail(14))
```

# Caveats

## 01 Indicator string is exact-case

Vendor rejects `allocation`/`allocations`; connector sends literal `"Allocation"`. *(Source: `OPERATIONAL_INDICATORS["allocations"] = "Allocation"` `connectors/entsog/endpoints.py L98`.)*

## 02 Allocations are post-flow

A row appears ~1 gas day after the flow date. For real-time analytics, use `nominations` or `physical_flows` instead. *(Source: vault Publication-lag table.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

`HTTP 404 + {"message":"No result found"}` is the empty convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Allocation ≠ physical flow

Allocation is the legally settled quantity; physical_flow is the metered throughput. They typically agree but differ when there are CMP adjustments. *(Source: domain knowledge / ENTSO-G data dictionary.)*

# Related datasets

- **`nominations`** — Pre-flow shipper-requested quantity. `daily`. Compare to allocations to grade nomination accuracy. *entsog · operational · daily*
- **`renominations`** — Within-day revisions before allocation. `daily`. Captures shipper adjustments. *entsog · operational · daily*
- **`physical_flows`** — Metered throughput. `daily`. The physical counterpart to allocations. *entsog · operational · daily*
- **`firm_booked`** — Booked capacity. `daily`. Sanity check that allocations don't exceed booked. *entsog · capacity · daily*
