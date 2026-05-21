---
source: entsog
dataset_key: urgent_market_messages
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Urgent Market Messages

## Overview

Operator unavailability notifications and other UMM bulletins.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/urgentMarketMessages` |
| Method           | GET |
| Auth             | None (public) |
| Rate limit       | Not vendor-published; project default 5 req/s |
| Pagination       | `limit` + `offset` |
| Historical depth | TODO |
| Publication lag  | TODO |
| Response format  | JSON |
| Pagination control | `limit` + `offset` only — no `from`/`to` accepted |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `limit` | int | Yes | Page size; `-1` returns all | `100` |
| `offset` | int | No | Page offset (0-based) | `0` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://transparency.entsog.eu/api/v1/urgentMarketMessages?limit=100"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/urgent_market_messages/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable.
**Granularity**: One file per fetch call.

### Bronze sample

```json
{
  "meta": {
    "limit": 100,
    "offset": 0,
    "count": 1,
    "total": 100
  },
  "urgentMarketMessages": [
    {
      "id": "5FF6EC12250430000000000000000000038576001",
      "messageId": "0000000000000000000038576_001",
      "marketParticipantKey": "DE-TSO-0009",
      "marketParticipantEic": "21X-DE-C-A0A0A-T",
      "marketParticipantName": "Open Grid Europe",
      "messageType": "Other",
      "publicationDateTime": "2021-01-07T12:08:29+01:00",
      "threadId": "0000000000000000000038576",
      "versionNumber": "001",
      "eventStatus": "Active",
      "eventType": null,
      "eventStart": "2021-10-01T06:00:00+02:00",
      "eventStop": "2030-01-01T06:00:00+01:00",
      "unavailabilityType": null,
      "unavailabilityReason": null,
      "unitMeasure": null,
      "balancingZoneKey": null,
      "balancingZoneEic": null,
      "balancingZoneName": null,
      "affectedAssetName": null,
      "affectedAssetEic": null,
      "direction": null,
      "unavailableCapacity": null,
      "availableCapacity": null,
      "technicalCapacity": null,
      "remarks": "Reduction of firm capacities for yearly auction (01.07.2019): OGE will not offer any firm freely allocable capacities at entry points (Entry-FZK) within the H-Gas market area in the yearly auction from 01.10.2021 onwards. Only interruptible capacities at entry points will be offered for a period of five years.",
      "lastUpdateDateTime": null,
      "sharePointPointId": null,
      "isLatestVersion": "Yes",
      "sharePointPublicationId": null,
      "uMMType": "Feeds",
      "isArchived": null
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsog/urgent_market_messages/year=YYYY/month=MM/urgent_market_messages_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer (subclass UrgentMarketMessagesTransformer)`
**Pydantic schema**: Generic — no Pydantic schema declared
**Dedup key**: `(id)` if present, else all non-`timestamp_utc` columns
**Point-in-time field**: `last_update_date_time` or `publication_date_time` (UMM)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| id | str | int | Yes | id |  |
| message_id | str | Yes | messageId |  |
| market_participant_key | str | Yes | marketParticipantKey |  |
| market_participant_eic | str | Yes | marketParticipantEic |  |
| market_participant_name | str | Yes | marketParticipantName |  |
| message_type | str | Yes | messageType |  |
| publication_date_time | datetime[UTC] | Yes | publicationDateTime |  |
| thread_id | str | Yes | threadId |  |
| version_number | str | Yes | versionNumber |  |
| event_status | str | Yes | eventStatus |  |
| event_type | str | Yes | eventType |  |
| event_start | datetime[UTC] | Yes | eventStart |  |
| event_stop | datetime[UTC] | Yes | eventStop |  |
| unavailability_type | str | Yes | unavailabilityType |  |
| unavailability_reason | str | Yes | unavailabilityReason |  |
| unit_measure | str | Yes | unitMeasure |  |
| balancing_zone_key | str | Yes | balancingZoneKey |  |
| balancing_zone_eic | str | Yes | balancingZoneEic |  |
| balancing_zone_name | str | Yes | balancingZoneName |  |
| affected_asset_name | str | Yes | affectedAssetName |  |
| affected_asset_eic | str | Yes | affectedAssetEic |  |
| direction | str | Yes | direction |  |
| unavailable_capacity | float | Yes | unavailableCapacity |  |
| available_capacity | float | Yes | availableCapacity |  |
| technical_capacity | float | Yes | technicalCapacity |  |
| remarks | str | Yes | remarks |  |
| last_update_date_time | datetime[UTC] | Yes | lastUpdateDateTime |  |
| share_point_point_id | str | Yes | sharePointPointId |  |
| is_latest_version | bool | Yes | isLatestVersion |  |
| share_point_publication_id | str | Yes | sharePointPublicationId |  |
| u_mm_type | str | Yes | uMMType |  |
| is_archived | bool | Yes | isArchived |  |
| data_provider | str | No | derived | Always `entsog` |
| ingested_at | datetime[UTC] | No | derived | Wall-clock at silver write |

### Silver sample

```python
[
    {
        "id": "5FF6EC12250430000000000000000000038576001",
        "message_id": "0000000000000000000038576_001",
        "market_participant_key": "DE-TSO-0009",
        "market_participant_eic": "21X-DE-C-A0A0A-T",
        "market_participant_name": "Open Grid Europe",
        "message_type": "Other",
        "publication_date_time": "2021-01-07T12:08:29+01:00",
        "thread_id": "0000000000000000000038576",
        "version_number": "001",
        "event_status": "Active",
        "event_type": null,
        "event_start": "2021-10-01T06:00:00+02:00",
        "event_stop": "2030-01-01T06:00:00+01:00",
        "unavailability_type": null,
        "unavailability_reason": null,
        "unit_measure": null,
        "balancing_zone_key": null,
        "balancing_zone_eic": null,
        "balancing_zone_name": null,
        "affected_asset_name": null,
        "affected_asset_eic": null,
        "direction": null,
        "unavailable_capacity": null,
        "available_capacity": null,
        "technical_capacity": null,
        "remarks": "Reduction of firm capacities for yearly auction (01.07.2019): OGE will not offer any firm freely allocable capacities at entry points (Entry-FZK) within the H-Gas market area in the yearly auction from 01.10.2021 onwards. Only interruptible capacities at entry points will be offered for a period of five years.",
        "last_update_date_time": null,
        "share_point_point_id": null,
        "is_latest_version": "Yes",
        "share_point_publication_id": null,
        "u_mm_type": "Feeds",
        "is_archived": null,
        "data_provider": "entsog",
        "ingested_at": "2026-05-08T18:00:00+00:00"
    }
]
```

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **Different schema from operationalData**: UMM has `messageId`, `eventStart`, `eventStop`, `unavailabilityType`, `affectedAssetEic` — designed for human-readable bulletins not numeric series.
- **No date filter accepted on the URL**: `from`/`to` are ignored; pagination via `limit`/`offset` is the only window control. `requires_dates=False` in the connector.
- **`messageType`**: `'unavailability'` is the dominant category but other types (e.g. `news`) appear. Don't filter on it without first inspecting.
- **`isLatestVersion`**: messages are versioned via `threadId`/`versionNumber`; downstream tooling should keep only `isLatestVersion=true`.

- **Indicator string is exact-case**: the connector sends the exact human-readable form (`Physical Flow`, `Nomination`, `Available through UIOLI long-term`). Sending lowercase or hyphen variants returns 404.
- **`timeZone=UCT` (note typo)**: ENTSOG documents the parameter as `timeZone=UCT` rather than `UTC`. The connector spells it the vendor's way. The response `meta.timezone` echoes back `CET` regardless of the request value.
- **`pointDirection` filter**: built as `operatorKey + pointKey + directionKey` concatenated with no separator (e.g. `UK-TSO-0001ITP-00005exit`). Multi-value lists are comma-joined.
- **Missing data returns HTTP 404**: ENTSOG returns `HTTP 404` with body `{"message":"No result found"}` when an indicator/window/point combination has no rows. This is the vendor's empty convention, not a true failure. The connector's retry policy must let 404 surface.
- **Field-case duplicates**: live records may carry both `isCamRelevant` and `isCAMRelevant` shape (or `isCmpRelevant`/`isCMPRelevant`) depending on indicator. The generic silver transformer `_normalise_column_names` collapses these via `pl.coalesce` into one snake_case column.
- **Datetime placeholders**: `lastUpdateDateTime` and `originalPeriodFrom` may be empty strings, `"-"`, `"N/A"`, or human-formatted strings (`"Jan 15 2024 06:00AM"`). `parse_entsog_datetime` returns `None` for unparseable values rather than raising.
- **`directionKey` casing varies**: lowercase (`entry`/`exit`) in `/operationalData`; capitalised (`Exit`) in `/cmpUnsuccessfulRequests`. Don't compare with `==` across families.
- **Period offset is +02:00 (CET)**: even with `timeZone=UCT`, `periodFrom` carries `+02:00` (CEST in summer / `+01:00` in winter). The silver transformer's `parse_entsog_datetime` converts to UTC.


---

## Implementation delta

- **Vendor empty convention**: HTTP 404 + `{"message":"No result found"}`.
- **Generic transformer**: dynamic schema; columns derived from live response.
- **`requires_dates=False` for UMM**: connector does not pass `from`/`to`. Date filtering is downstream.

---

## Modelling notes

TODO

---

## Links

- [Official API docs (PDF)](https://transparency.entsog.eu/api/archiveDirectories/8/api-manual/TP_REG715_Documentation_TP_API%20-%20v2.1.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsog/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsog/generic.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsog.py)
- [Gold view/builder](none)
