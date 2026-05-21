---
slug: firm_technical
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/FirmTechnical
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/firm_technical.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["firm_technical"] (line 102) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/20-firm-technical-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Maximum technical capacity at <span class="italic fg-accent">each point.</span>

**Lede:** Physical-pipeline maximum throughput per operator-point-direction — the canonical upper bound for all capacity-availability and flow calculations.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.firm_technical` |
| API PATH | `/api/v1/operationalData?indicator=Firm%20Technical` |
| FREQUENCY | daily (rarely changes) |
| PUBLICATION LAG | same-day on change |
| VOLUME | ~9 GB points/day (default filter) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | technical | Capacity-type (physical max) |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- firm_available
- firm_booked
- interruptible_total
- available_through_oversubscription
- connection_points

# Sample chart

- **Type:** `barsH`
- **Title:** "GB interconnection points · technical capacity"
- **Subtitle:** "Horizontal bars · GWh/day · current"
- **Seed:** 17
- **Toggles:** `current` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same canonical operational-data shape; differentiator is `indicator="Firm Technical"`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Validity window (often multi-year for technical capacity). | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Firm Technical"`. | dynamic |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction tuple. | dynamic |
| `capacity_type` | `str` | Yes | `capacityType` | `"Firm"` (technical-firm). | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"` typically. | dynamic |
| `value` | `float` | Yes | `value` | Technical maximum. | `silver/entsog/generic.py L122-124` |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/firm_technical/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| period_from | period_to | point_key | direction_key | unit | value |
|---|---|---|---|---|---|
| 2022-01-01T05:00:00+00:00 | 2028-05-01T04:00:00+00:00 | ITP-00005 | exit | kWh/d | 580,000,000 |
| 2022-01-01T05:00:00+00:00 | 2028-05-01T04:00:00+00:00 | ITP-00005 | entry | kWh/d | 590,000,000 |
| **2022-01-01T05:00:00+00:00** | **2028-05-01T04:00:00+00:00** | **ITP-00207** | **exit** | **kWh/d** | **200,000,000** |
| 2022-01-01T05:00:00+00:00 | 2028-05-01T04:00:00+00:00 | ITP-00207 | entry | kWh/d | 200,000,000 |
| 2022-01-01T05:00:00+00:00 | 2028-05-01T04:00:00+00:00 | ITP-00495 | entry | kWh/d | 100,000,000 |
| 2022-01-01T05:00:00+00:00 | 2028-05-01T04:00:00+00:00 | ITP-00495 | exit | kWh/d | 100,000,000 |
| 2022-01-01T05:00:00+00:00 | 2028-05-01T04:00:00+00:00 | ITP-00090 | entry | kWh/d | 80,000,000 |
| 2022-01-01T05:00:00+00:00 | 2028-05-01T04:00:00+00:00 | ITP-00063 | entry | kWh/d | 200,000,000 |

**Sources:** Synthesised — vault's documented multi-year capacity-validity shape applied to canonical Bacton/Moffat technical capacities (Bacton IUK ~580 GWh/d each way, BBL ~200 GWh/d, Moffat ~100 GWh/d). Highlighted row is BBL exit at 200 GWh/d — the physical upper bound that `firm_available` (180 GWh/d) and `firm_booked` (172 GWh/d) live underneath.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Firm Technical&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/firm_technical/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `FirmTechnicalTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Firm%20Technical&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Spare technical capacity vs current firm available (slack vs total)
WITH t AS (
  SELECT point_key, direction_key,
         MAX_BY(value, period_from) AS tech_kwh
  FROM read_parquet('data/silver/entsog/firm_technical/**/*.parquet')
  WHERE period_from <= current_date AND period_to > current_date
  GROUP BY 1, 2
),
a AS (
  SELECT point_key, direction_key,
         MAX_BY(value, period_from) AS avail_kwh
  FROM read_parquet('data/silver/entsog/firm_available/**/*.parquet')
  WHERE period_from <= current_date AND period_to > current_date
  GROUP BY 1, 2
)
SELECT t.point_key, t.direction_key,
       t.tech_kwh / 1e6 AS technical_gwh,
       a.avail_kwh / 1e6 AS firm_avail_gwh,
       (t.tech_kwh - a.avail_kwh) / 1e6 AS reserved_gwh
FROM t JOIN a USING (point_key, direction_key)
ORDER BY technical_gwh DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/firm_technical/**/*.parquet")
# Latest technical capacity per point/direction
latest = (
    df.sort("last_update_date_time", descending=True)
      .group_by(["point_key", "direction_key"])
      .agg(pl.col("value").first().alias("kwh_per_day"))
      .with_columns((pl.col("kwh_per_day") / 1e6).alias("gwh_per_day"))
      .sort("gwh_per_day", descending=True)
)
print(latest)
```

# Caveats

## 01 Indicator string is exact-case

Connector sends literal `"Firm Technical"`. *(Source: `OPERATIONAL_INDICATORS["firm_technical"] = "Firm Technical"` `connectors/entsog/endpoints.py L102`.)*

## 02 Technical capacity rarely changes

Long-validity multi-year products; most days return the same row as the previous day. Dedup on `id` to avoid double-counting. *(Source: `silver/entsog/generic.py L126-130`.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Upper bound on `firm_available`

By definition `firm_technical >= firm_available + firm_reserved_for_TSO_usage`. Use as the physical ceiling in capacity-allocation models. *(Source: domain knowledge / ENTSO-G data dictionary.)*

# Related datasets

- **`firm_available`** — Available capacity offered to shippers. `daily`. Below technical. *entsog · capacity · daily*
- **`firm_booked`** — Booked capacity. `daily`. Below available. *entsog · capacity · daily*
- **`interruptible_total`** — Total interruptible offered. `daily`. Complement to firm. *entsog · capacity · daily*
- **`connection_points`** — Reference data for the point identifiers. `snapshot`. Resolve `point_key` to physical-asset descriptions. *entsog · reference · snapshot*
