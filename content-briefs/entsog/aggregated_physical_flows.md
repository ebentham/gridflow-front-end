---
slug: aggregated_physical_flows
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: aggregatedData
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/aggregated_physical_flows.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — registered via `_make_transformer_class` at L223-238
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["aggregated_physical_flows"] (lines 167-179)
  - .planning/reconciliation/entsog/07-aggregated-physical-flows-manual-transformer-schema.md (wontfix v3-candidate — confirms dynamic-schema is by design)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Cross-border gas flows, <span class="italic fg-accent">zone by zone.</span>

**Lede:** Daily aggregated zone-level gas flows by adjacent system — the canonical EU view of Production, Storage, LNG, and cross-border flows for balancing-zone modelling.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /aggregatedData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.aggregated_physical_flows` |
| API PATH | `/api/v1/aggregatedData` |
| FREQUENCY | daily (gas day) |
| PUBLICATION LAG | ~1-2 days (Provisionnal → Final) |
| VOLUME | ~5 zone-directions/day (GB default); ~1k EU-wide |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | 5 | Adjacent system categories |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- physical_flows
- nominations
- allocations
- interruptions
- balancing_zones

# Sample chart

- **Type:** `barsH`
- **Title:** "British Balancing Zone · daily entry by adjacent system"
- **Subtitle:** "Horizontal bars · GWh/day · last 30 days"
- **Seed:** 13
- **Toggles:** `30d` (active) / `1y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically from the live response (`silver/entsog/generic.py L80`). Vault Bronze sample (live 2026-05-08) carries the fields below. Partitioned by `period_from`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation: `dataSet+Aggregates+countryKey+bzKey+operatorKey+directionKey+adjacentSystemsKey+periodFrom+periodTo+indicator`. Dedup key. | `silver/entsog/generic.py L126-130` |
| `period_from` | `datetime[UTC]` | Yes | `periodFrom` | Gas-day start. Vendor sends `+02:00`/`+01:00`; transformer converts to UTC. | `silver/entsog/generic.py L114-116, L28-44` |
| `period_to` | `datetime[UTC]` | Yes | `periodTo` | Gas-day end (same TZ behaviour). | `silver/entsog/generic.py L114-116` |
| `indicator` | `str` | Yes | `indicator` | Always `"Physical Flow"` for this endpoint. | dynamic |
| `country_key` | `str` | Yes | `countryKey` | ISO-style country code (`"UK"`, `"DE"`, `"FR"`). | dynamic |
| `bz_key` / `bz_short` / `bz_long` | `str` | Yes | `bzKey` / `bzShort` / `bzLong` | Balancing-zone identifiers (`"UK---------"`, `"UK"`, `"British Balancing Zone"`). | dynamic |
| `operator_key` / `operator_label` | `str` | Yes | `operatorKey` / `operatorLabel` | TSO identifier and human name (`"UK-TSO-0001"` = National Gas TSO). | dynamic |
| `tso_eic_code` | `str` | Yes | `tsoEicCode` | EIC cross-reference to ENTSO-E datasets. | dynamic |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` / `"exit"` (lowercase here; capitalised in `/cmpUnsuccessfulRequests`). | dynamic |
| `adjacent_systems_key` / `adjacent_systems_label` | `str` | Yes | `adjacentSystemsKey` / `adjacentSystemsLabel` | Counterparty category — `"Production"`, `"Storage"`, `"LNG Terminals"`, `"Distribution"`, or zone-pair keys. | dynamic |
| `unit` | `str` | Yes | `unit` | Always `"kWh/d"` — gas convention, NOT MWh. | dynamic |
| `value` | `float` | Yes | `value` | Flow value in declared `unit`. | `silver/entsog/generic.py L122-124` (`_looks_numeric`) |
| `count_point_presents` | `float` | Yes | `countPointPresents` | Number of physical points contributing to the aggregate. | dynamic |
| `flow_status` | `str` | Yes | `flowStatus` | `"Provisionnal"` (vendor typo preserved) or `"Final"`. | dynamic |
| `points_names` | `str` | Yes | `pointsNames` | `\|`-delimited contributing point names. | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp; may be `""`, `"-"`, `"N/A"`. | `silver/entsog/datetime.py::parse_entsog_datetime_expr` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/aggregated_physical_flows/year=YYYY/month=MM/`
**PARTITION BY:** `period_from (year + month)`
**DEDUP KEY:** `(id)` — falls back to all non-`timestamp_utc` columns if `id` is absent (`silver/entsog/generic.py L126-130`)

# Sample data

| period_from | country_key | bz_short | operator_key | direction_key | adjacent_systems_key | unit | value | flow_status |
|---|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | UK | UK | UK-TSO-0001 | entry | LNG Terminals | kWh/d | 100,259,283 | Provisionnal |
| 2026-05-06T00:00:00+00:00 | UK | UK | UK-TSO-0001 | entry | Production | kWh/d | 287,440,000 | Provisionnal |
| **2026-05-06T00:00:00+00:00** | **UK** | **UK** | **UK-TSO-0001** | **exit** | **Distribution** | **kWh/d** | **412,800,000** | **Provisionnal** |
| 2026-05-06T00:00:00+00:00 | UK | UK | UK-TSO-0001 | entry | Storage | kWh/d | 18,200,000 | Provisionnal |
| 2026-05-06T00:00:00+00:00 | DE | DE | DE-TSO-0011 | entry | Production | kWh/d | 1,140,000,000 | Final |
| 2026-05-06T00:00:00+00:00 | DE | DE | DE-TSO-0011 | exit | Distribution | kWh/d | 2,038,000,000 | Final |
| 2026-05-06T00:00:00+00:00 | FR | FR | FR-TSO-0001 | entry | LNG Terminals | kWh/d | 312,500,000 | Provisionnal |
| 2026-05-06T00:00:00+00:00 | NL | NL | NL-TSO-0001 | entry | Production | kWh/d | 487,200,000 | Final |

**Sources:** First UK row verbatim from vault Bronze sample (LNG entry, 2026-05-06); remaining UK rows synthesised respecting documented `adjacent_systems_key` categories. Continental rows synthesised to plausible 2026 daily flows. Highlighted row is UK Distribution exit — 412 GWh/day = the dominant outflow (gas going to domestic/industrial consumers). `kWh/d` unit throughout (NOT MWh — divide by 1000 if joining against power-market datasets). `flowStatus: Provisionnal` typo preserved.

# Adjacent system categories (codelist)

| Key | Meaning | Typical sign convention |
|---|---|---|
| `Production` | Domestic gas-production wells entering the network | entry |
| `Storage` | Storage facilities (injection = exit, withdrawal = entry) | both, seasonal |
| `LNG Terminals` | LNG regasification terminals | entry |
| `Distribution` | Downstream distribution networks (final consumers) | exit |
| `Final consumer` | Direct industrial offtake | exit |
| `<ZoneKey>` (e.g. `UK---------`) | Cross-border aggregate to neighbouring TSO zone | both |

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/aggregatedData?from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&forceDownload=true&limit=-1`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/aggregated_physical_flows/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `AggregatedPhysicalFlowsTransformer` via factory at `silver/entsog/generic.py L223-238`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/aggregatedData?from=2026-05-06&to=2026-05-06&timeZone=UCT&periodType=day&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- UK monthly LNG-vs-Production entry mix
SELECT date_trunc('month', period_from) AS month,
       adjacent_systems_key,
       SUM(value) / 1e9 AS twh
FROM read_parquet('data/silver/entsog/aggregated_physical_flows/**/*.parquet')
WHERE bz_short = 'UK'
  AND direction_key = 'entry'
  AND adjacent_systems_key IN ('LNG Terminals', 'Production', 'Storage')
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/aggregated_physical_flows/**/*.parquet")
# UK daily net flow (entry - exit) across all adjacent systems
net = (
    df.filter(pl.col("bz_short") == "UK")
      .with_columns(
          pl.when(pl.col("direction_key") == "entry")
            .then(pl.col("value"))
            .otherwise(-pl.col("value"))
            .alias("signed_kwh")
      )
      .group_by("period_from")
      .agg(pl.col("signed_kwh").sum().alias("net_kwh"))
      .sort("period_from")
)
print(net.tail(30))
```

# Caveats

## 01 Unit is `kWh/d`, NOT MWh

ENTSO-G reports gas flows in **kWh/day**. Divide by 1,000 for MWh; by 1e9 for TWh. Preserve the `unit` column rather than assuming. *(Source: vault Silver schema; `unit` constant.)*

## 02 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`; sending `UTC` returns HTTP 400. *(Source: `connectors/entsog/endpoints.py L17` `ENTSOG_TIMEZONE`.)*

## 03 `direction_key` casing varies across endpoints

Lowercase here (`"entry"`, `"exit"`); capitalised in `/cmpUnsuccessfulRequests`. Lowercase both sides when cross-endpoint joining. *(Source: vault Known Issues; `silver/entsog/generic.py::_normalise_column_names`.)*

## 04 `flow_status: "Provisionnal"` preserved verbatim

Vendor spelling `Provisionnal` (double-n) is preserved through bronze and silver. Filter on the exact string to distinguish from `"Final"`. *(Source: vault Known Issues; vendor JSON.)*

## 05 Period offset is CEST/CET even with `timeZone=UCT`

Despite requesting UCT, `periodFrom`/`periodTo` carry `+02:00` (CEST) / `+01:00` (CET). `parse_entsog_datetime_expr` converts to UTC at silver. *(Source: `silver/entsog/datetime.py`; vault Known Issues.)*

## 06 Empty windows return HTTP 404, not 200

ENTSO-G's empty convention is `HTTP 404 + {"message":"No result found"}`. Connector short-circuits as empty-bronze. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

# Related datasets

- **`physical_flows`** — Per-point detail behind these aggregations. `daily`. Use when the `points_names` pipe-list isn't enough resolution. *entsog · operational · daily*
- **`nominations`** — Shipper-submitted intended flows. `daily`. Compare against this dataset to measure nomination-vs-actual delivery accuracy per zone. *entsog · operational · daily*
- **`storage`** (GIE-AGSI) — Daily EU gas storage levels. `daily`. Pair with the Storage-direction rows for injection/withdrawal vs stock-level dynamics. *gie · storage · daily*
- **`actual_generation`** (ENTSO-E) — EU power generation by PSR type (incl. `B04` gas). `PT15M-PT60M`. Cross-reference gas burn against gas-fired generation share. *entsoe · generation · 15-60 min*
