---
slug: operator_point_directions
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: operatorPointDirections
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/operator_point_directions.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — `reference_dataset=True` single-file output
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["operator_point_directions"] (lines 231-239)
  - .planning/reconciliation/entsog/27-operator-point-directions-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Operator-point-direction combos with <span class="italic fg-accent">full metadata.</span>

**Lede:** Operator-point-direction triples with full validity, CAM/CMP flags, contract types, and GCV ranges — the canonical reference for resolving operational-data composite keys.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /operatorPointDirections](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.operator_point_directions` (single-file snapshot) |
| API PATH | `/api/v1/operatorPointDirections` |
| FREQUENCY | weekly snapshot |
| PUBLICATION LAG | on change (vendor updates daily) |
| VOLUME | ~5000 EU-wide combos |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | weekly | Snapshot cadence |
| 2 | snapshot | Output layout |
| 3 | ~5000 | Active combos |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- operators
- connection_points
- balancing_zones
- interconnections
- aggregate_interconnections

# Sample chart

- **Type:** `barsH`
- **Title:** "Operator-point combos by country · current inventory"
- **Subtitle:** "Horizontal bars · count · grouped by country"
- **Seed:** 49
- **Toggles:** `current` (active)

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` runs with `reference_dataset=True`. Schema below summarises the canonical fields; the full vault sample has 70+ columns (contract-product availability, CMP narrative sentences, GCV ranges).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `point_key` / `point_label` | `str` | Yes | `pointKey` / `pointLabel` | Connection-point identifier. | dynamic |
| `operator_key` / `operator_label` | `str` | Yes | `operatorKey` / `operatorLabel` | TSO. | dynamic |
| `tso_eic_code` | `str` | Yes | `tsoEicCode` | EIC cross-reference. | dynamic |
| `direction_key` | `str` | Yes | `directionKey` | `"entry"` / `"exit"`. | dynamic |
| `valid_from` / `valid_to` | `datetime[UTC]` | Yes | `validFrom` / `validTo` | Combo validity window. | `silver/entsog/datetime.py::parse_entsog_datetime_expr` |
| `has_data` | `bool` | Yes | `hasData` | Whether operational data exists for this combo. | dynamic |
| `is_cam_relevant` / `is_cmp_relevant` | `bool` | Yes | `isCAMRelevant` / `isCMPRelevant` | Regulatory flags (uppercase CAM/CMP coalesces with operationalData's camelCase via `_normalise_column_names`). | `silver/entsog/generic.py L264-290` |
| `t_so_country` / `t_so_balancing_zone` | `str` | Yes | `tSOCountry` / `tSOBalancingZone` | TSO country & balancing zone. Note awkward snake_case from `tSO` camel pattern. | dynamic |
| `cross_border_point_type` | `str` | Yes | `crossBorderPointType` | E.g. `"Cross-Border Transmission IP between EU and ExtEU"`. | dynamic |
| `adjacent_tso_eic` / `adjacent_operator_key` / `adjacent_country` | `str` | Yes | `adjacentTsoEic` / `adjacentOperatorKey` / `adjacentCountry` | The counterparty TSO across the interconnector. | dynamic |
| `adjacent_zones` | `str` | Yes | `adjacentZones` | Adjacent balancing zones list. | dynamic |
| `annual_contracts_is_available` / `quarterly_contracts_is_available` / `monthly_contracts_is_available` / `daily_contracts_is_available` / `day_ahead_contracts_is_available` / `half_annual_contracts_is_available` / `multi_annual_contracts_is_available` | `str` (yes/no text) | Yes | corresponding camelCase fields | Vendor-narrative product availability. | dynamic |
| `tp_tso_gcv_min` / `tp_tso_gcv_max` / `tp_tso_gcv_unit` | `str` / `float` | Yes | `tpTsoGCVMin` / `tpTsoGCVMax` / `tpTsoGCVUnit` | GCV (Gross Calorific Value) range for the point. | dynamic |
| `sentence_cmp_unsuccessful` / `sentence_cmp_unavailable` / `sentence_cmp_auction` / `sentence_cmp_made_available` | `str` | Yes | `sentenceCMP*` | Free-text CMP narrative sentences. | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/operator_point_directions.parquet` (single-file reference dataset)
**PARTITION BY:** none (single-file overwrite on weekly refresh)
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| operator_key | point_key | direction_key | t_so_country | t_so_balancing_zone | adjacent_country | is_cam_relevant | annual_contracts_is_available |
|---|---|---|---|---|---|---|---|
| UK-TSO-0001 | ITP-00005 | exit | UK | UK | UK | true | true |
| UK-TSO-0003 | ITP-00005 | entry | UK | UK | NL | true | true |
| UK-TSO-0001 | ITP-00207 | exit | UK | UK | NL | true | true |
| **UK-TSO-0004** | **ITP-00063** | **entry** | **NL** | **NL** | **UK** | **true** | **true** |
| IE-TSO-0002 | ITP-00495 | entry | IE | IE | UK | true | true |
| UK-TSO-0001 | ITP-00090 | entry | UK | UK | IE | true | true |
| AL-TSO-0001 | ITP-00008 | entry | AL | AL | IT | true | true |
| DE-TSO-0010 | ITP-00007 | entry | DE | DE | AT | true | true |

**Sources:** Synthesised — vault's documented columns applied to the canonical GB interconnection combos from `DEFAULT_POINT_DIRECTIONS` in `connectors/entsog/endpoints.py L24-34`. Highlighted row is the Dutch side of BBL (`UK-TSO-0004 ITP-00063 entry`) — note the operator country/zone is NL while the adjacent country is UK, the natural mirror of the UK-side row above. Use as the join table to attach country/zone metadata to operational rows.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/operatorPointDirections?limit=-1&hasData=1`
- AUTH: None (public). `hasData=1` filters to active combos.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/operator_point_directions/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `OperatorPointDirectionsTransformer`, `reference_dataset=True`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/operatorPointDirections?limit=-1&hasData=1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Attach country/zone metadata to physical_flows
SELECT pf.timestamp_utc, pf.point_key, pf.direction_key,
       opd.t_so_country, opd.t_so_balancing_zone, opd.adjacent_country,
       pf.flow_gwh_per_day
FROM read_parquet('data/silver/entsog/physical_flows/**/*.parquet') pf
LEFT JOIN read_parquet('data/silver/entsog/operator_point_directions.parquet') opd
  ON  pf.operator_key  = opd.operator_key
  AND pf.point_key     = opd.point_key
  AND pf.direction_key = opd.direction_key
WHERE pf.timestamp_utc >= current_date - INTERVAL 7 DAY
ORDER BY pf.timestamp_utc;
```

**Tab 3 — Python · polars**
```python
import polars as pl

opd = pl.read_parquet("data/silver/entsog/operator_point_directions.parquet")
# Which adjacent countries does UK have direct interconnections to?
uk_links = (
    opd.filter(pl.col("t_so_country") == "UK")
       .group_by("adjacent_country")
       .agg(pl.len().alias("combos"))
       .sort("combos", descending=True)
)
print(uk_links)
```

# Caveats

## 01 Single-file reference dataset (no time partitions)

Output is `operator_point_directions.parquet` overwritten on each refresh. *(Source: `silver/entsog/generic.py L196-202`; `endpoints.py L231-239` `reference=True`.)*

## 02 `is_cam_relevant` coalesces uppercase + camelCase variants

Vendor returns `isCAMRelevant` (uppercase CAM) here vs `isCamRelevant` in operationalData. `_normalise_column_names` collapses both into `is_cam_relevant` via `pl.coalesce`. *(Source: `silver/entsog/generic.py L264-290`; vault Known Issues.)*

## 03 `tSO*` fields produce odd snake_case (`t_so_country`)

The `_camel_to_snake` regex splits `tSO` as `t_s_o`, then collapses repeated `_` to `t_so`. Adjust queries to match the silver column name, not the camelCase. *(Source: `silver/entsog/generic.py L257-261`.)*

## 04 `timeZone` not accepted

Reference endpoints take no `from`/`to`/`timeZone` — full-snapshot only with `limit=-1`. *(Source: vault Query-params; `endpoints.py L231-239`.)*

## 05 `hasData=1` excludes recently-dormant combos

Use without the filter for full historical inventory; with the filter for currently-active combos only. *(Source: vault Known Issues.)*

# Related datasets

- **`operators`** — TSO inventory. `snapshot`. Resolve `operator_key` to TSO metadata. *entsog · reference · snapshot*
- **`connection_points`** — Point inventory. `snapshot`. Resolve `point_key` to point metadata. *entsog · reference · snapshot*
- **`physical_flows`** — Primary operational consumer of this reference. `daily`. Join on operator-point-direction. *entsog · operational · daily*
- **`interconnections`** — Same network topology but as directed-pair (`from`/`to`). `snapshot`. Complementary representation. *entsog · reference · snapshot*
