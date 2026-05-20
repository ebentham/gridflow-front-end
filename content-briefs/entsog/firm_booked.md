---
slug: firm_booked
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/FirmBooked
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/firm_booked.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["firm_booked"] (line 101) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/19-firm-booked-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Firm capacity booked by <span class="italic fg-accent">shippers.</span>

**Lede:** Firm-product capacity already reserved by shippers per operator-point-direction — the canonical demand-side complement to `firm_available`.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.firm_booked` |
| API PATH | `/api/v1/operationalData?indicator=Firm%20Booked` |
| FREQUENCY | daily |
| PUBLICATION LAG | same-day |
| VOLUME | ~9 GB points/day (default filter) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | firm | Capacity-type indicator |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- firm_available
- firm_technical
- interruptible_booked
- available_through_oversubscription
- nominations

# Sample chart

- **Type:** `sparkline`
- **Title:** "Bacton (IUK) exit · firm booked capacity"
- **Subtitle:** "Sparkline · GWh/day · 30-day window"
- **Seed:** 15
- **Toggles:** `30d` (active) / `1y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same canonical operational-data shape; differentiator is `indicator="Firm Booked"`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Booking-validity window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Firm Booked"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction tuple. | dynamic |
| `capacity_type` | `str` | Yes | `capacityType` | `"Firm"` for this indicator. | dynamic |
| `capacity_booking_status` | `str` | Yes | `capacityBookingStatus` | Vendor-defined status (e.g. `"Booked"`). | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"` typically. | dynamic |
| `value` | `float` | Yes | `value` | Booked capacity. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `is_cam_relevant` / `is_cmp_relevant` | `bool` | Yes | `isCamRelevant` / `isCmpRelevant` | Regulatory flags. | dynamic |
| `booking_platform_key` / `_label` / `_url` | `str` | Yes | `bookingPlatformKey` / `_Label` / `_URL` | E.g. `"PRISMA"`. | dynamic |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/firm_booked/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | period_to | point_key | direction_key | unit | value | booking_platform_key |
|---|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 245,000,000 | PRISMA |
| **2025-10-01T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **ITP-00207** | **exit** | **kWh/d** | **172,000,000** | **PRISMA** |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00495 | entry | kWh/d | 78,000,000 | PRISMA |
| 2026-04-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 60,000,000 | PRISMA |
| 2026-04-01T04:00:00+00:00 | 2026-07-01T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 40,000,000 | PRISMA |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 18,000,000 | PRISMA |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00207 | exit | kWh/d | 145,000,000 | PRISMA |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00090 | entry | kWh/d | 0 | PRISMA |

**Sources:** Synthesised respecting vault's documented kWh/d magnitudes and PRISMA platform attribution. Annual products (October-October) sit alongside quarterly and daily bookings. Highlighted row is the BBL exit annual firm booking at 172 GWh/d — close to but slightly under the corresponding `firm_available` of 180 GWh/d, illustrating the typical 95-100% utilisation pattern for GB-export firm capacity.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Firm Booked&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/firm_booked/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `FirmBookedTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Firm%20Booked&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Utilisation: firm booked / firm available per point as-of today
WITH a AS (
  SELECT point_key, direction_key, value AS avail
  FROM read_parquet('data/silver/entsog/firm_available/**/*.parquet')
  WHERE period_from <= current_date AND period_to > current_date
),
b AS (
  SELECT point_key, direction_key, value AS booked
  FROM read_parquet('data/silver/entsog/firm_booked/**/*.parquet')
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

df = pl.read_parquet("data/silver/entsog/firm_booked/**/*.parquet")
# Booking platform distribution
plat = df.group_by("booking_platform_key").agg(pl.len().alias("rows")).sort("rows", descending=True)
print(plat)
```

# Caveats

## 01 Indicator string is exact-case

Connector sends literal `"Firm Booked"`. *(Source: `OPERATIONAL_INDICATORS["firm_booked"] = "Firm Booked"` `connectors/entsog/endpoints.py L101`.)*

## 02 Booking platform is mostly `"PRISMA"`

EU-wide capacity-booking platform; alternative `"RBP"` / `"GSA"` appear regionally. Pair with `firm_available` to compute utilisation. *(Source: vault Bronze sample L125.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Long-product rows overlap short-product rows

A point may have an annual firm booking + a quarterly booking + a daily booking active simultaneously. Filter by product window when computing totals to avoid double-counting. *(Source: vault Bronze sample multiple-product shape.)*

# Related datasets

- **`firm_available`** — Capacity offered. `daily`. Compute headroom and utilisation. *entsog · capacity · daily*
- **`firm_technical`** — Maximum technical capacity. `daily`. Upper bound. *entsog · capacity · daily*
- **`nominations`** — Booked capacity is the upper bound on nominations. `daily`. Sanity check. *entsog · operational · daily*
- **`interruptible_booked`** — Interruptible-capacity bookings. `daily`. Pair for total booked view. *entsog · capacity · daily*
