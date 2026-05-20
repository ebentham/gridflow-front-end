---
slug: interruptible_booked
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/InterruptibleBooked
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/interruptible_booked.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["interruptible_booked"] (line 104) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/24-interruptible-booked-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Interruptible capacity booked by <span class="italic fg-accent">shippers.</span>

**Lede:** Interruptible-product capacity already reserved per operator-point-direction — the demand-side complement to `interruptible_available`.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.interruptible_booked` |
| API PATH | `/api/v1/operationalData?indicator=Interruptible%20Booked` |
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
- interruptible_total
- firm_booked
- nominations
- allocations

# Sample chart

- **Type:** `sparkline`
- **Title:** "Bacton (IUK) exit · interruptible booked capacity"
- **Subtitle:** "Sparkline · GWh/day · 30-day window"
- **Seed:** 28
- **Toggles:** `30d` (active) / `1y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same canonical operational-data shape; differentiator is `indicator="Interruptible Booked"`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Booking-validity window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Interruptible Booked"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction tuple. | dynamic |
| `capacity_type` | `str` | Yes | `capacityType` | `"Interruptible"`. | dynamic |
| `capacity_booking_status` | `str` | Yes | `capacityBookingStatus` | Booking-status vendor enum. | dynamic |
| `booking_platform_key` / `_label` / `_url` | `str` | Yes | `bookingPlatformKey` / `_Label` / `_URL` | PRISMA / RBP / GSA. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"`. | dynamic |
| `value` | `float` | Yes | `value` | Booked interruptible capacity. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/interruptible_booked/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | period_to | point_key | direction_key | unit | value | booking_platform_key |
|---|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 45,000,000 | PRISMA |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | entry | kWh/d | 60,000,000 | PRISMA |
| **2025-10-01T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **ITP-00207** | **exit** | **kWh/d** | **8,000,000** | **PRISMA** |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00495 | entry | kWh/d | 3,000,000 | RBP |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00090 | entry | kWh/d | 2,000,000 | PRISMA |
| 2026-04-01T04:00:00+00:00 | 2026-07-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 12,000,000 | PRISMA |
| 2026-05-01T04:00:00+00:00 | 2026-06-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 5,000,000 | PRISMA |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 0 | PRISMA |

**Sources:** Synthesised — interruptible bookings typically run at ~40-50% utilisation of `interruptible_available` (lower than firm, reflecting curtailment risk). Highlighted row is BBL exit interruptible at 8 GWh/d, about 40% of the offered 20 GWh/d. PRISMA dominates; RBP appears on the Moffat IE side.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Interruptible Booked&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/interruptible_booked/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `InterruptibleBookedTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Interruptible%20Booked&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Interruptible utilisation: booked / available per point
WITH a AS (
  SELECT point_key, direction_key, value AS avail
  FROM read_parquet('data/silver/entsog/interruptible_available/**/*.parquet')
  WHERE period_from <= current_date AND period_to > current_date
),
b AS (
  SELECT point_key, direction_key, value AS booked
  FROM read_parquet('data/silver/entsog/interruptible_booked/**/*.parquet')
  WHERE period_from <= current_date AND period_to > current_date
)
SELECT a.point_key, a.direction_key,
       (b.booked * 100.0 / NULLIF(a.avail, 0)) AS utilisation_pct
FROM a JOIN b USING (point_key, direction_key)
ORDER BY utilisation_pct DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/interruptible_booked/**/*.parquet")
# Booking platform split
print(df.group_by("booking_platform_key").agg(pl.col("value").sum()).sort("value", descending=True))
```

# Caveats

## 01 Indicator string is exact-case

Connector sends literal `"Interruptible Booked"`. *(Source: `OPERATIONAL_INDICATORS["interruptible_booked"] = "Interruptible Booked"` `connectors/entsog/endpoints.py L104`.)*

## 02 Interruptible bookings carry curtailment risk

Booked rows are not guaranteed to flow; shippers pay-as-used minus curtailment. Model with a discount factor. *(Source: domain knowledge / CMP mechanism docs.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Booking platform attribution varies regionally

PRISMA dominates EU-wide; RBP (Hungary/SK) and GSA (FR/IT) appear in regional sub-markets. Don't filter on platform without checking the operator-region map. *(Source: vault Bronze sample platform-key examples.)*

# Related datasets

- **`interruptible_available`** — Capacity offered. `daily`. Headroom = available - booked. *entsog · capacity · daily*
- **`interruptible_total`** — Total interruptible offered. `daily`. Sometimes equals available, sometimes higher (firm-equivalent). *entsog · capacity · daily*
- **`firm_booked`** — Firm bookings (the high-priority counterpart). `daily`. Pair for total booked view. *entsog · capacity · daily*
- **`nominations`** — Shippers nominate against booked capacity. `daily`. Cross-check that nominations don't exceed firm + interruptible booked. *entsog · operational · daily*
