---
source: entsog
dataset_key: interconnections
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Interconnections

## Overview

Bidirectional interconnections between two transmission systems.

This is a reference / inventory dataset — no time dimension, but
inventory does change weekly when ENTSOG approves new operators or points.
The connector schedule is `weekly` in `config/sources.yaml`.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/interconnections` |
| Method           | GET |
| Auth             | None (public) |
| Rate limit       | Not vendor-published; project default 5 req/s |
| Pagination       | `limit` + `offset` — pagination is REQUIRED for full inventory; iterate offsets until `count < limit` or fall back to `limit=-1` for a single all-records pull |
| Historical depth | n/a (snapshot) |
| Publication lag  | Vendor inventory updates daily |
| Response format  | JSON |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `limit` | int | Yes | Page size; `-1` returns all | `1000` |
| `offset` | int | No | Page offset (0-based) | `0` |
| `fromCountryKey` | str | No | Restrict to interconnections originating in a country | `UK` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://transparency.entsog.eu/api/v1/interconnections?limit=100&offset=0&fromCountryKey=UK"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/interconnections/<year>/<month>/<day>/raw_<uuid>.json` (one snapshot per weekly schedule)
**Format**: Raw JSON, as-received. Immutable.
**Granularity**: One file per fetch call (full inventory).

### Bronze sample

```json
{
  "meta": {
    "limit": 100,
    "offset": 0,
    "count": 100,
    "total": 100
  },
  "interconnections": [
    {
      "pointKey": "DIS-00015",
      "pointLabel": "Greater Belfast",
      "isSingleOperator": false,
      "pointTpMapX": -113.25,
      "pointTpMapY": 16.43,
      "fromSystemLabel": "NI",
      "fromInfrastructureTypeLabel": "Transmission",
      "fromCountryKey": "UK",
      "fromCountryLabel": "United Kingdom",
      "fromBzKey": "UK-NI------",
      "fromBzLabel": "NI",
      "fromBzLabelLong": "Northern Ireland Balancing Zone",
      "fromOperatorKey": "UK-TSO-0002",
      "fromOperatorLabel": "PTL",
      "fromOperatorLongLabel": "Premier Transmission Ltd",
      "fromPointKey": "DIS-00015",
      "fromPointLabel": "GREATER BELFAST",
      "fromIsCAM": false,
      "fromIsCMP": false,
      "fromBookingPlatformKey": "",
      "fromBookingPlatformLabel": null,
      "fromBookingPlatformURL": null,
      "toIsCAM": null,
      "toIsCMP": null,
      "toBookingPlatformKey": null,
      "toBookingPlatformLabel": null,
      "toBookingPlatformURL": null,
      "fromTsoItemIdentifier": "21Y0000000000492",
      "fromTsoPointLabel": null,
      "fromDirectionKey": "exit",
      "fromHasData": true,
      "toSystemLabel": "Distribution",
      "toInfrastructureTypeLabel": "Distribution",
      "toCountryKey": "UK",
      "toCountryLabel": "United Kingdom",
      "toBzKey": null,
      "toBzLabel": null,
      "toBzLabelLong": null,
      "toOperatorKey": null,
      "toOperatorLabel": null,
      "toOperatorLongLabel": null,
      "toPointKey": null,
      "toPointLabel": null,
      "toDirectionKey": null,
      "toHasData": false,
      "toTsoItemIdentifier": null,
      "toTsoPointLabel": null,
      "validFrom": null,
      "validto": null,
      "lastUpdateDateTime": "May  8 2026  6:43PM",
      "isInvalid": false,
      "entryTpNeMoUsage": null,
      "exitTpNeMoUsage": "Both",
      "id": "4InterconnectionsDIS-00015NIUK-TSO-0002DIS-00015exitDistribution",
      "dataSet": "4"
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsog/interconnections.parquet` (single-file overwrite — `reference_dataset=True`)
**Transformer class**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer (subclass InterconnectionsTransformer)`
**Pydantic schema**: Generic — no Pydantic schema declared
**Dedup key**: `(id)` if present, else inventory key (e.g. `point_key`, `operator_key`)
**Point-in-time field**: `last_update_date_time` (records carry per-row update timestamps)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| point_key | str | Yes | pointKey |  |
| point_label | str | Yes | pointLabel |  |
| is_single_operator | bool | Yes | isSingleOperator |  |
| point_tp_map_x | float | Yes | pointTpMapX |  |
| point_tp_map_y | float | Yes | pointTpMapY |  |
| from_system_label | str | Yes | fromSystemLabel |  |
| from_infrastructure_type_label | str | Yes | fromInfrastructureTypeLabel |  |
| from_country_key | str | Yes | fromCountryKey |  |
| from_country_label | str | Yes | fromCountryLabel |  |
| from_bz_key | str | Yes | fromBzKey |  |
| from_bz_label | str | Yes | fromBzLabel |  |
| from_bz_label_long | str | Yes | fromBzLabelLong |  |
| from_operator_key | str | Yes | fromOperatorKey |  |
| from_operator_label | str | Yes | fromOperatorLabel |  |
| from_operator_long_label | str | Yes | fromOperatorLongLabel |  |
| from_point_key | str | Yes | fromPointKey |  |
| from_point_label | str | Yes | fromPointLabel |  |
| from_is_cam | str | Yes | fromIsCAM |  |
| from_is_cmp | str | Yes | fromIsCMP |  |
| from_booking_platform_key | str | Yes | fromBookingPlatformKey |  |
| from_booking_platform_label | str | Yes | fromBookingPlatformLabel |  |
| from_booking_platform_url | str | Yes | fromBookingPlatformURL |  |
| to_is_cam | str | Yes | toIsCAM |  |
| to_is_cmp | str | Yes | toIsCMP |  |
| to_booking_platform_key | str | Yes | toBookingPlatformKey |  |
| to_booking_platform_label | str | Yes | toBookingPlatformLabel |  |
| to_booking_platform_url | str | Yes | toBookingPlatformURL |  |
| from_tso_item_identifier | str | Yes | fromTsoItemIdentifier |  |
| from_tso_point_label | str | Yes | fromTsoPointLabel |  |
| from_direction_key | str | Yes | fromDirectionKey |  |
| from_has_data | str | Yes | fromHasData |  |
| to_system_label | str | Yes | toSystemLabel |  |
| to_infrastructure_type_label | str | Yes | toInfrastructureTypeLabel |  |
| to_country_key | str | Yes | toCountryKey |  |
| to_country_label | str | Yes | toCountryLabel |  |
| to_bz_key | str | Yes | toBzKey |  |
| to_bz_label | str | Yes | toBzLabel |  |
| to_bz_label_long | str | Yes | toBzLabelLong |  |
| to_operator_key | str | Yes | toOperatorKey |  |
| to_operator_label | str | Yes | toOperatorLabel |  |
| to_operator_long_label | str | Yes | toOperatorLongLabel |  |
| to_point_key | str | Yes | toPointKey |  |
| to_point_label | str | Yes | toPointLabel |  |
| to_direction_key | str | Yes | toDirectionKey |  |
| to_has_data | str | Yes | toHasData |  |
| to_tso_item_identifier | str | Yes | toTsoItemIdentifier |  |
| to_tso_point_label | str | Yes | toTsoPointLabel |  |
| valid_from | datetime[UTC] | Yes | validFrom |  |
| validto | str | Yes | validto |  |
| last_update_date_time | datetime[UTC] | Yes | lastUpdateDateTime |  |
| is_invalid | bool | Yes | isInvalid |  |
| entry_tp_ne_mo_usage | str | Yes | entryTpNeMoUsage |  |
| exit_tp_ne_mo_usage | str | Yes | exitTpNeMoUsage |  |
| id | str | int | Yes | id |  |
| data_set | str | int | Yes | dataSet |  |
| data_provider | str | No | derived | Always `entsog` |
| ingested_at | datetime[UTC] | No | derived | Wall-clock at silver write |

### Silver sample

```python
[
    {
        "point_key": "DIS-00015",
        "point_label": "Greater Belfast",
        "is_single_operator": false,
        "point_tp_map_x": -113.25,
        "point_tp_map_y": 16.43,
        "from_system_label": "NI",
        "from_infrastructure_type_label": "Transmission",
        "from_country_key": "UK",
        "from_country_label": "United Kingdom",
        "from_bz_key": "UK-NI------",
        "from_bz_label": "NI",
        "from_bz_label_long": "Northern Ireland Balancing Zone",
        "from_operator_key": "UK-TSO-0002",
        "from_operator_label": "PTL",
        "from_operator_long_label": "Premier Transmission Ltd",
        "from_point_key": "DIS-00015",
        "from_point_label": "GREATER BELFAST",
        "from_is_cam": false,
        "from_is_cmp": false,
        "from_booking_platform_key": "",
        "from_booking_platform_label": null,
        "from_booking_platform_url": null,
        "to_is_cam": null,
        "to_is_cmp": null,
        "to_booking_platform_key": null,
        "to_booking_platform_label": null,
        "to_booking_platform_url": null,
        "from_tso_item_identifier": "21Y0000000000492",
        "from_tso_point_label": null,
        "from_direction_key": "exit",
        "from_has_data": true,
        "to_system_label": "Distribution",
        "to_infrastructure_type_label": "Distribution",
        "to_country_key": "UK",
        "to_country_label": "United Kingdom",
        "to_bz_key": null,
        "to_bz_label": null,
        "to_bz_label_long": null,
        "to_operator_key": null,
        "to_operator_label": null,
        "to_operator_long_label": null,
        "to_point_key": null,
        "to_point_label": null,
        "to_direction_key": null,
        "to_has_data": false,
        "to_tso_item_identifier": null,
        "to_tso_point_label": null,
        "valid_from": null,
        "validto": null,
        "last_update_date_time": "May  8 2026  6:43PM",
        "is_invalid": false,
        "entry_tp_ne_mo_usage": null,
        "exit_tp_ne_mo_usage": "Both",
        "id": "4InterconnectionsDIS-00015NIUK-TSO-0002DIS-00015exitDistribution",
        "data_set": "4",
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

- **No date filter — pagination required**: reference endpoints accept `limit` + `offset`. Default `limit` is small; pass `limit=1000` (or the full inventory size) and iterate offset for full extracts.
- **`hasData=1` shrinks operatorPointDirections / operators**: filters out points/operators without any operational data. Useful as a discovery filter, but loses validity-period rows for points that recently went dormant.
- **Field-case duplicates**: `isCAMRelevant` (uppercase CAM) appears here while `isCamRelevant` appears in operationalData. Generic silver coalesces both into `is_cam_relevant`.
- **Reference data refresh schedule**: weekly in `config/sources.yaml`. Static-ish, but new points and operator changes do appear when ENTSOG approves them.
- **`bzKey` separators**: balancing zone keys often contain trailing dashes (`UK---------`) — preserve as-is, do not strip.


---

## Implementation delta

- **Pagination required**: full inventory may exceed default page size. Connector defaults to `limit=-1`; live validation used `limit=100` to demonstrate paging shape. For production fetches, prefer `limit=-1` or iterate `offset` in chunks.
- **`reference_dataset=True` write path**: silver writes directly to `<silver_dir>/<dataset>.parquet`, bypassing the date-partitioned layout used by operational datasets.

---

## Modelling notes

TODO — primarily used as join keys for operational datasets.

---

## Links

- [Official API docs (PDF)](https://transparency.entsog.eu/api/archiveDirectories/8/api-manual/TP_REG715_Documentation_TP_API%20-%20v2.1.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsog/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsog/generic.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsog.py)
- [Gold view/builder](none)
