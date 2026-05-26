---
slug: nominations
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/Nomination
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/nominations.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — registered via `_make_transformer_class` at L223-238
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["nominations"] (line 97) + ENDPOINTS (lines 118-125)
  - .planning/reconciliation/entsog/26-nominations-manual-transformer-schema.md (wontfix v3-candidate — confirms dynamic-schema is by design)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Day-ahead nominations at <span class="italic fg-accent">each pipeline point.</span>

**Lede:** Shipper-submitted day-ahead nominations per operator-point-direction — the canonical pre-allocation signal for gas-supply tightness and CCGT dispatch likelihood.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.nominations` |
| API PATH | `/api/v1/operationalData?indicator=Nomination` |
| FREQUENCY | daily (gas day) |
| PUBLICATION LAG | same-day (day-ahead nomination) |
| VOLUME | ~9 GB points/day (default filter) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | day-ahead | Cadence relative to delivery |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- physical_flows
- renominations
- allocations
- firm_booked
- interruptible_booked

# Sample chart

- **Type:** `sparkline`
- **Title:** "Bacton (IUK) exit · daily nominations"
- **Subtitle:** "Sparkline · GWh/day · 30-day window"
- **Seed:** 23
- **Toggles:** `30d` (active) / `1y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically from the live response (`silver/entsog/generic.py L80`). Vault Bronze sample (live 2026-05-08) carries 35 columns; key fields below.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `periodFrom` (derived) | Set from `periodFrom` via priority list. | `silver/entsog/generic.py L118-120` |
| `period_from` / `period_to` | `datetime[UTC]` | Yes | `periodFrom` / `periodTo` | Gas-day window; `+02:00`/`+01:00` vendor offsets converted to UTC. | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Nomination"` for this endpoint. | dynamic |
| `period_type` | `str` | Yes | `periodType` | `"day"` default. | dynamic |
| `operator_key` / `operator_label` / `tso_eic_code` | `str` | Yes | `operatorKey` / `operatorLabel` / `tsoEicCode` | TSO identifiers. | dynamic |
| `point_key` / `point_label` / `tso_item_identifier` | `str` | Yes | `pointKey` / `pointLabel` / `tsoItemIdentifier` | Connection-point identifiers. | dynamic |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` / `"exit"` (lowercase here). | dynamic |
| `unit` | `str` | Yes | `unit` | Vendor unit string (typically `"kWh/d"`). | dynamic |
| `value` | `float` | Yes | `value` | Nominated quantity in `unit`. | `silver/entsog/generic.py L122-124` (`_looks_numeric`) |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. May be empty/`"-"`/`"N/A"`. | `silver/entsog/datetime.py::parse_entsog_datetime_expr` |
| `flow_status` | `str` | Yes | `flowStatus` | Often empty for nominations (allocations/physical_flows carry the status). | dynamic |
| `is_cam_relevant` / `is_cmp_relevant` | `bool` | Yes | `isCamRelevant` / `isCmpRelevant` | Regulatory flags. | dynamic |
| `booking_platform_key` / `_label` / `_url` | `str` | Yes | `bookingPlatformKey` / `_Label` / `_URL` | E.g. `"PRISMA"`. | dynamic |
| `original_period_from` | `datetime[UTC]` | Yes | `originalPeriodFrom` | Set for revisions. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/nominations/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation (`silver/entsog/generic.py L126-130`)

# Sample data

| period_from | point_key | point_label | operator_key | direction_key | unit | value | flow_status | last_update_date_time |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | UK-TSO-0001 | exit | kWh/d | 15,282,000 | (empty) | 2026-05-06T16:02:09+00:00 |
| 2026-05-06T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | UK-TSO-0003 | entry | kWh/d | 14,950,000 | (empty) | 2026-05-06T16:02:09+00:00 |
| **2026-05-06T04:00:00+00:00** | **ITP-00207** | **Bacton (BBL)** | **UK-TSO-0001** | **exit** | **kWh/d** | **149,200,000** | **(empty)** | **2026-05-06T16:02:09+00:00** |
| 2026-05-06T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | UK-TSO-0004 | entry | kWh/d | 146,800,000 | (empty) | 2026-05-06T16:02:09+00:00 |
| 2026-05-06T04:00:00+00:00 | ITP-00495 | Moffat (IE) | IE-TSO-0002 | entry | kWh/d | 88,500,000 | (empty) | 2026-05-06T16:02:09+00:00 |
| 2026-05-06T04:00:00+00:00 | ITP-00090 | Moffat | UK-TSO-0001 | entry | kWh/d | 0 | (empty) | 2026-05-06T16:02:09+00:00 |
| 2026-05-05T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | UK-TSO-0001 | exit | kWh/d | 12,500,000 | (empty) | 2026-05-05T16:02:09+00:00 |
| 2026-05-05T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | UK-TSO-0001 | exit | kWh/d | 142,200,000 | (empty) | 2026-05-05T16:02:09+00:00 |

**Sources:** First row verbatim from vault Bronze sample (`nominations.md` L113; `value=15282000` kWh/d at Bacton IUK exit). Remaining rows synthesised — respect the vendor's `kWh/d` unit and the typical Bacton/Moffat magnitude. Highlighted row is BBL exit nomination = 149 GWh/day, the dominant GB-to-NL pipeline flow signal. Note `flow_status` is empty in nominations (the booked/expected signal sits in `value` itself; status accrues for `physical_flows` and `allocations`).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Nomination&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/nominations/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `NominationsTransformer` via factory at `silver/entsog/generic.py L223-238`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Nomination&periodType=day&pointDirection=UK-TSO-0001ITP-00005exit&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- 30-day Bacton exit nominations vs actual physical flow (join to physical_flows)
SELECT n.period_from::date AS gas_day,
       n.point_key,
       n.value / 1e6 AS nominated_gwh,
       p.flow_gwh_per_day AS actual_gwh
FROM read_parquet('data/silver/entsog/nominations/**/*.parquet') n
JOIN read_parquet('data/silver/entsog/physical_flows/**/*.parquet') p
  ON  n.period_from = p.timestamp_utc
  AND n.point_key   = p.point_key
  AND n.direction_key = p.direction_key
WHERE n.point_key = 'ITP-00005'
  AND n.direction_key = 'exit'
  AND n.period_from >= current_date - INTERVAL 30 DAY
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/nominations/**/*.parquet")
# Daily aggregate nomination by GB direction
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

Vendor rejects `nomination` / `Nominations`; connector sends literal `"Nomination"`. *(Source: vault Known Issues; `OPERATIONAL_INDICATORS["nominations"] = "Nomination"` `connectors/entsog/endpoints.py L97`.)*

## 02 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`; sending `UTC` returns HTTP 400. *(Source: `connectors/entsog/endpoints.py L17` `ENTSOG_TIMEZONE`.)*

## 03 Empty windows return HTTP 404, not 200

ENTSO-G's empty convention is `HTTP 404 + {"message":"No result found"}`. Connector short-circuits as empty-bronze. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 04 Nominations precede allocations

A `Nomination` row is a shipper request; the eventual delivery sits in `Allocation` and `Physical Flow`. Join all three on `(timestamp_utc, point_key, operator_key, direction_key)` for nomination-vs-actual analysis. *(Source: vault Modelling notes; ENTSO-G data dictionary.)*

## 05 `flow_status` is typically empty for nominations

Unlike `physical_flows` (which carries `Provisional`/`Confirmed`), nominations are a single point-in-time submission and the `flow_status` field is generally empty. *(Source: vault Bronze sample L117.)*

## 06 Period offset is CEST/CET even with `timeZone=UCT`

Despite requesting UCT, `periodFrom`/`periodTo` carry `+02:00` / `+01:00`. `parse_entsog_datetime_expr` converts to UTC at silver. *(Source: `silver/entsog/datetime.py`; vault Known Issues.)*

# Related datasets

- **`physical_flows`** — Realised flow corresponding to these nominations. `daily`. The nomination-vs-actual delta is the canonical short-term gas signal. *entsog · operational · daily*
- **`renominations`** — Within-gas-day revisions to nominations. `daily`. Captures shipper adjustments after the day-ahead window closes. *entsog · operational · daily*
- **`allocations`** — Post-flow allocation (final settled quantity). `daily`. The settlement-grade counterpart to nominations. *entsog · operational · daily*
- **`firm_booked`** — Booked capacity backing these nominations. `daily`. Constraint check: nominations should not exceed booked capacity. *entsog · capacity · daily*
