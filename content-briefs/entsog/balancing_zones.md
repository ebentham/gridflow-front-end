---
slug: balancing_zones
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: balancingZones
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/balancing_zones.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — `reference_dataset=True` single-file output
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["balancing_zones"] (lines 223-230)
  - .planning/reconciliation/entsog/13-balancing-zones-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** European gas <span class="italic fg-accent">balancing zones.</span>

**Lede:** All ENTSO-G balancing zones with managers, EIC codes, and replacement history — the canonical reference for resolving `bz_key` codes used across aggregated flow data.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /balancingZones](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.balancing_zones` (single-file snapshot) |
| API PATH | `/api/v1/balancingZones` |
| FREQUENCY | weekly snapshot |
| PUBLICATION LAG | on change (vendor updates daily) |
| VOLUME | 48 EU-wide zones (per 2026-05-08 sample) |
| PRIMARY KEY | `(id)` — vendor concatenation (`dataSet + bzKey`) |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | weekly | Snapshot cadence |
| 2 | snapshot | Output layout |
| 3 | 48 | Active zones |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- operators
- operator_point_directions
- connection_points
- interconnections
- aggregate_interconnections

# Sample chart

- **Type:** `barsH`
- **Title:** "Zones per country · current inventory"
- **Subtitle:** "Horizontal bars · count · grouped by country"
- **Seed:** 53
- **Toggles:** `current` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` runs with `reference_dataset=True`. Vault Bronze sample documents the full field set.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `bz_key` / `bz_label` / `bz_label_long` | `str` | Yes | `bzKey` / `bzLabel` / `bzLabelLong` | Zone identifier and labels (e.g. `"UK---------"`, `"UK"`, `"British Balancing Zone"`). | dynamic |
| `bz_tooltip` | `str` | Yes | `bzTooltip` | Map-tooltip text (pipe-delimited zone-name + EIC). | dynamic |
| `bz_eic_code` | `str` | Yes | `bzEicCode` | EIC cross-reference. | dynamic |
| `bz_manager_key` / `bz_manager_label` | `str` | Yes | `bzManagerKey` / `bzManagerLabel` | The balancing-zone manager (e.g. `"AT-BRP-0001"` = Central European Gas Hub). | dynamic |
| `tp_map_x` / `tp_map_y` | `float` | Yes | `tpMapX` / `tpMapY` | Map coordinates. | dynamic |
| `control_point_type` | `str` | Yes | `controlPointType` | `"BALZONE"` for balancing-zone records. | dynamic |
| `replaced_since` / `replaced_by` | `str` | Yes | `replacedSince` / `replacedBy` | Zone-replacement history (when a zone merged into another). | dynamic |
| `is_deactivated` | `str` | Yes | `isDeactivated` | `"0"` / `"1"` text. | dynamic |
| `data_set` | `str` | Yes | `dataSet` | Vendor numeric dataset id. | dynamic |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/balancing_zones.parquet` (single-file reference dataset)
**PARTITION BY:** none (single-file overwrite on weekly refresh)
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| bz_key | bz_label | bz_label_long | bz_manager_key | bz_eic_code | is_deactivated |
|---|---|---|---|---|---|
| UK--------- | UK | British Balancing Zone | UK-BRP-0001 | 21X-GB-A-A0A0A-7 | 0 |
| **UK-NI------** | **NI** | **Northern Ireland Balancing Zone** | **UK-BRP-0002** | **21X-NI-A-A0A0A-X** | **0** |
| AT--------- | Austria | Austrian Balancing Zone | AT-BRP-0001 | 25Z-VTP-CEGH---5 | 0 |
| DE-MGAS---- | GASPOOL | GASPOOL Balancing Zone | DE-BRP-0001 | 21Y0000000000061 | 1 |
| DE-NCG----- | NCG | NetConnect Germany Balancing Zone | DE-BRP-0002 | 21Y0000000000150 | 1 |
| DE-THE----- | THE | Trading Hub Europe Balancing Zone | DE-BRP-0003 | 21Y0000000000300 | 0 |
| FR--------- | France | France Balancing Zone | FR-BRP-0001 | 25Z-PEG-NORD---H | 0 |
| NL--------- | TTF | TTF Balancing Zone | NL-BRP-0001 | 25Z-TTF-NL-----O | 0 |

**Sources:** First row corresponds to the canonical British Balancing Zone (verified from vault Bronze sample shape). Highlighted row is Northern Ireland's separate balancing zone (`UK-NI------`) — important to model GB and NI as distinct zones since they're served by different operators (UK-TSO-0001 vs UK-TSO-0002). German zones GASPOOL/NCG are shown as deactivated (`is_deactivated="1"`) — they merged into Trading Hub Europe (THE) in 2021.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/balancingZones?limit=-1`
- AUTH: None (public). Full snapshot.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/balancing_zones/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `BalancingZonesTransformer`, `reference_dataset=True`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/balancingZones?limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Active balancing zones (exclude deactivated)
SELECT bz_key, bz_label_long, bz_manager_label
FROM read_parquet('data/silver/entsog/balancing_zones.parquet')
WHERE is_deactivated = '0'
ORDER BY bz_label_long;
```

**Tab 3 — Python · polars**
```python
import polars as pl

bz = pl.read_parquet("data/silver/entsog/balancing_zones.parquet")
# Resolve aggregated_physical_flows bz keys to long names
agg = pl.read_parquet("data/silver/entsog/aggregated_physical_flows/**/*.parquet")
named = agg.join(bz, on="bz_key", how="left")
print(named.select(["period_from", "bz_label_long", "adjacent_systems_key", "value"]).head())
```

# Caveats

## 01 Single-file reference dataset (no time partitions)

Output is `balancing_zones.parquet` overwritten on each refresh. *(Source: `silver/entsog/generic.py L196-202`; `endpoints.py L223-230` `reference=True`.)*

## 02 `bz_key` carries trailing dashes — preserve verbatim

Zone keys like `"UK---------"` and `"DE-MGAS----"` use trailing dashes as padding. Do not strip; the dashes are part of the key. *(Source: vault Known Issues.)*

## 03 `is_deactivated` is `"0"`/`"1"` string

Vendor text, not bool. Cast as needed. *(Source: vault Bronze sample L83.)*

## 04 Pagination via `limit`+`offset`

No `from`/`to` accepted. Connector sets `limit=-1` for one-call extraction. *(Source: vault Query-params.)*

## 05 Zone-replacement history tracked via `replaced_since`/`replaced_by`

When zones merge (e.g. GASPOOL + NCG → THE), the old zones get `replaced_by` set with the new zone key. Use to reconstruct historical-zone-to-current-zone mappings. *(Source: vault Bronze sample L81-82.)*

# Related datasets

- **`operators`** — TSO inventory. `snapshot`. Each operator is associated with one zone. *entsog · reference · snapshot*
- **`operator_point_directions`** — Operator-point-direction combos. `snapshot`. Adds points-to-zones mapping. *entsog · reference · snapshot*
- **`aggregated_physical_flows`** — Zone-level operational data. `daily`. Resolves `bz_key` via this reference. *entsog · zone · daily*
- **`aggregate_interconnections`** — Zone-to-zone connectivity. `snapshot`. The interconnection counterpart. *entsog · reference · snapshot*
