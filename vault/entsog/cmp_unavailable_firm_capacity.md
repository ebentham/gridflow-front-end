---
source: entsog
dataset_key: cmp_unavailable_firm_capacity
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Cmp Unavailable Firm Capacity

## Overview

CMP unavailable firm capacity — firm capacity declared unavailable but allocated to others.

→ Related concepts:
  [Gas day](../../../20-domain/concepts/gas-day.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/cmpUnavailables` |
| Method           | GET |
| Auth             | None (public) |
| Rate limit       | Not vendor-published; project default 5 req/s |
| Pagination       | `limit` + `offset`; project sets `limit=-1` |
| Historical depth | TODO |
| Publication lag  | TODO |
| Response format  | JSON |
| Time zone | `timeZone=UCT` (ENTSOG's spelling — vendor typo) |
| `pointDirection` filter | Optional. Same `operatorKey + pointKey + directionKey` form as `/operationalData` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `from` | date (YYYY-MM-DD) | Yes | Window start | `2026-05-06` |
| `to` | date (YYYY-MM-DD) | Yes | Window end | `2026-05-06` |
| `timeZone` | str | Yes | `UCT` | `UCT` |
| `periodType` | str | No | `day` | `day` |
| `pointDirection` | str / list[str] | No | Optional point filter | `UK-TSO-0001ITP-00005exit` |
| `forceDownload` | bool | No | Bypass cache | `true` |
| `limit` | int | No | `-1` returns all | `-1` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://transparency.entsog.eu/api/v1/cmpUnavailables?from=2026-05-06&to=2026-05-06&timeZone=UCT&periodType=day&forceDownload=true&limit=1000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/cmp_unavailable_firm_capacity/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable.
**Granularity**: One file per fetch call (per calendar day window).

### Bronze sample

```json
{
  "meta": {
    "limit": 1000,
    "offset": 0,
    "count": 1,
    "total": 269,
    "query": {
      "from": "2026-05-06",
      "to": "2026-05-06",
      "timeZone": "UCT",
      "periodType": "day"
    },
    "timezone": "CET"
  },
  "cmpUnavailables": [
    {
      "periodFrom": "2015-10-01T00:00:00+02:00",
      "periodTo": "2026-09-30T00:00:00+02:00",
      "operatorKey": "FR-TSO-0003",
      "tsoEicCode": "21X-FR-A-A0A0A-S",
      "operatorLabel": "GRTgaz",
      "pointKey": "ITP-00039",
      "pointLabel": "Oltingue (FR) / Rodersdorf (CH)",
      "tsoItemIdentifier": "21Z000000000037W",
      "directionKey": "exit",
      "allocationProcess": "Auction",
      "auctionStartDate": "N/A",
      "itemRemarks": "N/A",
      "generalRemarks": null,
      "lastUpdateDateTime": "2020-11-27T18:01:55+01:00",
      "pointType": "Cross-Border Transmission IP between EU and Non-EU",
      "idPointType": 14,
      "id": "42015-09-30 22:00:00 +00:002026-09-29 22:00:00 +00:0021X-FR-A-A0A0A-SFR-TSO-0003ITP-00039exitAuction",
      "dataSet": 4,
      "indicator": null,
      "periodType": null,
      "unit": null,
      "value": null,
      "isUnlimited": null,
      "flowStatus": "",
      "interruptionType": null,
      "restorationInformation": null,
      "capacityType": null,
      "capacityBookingStatus": null,
      "isCamRelevant": null,
      "isNA": null,
      "originalPeriodFrom": null,
      "isCmpRelevant": null,
      "bookingPlatformKey": null,
      "bookingPlatformLabel": null,
      "bookingPlatformURL": null,
      "interruptionCalculationRemark": null,
      "isArchived": false
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsog/cmp_unavailable_firm_capacity/year=YYYY/month=MM/cmp_unavailable_firm_capacity_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer (subclass CmpUnavailableFirmCapacityTransformer)`
**Pydantic schema**: Generic — no Pydantic schema declared
**Dedup key**: `(id)` if present, else all non-`timestamp_utc` columns
**Point-in-time field**: `last_update_date_time`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| period_from | datetime[UTC] | Yes | periodFrom |  |
| period_to | datetime[UTC] | Yes | periodTo |  |
| operator_key | str | Yes | operatorKey |  |
| tso_eic_code | str | Yes | tsoEicCode |  |
| operator_label | str | Yes | operatorLabel |  |
| point_key | str | Yes | pointKey |  |
| point_label | str | Yes | pointLabel |  |
| tso_item_identifier | str | Yes | tsoItemIdentifier |  |
| direction_key | str | Yes | directionKey |  |
| allocation_process | str | Yes | allocationProcess |  |
| auction_start_date | datetime[UTC] | Yes | auctionStartDate |  |
| item_remarks | str | Yes | itemRemarks |  |
| general_remarks | str | Yes | generalRemarks |  |
| last_update_date_time | datetime[UTC] | Yes | lastUpdateDateTime |  |
| point_type | str | Yes | pointType |  |
| id_point_type | str | Yes | idPointType |  |
| id | str | int | Yes | id |  |
| data_set | str | int | Yes | dataSet |  |
| indicator | str | Yes | indicator |  |
| period_type | str | Yes | periodType |  |
| unit | str | Yes | unit |  |
| value | float | Yes | value |  |
| is_unlimited | bool | Yes | isUnlimited |  |
| flow_status | str | Yes | flowStatus |  |
| interruption_type | str | Yes | interruptionType |  |
| restoration_information | str | Yes | restorationInformation |  |
| capacity_type | str | Yes | capacityType |  |
| capacity_booking_status | str | Yes | capacityBookingStatus |  |
| is_cam_relevant | bool | Yes | isCamRelevant |  |
| is_na | str | Yes | isNA |  |
| original_period_from | datetime[UTC] | Yes | originalPeriodFrom |  |
| is_cmp_relevant | bool | Yes | isCmpRelevant |  |
| booking_platform_key | str | Yes | bookingPlatformKey |  |
| booking_platform_label | str | Yes | bookingPlatformLabel |  |
| booking_platform_url | str | Yes | bookingPlatformURL |  |
| interruption_calculation_remark | str | Yes | interruptionCalculationRemark |  |
| is_archived | bool | Yes | isArchived |  |
| data_provider | str | No | derived | Always `entsog` |
| ingested_at | datetime[UTC] | No | derived | Wall-clock at silver write |

### Silver sample

```python
[
    {
        "period_from": "2015-10-01T00:00:00+02:00",
        "period_to": "2026-09-30T00:00:00+02:00",
        "operator_key": "FR-TSO-0003",
        "tso_eic_code": "21X-FR-A-A0A0A-S",
        "operator_label": "GRTgaz",
        "point_key": "ITP-00039",
        "point_label": "Oltingue (FR) / Rodersdorf (CH)",
        "tso_item_identifier": "21Z000000000037W",
        "direction_key": "exit",
        "allocation_process": "Auction",
        "auction_start_date": "N/A",
        "item_remarks": "N/A",
        "general_remarks": null,
        "last_update_date_time": "2020-11-27T18:01:55+01:00",
        "point_type": "Cross-Border Transmission IP between EU and Non-EU",
        "id_point_type": 14,
        "id": "42015-09-30 22:00:00 +00:002026-09-29 22:00:00 +00:0021X-FR-A-A0A0A-SFR-TSO-0003ITP-00039exitAuction",
        "data_set": 4,
        "indicator": null,
        "period_type": null,
        "unit": null,
        "value": null,
        "is_unlimited": null,
        "flow_status": "",
        "interruption_type": null,
        "restoration_information": null,
        "capacity_type": null,
        "capacity_booking_status": null,
        "is_cam_relevant": null,
        "is_na": null,
        "original_period_from": null,
        "is_cmp_relevant": null,
        "booking_platform_key": null,
        "booking_platform_label": null,
        "booking_platform_url": null,
        "interruption_calculation_remark": null,
        "is_archived": false,
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

- **Date-bound but light**: CMP family endpoints accept `from` / `to` but most rows describe future capacity (`capacityFrom` / `capacityTo` years ahead). Don't dedup on period alone.
- **`isCAMRelevant` (uppercase CAM)**: CMP family uses the uppercase variant. Generic silver coalesces with operationalData's `isCamRelevant`.
- **`directionKey` capitalised**: `Exit` not `exit` in `/cmpUnsuccessfulRequests`. Compare case-insensitively.
- **HTTP 404 = empty**: same vendor empty convention applies.

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

- **Vendor empty convention**: HTTP 404 + `{"message":"No result found"}` for empty windows.
- **Generic silver transformer**: produces dynamic snake_case columns from the camelCase API fields. The CMP family carries `auctionFrom`/`auctionTo`/`capacityFrom`/`capacityTo` placeholders such as `"N/A"` — silver `parse_entsog_datetime` returns `None` for these.

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
