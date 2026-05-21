---
slug: urgent_market_messages
vendor: entsog
vendor_label: ENTSO-G Transparency
api_code: urgentMarketMessages
last_verified: 2026-05-08
sources_consulted:
  - vault/entsog/urgent_market_messages.md
  - gridflow/src/gridflow/schemas/entsog.py (absent — uses GenericEntsogJsonTransformer dynamic schema)
  - gridflow/src/gridflow/silver/entsog/generic.py::GenericEntsogJsonTransformer (line 80) — `reference_dataset=True` single-file output
  - gridflow/src/gridflow/connectors/entsog/endpoints.py::ENDPOINTS["urgent_market_messages"] (lines 198-205)
  - .planning/reconciliation/entsog/32-urgent-market-messages-manual-transformer-schema.md (wontfix v3-candidate)
discrepancies_found: []
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** TSO outage and event bulletins, <span class="italic fg-accent">in real time.</span>

**Lede:** Real-time TSO operator bulletins covering unavailability, capacity reductions, and other UMM events — the live notification stream for unplanned gas-network events.

**Verified line:** Verified against vendor docs: 2026-05-08 · [ENTSO-G Transparency · /urgentMarketMessages](https://transparency.entsog.eu/)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.urgent_market_messages` (single-file snapshot) |
| API PATH | `/api/v1/urgentMarketMessages` |
| FREQUENCY | as-published (event-driven) |
| PUBLICATION LAG | real-time |
| VOLUME | varies (event-driven; 100s/year EU-wide) |
| PRIMARY KEY | `(id)` — vendor concatenation |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | event-driven | Cadence |
| 2 | real-time | Publication lag |
| 3 | reference | Single-file snapshot |
| 4 | dynamic | Silver schema (no Pydantic class) |

# Sidebar siblings

- interruptions
- physical_flows
- firm_available
- interruptible_available
- operators

# Sample chart

- **Type:** `barsH`
- **Title:** "UMM events per market participant · last 12 months"
- **Subtitle:** "Horizontal bars · count · grouped by TSO"
- **Seed:** 41
- **Toggles:** `1y` (active) / `3y`

# Schema

No Pydantic class — `GenericEntsogJsonTransformer` runs with `reference_dataset=True` (`silver/entsog/generic.py L86, L169-191`), reading the most-recent bronze and writing a single `urgent_market_messages.parquet` instead of partitioned daily files.

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `id` | `str` | Yes | `id` | Vendor concatenation. Dedup key. | `silver/entsog/generic.py L126-130` |
| `message_id` | `str` | Yes | `messageId` | Vendor-internal message ID. | dynamic |
| `timestamp_utc` | `datetime[UTC]` | Yes | `publicationDateTime` (derived) | Set via `_TIMESTAMP_PRIORITY` (publication wins). | `silver/entsog/generic.py L118-120` |
| `publication_date_time` | `datetime[UTC]` | Yes | `publicationDateTime` | When the UMM was published. | `silver/entsog/datetime.py` |
| `event_start` / `event_stop` | `datetime[UTC]` | Yes | `eventStart` / `eventStop` | Outage window (vendor offsets converted to UTC). | `silver/entsog/datetime.py` |
| `event_status` | `str` | Yes | `eventStatus` | `Active` / `Closed` / etc. | dynamic |
| `event_type` | `str` | Yes | `eventType` | Vendor taxonomy. | dynamic |
| `message_type` | `str` | Yes | `messageType` | `"Other"` / vendor-specific. | dynamic |
| `market_participant_key` / `_eic` / `_name` | `str` | Yes | `marketParticipantKey` / `_Eic` / `_Name` | TSO identifiers. | dynamic |
| `unavailability_type` / `unavailability_reason` | `str` | Yes | `unavailabilityType` / `unavailabilityReason` | When known. | dynamic |
| `unit_measure` | `str` | Yes | `unitMeasure` | Capacity unit when applicable. | dynamic |
| `unavailable_capacity` / `available_capacity` / `technical_capacity` | `float` | Yes | `unavailableCapacity` / `availableCapacity` / `technicalCapacity` | Capacity figures in `unit_measure`. | `silver/entsog/generic.py L65-77` |
| `balancing_zone_key` / `_eic` / `_name` | `str` | Yes | `balancingZoneKey` / `_Eic` / `_Name` | When the UMM is zone-scoped. | dynamic |
| `affected_asset_name` / `_eic` | `str` | Yes | `affectedAssetName` / `_Eic` | Specific affected pipeline/station. | dynamic |
| `remarks` | `str` | Yes | `remarks` | Free-text vendor narrative. | dynamic |
| `u_mm_type` | `str` | Yes | `uMMType` | `"Feeds"` etc. (collapsed by `_normalise_column_names` from `uMMType`). | `silver/entsog/generic.py L264-290` |
| `is_latest_version` | `str` | Yes | `isLatestVersion` | `"Yes"` / `"No"` (string, not bool). | dynamic |
| `version_number` / `thread_id` | `str` | Yes | `versionNumber` / `threadId` | Revision tracking. | dynamic |
| `data_provider` | `str` (`"entsog"`) | No | _derived_ | Constant. | `silver/entsog/generic.py L132-136` |
| `ingested_at` | `datetime[UTC]` | No | _derived_ | Wall-clock at silver write. | `silver/entsog/generic.py L132-136` |

**PARQUET PATH:** `data/silver/entsog/urgent_market_messages.parquet` (single-file reference dataset — `silver/entsog/generic.py L196-202`)
**PARTITION BY:** none (single-file overwrite on weekly refresh)
**DEDUP KEY:** `(id)` — vendor concatenation

# Sample data

| publication_date_time | message_id | market_participant_name | event_status | event_start | event_stop | unavailable_capacity | unit_measure |
|---|---|---|---|---|---|---|---|
| 2021-01-07T11:08:29+00:00 | 0000000000000000000038576_001 | Open Grid Europe | Active | 2021-10-01T04:00:00+00:00 | 2030-01-01T05:00:00+00:00 | (null) | (null) |
| 2026-04-22T08:14:00+00:00 | 0000000000000000000044120_001 | National Gas TSO | Active | 2026-04-22T10:00:00+00:00 | 2026-04-22T18:00:00+00:00 | 25,000,000 | kWh/d |
| **2026-05-02T07:33:00+00:00** | **0000000000000000000044299_001** | **National Gas TSO** | **Active** | **2026-05-03T06:00:00+00:00** | **2026-05-03T14:00:00+00:00** | **50,000,000** | **kWh/d** |
| 2026-03-15T14:20:00+00:00 | 0000000000000000000043891_001 | Gas Networks Ireland | Closed | 2026-03-16T04:00:00+00:00 | 2026-03-16T20:00:00+00:00 | 30,000,000 | kWh/d |
| 2026-02-08T09:00:00+00:00 | 0000000000000000000043402_001 | bayernets | Closed | 2026-02-09T04:00:00+00:00 | 2026-02-10T04:00:00+00:00 | 100,000,000 | kWh/d |
| 2025-12-22T11:45:00+00:00 | 0000000000000000000042855_001 | Snam Rete Gas | Closed | 2025-12-23T04:00:00+00:00 | 2025-12-23T22:00:00+00:00 | 60,000,000 | kWh/d |
| 2025-11-30T16:00:00+00:00 | 0000000000000000000042580_001 | Open Grid Europe | Closed | 2025-12-01T04:00:00+00:00 | 2025-12-02T04:00:00+00:00 | 80,000,000 | kWh/d |
| 2025-10-18T07:00:00+00:00 | 0000000000000000000042199_001 | Transgaz | Closed | 2025-10-18T04:00:00+00:00 | 2025-10-18T20:00:00+00:00 | 40,000,000 | kWh/d |

**Sources:** First row verbatim from vault Bronze sample (`urgent_market_messages.md` L66-100; Open Grid Europe 2021 multi-year UMM). Remaining rows synthesised respecting the vendor's `eventStatus` (Active/Closed) and capacity-unit conventions. Highlighted row is a National Gas TSO UMM at Bacton published 2026-05-02, signalling a planned 8-hour 50 GWh/d capacity reduction on 2026-05-03 — the kind of forward-looking signal useful for gas-supply nowcasts.

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `transparency.entsog.eu/api/v1/urgentMarketMessages?limit=100&offset=0`
- AUTH: None (public). No `from`/`to` accepted — full-snapshot only.

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/entsog/urgent_market_messages/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer` (subclassed as `UrgentMarketMessagesTransformer`, `reference_dataset=True`)

**Tab 1 — Example URL**
```
https://transparency.entsog.eu/api/v1/urgentMarketMessages?limit=-1
```

**Tab 2 — DuckDB · SQL**
```sql
-- Active UMMs in the next 30 days (forward-looking outages)
SELECT publication_date_time, market_participant_name, message_type,
       event_start, event_stop,
       unavailable_capacity / 1e6 AS unavailable_gwh
FROM read_parquet('data/silver/entsog/urgent_market_messages.parquet')
WHERE event_status = 'Active'
  AND event_start BETWEEN current_timestamp AND current_timestamp + INTERVAL 30 DAY
ORDER BY event_start;
```

**Tab 3 — Python · polars**
```python
import polars as pl

df = pl.read_parquet("data/silver/entsog/urgent_market_messages.parquet")
# UMM event count by TSO in the last year
recent = (
    df.filter(pl.col("publication_date_time") >= pl.lit("2025-05-01"))
      .group_by("market_participant_name")
      .agg(pl.len().alias("events"))
      .sort("events", descending=True)
)
print(recent.head(15))
```

# Caveats

## 01 Single-file reference dataset (no time partitions)

Output is `urgent_market_messages.parquet` overwritten on each refresh, not the partitioned `year=YYYY/month=MM/` layout used by other operational datasets. *(Source: `silver/entsog/generic.py L196-202`; `endpoints.py L198-205` `reference=True`.)*

## 02 No `from`/`to` query params

The endpoint returns a full UMM snapshot; pagination via `limit`+`offset` only. Connector sets `limit=-1` (all records). *(Source: vault Query-params table; `endpoints.py L198-205`.)*

## 03 `uMMType` → `u_mm_type` snake_case

Vendor camelCase `uMMType` is normalised to `u_mm_type` (extra underscore between M and M is a `_camel_to_snake` artefact, not a typo). *(Source: `silver/entsog/generic.py L257-261, L264-290`.)*

## 04 `is_latest_version` is a string, not bool

Vendor returns `"Yes"`/`"No"` text — the transformer preserves it as `str`. Cast in DuckDB if you need a boolean predicate. *(Source: vault Bronze sample L95; `silver/entsog/generic.py` does not coerce.)*

## 05 Long-running events (years-spanning)

A single UMM can span years (e.g. the 2021 OGE notification with `eventStop=2030-01-01`). Filter on `eventStatus = "Active"` and the relevant `event_start` window, not on `publicationDateTime` alone. *(Source: vault Bronze sample L78-79.)*

# Related datasets

- **`interruptions`** — Historic interruption events (endpoint withdrawn 2026-05-19). `event-driven`. UMM partially replaces the live signal. *entsog · UMM · historic*
- **`operators`** — TSO reference data joinable on `market_participant_key`. `snapshot`. Attach human TSO names and country. *entsog · reference · snapshot*
- **`physical_flows`** — Flow at affected points. `daily`. Cross-check UMM windows against actual flow drops. *entsog · operational · daily*
- **`firm_available`** — Available firm capacity. `daily`. UMMs typically signal forthcoming reductions to this dataset. *entsog · capacity · daily*
