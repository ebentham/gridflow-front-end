---
slug: interruptible_available
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/InterruptibleAvailable
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/interruptible_available.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["interruptible_available"] (line 103) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/23-interruptible-available-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Interruptible capacity available <span class="italic fg-accent">for booking.</span>

**Lede:** Interruptible-product capacity offered per operator-point-direction — the canonical signal for capacity available only when firm capacity is not curtailed.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.interruptible_available` |
| API PATH | `/api/v1/operationalData?indicator=Interruptible%20Available` |
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

- interruptible_booked
- interruptible_total
- firm_available
- available_through_uioli_short_term
- available_through_uioli_long_term

# Sample chart

- **Type:** `sparkline`
- **Title:** "Bacton (IUK) exit · interruptible available capacity"
- **Subtitle:** "Sparkline · GWh/day · 30-day window"
- **Seed:** 26
- **Toggles:** `30d` (active) / `1y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same operational-data shape; differentiator is `indicator="Interruptible Available"` and `capacity_type="Interruptible"`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Validity window. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Interruptible Available"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction tuple. | dynamic |
| `capacity_type` | `str` | Yes | `capacityType` | `"Interruptible"`. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"` typically. | dynamic |
| `value` | `float` | Yes | `value` | Available interruptible capacity. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/interruptible_available/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | period_to | point_key | direction_key | capacity_type | unit | value |
|---|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | exit | Interruptible | kWh/d | 95,000,000 |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | entry | Interruptible | kWh/d | 110,000,000 |
| **2025-10-01T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **ITP-00207** | **exit** | **Interruptible** | **kWh/d** | **20,000,000** |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00207 | entry | Interruptible | kWh/d | 25,000,000 |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00495 | entry | Interruptible | kWh/d | 8,000,000 |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00495 | exit | Interruptible | kWh/d | 12,000,000 |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00090 | entry | Interruptible | kWh/d | 5,000,000 |
| 2026-04-01T04:00:00+00:00 | 2026-07-01T04:00:00+00:00 | ITP-00005 | exit | Interruptible | kWh/d | 30,000,000 |

**Sources:** Synthesised — interruptible capacity is typically much smaller than firm at GB points (the firm allocation dominates). Highlighted row is BBL exit interruptible at 20 GWh/d — about 10% of the 200 GWh/d technical capacity. Quarterly product on the last row (2026-04-01 to 2026-07-01) demonstrates that short-product overlay alongside annual product.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Interruptible Available&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/interruptible_available/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `InterruptibleAvailableTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Interruptible%20Available&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Total offered capacity per point (firm + interruptible) as-of today
SELECT a.point_key, a.direction_key,
       (a.value + COALESCE(i.value, 0)) / 1e6 AS total_offered_gwh
FROM read_parquet('data/silver/entsog/firm_available/**/*.parquet') a
LEFT JOIN read_parquet('data/silver/entsog/interruptible_available/**/*.parquet') i
  ON  a.point_key = i.point_key
  AND a.direction_key = i.direction_key
  AND i.period_from <= current_date AND i.period_to > current_date
WHERE a.period_from <= current_date AND a.period_to > current_date
ORDER BY total_offered_gwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/interruptible_available/**/*.parquet")
# Latest interruptible offered per point
latest = (
    df.sort("last_update_date_time", descending=True)
      .group_by(["point_key", "direction_key"])
      .agg(pl.col("value").first().alias("kwh_per_day"))
)
print(latest)
```

# Caveats

## 01 Indicator string is exact-case

Connector sends literal `"Interruptible Available"`. *(Source: `OPERATIONAL_INDICATORS["interruptible_available"] = "Interruptible Available"` `connectors/entsog/endpoints.py L103`.)*

## 02 Interruptible is subordinate to firm

Interruptible capacity is curtailed first when system stress exceeds firm. Don't model interruptible-booked as guaranteed delivery. *(Source: domain knowledge / vault Modelling notes.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 GB interruptible is small relative to firm

Bacton/Moffat firm dominates; interruptible is typically <15% of technical capacity. *(Source: vault Modelling notes; documented kWh/d magnitudes.)*

# Related datasets

- **`interruptible_booked`** — Booked interruptible. `daily`. Pair to compute interruptible utilisation. *entsog · capacity · daily*
- **`interruptible_total`** — Total interruptible offered (firm-equivalent capacity). `daily`. Sometimes equals or exceeds `interruptible_available`. *entsog · capacity · daily*
- **`firm_available`** — Firm-product available. `daily`. Total offered = firm + interruptible. *entsog · capacity · daily*
- **`available_through_uioli_short_term`** — UIOLI short-term capacity (interruptible-adjacent). `daily`. Pair when modelling CMP mechanisms. *entsog · capacity · daily*
