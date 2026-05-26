---
slug: cmp_unavailable_firm_capacity
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: cmpUnavailables
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/cmp_unavailable_firm_capacity.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["cmp_unavailable_firm_capacity"] (lines 137-145)
  - .planning/reconciliation/entsog/15-cmp-unavailable-firm-capacity-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Firm capacity declared <span class="italic fg-accent">unavailable.</span>

**Lede:** Firm capacity classified as unavailable but allocated — the canonical CMP signal that triggers UIOLI and oversubscription mechanisms.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /cmpUnavailables](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.cmp_unavailable_firm_capacity` |
| API PATH | `/api/v1/cmpUnavailables` |
| FREQUENCY | as published |
| PUBLICATION LAG | as published |
| VOLUME | varies (CMP-event-driven) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | as published | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | CMP-trigger | Cadence |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- cmp_unsuccessful_requests
- cmp_auction_premiums
- available_through_uioli_long_term
- available_through_oversubscription
- firm_booked

# Sample chart

- **Type:** `barsH`
- **Title:** "Points with unavailable firm capacity · last 12 months"
- **Subtitle:** "Horizontal bars · unavailable GWh/day · grouped by point"
- **Seed:** 42
- **Toggles:** `1y` (active) / `3y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Same CMP shape as `cmp_unsuccessful_requests`; the differentiator is `unavailable_capacity` (vs `requested`/`allocated`/`unallocated`).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `capacityFrom` (derived) | Set via `_TIMESTAMP_PRIORITY`. | `silver/entsog/generic.py L118-120, L45-53` |
| `capacity_from` / `capacity_to` | `datetime[UTC]` | Yes | `capacityFrom` / `capacityTo` | Capacity-validity window. | `silver/entsog/datetime.py` |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction (capitalised on this endpoint). | dynamic |
| `unavailable_capacity` | `float` | Yes | `unavailableCapacity` | Firm capacity declared unavailable. | `silver/entsog/generic.py L65-77` (`_NUMERIC_NAMES`) |
| `available_capacity` | `float` | Yes | `availableCapacity` | Currently available portion. | `silver/entsog/generic.py L65-77` |
| `technical_capacity` | `float` | Yes | `technicalCapacity` | Maximum technical capacity (reference). | `silver/entsog/generic.py L65-77` |
| `unit` | `str` | Yes | `unit` | `"kWh/d"`. | dynamic |
| `is_cam_relevant` / `is_cmp_relevant` | `bool` | Yes | `isCamRelevant` / `isCmpRelevant` | Regulatory flags. | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/cmp_unavailable_firm_capacity/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| capacity_from | capacity_to | point_key | direction_key | unavailable_capacity | available_capacity | technical_capacity | unit |
|---|---|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | Exit | 50,000,000 | 500,000,000 | 580,000,000 | kWh/d |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00207 | Exit | 15,000,000 | 175,000,000 | 200,000,000 | kWh/d |
| **2025-10-01T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **ITP-00495** | **Entry** | **8,000,000** | **90,000,000** | **100,000,000** | **kWh/d** |
| 2024-10-01T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | ITP-00005 | Exit | 35,000,000 | 510,000,000 | 580,000,000 | kWh/d |
| 2024-10-01T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | ITP-00207 | Exit | 22,000,000 | 170,000,000 | 200,000,000 | kWh/d |
| 2026-04-01T04:00:00+00:00 | 2026-07-01T04:00:00+00:00 | ITP-00005 | Exit | 25,000,000 | 520,000,000 | 580,000,000 | kWh/d |
| 2026-04-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00005 | Exit | 30,000,000 | 515,000,000 | 580,000,000 | kWh/d |
| 2023-10-01T04:00:00+00:00 | 2024-10-01T04:00:00+00:00 | ITP-00005 | Exit | 40,000,000 | 505,000,000 | 580,000,000 | kWh/d |

**Sources:** Synthesised — the vault Bronze sample's structural fields applied to canonical GB point capacities. Highlighted row is Moffat IE entry at 8 GWh/d unavailable out of 90 GWh/d available — small absolute but proportionally significant for IE supply security. Note `direction_key` is capitalised here (CMP-family convention).

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/cmpUnavailables?from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/cmp_unavailable_firm_capacity/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `CmpUnavailableFirmCapacityTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/cmpUnavailables?from=2026-05-06&to=2026-05-06&timeZone=UCT&periodType=day&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Unavailability as a percentage of technical capacity per point (current gas year)
SELECT point_key, point_label, direction_key,
       MAX_BY(unavailable_capacity, capacity_from) / 1e6 AS unavailable_gwh,
       MAX_BY(technical_capacity, capacity_from)   / 1e6 AS technical_gwh,
       (MAX_BY(unavailable_capacity, capacity_from) * 100.0
        / NULLIF(MAX_BY(technical_capacity, capacity_from), 0)) AS pct_unavailable
FROM read_parquet('data/silver/entsog/cmp_unavailable_firm_capacity/**/*.parquet')
WHERE capacity_from <= current_date AND capacity_to > current_date
GROUP BY 1, 2, 3
ORDER BY pct_unavailable DESC;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/cmp_unavailable_firm_capacity/**/*.parquet")
# How does unavailability evolve year-over-year at Bacton?
yoy = (
    df.filter(pl.col("point_key") == "ITP-00005")
      .with_columns(pl.col("capacity_from").dt.year().alias("year"))
      .group_by("year")
      .agg((pl.col("unavailable_capacity").mean() / 1e6).alias("avg_unavailable_gwh"))
      .sort("year")
)
print(yoy)
```

# Caveats

## 01 `direction_key` is capitalised (`"Exit"`/`"Entry"`)

CMP-family endpoints capitalise direction values — unlike `/operationalData`. Lowercase both sides for cross-family joins. *(Source: vault Known Issues; CMP-family convention.)*

## 02 Triggers UIOLI / oversubscription

When `unavailable_capacity` is significant relative to `technical_capacity`, the TSO is required to consider UIOLI long-term or oversubscription. Pair with `available_through_*` datasets to verify the response. *(Source: ENTSO-G CMP Network Code.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 `available_capacity` + `unavailable_capacity` typically < `technical_capacity`

The residual is TSO-reserved (system balancing, frequency control). Don't model `technical = available + unavailable` exactly. *(Source: ENTSO-G data dictionary.)*

# Related datasets

- **`cmp_unsuccessful_requests`** — Auction requests that failed because of unavailability. `as published`. Causal companion to this dataset. *entsog · CMP · daily*
- **`cmp_auction_premiums`** — Premiums when scarcity drove prices up. `as published`. Price counterpart to unavailability. *entsog · CMP · daily*
- **`available_through_uioli_long_term`** — UIOLI long-term recovery (the response). `daily`. Expected uplift when this dataset shows persistent unavailability. *entsog · capacity · daily*
- **`firm_technical`** — Maximum technical capacity. `daily`. Reference ceiling. *entsog · capacity · daily*
