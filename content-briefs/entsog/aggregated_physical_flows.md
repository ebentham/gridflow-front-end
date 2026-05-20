---
slug: aggregated_physical_flows
vendor: entsog
vendor_label: ENTSOG Transparency
api_code: aggregatedData
last_verified: 2026-05-08
sources_consulted:
  - quant-vault/30-vendors/entsog/datasets/aggregated_physical_flows.md (vault not yet vendored to gridflow-front-end/vault/entsog/ — Phase 10 vendoring deferred)
  - gridflow/src/gridflow/schemas/entsog.py (absent — no AggregatedPhysicalFlows class; only EntsogPhysicalFlow exists at L12 for a different dataset)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — dynamic-column transformer registered as AggregatedPhysicalFlowsTransformer subclass at L220-229 via _make_transformer_class factory
  - gridflow/src/gridflow/connectors/entsog/endpoints.py (lines 167-169, EntsogEndpoint registration for `/aggregatedData` with response_key="aggregatedData")
  - https://transparency.entsog.eu/api/v1/aggregatedData (JSON API; documented via PDF only — no browsable HTML page to WebFetch)
discrepancies_found:
  - source_a: "gridflow schemas/entsog.py"
    source_a_says: "No AggregatedPhysicalFlows Pydantic class declared; EntsogPhysicalFlow at L12 is for a different dataset (/operationalData per-point flows)"
    source_b: "gridflow silver/entsog/generic.py::GenericEntsogJsonTransformer"
    source_b_says: "Transformer is dynamic-schema by design — columns derived from whatever the live response contains; 29 columns observed in 2026-05-08 sample"
    orchestrator_recommendation: "trust silver transformer — this is the dynamic-schema pattern intended for ENTSOG's generic indicator endpoints. Same Category-1 shape as the 21 Elexon datasets without Pydantic classes; see handover P3 ADR proposal. Document as design-intent rather than treating as a gap."
  - source_a: "vault: timeZone parameter spelled UCT"
    source_a_says: "ENTSOG documents (and the connector sends) timeZone=UCT — NOT timeZone=UTC. The response meta.timezone echoes CET regardless."
    source_b: "gridflow connectors/entsog/endpoints.py — uses UCT verbatim"
    orchestrator_recommendation: "documented vendor typo, not a bug. Surface in caveats so downstream consumers don't try to 'fix' the param spelling."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Cross-border gas flows, <span class="italic fg-accent">zone by zone.</span>

**Lede:** Daily aggregated physical gas flows for every European balancing zone, broken down by adjacent system (Production, Storage, LNG Terminals, neighbouring TSOs). Reported in kWh/day per `(zone, operator, direction, adjacent-system)` tuple. The canonical view of who is moving how much gas to whom across the European pipeline network.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSOG Transparency Platform · /aggregatedData](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.aggregated_physical_flows` |
| API PATH | `/api/v1/aggregatedData` |
| FREQUENCY | daily |
| PUBLICATION LAG | ~2 days |
| VOLUME | ~1k rows / day (all zones) |
| PRIMARY KEY | `(id)` (vendor concatenation of zone+operator+direction+adj-system+window) |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | daily | Period type |
| 2 | kWh/d | Reporting unit |
| 3 | 29 | Silver columns (dynamic schema) |
| 4 | UCT (sic) | Vendor timezone-param spelling |

# Sidebar siblings

- physical_flows
- nominations
- interruptions
- allocations
- balancing_zones

# Overview

1. <code>aggregated_physical_flows</code> is the **zone-level rollup of daily gas flows** published by ENTSOG, the European TSO association. Each row aggregates a single `(country, balancing-zone, TSO operator, direction=entry|exit, adjacent-system)` tuple over one day, with `value` in **kWh/day** (not MWh — gas conventions differ from power) and `flow_status` indicating whether the day is `Provisionnal` (vendor spelling preserved) or `Final`. Adjacent systems enumerate the gas-network counterparty type: `Production`, `Storage`, `LNG Terminals`, `Distribution`, plus zone-pair keys for cross-border aggregates.

2. Gridflow fetches it from the JSON endpoint <code>/api/v1/aggregatedData</code> with three required query params: `from`/`to` (date window) and `timeZone=UCT` (vendor's idiosyncratic spelling of UTC — see Caveats #02). The connector dispatch lives at <code>connectors/entsog/endpoints.py L167-169</code> with `response_key="aggregatedData"` declaring which top-level key in the JSON envelope holds the rows. Authentication is none (public). The transformer is the <code>GenericEntsogJsonTransformer</code> at <code>silver/entsog/generic.py L80</code> — a **dynamic-schema design** that derives the silver column set from whatever the live response contains, registered as the dataset's transformer via the factory at L220-229. There is no per-dataset Pydantic class; the generic shape covers ENTSOG's family of indicator endpoints.

3. Cadence is daily snapshots. Verified against the live API on 2026-05-08; a single-day call for 2026-05-06 returned the British Balancing Zone's LNG-entry aggregate at 100,259,283 kWh/day (≈100 GWh, equivalent to ~9 mcm of natural gas — about one day's worth of typical LNG-terminal sendout). Each row carries `points_names` listing the underlying physical points contributing to the aggregate (e.g. `Isle of Grain|Milford Haven`). Use this dataset for monthly LNG-vs-pipeline imports analysis, storage-injection seasonality, and cross-border flow validation against the per-point `physical_flows` dataset.

# Sample chart

- **Type:** `barsH`
- **Title:** "British Balancing Zone · daily entry by adjacent system"
- **Subtitle:** "Horizontal bars · GWh/day · last 30 days"
- **Seed:** 13
- **Toggles:** `30d` (active) / `1y`

# Schema

Dynamic schema — column set is derived from the live API response by the `GenericEntsogJsonTransformer`. No fixed Pydantic class; the table below reflects the 29 columns observed in the 2026-05-08 live sample. Partitioned by `period_from` (year + month). Point-in-time field: `last_update_date_time`.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation: dataSet + Aggregates + countryKey + bzKey + operatorKey + directionKey + adjacentSystemsKey + periodFrom + periodTo + indicator. Used as dedup key. | `silver/entsog/generic.py L80+` (dedup logic) |
| `data_set` | `str` | Yes | `dataSet` | ENTSOG dataset numeric ID (e.g. `"1"` for Aggregates). | dynamic |
| `data_set_label` | `str` | Yes | `dataSetLabel` | Human label (e.g. `"Aggregates"`). | dynamic |
| `indicator` | `str` | Yes | `indicator` | Always `"Physical Flow"` for this endpoint (single-indicator). | dynamic |
| `period_type` | `str` | Yes | `periodType` | `"day"` for this endpoint (no sub-daily aggregation). | dynamic |
| `period_from` | `datetime[UTC]` | Yes | `periodFrom` | Period start. Carries `+02:00` (CEST) in summer / `+01:00` (CET) in winter; `parse_entsog_datetime` converts to UTC. | dynamic; see `silver/entsog/datetime.py` |
| `period_to` | `datetime[UTC]` | Yes | `periodTo` | Period end. Same TZ behaviour. | dynamic |
| `country_key` | `str` | Yes | `countryKey` | ISO-style country code (e.g. `"UK"`, `"DE"`, `"FR"`). | dynamic |
| `country_label` | `str` | Yes | `countryLabel` | Human country name. | dynamic |
| `bz_key` | `str` | Yes | `bzKey` | Balancing zone EIC-style key (e.g. `"UK---------"` for British Balancing Zone). | dynamic |
| `bz_short` | `str` | Yes | `bzShort` | Short label (`"UK"`). | dynamic |
| `bz_long` | `str` | Yes | `bzLong` | Long label (`"British Balancing Zone"`). | dynamic |
| `operator_key` | `str` | Yes | `operatorKey` | TSO identifier (e.g. `"UK-TSO-0001"` = National Gas Transmission). | dynamic |
| `operator_label` | `str` | Yes | `operatorLabel` | TSO human name. | dynamic |
| `tso_eic_code` | `str` | Yes | `tsoEicCode` | EIC code for the TSO (cross-references ENTSO-E). | dynamic |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` or `"exit"` (lowercase here; capitalised in `/cmpUnsuccessfulRequests` — see Caveats #03). | dynamic |
| `adjacent_systems_key` | `str` | Yes | `adjacentSystemsKey` | Counterparty category: `"Production"`, `"Storage"`, `"LNG Terminals"`, `"Distribution"`, or zone-pair keys. | dynamic |
| `adjacent_systems_label` | `str` | Yes | `adjacentSystemsLabel` | Human label (often same as key). | dynamic |
| `year`, `month`, `day` | `str` | Yes | `year` / `month` / `day` | String-typed (not int); from vendor JSON verbatim. | dynamic |
| `unit` | `str` | Yes | `unit` | Always `"kWh/d"` for this endpoint. **kWh/day NOT MWh** — gas convention. | dynamic |
| `value` | `float` | Yes | `value` | The aggregated flow value in the `unit`-declared units. | dynamic |
| `count_point_presents` | `float` | Yes | `countPointPresents` | Number of underlying physical points contributing to the aggregate. | dynamic |
| `flow_status` | `str` | Yes | `flowStatus` | `"Provisionnal"` (vendor typo, preserved) or `"Final"`. | dynamic |
| `points_names` | `str` | Yes | `pointsNames` | `\|`-delimited list of contributing point names (e.g. `"Isle of Grain\|Milford Haven"`). | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. May be empty, `"-"`, or `"N/A"` for older records; `parse_entsog_datetime` returns None for unparseable. | `silver/entsog/datetime.py::parse_entsog_datetime` |
| `data_provider` | `str` | No | _derived_ | Always `"entsog"`. | dynamic |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | dynamic |

**PARQUET PATH:** `data/silver/entsog/aggregated_physical_flows/year=YYYY/month=MM/`
**PARTITION BY:** `period_from (year + month)`
**DEDUP KEY:** `(id)` (vendor concatenation) — falls back to all non-`timestamp_utc` columns if `id` is absent

# Sample data

| period_from | country_key | bz_short | operator_key | direction_key | adjacent_systems_key | unit | value | flow_status | last_update_date_time |
|---|---|---|---|---|---|---|---|---|---|
| 2026-05-06T00:00:00+00:00 | UK | UK | UK-TSO-0001 | entry | LNG Terminals | kWh/d | 100,259,283 | Provisionnal | 2026-05-08T16:33:42+00:00 |
| 2026-05-06T00:00:00+00:00 | UK | UK | UK-TSO-0001 | entry | Production | kWh/d | 287,440,000 | Provisionnal | 2026-05-08T16:33:42+00:00 |
| _ROW HIGHLIGHTED_ 2026-05-06T00:00:00+00:00 | UK | UK | UK-TSO-0001 | exit | Distribution | kWh/d | 412,800,000 | Provisionnal | 2026-05-08T16:33:42+00:00 |
| 2026-05-06T00:00:00+00:00 | UK | UK | UK-TSO-0001 | entry | Storage | kWh/d | 18,200,000 | Provisionnal | 2026-05-08T16:33:42+00:00 |
| 2026-05-06T00:00:00+00:00 | DE | DE | DE-TSO-0011 | entry | Production | kWh/d | 1,140,000,000 | Final | 2026-05-08T18:00:00+00:00 |
| 2026-05-06T00:00:00+00:00 | DE | DE | DE-TSO-0011 | exit | Distribution | kWh/d | 2,038,000,000 | Final | 2026-05-08T18:00:00+00:00 |
| 2026-05-06T00:00:00+00:00 | FR | FR | FR-TSO-0001 | entry | LNG Terminals | kWh/d | 312,500,000 | Provisionnal | 2026-05-08T17:15:00+00:00 |
| 2026-05-06T00:00:00+00:00 | NL | NL | NL-TSO-0001 | entry | Production | kWh/d | 487,200,000 | Final | 2026-05-08T18:00:00+00:00 |

[1] First row from vault Bronze sample (UK LNG-entry, 2026-05-06, captured live 2026-05-08); subsequent UK rows synthesised respecting the vault's documented shape (Production / Storage / Distribution adjacent-system categories). Continental rows (DE, FR, NL) synthesised to plausible 2026 daily flows. The highlighted row is the UK Distribution exit — 412 GWh/day = the dominant outflow from the British Balancing Zone (gas going to domestic and industrial consumers). Note the `kWh/d` unit throughout (NOT MWh — convert by ÷1000 if joining against power-market datasets). `flowStatus: Provisionnal` is preserved with vendor typo.

# Adjacent system categories (codelist)

ENTSOG's `adjacent_systems_key` enumerates the counterparty type for each aggregated flow. The set is small and stable across zones — useful for filtering / aggregating.

| Key | Meaning | Typical sign convention |
|---|---|---|
| `Production` | Domestic gas production wells entering the network | entry (positive into zone) |
| `Storage` | Gas storage facilities (injection = exit, withdrawal = entry) | both directions, seasonal |
| `LNG Terminals` | LNG regasification terminals | entry (LNG vapourising into pipeline) |
| `Distribution` | Downstream distribution networks (final consumers) | exit (gas leaving for consumption) |
| `Final consumer` | Direct industrial offtake | exit |
| `Other` | Catch-all (compressor stations, line-pack, etc.) | both |
| `<ZoneKey>` (e.g. `UK---------`) | Cross-border aggregate to neighbouring TSO zone | both (interconnector flows) |

# API & ingestion

**Endpoint card:**
- **ENDPOINT**: `transparency.entsog.eu/api/v1/aggregatedData?from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&forceDownload=true&limit=-1`
- **AUTH**: None (public)

**Bronze + Transformer card:**
- **BRONZE PATH**: `data/bronze/entsog/aggregated_physical_flows/<year>/<month>/<day>/raw_<uuid>.json`
- **TRANSFORMER**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `AggregatedPhysicalFlowsTransformer` via factory at `silver/entsog/generic.py L220-229`)

**Tab 1 — Example URL:**
```
https://transparency.entsog.eu/api/v1/aggregatedData
  ?from=2026-05-06
  &to=2026-05-06
  &timeZone=UCT
  &periodType=day
  &forceDownload=true
  &limit=1000
```

**Tab 2 — DuckDB · SQL:**
```sql
-- UK monthly LNG-vs-Production entry mix
SELECT date_trunc('month', period_from) AS month,
       adjacent_systems_key,
       sum(value) / 1e9 AS twh
FROM read_parquet('data/silver/entsog/aggregated_physical_flows/**/*.parquet')
WHERE bz_short = 'UK'
  AND direction_key = 'entry'
  AND adjacent_systems_key IN ('LNG Terminals', 'Production', 'Storage')
GROUP BY 1, 2
ORDER BY 1, 2;
```

**Tab 3 — Python · parquet:**
```python
import polars as pl

df = pl.read_parquet(
    "data/silver/entsog/aggregated_physical_flows/**/*.parquet",
)
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

## 01 Unit is `kWh/d` — NOT MWh

ENTSOG reports gas flows in **kWh/day**, not MWh/day. Divide by 1,000 to compare against MWh-denominated power-market datasets, or by 1e9 to express in TWh. The vendor `unit` column makes this explicit (`"kWh/d"`) — preserve it through any analytics pipeline rather than assuming. *Source: vault Silver schema + Bronze sample.*

## 02 `timeZone=UCT` (vendor typo, intentional)

The connector sends `timeZone=UCT` — not `timeZone=UTC` — because that is the parameter spelling ENTSOG documents and accepts. Sending `UTC` returns an HTTP 400 with a parameter-validation error. The response's `meta.timezone` echoes back `"CET"` regardless of the request value. Do not try to "fix" this in the connector. *Source: vault Implementation Delta + tested 2026-05-08.*

## 03 `direction_key` casing varies across endpoints

In `/aggregatedData` (this dataset), `direction_key` values are lowercase (`"entry"`, `"exit"`). In `/cmpUnsuccessfulRequests` (a different ENTSOG endpoint), the same field returns capitalised values (`"Exit"`). Cross-endpoint joins on direction must lowercase both sides — or use the `_normalise_column_names` helper that the `GenericEntsogJsonTransformer` applies. *Source: vault Known Issues #6.*

## 04 `flow_status: "Provisionnal"` preserved with vendor typo

The vendor spells the provisional flow-status as `"Provisionnal"` (double-n, single-l) — preserved verbatim in bronze and silver. Filter on the exact string when distinguishing provisional from `"Final"` data. Normalise downstream if your analytics layer doesn't tolerate the typo. *Source: vault Known Issues #3.*

## 05 Period offset is CEST/CET even with `timeZone=UCT`

Despite requesting UCT, `periodFrom` and `periodTo` carry `+02:00` (CEST in summer) or `+01:00` (CET in winter). The transformer's `parse_entsog_datetime` (`silver/entsog/datetime.py`) converts these to UTC for the silver layer. Bronze JSON preserves the original vendor offset. *Source: vault Known Issues #10.*

## 06 Empty windows return HTTP 404, not 200 with empty body

ENTSOG's empty-result convention is HTTP 404 with body `{"message":"No result found"}` — not a normal 200 response. The connector's retry policy must let 404 surface as "empty" rather than triggering a retry storm. Don't treat 404 as an error in downstream code. *Source: vault Known Issues #8.*

# Related datasets

- **`physical_flows`** (ENTSOG) — Per-physical-point detail; chip `daily` — the granular companion data behind this dataset's aggregations. Use this when the `points_names` column's pipe-delimited list isn't enough resolution. *entsog · transmission · daily*

- **`nominations`** (ENTSOG) — Shipper-submitted nomination quantities (planned flows); chip `daily` — compare against this dataset to measure nomination-vs-actual delivery accuracy per zone. *entsog · transmission · daily*

- **`storage`** (GIE-AGSI) — Daily gas storage levels for European facilities; chip `daily` — pair with the Storage-direction rows in this dataset to derive injection/withdrawal vs stock-level dynamics. *gie · storage · daily*

- **`actual_generation`** (ENTSO-E) — European power generation by PSR type, including `B04` (Fossil Gas); chip `15min–60min` — cross-reference gas burn (from this dataset) against gas-fired power generation (B04 share) for power-vs-heat split attribution. *entsoe · generation · 15-60 min*
