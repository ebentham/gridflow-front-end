---
slug: physical_flows
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operationalData/PhysicalFlow
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/physical_flows.md
  - gridflow/src/gridflow/schemas/entsog.py::EntsogPhysicalFlow (lines 12-30)
  - gridflow/src/gridflow/silver/entsog/physical_flows.py::PhysicalFlowsTransformer (lines 36-162)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::OPERATIONAL_INDICATORS["physical_flows"] (line 96) + ENDPOINTS (lines 118-125)
  - gridflow/src/gridflow/connectors/entsog/client.py::EntsogConnector (lines 31-117) — 404 'No result found' short-circuit
  - .planning/reconciliation/entsog/05-physical-flows-schema-table-rewrite.md (closed 2026-05-19 — vault table rewritten to canonical 8-field shape)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Physical gas flows at each <span class="italic fg-accent">interconnection point.</span>

**Lede:** Daily physical gas throughput per operator-point-direction — the canonical observation for European cross-border gas flow, supply tightness, and storage-cycle attribution.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operationalData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.physical_flows` |
| API PATH | `/api/v1/operationalData?indicator=Physical%20Flow` |
| FREQUENCY | daily (gas day) |
| PUBLICATION LAG | same-day (Provisional) → ~1 week (Confirmed) |
| VOLUME | ~9 points/day default; full-system on demand |
| PRIMARY KEY | `(timestamp_utc, point_key, operator_key, direction_key)` |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | same-day | Publication lag |
| 3 | 1 | Typed Pydantic schema (only one in ENTSO-G) |
| 4 | 10 | Silver columns |

# Sidebar siblings

- aggregated_physical_flows
- nominations
- allocations
- renominations
- firm_available

# Sample chart

- **Type:** `sparkline`
- **Title:** "Bacton (IUK) exit · daily physical flow"
- **Subtitle:** "Sparkline · GWh/day · 30-day window"
- **Seed:** 21
- **Toggles:** `30d` (active) / `1y`

# Schema

Defined in `gridflow/schemas/entsog.py` · `EntsogPhysicalFlow` (lines 12-30). Silver transformer (`PhysicalFlowsTransformer`) converts the vendor `value`+`unit` pair into a normalised `flow_gwh_per_day` column. The only ENTSO-G dataset with a typed Pydantic class.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `timestamp_utc` | `datetime[UTC]` | No | `periodFrom` | tz-aware UTC; vendor sends `+02:00` (CEST) / `+01:00` (CET) — `parse_entsog_datetime_expr` normalises. Validator requires tzinfo. | `schemas/entsog.py L15, L25-30`; `silver/entsog/physical_flows.py L87-89` |
| `point_key` | `str` | No | `pointKey` | Connection-point identifier (e.g. `ITP-00005` = Bacton IUK). Required. | `schemas/entsog.py L16`; `silver/entsog/physical_flows.py L73-74` |
| `point_label` | `str` (default `""`) | Yes (default empty) | `pointLabel` | Human-readable point name (e.g. `"Bacton (IUK)"`). | `schemas/entsog.py L17` |
| `operator_key` | `str` (default `""`) | Yes (default empty) | `operatorKey` | TSO identifier (e.g. `UK-TSO-0001` = National Gas TSO). | `schemas/entsog.py L18` |
| `operator_label` | `str` (default `""`) | Yes (default empty) | `operatorLabel` | TSO human name. | `schemas/entsog.py L19` |
| `direction_key` | `str` (default `""`) | Yes (default empty) | `directionKey` | `"entry"` or `"exit"` (lowercase in `/operationalData`). | `schemas/entsog.py L20` |
| `flow_gwh_per_day` | `float` (default `0.0`) | No | derived from `value`+`unit` | Normalised to GWh/day. `kWh/d ÷ 1e6`; `kWh/h × 24 ÷ 1e6`. | `schemas/entsog.py L21`; `silver/entsog/physical_flows.py L24-33, L106-128` |
| `unit` | `str` (default `""`) | Yes (default empty) | `unit` | Raw vendor unit string (e.g. `"kWh/d"`). Preserved for audit. | `schemas/entsog.py L22` |
| `data_provider` | `str` (default `"entsog"`) | No | _constant_ | Always `"entsog"`. | `schemas/entsog.py L23` |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Wall-clock at silver write. | `silver/entsog/physical_flows.py L137-141` |

**PARQUET PATH:** `data/silver/entsog/physical_flows/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(timestamp_utc, point_key, operator_key, direction_key)` — keep last (`silver/entsog/physical_flows.py L130-135`)

# Sample data

| timestamp_utc | point_key | point_label | operator_key | direction_key | flow_gwh_per_day | unit | data_provider |
|---|---|---|---|---|---|---|---|
| 2026-05-06T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | UK-TSO-0001 | exit | 203.102928 | kWh/d | entsog |
| 2026-05-06T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | UK-TSO-0003 | entry | 198.450 | kWh/d | entsog |
| 2026-05-06T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | UK-TSO-0001 | exit | 152.380 | kWh/d | entsog |
| **2026-05-06T04:00:00+00:00** | **ITP-00207** | **Bacton (BBL)** | **UK-TSO-0004** | **entry** | **149.220** | **kWh/d** | **entsog** |
| 2026-05-06T04:00:00+00:00 | ITP-00495 | Moffat (IE) | IE-TSO-0002 | entry | 88.720 | kWh/d | entsog |
| 2026-05-06T04:00:00+00:00 | ITP-00090 | Moffat | UK-TSO-0001 | entry | 0.000 | kWh/d | entsog |
| 2026-05-05T04:00:00+00:00 | ITP-00005 | Bacton (IUK) | UK-TSO-0001 | exit | 187.310 | kWh/d | entsog |
| 2026-05-05T04:00:00+00:00 | ITP-00207 | Bacton (BBL) | UK-TSO-0001 | exit | 142.880 | kWh/d | entsog |

**Sources:** First row verbatim from vault Bronze sample (`physical_flows.md` L114; vendor `value=203102928` kWh/d → silver `203.102928` GWh/d). Remaining rows synthesised respecting the schema (positive entry, positive exit; ~150 GWh/d typical Bacton flow). Highlighted row is BBL entry into UK — the counter-flow visible when continental gas was being imported in early May 2026. Note both sides of an interconnector show as `exit` (UK side) and `entry` (counterparty side) — pair these for net-flow analysis.

# Interconnection points (DEFAULT_POINT_DIRECTIONS · GB/IE focus)

The connector deliberately omits the `pointDirection` filter for `physical_flows` to capture a full-system snapshot. The 9 keys below are the default GB/IE focus used by every other operational dataset.

- `UK-TSO-0001ITP-00005exit` — Bacton (IUK) · National Gas TSO exit
- `UK-TSO-0003ITP-00005entry` · `UK-TSO-0003ITP-00005exit` — Bacton (IUK) · Interconnector entry/exit
- `UK-TSO-0001ITP-00207exit` — Bacton (BBL) · National Gas TSO exit
- `UK-TSO-0004ITP-00063entry` · `UK-TSO-0004ITP-00063exit` — Julianadorp/Balgzand (BBL) · Dutch side
- `IE-TSO-0002ITP-00495entry` · `IE-TSO-0002ITP-00495exit` — Moffat (IE) · Gas Networks Ireland
- `UK-TSO-0001ITP-00090entry` — Moffat · National Gas TSO entry

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operationalData?indicator=Physical Flow&from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/physical_flows/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.physical_flows.PhysicalFlowsTransformer`

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Physical%20Flow&periodType=day&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Daily net flow into GB across Bacton + Moffat (last 30 days)
SELECT timestamp_utc::date AS gas_day,
       SUM(CASE WHEN direction_key = 'entry' THEN flow_gwh_per_day
                WHEN direction_key = 'exit'  THEN -flow_gwh_per_day END) AS net_gb_gwh
FROM read_parquet('data/silver/entsog/physical_flows/**/*.parquet')
WHERE operator_key = 'UK-TSO-0001'
  AND point_key IN ('ITP-00005', 'ITP-00207', 'ITP-00090')
  AND timestamp_utc >= current_date - INTERVAL 30 DAY
GROUP BY 1
ORDER BY 1;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/physical_flows/**/*.parquet")
# Pivot to per-point daily flow
wide = df.pivot(
    index="timestamp_utc", on="point_key",
    values="flow_gwh_per_day", aggregate_function="sum",
).sort("timestamp_utc")
print(wide.tail(7))
```

# Caveats

## 01 Indicator string is exact-case

Vendor rejects `physical flow` / `physical-flow`; connector sends literal `"Physical Flow"`. *(Source: vault Known Issues; `connectors/entsog/endpoints.py L96` `PHYSICAL_FLOW_INDICATOR`.)*

## 02 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`; sending `UTC` returns HTTP 400. Response `meta.timezone` echoes `"CET"` regardless. *(Source: `connectors/entsog/endpoints.py L17` `ENTSOG_TIMEZONE`.)*

## 03 Connector drops `pointDirection` for full-system fetch

Unlike sibling operational endpoints (which attach `DEFAULT_POINT_DIRECTIONS`), `physical_flows` deliberately omits the filter and returns every point per call. *(Source: `connectors/entsog/endpoints.py L122` and vault Known Issues.)*

## 04 Empty windows return HTTP 404, not 200

ENTSO-G's empty-set convention is `HTTP 404 + {"message":"No result found"}`. Connector short-circuits this as "empty bronze" — never as an error. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Storage flows are signed by direction (not by sign)

A storage facility's withdrawal appears as `direction_key="entry"` into the gas-grid zone; injection appears as `"exit"`. The numeric `flow_gwh_per_day` stays positive — sign convention lives in `direction_key`. *(Source: domain knowledge / vault Modelling notes.)*

## 06 `flowStatus` switches Provisional → Confirmed within ~1 week

Filter on `flowStatus = "Confirmed"` for backtests; `Provisional` (vendor preserves alongside `"Provisionnal"` typo elsewhere) for live model serving. *(Source: vault Known Issues.)*

# Related datasets

- **`aggregated_physical_flows`** — Zone-level rollup of the same flows. `daily`. Use when point-level resolution is too granular; cross-check the `points_names` list. *entsog · zone · daily*
- **`nominations`** — Day-ahead shipper-requested flows at the same points. `daily`. Pair with this dataset to measure nomination-vs-actual delivery accuracy. *entsog · operational · daily*
- **`storage`** (GIE-AGSI) — EU gas storage levels. `daily`. Pair Bacton/Moffat entry flows with storage withdrawal for GB supply-adequacy analysis. *gie · storage · daily*
- **`fuelhh`** (Elexon) — GB CCGT generation. `30 min`. Closes the gas-to-power chain: gas entering at Bacton → GB CCGT MW. *elexon · generation · 30 min*
