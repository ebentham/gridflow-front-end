---
slug: aggregate_interconnections
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: aggregateInterconnections
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/aggregate_interconnections.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — `reference_dataset=True` single-file output
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["aggregate_interconnections"] (lines 249-257)
  - .planning/reconciliation/entsog/06-aggregate-interconnections-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Zone-to-zone aggregated <span class="italic fg-accent">interconnections.</span>

**Lede:** Zone-pair-aggregated network topology with adjacent-system counts — the canonical reference for resolving zone-level flow data joins.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /aggregateInterconnections](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.aggregate_interconnections` (single-file snapshot) |
| API PATH | `/api/v1/aggregateInterconnections` |
| FREQUENCY | weekly snapshot |
| PUBLICATION LAG | on change |
| VOLUME | 27 UK records (2026-05-08 sample) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | weekly | Snapshot cadence |
| 2 | snapshot | Output layout |
| 3 | 27 | UK records (default filter) |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- interconnections
- aggregated_physical_flows
- balancing_zones
- operators
- operator_point_directions

# Sample chart

- **Type:** `barsH`
- **Title:** "Aggregate UK interconnections by adjacent system"
- **Subtitle:** "Horizontal bars · count · grouped by adjacent system"
- **Seed:** 57
- **Toggles:** `current` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` runs with `reference_dataset=True`. The dataset rolls up `interconnections` into zone-pair tuples.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `country_key` / `country_label` | `str` | Yes | `countryKey` / `countryLabel` | Country of the source zone (e.g. `"UK"` / `"United Kingdom"`). | dynamic |
| `bz_key` / `bz_label` / `bz_label_long` | `str` | Yes | `bzKey` / `bzLabel` / `bzLabelLong` | Source-zone identifier (e.g. `"UK---------"` / `"UK"` / `"British Balancing Zone"`). | dynamic |
| `operator_key` / `operator_label` | `str` | Yes | `operatorKey` / `operatorLabel` | The TSO at the source side. | dynamic |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` / `"exit"` (lowercase). | dynamic |
| `adjacent_systems_key` | `str` | Yes | `adjacentSystemsKey` | Concatenation of adjacent systems (e.g. `"TransmissionUK-NI------"`). | dynamic |
| `adjacent_systems_count` | `float` | Yes | `adjacentSystemsCount` | How many adjacent systems are aggregated. | `silver/entsog/generic.py L65-77` (`_NUMERIC_NAMES`) |
| `adjacent_systems_are_balancing_zones` | `str` | Yes | `adjacentSystemsAreBalancingZones` | Vendor-narrative flag. | dynamic |
| `adjacent_systems_label` | `str` | Yes | `adjacentSystemsLabel` | Human label for the adjacent-system aggregate. | dynamic |
| `data_set` | `str` | Yes | `dataSet` | Vendor numeric dataset id. | dynamic |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/aggregate_interconnections.parquet` (single-file reference dataset)
**PARTITION BY:** none (single-file overwrite on weekly refresh)
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| country_key | bz_label_long | operator_key | direction_key | adjacent_systems_key | adjacent_systems_label | adjacent_systems_count |
|---|---|---|---|---|---|---|
| UK | British Balancing Zone | IE-TSO-0001 | entry | TransmissionUK-NI------ | NI | 1 |
| UK | British Balancing Zone | IE-TSO-0001 | exit | TransmissionUK-NI------ | NI | 1 |
| **UK** | **British Balancing Zone** | **UK-TSO-0001** | **entry** | **LNG Terminals** | **LNG Terminals** | **2** |
| UK | British Balancing Zone | UK-TSO-0001 | entry | Production | Production | 3 |
| UK | British Balancing Zone | UK-TSO-0001 | entry | Storage | Storage | 5 |
| UK | British Balancing Zone | UK-TSO-0001 | exit | Distribution | Distribution | 1 |
| UK | British Balancing Zone | UK-TSO-0001 | exit | Final consumer | Final consumer | 1 |
| UK | British Balancing Zone | UK-TSO-0003 | entry | TransmissionBE--------- | BE | 1 |

**Sources:** First two rows from vault Bronze sample (`aggregate_interconnections.md` L70-86; UK→NI via IE-TSO-0001). Remaining rows synthesised to demonstrate the zone-pair-aggregation shape — note `adjacent_systems_count` reveals how many sub-elements roll up to each tuple. Highlighted row is UK LNG-terminals aggregate (Isle of Grain + Milford Haven + South Hook = 2 active counted here). Use this dataset to enumerate which adjacent-system keys are available in `aggregated_physical_flows`.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/aggregateInterconnections?limit=-1&countryKey=UK`
- AUTH: None (public). Default filter `countryKey=UK` per connector default.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/aggregate_interconnections/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `AggregateInterconnectionsTransformer`, `reference_dataset=True`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/aggregateInterconnections?limit=-1&countryKey=UK
```

**Tab 2 — DuckDB · SQL**
```sql
-- All UK adjacent-system aggregates by direction
SELECT direction_key, adjacent_systems_label,
       SUM(adjacent_systems_count) AS total_sub_systems
FROM read_parquet('data/silver/entsog/aggregate_interconnections.parquet')
WHERE country_key = 'UK'
GROUP BY 1, 2
ORDER BY 1, total_sub_systems DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

agg_ic = pl.read_parquet("data/silver/entsog/aggregate_interconnections.parquet")
# Enumerate adjacent-system keys for UK (the codelist for aggregated_physical_flows)
print(agg_ic.filter(pl.col("country_key") == "UK").select("adjacent_systems_key").unique())
```

# Caveats

## 01 Single-file reference dataset (no time partitions)

Output is `aggregate_interconnections.parquet` overwritten on each refresh. *(Source: `silver/entsog/generic.py L196-202`; `endpoints.py L249-257` `reference=True`.)*

## 02 Default `countryKey=UK` filter

The connector passes `countryKey=UK` by default (`endpoints.py L255`). For full EU connectivity, override the param. *(Source: `connectors/entsog/endpoints.py L255`.)*

## 03 `direction_key` is lowercase here (`"entry"`/`"exit"`)

Same casing as `/operationalData` and `/aggregatedData` (vs capitalised in `/cmpUnsuccessfulRequests`). Safe to join directly to `aggregated_physical_flows`. *(Source: vault Bronze sample L78.)*

## 04 `adjacent_systems_key` is a concatenation, not a categorical

Values like `"TransmissionUK-NI------"` and `"LNG Terminals"` mix infrastructure types with zone keys. Parse with care for downstream taxonomies. *(Source: vault Bronze sample L79.)*

## 05 Pagination via `limit`+`offset`

No `from`/`to` accepted. Connector sets `limit=-1` for one-call extraction. *(Source: vault Query-params.)*

# Related datasets

- **`interconnections`** — Point-level interconnection records (the underlying detail). `snapshot`. The granular companion. *entsog · reference · snapshot*
- **`aggregated_physical_flows`** — Zone-level operational data using these zone-pair keys. `daily`. Primary downstream consumer. *entsog · zone · daily*
- **`balancing_zones`** — Zone inventory. `snapshot`. Resolves `bz_key` to human zone names. *entsog · reference · snapshot*
- **`operators`** — TSO inventory. `snapshot`. Resolves `operator_key`. *entsog · reference · snapshot*
