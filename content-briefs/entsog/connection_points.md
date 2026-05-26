---
slug: connection_points
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: connectionPoints
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/connection_points.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — `reference_dataset=True` single-file output
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["connection_points"] (lines 206-213)
  - .planning/reconciliation/entsog/17-connection-points-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** All ENTSO-G connection points <span class="italic fg-accent">on the map.</span>

**Lede:** Full ENTSO-G connection-point inventory with map coordinates, infrastructure type, and cross-border flags — the canonical reference for resolving `point_key` codes.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /connectionPoints](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.connection_points` (single-file snapshot) |
| API PATH | `/api/v1/connectionPoints` |
| FREQUENCY | weekly snapshot |
| PUBLICATION LAG | on change (vendor updates daily) |
| VOLUME | ~3000 EU-wide points |
| PRIMARY KEY | `(id)` — vendor concatenation (`dataSet + pointKey`) |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | weekly | Snapshot cadence |
| 2 | snapshot | Output layout |
| 3 | ~3000 | Active points |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- operators
- operator_point_directions
- balancing_zones
- interconnections
- aggregate_interconnections

# Sample chart

- **Type:** `donut`
- **Title:** "Connection points by infrastructure type"
- **Subtitle:** "Donut · share · current inventory"
- **Seed:** 51
- **Toggles:** `current` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` runs with `reference_dataset=True`. Vault Bronze sample documents the field set.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation (`dataSet + pointKey`). Dedup key. | `silver/entsog/generic.py L126-130` |
| `point_key` / `point_label` | `str` | Yes | `pointKey` / `pointLabel` | Connection-point identifier and label. | dynamic |
| `point_tooltip` | `str` | Yes | `pointTooltip` | Vendor map-tooltip text. | dynamic |
| `point_eic_code` | `str` | Yes | `pointEicCode` | EIC cross-reference. | dynamic |
| `is_single_operator` | `str` | Yes | `isSingleOperator` | `"0"` / `"1"` text. | dynamic |
| `control_point_type` | `str` | Yes | `controlPointType` | E.g. `"O_P_INCOUN_IN_DIS"`. | dynamic |
| `tp_map_x` / `tp_map_y` | `float` | Yes | `tpMapX` / `tpMapY` | Map coordinates (transparency-platform internal). | dynamic |
| `point_type` | `str` | Yes | `pointType` | E.g. `"Distribution Point"`, `"Cross-Border Transmission IP between EU and ExtEU"`. | dynamic |
| `commercial_type` | `str` | Yes | `commercialType` | E.g. `"Physical"`. | dynamic |
| `import_from_country_key` / `import_from_country_label` | `str` | Yes | `importFromCountryKey` / `importFromCountryLabel` | When the point imports from a specific country. | dynamic |
| `has_virtual_point` / `virtual_point_key` / `virtual_point_label` | `str` | Yes | `hasVirtualPoint` / `virtualPointKey` / `virtualPointLabel` | Virtual-point linkage. | dynamic |
| `has_data` | `bool` | Yes | `hasData` | Whether operational data exists. | dynamic |
| `is_planned` / `is_interconnection` / `is_import` / `is_cross_border` / `is_macro_point` / `is_pipe_in_pipe` / `is_invalid` | `bool` | Yes | `isPlanned` / `isInterconnection` / `isImport` / `isCrossBorder` / `isMacroPoint` / `isPipeInPipe` / `isInvalid` | Boolean flags. | dynamic |
| `infrastructure_key` / `infrastructure_label` | `str` | Yes | `infrastructureKey` / `infrastructureLabel` | E.g. `"DIS"` / `"Distribution"`. | dynamic |
| `eu_crossing` | `str` | Yes | `euCrossing` | `"EU"` / `"ExtEU"`. | dynamic |
| `is_cam_relevant` / `is_cmp_relevant` | `bool` | Yes | `isCAMRelevant` / `isCMPRelevant` | Regulatory flags (uppercase coalesces with operationalData camelCase). | `silver/entsog/generic.py L264-290` |
| `data_set` | `str` | Yes | `dataSet` | Vendor numeric dataset id. | dynamic |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/connection_points.parquet` (single-file reference dataset)
**PARTITION BY:** none (single-file overwrite on weekly refresh)
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| point_key | point_label | infrastructure_label | point_type | is_cross_border | is_interconnection | has_data |
|---|---|---|---|---|---|---|
| ITP-00005 | Bacton (IUK) | Transmission | Cross-Border Transmission IP between EU and ExtEU | true | true | true |
| ITP-00207 | Bacton (BBL) | Transmission | Cross-Border Transmission IP between EU and ExtEU | true | true | true |
| **ITP-00495** | **Moffat (IE)** | **Transmission** | **Cross-Border Transmission IP within EU** | **true** | **true** | **true** |
| ITP-00090 | Moffat | Transmission | Cross-Border Transmission IP within EU | true | true | true |
| DIS-00015 | Greater Belfast | Distribution | Distribution Point | false | true | true |
| ITP-00007 | Überackern SUDAL (AT) / Überackern 2 (DE) | Transmission | Cross-Border Transmission IP within EU | true | true | true |
| ITP-00008 | Melendugno - IT / TAP | Transmission | Cross-Border Transmission IP between EU and ExtEU | true | true | true |
| DIS-00001 | Distribution (PT) | Distribution | Distribution Point | false | true | true |

**Sources:** Synthesised respecting the vault's documented field set. Highlighted row is Moffat (IE) — `Cross-Border Transmission IP within EU` (UK-IE), distinct from Bacton (IUK)'s `IP between EU and ExtEU` designation (UK was reclassified ExtEU after Brexit). Use this dataset to filter operational data by point type or cross-border status.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/connectionPoints?limit=-1`
- AUTH: None (public). Full snapshot.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/connection_points/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `ConnectionPointsTransformer`, `reference_dataset=True`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/connectionPoints?limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Cross-border transmission IPs with operational data
SELECT point_key, point_label, point_type
FROM read_parquet('data/silver/entsog/connection_points.parquet')
WHERE is_cross_border = true
  AND infrastructure_label = 'Transmission'
  AND has_data = true
ORDER BY point_label;
```

**Tab 3 — Python · polars**
```python
import polars as pl

cp = pl.read_parquet("data/silver/entsog/connection_points.parquet")
# Infrastructure type breakdown
print(cp.group_by("infrastructure_label").agg(pl.len().alias("points")).sort("points", descending=True))
```

# Caveats

## 01 Single-file reference dataset (no time partitions)

Output is `connection_points.parquet` overwritten on each refresh. *(Source: `silver/entsog/generic.py L196-202`; `endpoints.py L206-213` `reference=True`.)*

## 02 `is_cam_relevant` coalesces uppercase + camelCase

Vendor returns `isCAMRelevant` here vs `isCamRelevant` in operationalData. `_normalise_column_names` collapses both. *(Source: `silver/entsog/generic.py L264-290`.)*

## 03 `is_single_operator` is `"0"`/`"1"` string

Vendor returns text, not bool. Cast as needed. *(Source: vault Bronze sample L73.)*

## 04 Pagination via `limit`+`offset`

No `from`/`to` accepted. Connector sets `limit=-1` for one-call extraction. *(Source: vault Query-params.)*

## 05 `pointType` taxonomy is vendor-fixed

Values include `"Cross-Border Transmission IP between EU and ExtEU"`, `"Cross-Border Transmission IP within EU"`, `"Distribution Point"`, `"Storage Point"`, `"LNG Terminal"`. Use as a categorical filter. *(Source: vault Bronze sample L79.)*

# Related datasets

- **`operator_point_directions`** — Same points with operator-direction context. `snapshot`. Joins point inventory to operator metadata. *entsog · reference · snapshot*
- **`interconnections`** — Same network as directed `from`/`to` pairs. `snapshot`. Complementary representation. *entsog · reference · snapshot*
- **`balancing_zones`** — Zone inventory. `snapshot`. Points sit inside zones. *entsog · reference · snapshot*
- **`physical_flows`** — Operational data per point. `daily`. Primary downstream consumer. *entsog · operational · daily*
