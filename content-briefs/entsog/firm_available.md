---
slug: firm_available
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/FirmAvailable
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/firm_available.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["firm_available"] (line 100) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/18-firm-available-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Firm capacity offered for sale, <span class="italic fg-accent">per point.</span>

**Lede:** Firm-product capacity available for shipper booking per operator-point-direction — the canonical signal for headroom to nominate firm gas flows.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.firm_available` |
| API PATH | `/api/v1/operationalData?indicator=Firm%20Available` |
| FREQUENCY | daily (gas day; long-validity products) |
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

- firm_booked
- firm_technical
- interruptible_available
- available_through_oversubscription
- available_through_surrender

# Sample chart

- **Type:** `sparkline`
- **Title:** "Bacton (IUK) exit · firm available capacity"
- **Subtitle:** "Sparkline · GWh/day · 30-day window"
- **Seed:** 14
- **Toggles:** `30d` (active) / `1y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Schema is the canonical operational-data shape; the differentiator is `indicator="Firm Available"` and `capacity_type="Firm"`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Capacity-validity window (can span years for long products). | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Firm Available"`. | dynamic |
| `operator_key` / `operator_label` | `str` | Yes | `operatorKey` / `operatorLabel` | TSO. | dynamic |
| `point_key` / `point_label` | `str` | Yes | `pointKey` / `pointLabel` | Connection-point. | dynamic |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` / `"exit"`. | dynamic |
| `capacity_type` | `str` | Yes | `capacityType` | `"Firm"` for this indicator. | dynamic |
| `is_unlimited` | `bool` / `str` | Yes | `isUnlimited` | `"0"` / `"1"` / null. | dynamic |
| `unit` | `str` | Yes | `unit` | Typically `"kWh/d"` (some endpoints `kWh/h`). | dynamic |
| `value` | `float` | Yes | `value` | Available capacity in `unit`. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/firm_available/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | period_to | point_key | direction_key | capacity_type | unit | value | last_update_date_time |
|---|---|---|---|---|---|---|---|
| 2022-01-01T05:00:00+00:00 | 2028-05-01T04:00:00+00:00 | ITP-00005 | exit | Firm | kWh/d | 518,112,451 | 2026-05-01T00:11:58+00:00 |
| 2024-10-01T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | ITP-00005 | exit | Firm | kWh/d | 460,000,000 | 2025-09-15T08:00:00+00:00 |
| **2025-10-01T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **ITP-00207** | **exit** | **Firm** | **kWh/d** | **180,000,000** | **2025-09-15T08:00:00+00:00** |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00495 | entry | Firm | kWh/d | 95,000,000 | 2025-09-20T08:00:00+00:00 |
| 2025-04-01T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | ITP-00207 | exit | Firm | kWh/d | 175,000,000 | 2025-03-20T08:00:00+00:00 |
| 2026-04-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00207 | exit | Firm | kWh/d | 185,000,000 | 2026-03-20T08:00:00+00:00 |
| 2026-05-06T04:00:00+00:00 | 2026-05-07T04:00:00+00:00 | ITP-00090 | entry | Firm | kWh/d | 0 | 2026-05-05T08:00:00+00:00 |
| 2024-10-01T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | ITP-00495 | entry | Firm | kWh/d | 90,000,000 | 2024-09-15T08:00:00+00:00 |

**Sources:** First row verbatim from vault Bronze sample (`firm_available.md` L113; `value=518112451` kWh/d at Bacton IUK for the 2022-01-01..2028-05-01 product). Remaining rows synthesised respecting the multi-year-product cadence — capacity windows align to gas years (October-to-October) and quarterly products. Highlighted row is the 2025-10-01 BBL exit annual firm product (180 GWh/d) — the kind of long-validity record useful for capacity-allocation modelling.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Firm Available&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/firm_available/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `FirmAvailableTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Firm%20Available&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Firm-available headroom: capacity vs booked for the current gas year
WITH avail AS (
  SELECT point_key, direction_key,
         MAX_BY(value, period_from) AS firm_avail_kwh
  FROM read_parquet('data/silver/entsog/firm_available/**/*.parquet')
  WHERE period_from <= current_date AND period_to > current_date
  GROUP BY 1, 2
),
booked AS (
  SELECT point_key, direction_key,
         MAX_BY(value, period_from) AS firm_booked_kwh
  FROM read_parquet('data/silver/entsog/firm_booked/**/*.parquet')
  WHERE period_from <= current_date AND period_to > current_date
  GROUP BY 1, 2
)
SELECT a.point_key, a.direction_key,
       a.firm_avail_kwh / 1e6 AS avail_gwh,
       b.firm_booked_kwh / 1e6 AS booked_gwh,
       (a.firm_avail_kwh - b.firm_booked_kwh) / 1e6 AS headroom_gwh
FROM avail a JOIN booked b USING (point_key, direction_key)
ORDER BY headroom_gwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/firm_available/**/*.parquet")
# Latest firm available per point (as-of today)
latest = (
    df.filter(pl.col("period_from") <= pl.lit("2026-05-20"))
      .filter(pl.col("period_to")   >  pl.lit("2026-05-20"))
      .sort("last_update_date_time", descending=True)
      .group_by(["point_key", "direction_key"])
      .agg(pl.col("value").first().alias("gwh"))
)
print(latest.head(10))
```

# Caveats

## 01 Indicator string is exact-case

Vendor rejects `firm available`; connector sends literal `"Firm Available"`. *(Source: `OPERATIONAL_INDICATORS["firm_available"] = "Firm Available"` `connectors/entsog/endpoints.py L100`.)*

## 02 Capacity windows can span years

`period_from`/`period_to` may bracket multi-year firm products. Filter to as-of-date when extracting "current" capacity. *(Source: vault Bronze sample L101-102.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

`HTTP 404 + {"message":"No result found"}` empty convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 `is_unlimited` is string `"0"`/`"1"`, not bool

Vendor returns text — cast as needed in downstream code. *(Source: vault Bronze sample L115.)*

# Related datasets

- **`firm_booked`** — Capacity already booked by shippers. `daily`. Compute headroom: `firm_available - firm_booked`. *entsog · capacity · daily*
- **`firm_technical`** — Maximum technical capacity. `daily`. The upstream constraint behind `firm_available`. *entsog · capacity · daily*
- **`interruptible_available`** — Interruptible capacity (firm-on-condition). `daily`. Pair for total offered-capacity view. *entsog · capacity · daily*
- **`available_through_oversubscription`** — Oversubscription-mechanism extra capacity. `daily`. CMP-related supplement to firm. *entsog · capacity · daily*
