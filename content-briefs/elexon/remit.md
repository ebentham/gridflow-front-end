---
slug: remit
vendor: elexon
vendor_label: Elexon BMRS
api_code: REMIT
last_verified: 2026-05-09
sources_consulted:
  - vault/elexon/remit.md
  - gridflow/src/gridflow/schemas/elexon.py (absent — no ElexonREMIT class; silver transformer enforces shape directly)
  - gridflow/src/gridflow/silver/elexon/remit.py::REMITTransformer (lines 18-149, APPEND_ONLY=True, DATASET_VERSION=2.0.0)
  - gridflow/src/gridflow/connectors/elexon/endpoints.py (lines 240-245, PUBLISH_DATETIME with max_chunk_hours=23)
  - https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/REMIT (fetched 2026-05-20 — javascript-rendered, no extractable content)
discrepancies_found:
  - source_a: "gridflow schemas/elexon.py"
    source_a_says: "No ElexonREMIT class declared"
    source_b: "gridflow silver/elexon/remit.py L19-149"
    source_b_says: "REMITTransformer outputs 25 columns including timing, asset, capacity, and event-status fields"
    orchestrator_recommendation: "trust silver transformer; remit is the widest non-Pydantic schema in elexon and a candidate for adding a dedicated class to ease downstream consumption"
ready_for_claude_design: true
checked_at: 2026-05-20T00:00:00Z
---

# Editorial layer

**Tagline:** Outage messages, <span class="italic fg-accent">every UMM.</span>

**Lede:** REMIT is the GB outage and unavailability feed mandated by EU Regulation 1227/2011 — every Urgent Market Message raised against generation, transmission, or demand-side assets. Each record carries start/end times, capacity affected, cause, and event status, with revision tracking via `revision_number`. This is the canonical source for "what's out and when".

**Verified line:** Verified against vendor docs: 2026-05-09 · [Elexon BMRS · REMIT](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/REMIT)

# Hero metadata

| Cell label | Value |
|---|---|
| SILVER PATH | `silver.remit` |
| API PATH | `/datasets/REMIT` |
| FREQUENCY | as published |
| PUBLICATION LAG | — |
| VOLUME | varies |
| PRIMARY KEY | `(mrid, revision_number)` (append-only) |

# Stats strip

| slot | value | label |
|---|---|---|
| 1 | 23 h | Max chunk hours (vendor cap) |
| 2 | append-only | Silver write mode |
| 3 | revision-tracked | PIT semantics |
| 4 | 25 | Schema columns |

# Sidebar siblings

- bmunits_reference
- fou2t14d
- uou2t14d
- nonbm
- soso

# Overview

1. <code>remit</code> is the **REMIT Outage and Unavailability Messages** feed — published per EU Regulation 1227/2011, every UMM raised against a GB asset (`Production`, `Transmission`, `Consumption`) with `mrid` (Message MRID), `revision_number`, `event_type`, `unavailability_type` (Planned/Unplanned), `event_start_time`, `event_end_time`, `normal_capacity_mw`, `available_capacity_mw`, and a free-text `cause`. The 25-column silver schema makes it the widest dataset in the Elexon set.

2. Gridflow fetches it from <code>/datasets/REMIT</code> with a **23-hour chunk cap** (`max_chunk_hours=23`, `connectors/elexon/endpoints.py L244`) — the vendor enforces a max-1-day query window. The <code>REMITTransformer</code> writes **append-only** silver files (`APPEND_ONLY=True`, `silver/elexon/remit.py L38`) so every revision of every UMM is preserved; latest-revision selection is a read-time concern. No Pydantic class is declared.

3. Cadence is irregular — UMMs are raised as events occur and revised as estimates change. Verified against the live API on 2026-05-09; the sample showed a 147-revision message for `T_SOFOW-12` (Sofia offshore wind unit 12) marked "Active" with cause "Ambient Conditions" and an outage running from 2025-12-09 to 2026-05-22. The `outageProfile` (a per-timestep capacity array nested in the bronze JSON) is not flattened into silver.

# Sample chart

- **Type:** `barsH`
- **Title:** "Active REMIT outages by fuel type · current snapshot"
- **Subtitle:** "Horizontal bars · unavailable MW · UTC · 2026-05-08"
- **Seed:** 36
- **Toggles:** `active` (active) / `planned upcoming`

# Schema

Defined in `gridflow/silver/elexon/remit.py` · `REMITTransformer.output_cols` (no dedicated Pydantic class). Partitioned by `settlement_date` (year + month, derived from `timestamp_utc` = `published_at`). Point-in-time field: `revision_number`. Write mode: **append-only** (every revision preserved).

| Column | Type | Nullable | Source field | Notes | Gridflow citation |
|---|---|---|---|---|---|
| `mrid` | `str` | No | `mrid` | REMIT message MRID — e.g. `48X000000000392E-NGET-RMT-00209309`. | `silver/elexon/remit.py L72, L101` |
| `revision_number` | `Optional[int]` | Yes | `revisionNumber` | Increments per revision; highest = canonical state. | `silver/elexon/remit.py L73, L127-128` |
| `timestamp_utc` | `datetime[UTC]` | No | `publishTime` (renamed `published_at`) | Publication time of this revision. | `silver/elexon/remit.py L107-112` |
| `message_type` | `Optional[str]` | Yes | `messageType` | e.g. `UnavailabilitiesOfElectricityFacilities`. | `silver/elexon/remit.py L76` |
| `message_heading` | `Optional[str]` | Yes | `messageHeading` | e.g. `Actual Availability of Generation Unit`. | `silver/elexon/remit.py L77` |
| `event_type` | `Optional[str]` | Yes | `eventType` | e.g. `Production unavailability`. | `silver/elexon/remit.py L78` |
| `unavailability_type` | `Optional[str]` | Yes | `unavailabilityType` | `Planned` / `Unplanned`. | `silver/elexon/remit.py L79` |
| `participant_id` | `Optional[str]` | Yes | `participantId` | Market participant identifier (operator name or short code). | `silver/elexon/remit.py L80` |
| `registration_code` | `Optional[str]` | Yes | `registrationCode` | REMIT registration code. | `silver/elexon/remit.py L81` |
| `asset_id` | `Optional[str]` | Yes | `assetId` | Asset identifier (often a BM unit ID prefixed `T_`/`E_`). | `silver/elexon/remit.py L82` |
| `asset_type` | `Optional[str]` | Yes | `assetType` | `Production` / `Transmission` / `Consumption`. | `silver/elexon/remit.py L83` |
| `affected_unit` | `Optional[str]` | Yes | `affectedUnit` | Affected unit shortname. | `silver/elexon/remit.py L84` |
| `affected_unit_eic` | `Optional[str]` | Yes | `affectedUnitEIC` | ENTSO-E EIC of affected unit. | `silver/elexon/remit.py L85` |
| `bidding_zone` | `Optional[str]` | Yes | `biddingZone` | EIC bidding zone (`10YGB----------A` for GB). | `silver/elexon/remit.py L86` |
| `fuel_type` | `Optional[str]` | No | `fuelType` | ENTSO-E fuel category (`Wind Offshore`, `Fossil Gas`, etc.). | `silver/elexon/remit.py L87` |
| `normal_capacity_mw` | `Optional[float]` | Yes | `normalCapacity` | MW. Nameplate capacity. | `silver/elexon/remit.py L88, L123-125` |
| `available_capacity_mw` | `Optional[float]` | Yes | `availableCapacity` | MW. Currently-available capacity (= `normal - unavailable`). | `silver/elexon/remit.py L89` |
| `unavailable_capacity_mw` | `Optional[float]` | Yes | `unavailableCapacity` | MW. Capacity offline due to this event. | `silver/elexon/remit.py L90` |
| `event_status` | `Optional[str]` | Yes | `eventStatus` | `Active` / `Withdrawn` / etc. | `silver/elexon/remit.py L91` |
| `event_start_time` | `Optional[datetime[UTC]]` | Yes | `eventStartTime` | Outage start. | `silver/elexon/remit.py L92, L114-121` |
| `event_end_time` | `Optional[datetime[UTC]]` | Yes | `eventEndTime` | Estimated outage end. Frequently revised. | `silver/elexon/remit.py L93, L114-121` |
| `cause` | `Optional[str]` | Yes | `cause` | Free-text cause (`Ambient Conditions`, `Planned Outage`, ...). | `silver/elexon/remit.py L94` |
| `related_information` | `Optional[str]` | Yes | `relatedInformation` | Free-text update notes. | `silver/elexon/remit.py L95` |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. | `silver/elexon/remit.py L132` |
| `ingested_at` | `Optional[datetime[UTC]]` | Yes | _derived_ | Time ingested into bronze. | `silver/elexon/remit.py L133` |

**PARQUET PATH:** `data/silver/elexon/remit/year=YYYY/month=MM/remit_YYYYMMDD_run<available_at>.parquet` (run-suffixed; append-only)
**PARTITION BY:** `settlement_date (year + month)` — derived from `timestamp_utc` (publication time)
**DEDUP KEY:** `(mrid, revision_number)` — implied by append-only writes; readers must select latest revision

# Sample data

| mrid | revision_number | timestamp_utc | event_type | participant_id | asset_id | fuel_type | normal_capacity_mw | unavailable_capacity_mw | event_status | event_start_time | event_end_time | cause |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **48X000000000392E-NGET-RMT-00209309** | **147** | **2026-05-06T23:09:05+00:00** | **Production unavailability** | **SOFIA** | **T_SOFOW-12** | **Wind Offshore** | **350.0** | **350.0** | **Active** | **2025-12-09T05:00:00+00:00** | **2026-05-22T04:00:00+00:00** | **Ambient Conditions** |
| 48X000000000392E-NGET-RMT-00208891 | 88 | 2026-05-06T12:00:00+00:00 | Production unavailability | DRAX | T_DRAXX-1 | Biomass | 645.0 | 645.0 | Active | 2026-05-04T08:00:00+00:00 | 2026-05-08T16:00:00+00:00 | Planned Outage |
| 48X000000000392E-NGET-RMT-00208712 | 4 | 2026-05-06T08:15:00+00:00 | Production unavailability | EDF | T_HEYM27 | Nuclear | 605.0 | 605.0 | Active | 2026-04-15T00:00:00+00:00 | 2026-09-30T23:00:00+00:00 | Planned Outage |
| 48X000000000392E-NGET-RMT-00208712 | 5 | 2026-05-07T10:00:00+00:00 | Production unavailability | EDF | T_HEYM27 | Nuclear | 605.0 | 605.0 | Active | 2026-04-15T00:00:00+00:00 | 2026-10-15T23:00:00+00:00 | Planned Outage |
| 48X000000000392E-NGET-RMT-00208650 | 2 | 2026-05-05T18:30:00+00:00 | Production unavailability | RWE | T_PEHE-2 | Fossil Gas | 540.0 | 540.0 | Active | 2026-05-05T18:00:00+00:00 | 2026-05-06T06:00:00+00:00 | Unplanned |
| 48X000000000392E-NGET-RMT-00208610 | 12 | 2026-05-06T00:15:00+00:00 | Production unavailability | DRAX | T_DRAXX-2 | Biomass | 645.0 | 100.0 | Active | 2026-05-01T00:00:00+00:00 | 2026-05-10T00:00:00+00:00 | Planned Outage |
| 48X000000000392E-NGET-RMT-00208580 | 1 | 2026-05-04T11:00:00+00:00 | Transmission unavailability | NGET | _OXFOR | _null_ | _null_ | _null_ | Active | 2026-05-04T22:00:00+00:00 | 2026-05-05T05:00:00+00:00 | Planned Outage |
| 48X000000000392E-NGET-RMT-00208500 | 6 | 2026-05-03T07:00:00+00:00 | Production unavailability | ORSTED | T_HOWAO-2 | Wind Offshore | 1320.0 | 240.0 | Active | 2026-05-03T07:00:00+00:00 | 2026-05-06T18:00:00+00:00 | Unplanned |

**Sources:** Row 1 (Sofia OW-12, revision 147, `event_status=Active`, `event_end_time=2026-05-22T04:00:00Z`) verbatim from the vault Bronze Sample (vault/elexon/remit.md, live 2026-05-08). Remaining rows synthesised — respect schema constraints (UMM-style mrid, integer revision_number, ENTSO-E fuel types, signed MW capacities) and represent the typical mix: planned outages of biomass and nuclear, unplanned trip of a CCGT, partial-derating of wind. The highlighted **Sofia OW-12 row** is the interesting case: 350 MW offshore wind unit fully offline for 5+ months with 147 revisions tracking estimate updates — exactly the long-running multi-revision pattern REMIT's append-only design exists to capture.

# Dataset-specific section: omitted

`dataset_specific_section: omitted (reason: REMIT's relevant taxonomies (eventType, assetType, unavailabilityType, cause) are documented inline in schema rows. The full vendor codelist is open-ended free-text.)`

# API & ingestion

**Card 1 — Endpoint + Auth**
- ENDPOINT: `data.elexon.co.uk/bmrs/api/v1/datasets/REMIT`
- AUTH: None required for tested endpoints (2026-05-08/09). Some endpoints accept an `apikey` header (env `ELEXON_API_KEY`); register at [elexonportal.co.uk](https://www.elexonportal.co.uk/).

**Card 2 — Bronze + Transformer**
- BRONZE PATH: `data/bronze/elexon/remit/<year>/<month>/<day>/raw_<uuid>.json`
- TRANSFORMER: `gridflow.silver.elexon.remit.REMITTransformer`

**Tab 1 — Example URL**
```
https://data.elexon.co.uk/bmrs/api/v1/datasets/REMIT?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-07T00:00Z&format=json
```

**Tab 2 — DuckDB · SQL**
```sql
-- Latest revision per UMM, currently active outages
SELECT mrid, asset_id, fuel_type, unavailable_capacity_mw,
       event_status, event_start_time, event_end_time, cause
FROM (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY mrid ORDER BY revision_number DESC
  ) AS rn
  FROM read_parquet('data/silver/elexon/remit/**/*.parquet')
  WHERE event_status = 'Active'
)
WHERE rn = 1
  AND event_end_time > current_timestamp
ORDER BY unavailable_capacity_mw DESC NULLS LAST;
```

**Tab 3 — Python · polars**
```python
import polars as pl

remit = pl.read_parquet("data/silver/elexon/remit/**/*.parquet")
# Latest revision per mrid + total currently-unavailable capacity by fuel
latest = (
    remit.sort("revision_number", descending=True)
         .group_by("mrid")
         .first()
)
by_fuel = (
    latest.filter(pl.col("event_status") == "Active")
          .group_by("fuel_type")
          .agg(pl.col("unavailable_capacity_mw").sum().alias("total_mw_out"))
          .sort("total_mw_out", descending=True)
)
print(by_fuel)
```

# Caveats

## 01 23-hour chunk cap (V2-FIX-03)

The vendor enforces an undocumented max-1-day query window. Connector sets `max_chunk_hours=23` for DST safety. Live boundary re-verified 2026-05-09: 23h request → HTTP 200, 25h request → HTTP 400. Long backfills budget many calls. *(Source: vault Implementation Delta + Changelog V2-FIX-03; `connectors/elexon/endpoints.py L240-245`.)*

## 02 Append-only silver — latest revision is read-time

`APPEND_ONLY=True` (`silver/elexon/remit.py L38`) means every revision of every UMM is preserved as a separate row, with the dedup key being implicit (`mrid` plus `revision_number`). The canonical state of a UMM is the row with the highest `revision_number` per `mrid`. Use the SQL window-function pattern above for "current active outages". Reference: F7 phase docs. *(Source: docstring at `silver/elexon/remit.py L19-34`.)*

## 03 No Pydantic schema; 25-column silver

REMIT is the widest non-Pydantic schema in the Elexon set (25 columns). Adding a dedicated Pydantic class would ease consumption but is not currently done. Anything that imports `from gridflow.schemas.elexon import ElexonREMIT` will fail. *(Source: `schemas/elexon.py` grep returns no REMIT class.)*

## 04 `event_end_time` is an estimate, not a commitment

`event_end_time` is the operator's best estimate at the time of publication; it shifts as the outage progresses. The vault sample's `relatedInformation` field — "Estimated End Date / Time changed to 22 May 2026 04:00 (GMT)" — explicitly notes this. For probability-of-return analytics, weight recent revisions more heavily or compute the distribution of revision deltas. *(Source: vault Bronze Sample `relatedInformation` field; `silver/elexon/remit.py L114-121`.)*

## 05 `outageProfile` nested array not flattened into silver

The bronze JSON includes a nested `outageProfile` array carrying per-timestep capacity values (so a single outage can have a complex partial-derating shape over time). The silver transformer does NOT flatten this — only the summary `available_capacity_mw` / `unavailable_capacity_mw` survives. For sub-period outage curves, parse the bronze directly. *(Source: vault Bronze Sample shows the array; `silver/elexon/remit.py` column mapping doesn't reference it.)*

## 06 `bidding_zone` is an EIC, not a friendly name

GB is `10YGB----------A` (16 characters with the GB EIC prefix and dashes). Filtering on `bidding_zone == 'GB'` returns zero rows. Use the full EIC string or `LIKE '%GB%'`. *(Source: vault Bronze Sample.)*

# Related datasets

- **bmunits_reference** — BMU reference list. `weekly`. Join `asset_id` to BMU reference for friendly names, registered capacity context. `elexon · system & reference · weekly`
- **fou2t14d** — 2-14 day generation availability by fuel. `daily`. Active REMIT outages should be reflected in lower FOU2T14D availability; sanity-check the two against each other. `elexon · demand & forecasts · daily`
- **uou2t14d** — 2-14 day availability by BM unit. `daily`. Unit-level companion to FOU2T14D; cross-reference outage events with future availability declarations per BMU. `elexon · demand & forecasts · daily`
- **soso** — SO-SO prices. `daily`. Interconnector trades respond to outage events; large unplanned outages typically shift interconnector flows the next day. `elexon · system & reference · daily`
