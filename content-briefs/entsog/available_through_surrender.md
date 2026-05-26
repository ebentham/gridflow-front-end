---
slug: available_through_surrender
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/AvailableThroughSurrender
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/available_through_surrender.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["available_through_surrender"] (line 112) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/10-available-through-surrender-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Capacity returned via the <span class="italic fg-accent">surrender mechanism.</span>

**Lede:** Capacity surrendered by shippers back to the TSO and re-offered — the canonical signal for CMP capacity recycled from underused firm bookings.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.available_through_surrender` |
| API PATH | `/api/v1/operationalData?indicator=Available%20through%20Surrender` |
| FREQUENCY | daily |
| PUBLICATION LAG | same-day |
| VOLUME | ~9 GB points/day (default filter); often 0 rows |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | CMP | Mechanism (surrender) |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- available_through_oversubscription
- available_through_uioli_long_term
- available_through_uioli_short_term
- cmp_unavailable_firm_capacity
- firm_booked

# Sample chart

- **Type:** `sparkline`
- **Title:** "Surrender capacity at GB points · 1-year window"
- **Subtitle:** "Sparkline · GWh/day · last 12 months"
- **Seed:** 35
- **Toggles:** `1y` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same canonical operational-data shape; differentiator is `indicator="Available through Surrender"`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Validity window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Available through Surrender"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction. | dynamic |
| `is_cmp_relevant` | `bool` | Yes | `isCmpRelevant` | `true` for this indicator. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"`. | dynamic |
| `value` | `float` | Yes | `value` | Surrendered capacity re-offered. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/available_through_surrender/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | period_to | point_key | direction_key | unit | value | last_update_date_time |
|---|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 0 | 2025-10-01T08:00:00+00:00 |
| **2026-02-15T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **ITP-00005** | **exit** | **kWh/d** | **15,000,000** | **2026-02-14T16:30:00+00:00** |
| 2026-02-15T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 4,000,000 | 2026-02-14T16:30:00+00:00 |
| 2026-04-01T04:00:00+00:00 | 2026-07-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 8,000,000 | 2026-03-25T11:00:00+00:00 |
| 2026-04-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 5,000,000 | 2026-03-30T09:00:00+00:00 |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 2,000,000 | 2026-05-05T17:00:00+00:00 |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 0 | 2026-05-05T17:00:00+00:00 |
| 2025-04-10T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 22,000,000 | 2025-04-08T11:20:00+00:00 |

**Sources:** Synthesised — surrender is event-driven and event-spiky. Highlighted row is a mid-gas-year surrender event at Bacton IUK on 2026-02-14 surrendering 15 GWh/d for the remaining ~7 months — the kind of event signalling that a shipper is releasing booked capacity, useful for nowcasting reduced GB-exit pressure.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Available through Surrender&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/available_through_surrender/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `AvailableThroughSurrenderTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Available%20through%20Surrender&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Surrender events in the last 90 days (non-zero updates)
SELECT last_update_date_time, point_key, direction_key,
       period_from, period_to,
       value / 1e6 AS surrendered_gwh
FROM read_parquet('data/silver/entsog/available_through_surrender/**/*.parquet')
WHERE last_update_date_time >= current_timestamp - INTERVAL 90 DAY
  AND value > 0
ORDER BY last_update_date_time DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/available_through_surrender/**/*.parquet")
# Total surrendered per point in 2026
total = (
    df.filter(pl.col("period_from") >= pl.lit("2026-01-01"))
      .group_by("point_key")
      .agg((pl.col("value").sum() / 1e6).alias("total_surrendered_gwh"))
      .sort("total_surrendered_gwh", descending=True)
)
print(total)
```

# Caveats

## 01 Indicator string is exact-case (mixed case)

Connector sends literal `"Available through Surrender"` — lowercase `through`. *(Source: `OPERATIONAL_INDICATORS["available_through_surrender"]` `connectors/entsog/endpoints.py L112`.)*

## 02 Surrender is event-driven, not steady-state

Most days return zero rows or zero values. The signal is in the few non-zero events when a shipper releases capacity. *(Source: domain knowledge / CMP mechanism docs.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Surrendered capacity re-enters firm_available

Once surrendered, capacity is re-offered through the standard auction; check `firm_available` for the downstream uplift. *(Source: ENTSO-G CMP Network Code.)*

# Related datasets

- **`available_through_oversubscription`** — Oversubscription mechanism. `daily`. Sister CMP procedure. *entsog · capacity · daily*
- **`available_through_uioli_long_term`** — UIOLI long-term capacity. `daily`. Forced-surrender alternative. *entsog · capacity · daily*
- **`available_through_uioli_short_term`** — UIOLI short-term capacity. `daily`. Day-ahead UIOLI window. *entsog · capacity · daily*
- **`firm_booked`** — Booked firm before surrender. `daily`. Track surrender as a delta on `firm_booked`. *entsog · capacity · daily*
