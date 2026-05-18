---
source: elexon
dataset_key: remit
vendor: Elexon BMRS
last_verified: 2026-05-09
layer_coverage: bronze, silver
---

# Elexon - REMIT Outage and Unavailability Messages (`REMIT`)

## Overview

REMIT outage and unavailability messages — Regulation (EU) No 1227/2011 mandates publication of generation, transmission, and demand-side asset unavailability events. The dataset carries every UMM (Urgent Market Message) raised against GB assets, with start/end times, capacity affected, cause, and event status.

→ Link to relevant domain concept notes if they exist, e.g.:
  [Imbalance pricing](../../../20-domain/markets/imbalance-price.md)
  [Settlement period](../../../20-domain/concepts/settlement-period.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://data.elexon.co.uk/bmrs/api/v1` |
| Path             | `/datasets/REMIT` |
| Method           | GET |
| Auth             | None required for tested endpoints (2026-05-08). Some endpoints accept an `apikey` header (env: `ELEXON_API_KEY`); registration at https://www.elexonportal.co.uk/. |
| Rate limit       | Vendor-published: not stated. Project default 2 req/sec (asyncio.Semaphore); verified safe 2026-05-08. |
| Pagination       | Connector handles via `page=N` query param; stops when `page >= total_pages`. Reference endpoints (`/reference/bmunits/all`) are not paginated. |
| Historical depth | Active and recent expired messages; full history per UMM lifecycle. |
| Publication lag  | Real-time as messages are raised. |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `publishDateTimeFrom` | string | Yes | As per Elexon Swagger spec for remit. | `2026-05-06T00:00Z` |
| `publishDateTimeTo` | string | Yes | As per Elexon Swagger spec for remit. | `2026-05-06T03:00Z` |
| `format` | string | No | Response data format. Use json/xml to include metadata. | `json` |

### Working curl example

```bash
# Replace <ELEXON_API_KEY> with your env var if you choose to send one (Elexon endpoints
# tested 2026-05-08 do NOT require a key; set anyway for vendor courtesy).
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://data.elexon.co.uk/bmrs/api/v1/datasets/REMIT?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-07T00:00Z&format=json" \
  -o "/tmp/elexon-remit.json"
```

---

## Bronze layer

**Path pattern**: `data/bronze/elexon/remit/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per API call (paginated requests append additional files for the same date partition).

### Bronze sample

Captured live 2026-05-08 from the https://data.elexon.co.uk/bmrs/api/v1/datasets/REMIT?publishDateTimeFrom=2026-05-06T00:00Z&publishDateTimeTo=2026-05-07T00:00Z&format=json:

```json
{
  "data": [
    {
      "dataset": "REMIT",
      "mrid": "48X000000000392E-NGET-RMT-00209309",
      "revisionNumber": 147,
      "publishTime": "2026-05-06T23:09:05Z",
      "createdTime": "2026-05-06T23:00:13Z",
      "messageType": "UnavailabilitiesOfElectricityFacilities",
      "messageHeading": "Actual Availability of Generation Unit",
      "eventType": "Production unavailability",
      "unavailabilityType": "Unplanned",
      "participantId": "SOFIA",
      "registrationCode": "48X000000000392E",
      "assetId": "T_SOFOW-12",
      "assetType": "Production",
      "affectedUnit": "SOFWO-12",
      "affectedUnitEIC": "48W0000SOFOW-12T",
      "biddingZone": "10YGB----------A",
      "fuelType": "Wind Offshore",
      "normalCapacity": 350.0,
      "availableCapacity": 0.0,
      "unavailableCapacity": 0.0,
      "eventStatus": "Active",
      "eventStartTime": "2025-12-09T05:00:00Z",
      "eventEndTime": "2026-05-22T04:00:00Z",
      "cause": "Ambient Conditions",
      "relatedInformation": "Estimated End Date / Time changed to 22 May 2026 04:00 (GMT); Detailed MEL profile has changed",
      "outageProfile": [
        {
          "startTime": "2025-12-09T05:00:00Z",
          "endTime": "2025-12-09T05:00:00Z",
          "capacity": 0.0
        },
        {
          "startTime": "2025-12-09T05:00:00Z",
          "endTime": "2026-05-22T04:00:00Z",
          "capacity": 0.0
        }
      ]
    },
    "... (truncated)"
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/elexon/remit/year=YYYY/month=MM/remit_YYYYMMDD_run<available_at>.parquet`
**Write mode**: append-only revision-preserving Silver files (`APPEND_ONLY = True`).
**Transformer class**: `gridflow.silver.elexon.remit.REMITTransformer`
**Pydantic schema**: _Not declared in `schemas/elexon.py` — silver transformer enforces shape directly. See Implementation delta._
**Dedup key**: _inline in transformer (see `silver/elexon/remit.py`)_
**Point-in-time field**: `revision_number`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `mrid` | `str` | No | `mrid` | REMIT message MRID. |
| `revision_number` | `int` | Yes | `revisionNumber` | Revision number. |
| `timestamp_utc` | `datetime[UTC]` | No | _derived_ | Derived from (settlement_date, settlement_period) via `utils/time.settlement_period_to_utc`. |
| `message_type` | `str` | Yes | `messageType` | REMIT message type. |
| `message_heading` | `str` | Yes | `messageHeading` | Message heading. |
| `event_type` | `str` | Yes | `eventType` | Event type code. |
| `unavailability_type` | `str` | Yes | `unavailabilityType` | Planned/Unplanned. |
| `participant_id` | `str` | Yes | `participantId` | Market participant identifier. |
| `registration_code` | `str` | Yes | `registrationCode` | REMIT registration code. |
| `asset_id` | `str` | Yes | `assetId` | Asset identifier. |
| `asset_type` | `str` | Yes | `assetType` | Asset type. |
| `affected_unit` | `str` | Yes | `affectedUnit` | Affected unit name. |
| `affected_unit_eic` | `str` | Yes | `affectedUnitEIC` | EIC of affected unit. |
| `bidding_zone` | `str` | Yes | `biddingZone` | Bidding zone code. |
| `fuel_type` | `str` | No | `fuelType` | Fuel category (CCGT, COAL, NUCLEAR, WIND, etc.). |
| `normal_capacity_mw` | `float` | Yes | `normalCapacity` | MW. |
| `available_capacity_mw` | `float` | Yes | `availableCapacity` | MW. |
| `unavailable_capacity_mw` | `float` | Yes | `unavailableCapacity` | MW. |
| `event_status` | `str` | Yes | `eventStatus` | Active / Withdrawn etc. |
| `event_start_time` | `datetime[UTC]` | Yes | `eventStartTime` | Outage start. |
| `event_end_time` | `datetime[UTC]` | Yes | `eventEndTime` | Outage end. |
| `cause` | `str` | Yes | `cause` | Free-text cause. |
| `related_information` | `str` | Yes | `relatedInformation` | Related information field. |
| `data_provider` | `str` | No | _derived_ | Default `"elexon"`. |
| `ingested_at` | `datetime[UTC]` | Yes | _derived_ | Time ingested into bronze. |

### Silver sample

```python
[
    {
        "mrid": "48X000000000392E-NGET-RMT-00209309",
        "revision_number": 147,
        "timestamp_utc": "2026-05-06T00:00:00+00:00",
        "message_type": "UnavailabilitiesOfElectricityFacilities",
        "message_heading": "Actual Availability of Generation Unit",
        "event_type": "Production unavailability",
        "unavailability_type": "Unplanned",
        "participant_id": "SOFIA",
        "registration_code": "48X000000000392E",
        "asset_id": "T_SOFOW-12",
        "asset_type": "Production",
        "affected_unit": "SOFWO-12",
        "affected_unit_eic": "48W0000SOFOW-12T",
        "bidding_zone": "10YGB----------A",
        "fuel_type": "Wind Offshore",
        "normal_capacity_mw": 350.0,
        "available_capacity_mw": 0.0,
        "unavailable_capacity_mw": 0.0,
        "event_status": "Active",
        "event_start_time": "2025-12-09T05:00:00Z",
        "event_end_time": "2026-05-22T04:00:00Z",
        "cause": "Ambient Conditions",
        "related_information": "Estimated End Date / Time changed to 22 May 2026 04:00 (GMT); Detailed MEL profile has changed",
        "data_provider": "elexon",
        "ingested_at": "2026-05-08T12:00:00Z"
    },
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **Max-1-day query window enforced** — see Implementation delta.
- **Revisions**: `revisionNumber` increments — keep the highest per `mrid` for the canonical state.

---

## Implementation delta

- **Vendor-enforced max 1-day query window — RESOLVED in V2 (2026-05-09).** Connector now declares `max_chunk_hours=23` on `ENDPOINTS["remit"]` so chunks stay safely under the undocumented 1-day cap. Boundary re-verified live 2026-05-09: 23h request → HTTP 200, 25h request → HTTP 400 (same vendor error body). See gridflow commit `fix(V2-C):`.
- **No Pydantic schema** in `schemas/elexon.py`; silver `REMITTransformer` enforces 24-column output set.

---

## Changelog

- **2026-05-09 — V2-FIX-03.** `max_chunk_hours=23` for safe DST margin. Regression test in `tests/unit/test_elexon_endpoints.py::TestRemitSosoMaxChunkHours`. Live-revalidated 23h pass / 25h fail boundary.
- **2026-05-08 — V1.** Live-validated; vendor 1-day cap surfaced.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (Swagger UI)](https://bmrs.elexon.co.uk/api-documentation)
- [Connector source](../../../../../../Python/gridflow/src/gridflow/connectors/elexon/endpoints.py)
- [Silver transformer](../../../../../../Python/gridflow/src/gridflow/silver/elexon/remit.py)
- [Pydantic schema](../../../../../../Python/gridflow/src/gridflow/schemas/elexon.py)
- [Gold view/builder](none)
- [Domain: GB Balancing Mechanism](../../../20-domain/markets/gb-balancing-mechanism.md)
