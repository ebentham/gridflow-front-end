---
slug: cmp_unsuccessful_requests
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: cmpUnsuccessfulRequests
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/cmp_unsuccessful_requests.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80)
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["cmp_unsuccessful_requests"] (lines 128-136)
  - .planning/reconciliation/entsog/16-cmp-unsuccessful-requests-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found:
  - source_a: "vault Bronze sample (cmp_unsuccessful_requests.md L93)"
    source_a_says: "directionKey is capitalised: 'Exit' (vs lowercase 'exit' in /operationalData)"
    source_b: "vault Known Issues; GenericEntsogJsonTransformer._normalise_column_names"
    source_b_says: "Casing variance documented as cross-endpoint quirk"
    orchestrator_recommendation: "Surface in Caveats #02 — lowercase both sides when joining to operationalData family."
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Auction requests that <span class="italic fg-accent">didn't win.</span>

**Lede:** Capacity auction requests that exceeded allocated volume — the canonical CMP signal for excess shipper demand at congested interconnection points.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /cmpUnsuccessfulRequests](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.cmp_unsuccessful_requests` |
| API PATH | `/api/v1/cmpUnsuccessfulRequests` |
| FREQUENCY | as published (post-auction) |
| PUBLICATION LAG | as published |
| VOLUME | varies (auction-event-driven) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | as published | Frequency |
| 2 | kWh/d | Reporting unit |
| 3 | post-auction | Cadence relative to auction |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- cmp_unavailable_firm_capacity
- cmp_auction_premiums
- available_through_oversubscription
- available_through_uioli_long_term
- firm_available

# Sample chart

- **Type:** `barsH`
- **Title:** "Top 10 unsuccessful-request points · last 12 months"
- **Subtitle:** "Horizontal bars · unallocated GWh/day · grouped by point"
- **Seed:** 39
- **Toggles:** `1y` (active) / `3y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` derives columns dynamically. Endpoint-specific fields include `requestedVolume` / `allocatedVolume` / `unallocatedVolume` and `occurenceCount` (vendor spelling preserved).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation including capacity-window timestamps. Dedup key. | `silver/entsog/generic.py L126-130` |
| `timestamp_utc` | `datetime[UTC]` | Yes | `capacityFrom` (derived) | Set via `_TIMESTAMP_PRIORITY` (`capacity_from` is L51). | `silver/entsog/generic.py L118-120, L45-53` |
| `auction_from` / `auction_to` | `datetime[UTC]` | Yes | `auctionFrom` / `auctionTo` | Auction window (may be `"N/A"` → null). | `silver/entsog/datetime.py::parse_entsog_datetime_expr` |
| `capacity_from` / `capacity_to` | `datetime[UTC]` | Yes | `capacityFrom` / `capacityTo` | Capacity-validity window. | `silver/entsog/datetime.py` |
| `operator_key` / `point_key` / `direction_key` | `str` | Yes | `operatorKey` / `pointKey` / `directionKey` | Operator-point-direction. **`direction_key` is capitalised here (`"Exit"`/`"Entry"`)** — see Caveats #02. | dynamic |
| `requested_volume` | `float` | Yes | `requestedVolume` | Capacity requested. | `silver/entsog/generic.py L65-77` (`_NUMERIC_NAMES`) |
| `allocated_volume` | `float` | Yes | `allocatedVolume` | Capacity allocated (less than requested). | `silver/entsog/generic.py L65-77` |
| `unallocated_volume` | `float` | Yes | `unallocatedVolume` | `requested - allocated`. | `silver/entsog/generic.py L65-77` |
| `occurence_count` | `int` (cast to float by generic) | Yes | `occurenceCount` | Vendor spelling — single `r`. Number of unsuccessful requests aggregated. | dynamic |
| `unit` | `str` | Yes | `unit` | `"kWh/d"`. | dynamic |
| `is_cam_relevant` | `bool` | Yes | `isCamRelevant` | CAM-network-code flag. | dynamic |
| `last_update_date_time` | `datetime[UTC]` | Yes | `lastUpdateDateTime` | Vendor publication timestamp. | `silver/entsog/datetime.py` |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/cmp_unsuccessful_requests/year=YYYY/month=MM/`
**PARTITION BY:** `timestamp_utc (year + month)`
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| capacity_from | capacity_to | point_key | direction_key | requested_volume | allocated_volume | unallocated_volume | occurence_count |
|---|---|---|---|---|---|---|---|
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00526 | Exit | 3,458,880 | 216,000 | 3,242,880 | 14 |
| **2025-10-01T04:00:00+00:00** | **2026-10-01T04:00:00+00:00** | **ITP-00005** | **Exit** | **20,000,000** | **12,000,000** | **8,000,000** | **6** |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00207 | Exit | 40,000,000 | 30,000,000 | 10,000,000 | 4 |
| 2025-10-01T04:00:00+00:00 | 2026-10-01T04:00:00+00:00 | ITP-00495 | Entry | 18,000,000 | 8,000,000 | 10,000,000 | 5 |
| 2024-10-01T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | ITP-00005 | Exit | 25,000,000 | 22,000,000 | 3,000,000 | 3 |
| 2024-10-01T04:00:00+00:00 | 2025-10-01T04:00:00+00:00 | ITP-00207 | Exit | 35,000,000 | 35,000,000 | 0 | 0 |
| 2024-07-01T04:00:00+00:00 | 2024-10-01T04:00:00+00:00 | ITP-00005 | Exit | 15,000,000 | 10,000,000 | 5,000,000 | 4 |
| 2024-04-01T04:00:00+00:00 | 2024-07-01T04:00:00+00:00 | ITP-00005 | Exit | 12,000,000 | 9,000,000 | 3,000,000 | 2 |

**Sources:** First row verbatim from vault Bronze sample (`cmp_unsuccessful_requests.md` L83-101; FR-TSO `ITP-00526` `VIRTUALYS` Exit, 14 unsuccessful requests aggregating 3.24 GWh/d unallocated). Remaining rows synthesised — note `direction_key` is **capitalised** (`"Exit"`/`"Entry"`) here, unlike `/operationalData`. Highlighted row is a synthesised Bacton IUK 2025-26 annual auction where 8 GWh/d went unallocated across 6 unsuccessful requests — typical signal of congestion.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/cmpUnsuccessfulRequests?from={YYYY-MM-DD}&to={YYYY-MM-DD}&timeZone=UCT&periodType=day&pointDirection={...}`
- AUTH: None (public).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/cmp_unsuccessful_requests/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `CmpUnsuccessfulRequestsTransformer`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/cmpUnsuccessfulRequests?from=2026-05-06&to=2026-05-06&timeZone=UCT&periodType=day&forceDownload=true&limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Top 10 GB points by unallocated volume in the current gas year
SELECT point_key, point_label, direction_key,
       SUM(unallocated_volume) / 1e6 AS total_unallocated_gwh,
       SUM(occurence_count) AS total_unsuccessful_requests
FROM read_parquet('data/silver/entsog/cmp_unsuccessful_requests/**/*.parquet')
WHERE operator_key LIKE 'UK-TSO%'
  AND capacity_from >= '2025-10-01'
  AND capacity_from <  '2026-10-01'
GROUP BY 1, 2, 3
ORDER BY total_unallocated_gwh DESC
LIMIT 10;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/cmp_unsuccessful_requests/**/*.parquet")
# Lowercase direction_key to align with operationalData family
joined = df.with_columns(pl.col("direction_key").str.to_lowercase())
# Top 10 points by unsuccessful request count
print(
    joined.group_by(["point_key", "direction_key"])
          .agg(pl.col("occurence_count").sum())
          .sort("occurence_count", descending=True)
          .head(10)
)
```

# Caveats

## 01 `occurenceCount` (vendor typo) — single `r`

Vendor spells `occurenceCount` (missing the second `r` in `occurrence`). Preserved verbatim in silver as `occurence_count`. *(Source: vault Bronze sample L101.)*

## 02 `direction_key` is capitalised here (`"Exit"`/`"Entry"`)

Unlike `/operationalData` (lowercase `entry`/`exit`), this endpoint returns capitalised values. Lowercase both sides before joining across endpoint families. *(Source: vault Bronze sample L93; vault Known Issues.)*

## 03 `timeZone=UCT` (vendor typo, intentional)

Connector sends `UCT` not `UTC`. *(Source: `connectors/entsog/endpoints.py L17`.)*

## 04 Empty windows return HTTP 404

ENTSO-G's empty-set convention. *(Source: `connectors/entsog/client.py L24-28, L109-115`.)*

## 05 Auction-from can be `"N/A"`

Some CMP records have no specific auction window (long-standing congestion declarations). `parse_entsog_datetime_expr` returns null for unparseable values. *(Source: vault Bronze sample L83; `silver/entsog/datetime.py`.)*

# Related datasets

- **`cmp_unavailable_firm_capacity`** — Firm capacity declared unavailable. `daily`. CMP trigger condition. *entsog · CMP · daily*
- **`cmp_auction_premiums`** — Premiums paid at auctions. `daily`. Pair to derive market-clearing prices at congested points. *entsog · CMP · daily*
- **`available_through_oversubscription`** — Oversubscription-released capacity. `daily`. CMP response to unsuccessful requests. *entsog · capacity · daily*
- **`available_through_uioli_long_term`** — UIOLI-released long-term capacity. `daily`. Sister CMP procedure. *entsog · capacity · daily*
