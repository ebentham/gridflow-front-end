---
slug: renominations
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/Renomination
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/renominations.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — registered via `_make_transformer_class` at L223-238
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["renominations"] (line 99) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/29-renominations-manual-transformer-schema.md (wontfix v3-candidate — confirms dynamic-schema is by design)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Within-day revisions to <span class="italic fg-accent">gas nominations.</span>

**Lede:** Shipper renominations updating intra-day flow quantities at each point — the canonical signal for late shifts in expected gas supply and demand.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.renominations` |
| API PATH | `/api/v1/operationalData?indicator=Renomination` |
| FREQUENCY | daily (gas day; possibly multiple within-day revisions per point) |
| PUBLICATION LAG | same-day (within gas-day window) |
| VOLUME | ~9 GB points/day (default filter); 0 on days with no revisions |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | within-day | Revision cadence |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- nominations
- physical_flows
- allocations
- firm_booked
- interruptible_booked

# Sample chart

- **Type:** `sparkline`
- **Title:** "Bacton (IUK) exit · renomination delta vs initial nomination"
- **Subtitle:** "Sparkline · GWh/day · 30-day window"
- **Seed:** 27
- **Toggles:** `30d` (active) / `1y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically from the live response. Same column set as `nominations`; the differentiator is `indicator="Renomination"` and the presence of `original_period_from` (set to the original gas-day for which the renomination applies).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set from `periodFrom`. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Gas-day window. | `silver/entsog/generic.py L114-116` |
| `original_period_from` | `datetime[UTC]` | Yes | `originalPeriodFrom` | Set on renominations — the original gas-day being revised. | `silver/entsog/datetime.py::parse_entsog_datetime_expr` |
| `indicator` | `str` | Yes | `indicator` | Always `"Renomination"` for this endpoint. | dynamic |
| `operator_key` / `operator_label` | `str` | Yes | `operatorKey` / `operatorLabel` | TSO. | dynamic |
| `point_key` / `point_label` | `str` | Yes | `pointKey` / `pointLabel` | Connection-point. | dynamic |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` / `"exit"`. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"` typically. | dynamic |
| `value` | `float` | Yes | `value` | Revised nomination quantity. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/renominations/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | original_period_from | point_key | direction_key | unit | value | last_update_date_time |
|---|---|---|---|---|---|---|
| 2026-05-06T04:00:00+00:00 | 2026-05-06T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 18,500,000 | 2026-05-06T10:14:22+00:00 |
| 2026-05-06T04:00:00+00:00 | 2026-05-06T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 19,100,000 | 2026-05-06T13:02:00+00:00 |
| **2026-05-06T04:00:00+00:00** | **2026-05-06T04:00:00+00:00** | **ITP-00207** | **exit** | **kWh/d** | **155,400,000** | **2026-05-06T11:48:33+00:00** |
| 2026-05-06T04:00:00+00:00 | 2026-05-06T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 158,100,000 | 2026-05-06T14:22:10+00:00 |
| 2026-05-06T04:00:00+00:00 | 2026-05-06T04:00:00+00:00 | ITP-00495 | entry | kWh/d | 90,200,000 | 2026-05-06T12:05:55+00:00 |
| 2026-05-05T04:00:00+00:00 | 2026-05-05T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 14,200,000 | 2026-05-05T09:55:11+00:00 |
| 2026-05-05T04:00:00+00:00 | 2026-05-05T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 146,300,000 | 2026-05-05T11:30:00+00:00 |
| 2026-05-05T04:00:00+00:00 | 2026-05-05T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 148,800,000 | 2026-05-05T15:45:00+00:00 |

**Sources:** Synthesised to demonstrate the within-day revision pattern (multiple rows per `(period_from, point_key, direction_key)` distinguished by `last_update_date_time`). Magnitudes match the vault's documented `kWh/d` scale for Bacton/Moffat. Highlighted row is the first BBL exit renomination of 2026-05-06 at 11:48 UTC, raising the nomination from 149 GWh/day to 155 GWh/day — within-day revisions like this are the prime use case.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Renomination&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/renominations/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `RenominationsTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Renomination&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Within-day nomination drift: max - first per gas day per point
WITH ordered AS (
  SELECT period_from, point_key, direction_key, value, last_update_date_time,
         ROW_NUMBER() OVER (PARTITION BY period_from, point_key, direction_key
                            ORDER BY last_update_date_time) AS rev_n
  FROM read_parquet('data/silver/entsog/renominations/**/*.parquet')
)
SELECT period_from::date AS gas_day, point_key, direction_key,
       MAX(value) - MIN(value) AS drift_kwh
FROM ordered
WHERE period_from >= current_date - INTERVAL 30 DAY
GROUP BY 1, 2, 3
ORDER BY 1, drift_kwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/renominations/**/*.parquet")
# Count renominations per point per gas day
counts = (
    df.group_by(["period_from", "point_key", "direction_key"])
      .agg(pl.len().alias("revisions"))
      .filter(pl.col("revisions") > 1)
      .sort("revisions", descending=True)
)
print(counts.head(10))
```

# Caveats

## 01 Indicator string is exact-case

Vendor rejects `renomination` / `re-nomination`; connector sends literal `"Renomination"`. *(Source: vault Known Issues; `OPERATIONAL_INDICATORS["renominations"] = "Renomination"` `connectors/entsog/endpoints.py L99`.)*

## 02 Multiple renominations per gas day are expected

A single `(period_from, point_key, direction_key)` may carry multiple silver rows distinguished by `last_update_date_time`. Dedup on `id` (vendor concatenation includes the revision sequence). *(Source: `silver/entsog/generic.py L126-130`.)*

## 03 `original_period_from` identifies the revised gas-day

For revisions made after the gas-day window closes (rare), `original_period_from` differs from `period_from`. *(Source: vault Bronze sample field reference.)*

## 04 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17` `ENTSOG_TIMEZONE`.)*

## 05 Empty windows return HTTP 404, not 200

ENTSO-G's empty convention is `HTTP 404 + {"message":"No result found"}`. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 06 Period offset is CEST/CET even with `timeZone=UCT`

`periodFrom` carries `+02:00`/`+01:00`; `parse_entsog_datetime_expr` converts to UTC. *(Source: `silver/entsog/datetime.py`.)*

# Related datasets

- **`nominations`** — Initial day-ahead nomination. `daily`. Compare against renominations to measure within-day drift. *entsog · operational · daily*
- **`physical_flows`** — Realised flow at the same points. `daily`. Final settlement against which renominations are graded. *entsog · operational · daily*
- **`allocations`** — Settled allocated quantity. `daily`. The final-state record. *entsog · operational · daily*
- **`interruptions`** — Capacity interruption events. `daily`. Pair when renominations cluster around interruption windows. *entsog · operational · daily*
