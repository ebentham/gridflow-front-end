---
slug: interruptible_total
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/InterruptibleTotal
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/interruptible_total.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["interruptible_total"] (line 105) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/25-interruptible-total-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Total interruptible capacity, <span class="italic fg-accent">offered.</span>

**Lede:** Total interruptible-product capacity per operator-point-direction — the upper-bound on interruptible offered, distinct from `interruptible_available`.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.interruptible_total` |
| API PATH | `/api/v1/operationalData?indicator=Interruptible%20Total` |
| FREQUENCY | daily |
| PUBLICATION LAG | same-day |
| VOLUME | ~9 GB points/day (default filter) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | interruptible | Capacity-type indicator |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- interruptible_available
- interruptible_booked
- firm_technical
- available_through_oversubscription
- firm_available

# Sample chart

- **Type:** `barsH`
- **Title:** "GB points · total interruptible offered vs firm available"
- **Subtitle:** "Horizontal bars · GWh/day · current"
- **Seed:** 32
- **Toggles:** `current` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same canonical operational-data shape; differentiator is `indicator="Interruptible Total"`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Validity window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Interruptible Total"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction. | dynamic |
| `capacity_type` | `str` | Yes | `capacityType` | `"Interruptible"`. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"`. | dynamic |
| `value` | `float` | Yes | `value` | Total interruptible capacity offered. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/interruptible_total/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | period_to | point_key | direction_key | unit | value |
|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 95,000,000 |
| **2025-10-01T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **ITP-00207** | **exit** | **kWh/d** | **20,000,000** |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00495 | entry | kWh/d | 8,000,000 |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00090 | entry | kWh/d | 5,000,000 |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 32,000,000 |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 8,000,000 |
| 2026-04-01T04:00:00+00:00 | 2026-07-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 30,000,000 |
| 2025-04-01T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 100,000,000 |

**Sources:** Synthesised — `interruptible_total` typically matches or slightly exceeds `interruptible_available` because the available view subtracts booked-but-unconverted rollover capacity. Highlighted row is BBL exit at 20 GWh/d — the same as `interruptible_available`, indicating no rollover headroom for BBL.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Interruptible Total&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/interruptible_total/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `InterruptibleTotalTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Interruptible%20Total&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Total offered (firm + interruptible_total) vs technical
WITH t AS (
  SELECT point_key, direction_key, value AS tech
  FROM read_parquet('data/silver/entsog/firm_technical/**/*.parquet')
  WHERE period_from <= current_date AND period_to > current_date
),
fa AS (
  SELECT point_key, direction_key, value AS fa
  FROM read_parquet('data/silver/entsog/firm_available/**/*.parquet')
  WHERE period_from <= current_date AND period_to > current_date
),
it AS (
  SELECT point_key, direction_key, value AS it
  FROM read_parquet('data/silver/entsog/interruptible_total/**/*.parquet')
  WHERE period_from <= current_date AND period_to > current_date
)
SELECT t.point_key, t.direction_key,
       t.tech / 1e6 AS tech_gwh,
       (fa.fa + COALESCE(it.it, 0)) / 1e6 AS total_offered_gwh
FROM t LEFT JOIN fa USING (point_key, direction_key)
      LEFT JOIN it USING (point_key, direction_key)
ORDER BY tech_gwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/interruptible_total/**/*.parquet")
# Latest total interruptible per point
latest = (
    df.sort("last_update_date_time", descending=True)
      .group_by(["point_key", "direction_key"])
      .agg(pl.col("value").first().alias("kwh_per_day"))
)
print(latest)
```

# Caveats

## 01 Indicator string is exact-case

Connector sends literal `"Interruptible Total"`. *(Source: `OPERATIONAL_INDICATORS["interruptible_total"] = "Interruptible Total"` `connectors/entsog/endpoints.py L105`.)*

## 02 `interruptible_total` ≥ `interruptible_available`

`total` is the firm-equivalent offered; `available` subtracts unconverted rollover. Use `total` for theoretical headroom, `available` for what shippers can actually book today. *(Source: vault Modelling notes; ENTSO-G data dictionary.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Day-level rows are rare — long products dominate

Most rows have multi-month or multi-year validity windows; daily rows appear only for short-product UIOLI capacity. *(Source: vault Bronze sample period-window shape.)*

# Related datasets

- **`interruptible_available`** — Currently bookable interruptible. `daily`. Subset of total. *entsog · capacity · daily*
- **`interruptible_booked`** — Booked portion. `daily`. Pair for total utilisation. *entsog · capacity · daily*
- **`firm_technical`** — Physical pipeline maximum. `daily`. Theoretical ceiling on `interruptible_total + firm_total`. *entsog · capacity · daily*
- **`available_through_oversubscription`** — Oversubscription-mechanism extra capacity. `daily`. CMP-related supplement. *entsog · capacity · daily*
