---
source: entsog
dataset_key: balancing_zones
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Balancing Zones

## Overview

European balancing zones (one per operator/group).

This is a reference / inventory dataset — no time dimension, but
inventory does change weekly when ENTSOG approves new operators or points.
The connector schedule is `weekly` in `config/sources.yaml`.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/balancingZones` |
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


### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://transparency.entsog.eu/api/v1/balancingZones?limit=100&offset=0"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/balancing_zones/<year>/<month>/<day>/raw_<uuid>.json` (one snapshot per weekly schedule)
**Format**: Raw JSON, as-received. Immutable.
**Granularity**: One file per fetch call (full inventory).

### Bronze sample

```json
{
  "meta": {
    "limit": 100,
    "offset": 0,
    "count": 48,
    "total": 48
  },
  "balancingZones": [
    {
      "tpMapX": -4.13,
      "tpMapY": -37.37,
      "controlPointType": "BALZONE",
      "bzKey": "AT---------",
      "bzLabel": "Austria",
      "bzLabelLong": "Austrian Balancing Zone",
      "bzTooltip": "Austrian Balancing Zone|25Z-VTP-CEGH---5",
      "bzEicCode": "25Z-VTP-CEGH---5",
      "bzManagerKey": "AT-BRP-0001",
      "bzManagerLabel": "Central European Gas Hub AG",
      "replacedSince": null,
      "replacedBy": "",
      "isDeactivated": "0",
      "id": "3AT---------",
      "dataSet": "3"
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsog/balancing_zones.parquet` (single-file overwrite — `reference_dataset=True`)
**Transformer class**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer (subclass BalancingZonesTransformer)`
**Pydantic schema**: Generic — no Pydantic schema declared
**Dedup key**: `(id)` if present, else inventory key (e.g. `point_key`, `operator_key`)
**Point-in-time field**: `last_update_date_time` (records carry per-row update timestamps)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| tp_map_x | float | Yes | tpMapX |  |
| tp_map_y | float | Yes | tpMapY |  |
| control_point_type | str | Yes | controlPointType |  |
| bz_key | str | Yes | bzKey |  |
| bz_label | str | Yes | bzLabel |  |
| bz_label_long | str | Yes | bzLabelLong |  |
| bz_tooltip | str | Yes | bzTooltip |  |
| bz_eic_code | str | Yes | bzEicCode |  |
| bz_manager_key | str | Yes | bzManagerKey |  |
| bz_manager_label | str | Yes | bzManagerLabel |  |
| replaced_since | str | Yes | replacedSince |  |
| replaced_by | str | Yes | replacedBy |  |
| is_deactivated | str | Yes | isDeactivated |  |
| id | str | int | Yes | id |  |
| data_set | str | int | Yes | dataSet |  |
| data_provider | str | No | derived | Always `entsog` |
| ingested_at | datetime[UTC] | No | derived | Wall-clock at silver write |

### Silver sample

```python
[
    {
        "tp_map_x": -4.13,
        "tp_map_y": -37.37,
        "control_point_type": "BALZONE",
        "bz_key": "AT---------",
        "bz_label": "Austria",
        "bz_label_long": "Austrian Balancing Zone",
        "bz_tooltip": "Austrian Balancing Zone|25Z-VTP-CEGH---5",
        "bz_eic_code": "25Z-VTP-CEGH---5",
        "bz_manager_key": "AT-BRP-0001",
        "bz_manager_label": "Central European Gas Hub AG",
        "replaced_since": null,
        "replaced_by": "",
        "is_deactivated": "0",
        "id": "3AT---------",
        "data_set": "3",
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
