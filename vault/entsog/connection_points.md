---
source: entsog
dataset_key: connection_points
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Connection Points

## Overview

All transmission connection points visible on the ENTSOG map.

This is a reference / inventory dataset — no time dimension, but
inventory does change weekly when ENTSOG approves new operators or points.
The connector schedule is `weekly` in `config/sources.yaml`.

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/connectionPoints` |
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
  "https://transparency.entsog.eu/api/v1/connectionPoints?limit=100&offset=0"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/connection_points/<year>/<month>/<day>/raw_<uuid>.json` (one snapshot per weekly schedule)
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
  "connectionPoints": [
    {
      "pointKey": "DIS-00001",
      "pointLabel": "Distribution (PT)",
      "isSingleOperator": "0",
      "pointTooltip": "",
      "pointEicCode": "?",
      "controlPointType": "O_P_INCOUN_IN_DIS",
      "tpMapX": -128.19,
      "tpMapY": -69.5,
      "pointType": "Distribution Point",
      "commercialType": "Physical",
      "importFromCountryKey": null,
      "importFromCountryLabel": null,
      "hasVirtualPoint": false,
      "virtualPointKey": null,
      "virtualPointLabel": null,
      "hasData": true,
      "isPlanned": false,
      "isInterconnection": true,
      "isImport": false,
      "infrastructureKey": "DIS",
      "infrastructureLabel": "Distribution",
      "isCrossBorder": false,
      "euCrossing": "EU",
      "isInvalid": false,
      "isMacroPoint": null,
      "isCAMRelevant": false,
      "isPipeInPipe": false,
      "isCMPRelevant": false,
      "id": "2DIS-00001",
      "dataSet": "2"
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsog/connection_points.parquet` (single-file overwrite — `reference_dataset=True`)
**Transformer class**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer (subclass ConnectionPointsTransformer)`
**Pydantic schema**: Generic — no Pydantic schema declared
**Dedup key**: `(id)` if present, else inventory key (e.g. `point_key`, `operator_key`)
**Point-in-time field**: `last_update_date_time` (records carry per-row update timestamps)

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| point_key | str | Yes | pointKey |  |
| point_label | str | Yes | pointLabel |  |
| is_single_operator | bool | Yes | isSingleOperator |  |
| point_tooltip | str | Yes | pointTooltip |  |
| point_eic_code | str | Yes | pointEicCode |  |
| control_point_type | str | Yes | controlPointType |  |
| tp_map_x | float | Yes | tpMapX |  |
| tp_map_y | float | Yes | tpMapY |  |
| point_type | str | Yes | pointType |  |
| commercial_type | str | Yes | commercialType |  |
| import_from_country_key | str | Yes | importFromCountryKey |  |
| import_from_country_label | str | Yes | importFromCountryLabel |  |
| has_virtual_point | str | Yes | hasVirtualPoint |  |
| virtual_point_key | str | Yes | virtualPointKey |  |
| virtual_point_label | str | Yes | virtualPointLabel |  |
| has_data | bool | Yes | hasData |  |
| is_planned | bool | Yes | isPlanned |  |
| is_interconnection | bool | Yes | isInterconnection |  |
| is_import | bool | Yes | isImport |  |
| infrastructure_key | str | Yes | infrastructureKey |  |
| infrastructure_label | str | Yes | infrastructureLabel |  |
| is_cross_border | bool | Yes | isCrossBorder |  |
| eu_crossing | str | Yes | euCrossing |  |
| is_invalid | bool | Yes | isInvalid |  |
| is_macro_point | bool | Yes | isMacroPoint |  |
| is_cam_relevant | bool | Yes | isCAMRelevant |  |
| is_pipe_in_pipe | bool | Yes | isPipeInPipe |  |
| is_cmp_relevant | bool | Yes | isCMPRelevant |  |
| id | str | int | Yes | id |  |
| data_set | str | int | Yes | dataSet |  |
| data_provider | str | No | derived | Always `entsog` |
| ingested_at | datetime[UTC] | No | derived | Wall-clock at silver write |

### Silver sample

```python
[
    {
        "point_key": "DIS-00001",
        "point_label": "Distribution (PT)",
        "is_single_operator": "0",
        "point_tooltip": "",
        "point_eic_code": "?",
        "control_point_type": "O_P_INCOUN_IN_DIS",
        "tp_map_x": -128.19,
        "tp_map_y": -69.5,
        "point_type": "Distribution Point",
        "commercial_type": "Physical",
        "import_from_country_key": null,
        "import_from_country_label": null,
        "has_virtual_point": false,
        "virtual_point_key": null,
        "virtual_point_label": null,
        "has_data": true,
        "is_planned": false,
        "is_interconnection": true,
        "is_import": false,
        "infrastructure_key": "DIS",
        "infrastructure_label": "Distribution",
        "is_cross_border": false,
        "eu_crossing": "EU",
        "is_invalid": false,
        "is_macro_point": null,
        "is_cam_relevant": false,
        "is_pipe_in_pipe": false,
        "is_cmp_relevant": false,
        "id": "2DIS-00001",
        "data_set": "2",
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
