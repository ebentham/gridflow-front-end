---
slug: interconnections
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: interconnections
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/interconnections.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — `reference_dataset=True` single-file output
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["interconnections"] (lines 240-247)
  - .planning/reconciliation/entsog/22-interconnections-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Interconnections from/to <span class="italic fg-accent">the UK.</span>

**Lede:** Directed `from`/`to` connectivity per point — the canonical EU gas-network topology graph, returning UK-relevant interconnections by default.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /interconnections](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.interconnections` (single-file snapshot) |
| API PATH | `/api/v1/interconnections` |
| FREQUENCY | weekly snapshot |
| PUBLICATION LAG | on change |
| VOLUME | ~100 UK-relevant interconnection records |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | weekly | Snapshot cadence |
| 2 | snapshot | Output layout |
| 3 | ~100 | UK records (default filter) |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- aggregate_interconnections
- operators
- operator_point_directions
- connection_points
- balancing_zones

# Sample chart

- **Type:** `barsH`
- **Title:** "UK interconnections by adjacent country"
- **Subtitle:** "Horizontal bars · count · grouped by from/to country"
- **Seed:** 55
- **Toggles:** `current` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` runs with `reference_dataset=True`. Each row carries a `from*` and `to*` block describing the directed interconnection.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `point_key` / `point_label` | `str` | Yes | `pointKey` / `pointLabel` | Connection-point identifier. | dynamic |
| `is_single_operator` | `bool` | Yes | `isSingleOperator` | Whether one operator handles both sides. | dynamic |
| `point_tp_map_x` / `point_tp_map_y` | `float` | Yes | `pointTpMapX` / `pointTpMapY` | Map coordinates. | dynamic |
| `from_country_key` / `from_country_label` / `from_bz_key` / `from_bz_label_long` | `str` | Yes | `fromCountryKey` / `fromCountryLabel` / `fromBzKey` / `fromBzLabelLong` | Source-side country + zone. | dynamic |
| `from_operator_key` / `from_operator_label` / `from_operator_long_label` | `str` | Yes | `fromOperatorKey` / `fromOperatorLabel` / `fromOperatorLongLabel` | Source-side TSO. | dynamic |
| `from_point_key` / `from_point_label` / `from_direction_key` | `str` | Yes | `fromPointKey` / `fromPointLabel` / `fromDirectionKey` | Source-side point identifiers. | dynamic |
| `from_is_cam` / `from_is_cmp` | `str` | Yes | `fromIsCAM` / `fromIsCMP` | Source-side CAM/CMP flags. | dynamic |
| `from_has_data` | `str` | Yes | `fromHasData` | Whether the source side has operational data. | dynamic |
| `to_country_key` / `to_country_label` / `to_bz_key` / `to_bz_label_long` | `str` | Yes | `toCountryKey` / `toCountryLabel` / `toBzKey` / `toBzLabelLong` | Destination-side country + zone (may be null for distribution endpoints). | dynamic |
| `to_operator_key` / `to_operator_label` / `to_point_key` / `to_direction_key` | `str` | Yes | `toOperatorKey` / `toOperatorLabel` / `toPointKey` / `toDirectionKey` | Destination-side TSO + point + direction. | dynamic |
| `to_has_data` | `str` | Yes | `toHasData` | Whether the destination side has operational data. | dynamic |
| `from_system_label` / `to_system_label` | `str` | Yes | `fromSystemLabel` / `toSystemLabel` | E.g. `"NI"` / `"Distribution"`. | dynamic |
| `from_infrastructure_type_label` / `to_infrastructure_type_label` | `str` | Yes | `fromInfrastructureTypeLabel` / `toInfrastructureTypeLabel` | E.g. `"Transmission"` / `"Distribution"`. | dynamic |
| `valid_from` | `datetime[UTC]` | Yes | `validFrom` | Validity start. | `silver/entsog/datetime.py` |
| `validto` | `str` | Yes | `validto` | Vendor field-name typo preserved: `validto` (lowercase, no underscore). | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `is_invalid` | `bool` | Yes | `isInvalid` | Whether the record is invalidated. | dynamic |
| `entry_tp_ne_mo_usage` / `exit_tp_ne_mo_usage` | `str` | Yes | `entryTpNeMoUsage` / `exitTpNeMoUsage` | Network-emergency / monitoring usage flags. | dynamic |
| `data_set` | `str` | Yes | `dataSet` | Vendor numeric dataset id. | dynamic |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/interconnections.parquet` (single-file reference dataset)
**PARTITION BY:** none (single-file overwrite on weekly refresh)
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| point_key | from_country_key | from_bz_label_long | to_country_key | to_bz_label_long | from_direction_key | to_direction_key | last_update_date_time |
|---|---|---|---|---|---|---|---|
| ITP-00005 | UK | British Balancing Zone | BE | Belgium | exit | entry | 2026-05-08T16:43:00+00:00 |
| ITP-00207 | UK | British Balancing Zone | NL | TTF Balancing Zone | exit | entry | 2026-05-08T16:43:00+00:00 |
| **ITP-00495** | **UK** | **British Balancing Zone** | **IE** | **Republic of Ireland Balancing Zone** | **exit** | **entry** | **2026-05-08T16:43:00+00:00** |
| ITP-00090 | UK | British Balancing Zone | UK | Northern Ireland Balancing Zone | exit | entry | 2026-05-08T16:43:00+00:00 |
| DIS-00015 | UK | NI Balancing Zone | UK | (Distribution) | exit | (null) | 2026-05-08T16:43:00+00:00 |
| ITP-00007 | DE | NCG Balancing Zone | AT | Austrian Balancing Zone | entry | exit | 2026-05-08T16:43:00+00:00 |
| ITP-00008 | AL | (Albania) | IT | PSV Balancing Zone | exit | entry | 2026-05-08T16:43:00+00:00 |
| ITP-00526 | FR | Trading Region France | BE | Belgium | exit | entry | 2026-05-08T16:43:00+00:00 |

**Sources:** First row from vault Bronze sample (`interconnections.md` L70-126 with DIS-00015 Greater Belfast distribution). Other rows synthesised respecting the directed `from`/`to` convention applied to canonical UK interconnections. Highlighted row is the UK-IE Moffat interconnection — directed source-side (UK exit at ITP-00495 to IE entry). Note the `to_*` block is largely null for distribution endpoints (DIS-* records).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/interconnections?limit=-1&fromCountryKey=UK`
- AUTH: None (public). Default filter `fromCountryKey=UK` per connector default.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/interconnections/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `InterconnectionsTransformer`, `reference_dataset=True`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/interconnections?limit=-1&fromCountryKey=UK
```

**Tab 2 — DuckDB · SQL**
```sql
-- All UK cross-border interconnections
SELECT point_key, point_label,
       from_bz_label_long, to_bz_label_long,
       from_direction_key, to_direction_key
FROM read_parquet('data/silver/entsog/interconnections.parquet')
WHERE from_country_key = 'UK'
  AND to_country_key != 'UK'
ORDER BY point_label;
```

**Tab 3 — Python · polars**
```python
import polars as pl

ic = pl.read_parquet("data/silver/entsog/interconnections.parquet")
# How many UK interconnections per adjacent country?
adj = (
    ic.filter(pl.col("from_country_key") == "UK")
      .filter(pl.col("to_country_key").is_not_null())
      .group_by("to_country_label")
      .agg(pl.len().alias("links"))
      .sort("links", descending=True)
)
print(adj)
```

# Caveats

## 01 Single-file reference dataset (no time partitions)

Output is `interconnections.parquet` overwritten on each refresh. *(Source: `silver/entsog/generic.py L196-202`; `endpoints.py L240-247` `reference=True`.)*

## 02 Default `fromCountryKey=UK` filter

The connector passes `fromCountryKey=UK` by default (`endpoints.py L246`). For full EU connectivity, override the param. *(Source: `connectors/entsog/endpoints.py L246`.)*

## 03 `validto` vendor field-name typo preserved

Vendor uses `validto` (lowercase, no `_To`) rather than `validTo`. Preserved verbatim. *(Source: vault Bronze sample L119.)*

## 04 `to_*` block is mostly null for distribution endpoints

Records where `to_system_label="Distribution"` have null `to_country_key`, `to_operator_key`, etc. Filter on non-null `to_country_key` for cross-border-only views. *(Source: vault Bronze sample L102-114.)*

## 05 `lastUpdateDateTime` carries human-formatted strings

Vendor occasionally returns `"May  8 2026  6:43PM"`-style strings. `parse_entsog_datetime_expr` handles common formats but may return null for unparseable strings. *(Source: vault Bronze sample L120; `silver/entsog/datetime.py`.)*

# Related datasets

- **`aggregate_interconnections`** — Zone-level aggregation of these point-level interconnections. `snapshot`. Coarser-grained network topology. *entsog · reference · snapshot*
- **`connection_points`** — Reference for `point_key`. `snapshot`. The point-by-point inventory. *entsog · reference · snapshot*
- **`operator_point_directions`** — Operator-point-direction combos. `snapshot`. Adds CAM/CMP/contract context. *entsog · reference · snapshot*
- **`physical_flows`** — Operational flow at these interconnections. `daily`. Primary downstream consumer. *entsog · operational · daily*
