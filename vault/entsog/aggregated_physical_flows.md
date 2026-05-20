---
source: entsog
dataset_key: aggregated_physical_flows
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Aggregated Physical Flows

## Overview

Zone-level aggregated physical flows by adjacent system (Production / Storage / LNG / interconnection).

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/aggregatedData` |
| Method           | GET |
| Auth             | None (public) |
| Rate limit       | Not vendor-published; project default 5 req/s |
| Pagination       | `limit` + `offset`; project sets `limit=-1` |
| Historical depth | TODO |
| Publication lag  | TODO |
| Response format  | JSON |
| Indicator | `Physical Flow` (only indicator served by `/aggregatedData`) |
| Time zone | `timeZone=UCT` (ENTSOG's spelling) |
| `pointDirection` filter | aggregate-zone form (`bzKey + operatorKey + directionKey + adjacentSystemsKey`) |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `from` | date | Yes | Window start | `2026-05-06` |
| `to` | date | Yes | Window end | `2026-05-06` |
| `timeZone` | str | Yes | `UCT` | `UCT` |
| `pointDirection` | str / list[str] | No | aggregate-zone form (`bzKey + operatorKey + directionKey + adjacentSystemsKey`) | see Working curl example |
| `forceDownload` | bool | No | Bypass cache | `true` |
| `limit` | int | No | `-1` returns all | `-1` |

### Working curl example

```bash
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://transparency.entsog.eu/api/v1/aggregatedData?from=2026-05-06&to=2026-05-06&timeZone=UCT&periodType=day&forceDownload=true&limit=1000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/aggregated_physical_flows/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable.
**Granularity**: One file per fetch call.

### Bronze sample

```json
{
  "meta": {
    "limit": 1000,
    "offset": 0,
    "count": 1,
    "total": 2,
    "query": {
      "from": "2026-05-06",
      "to": "2026-05-06",
      "timeZone": "UCT"
    },
    "timezone": "CET"
  },
  "aggregatedData": [
    {
      "id": "1AggregatesUKUK---------UK-TSO-0001entryLNG Terminals2026-05-06T00:00:00+00:002026-05-07T00:00:00+00:00Physical Flow",
      "dataSet": "1",
      "dataSetLabel": "Aggregates",
      "indicator": "Physical Flow",
      "periodType": "day",
      "periodFrom": "2026-05-06T06:00:00+02:00",
      "periodTo": "2026-05-07T06:00:00+02:00",
      "countryKey": "UK",
      "countryLabel": "United Kingdom",
      "bzKey": "UK---------",
      "bzShort": "UK",
      "bzLong": "British Balancing Zone",
      "operatorKey": "UK-TSO-0001",
      "operatorLabel": "National Gas Transmission",
      "tsoEicCode": "21X-GB-A-A0A0A-7",
      "directionKey": "entry",
      "adjacentSystemsKey": "LNG Terminals",
      "adjacentSystemsLabel": "LNG Terminals",
      "year": "2026",
      "month": "5",
      "day": "6",
      "unit": "kWh/d",
      "value": 100259283,
      "countPointPresents": "2",
      "flowStatus": "Provisionnal",
      "pointsNames": "Isle of Grain|Milford Haven",
      "lastUpdateDateTime": "2026-05-08T18:33:42+02:00"
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsog/aggregated_physical_flows/year=YYYY/month=MM/aggregated_physical_flows_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsog.generic.GenericEntsogJsonTransformer (subclass AggregatedPhysicalFlowsTransformer)`
**Pydantic schema**: Generic — no Pydantic schema declared
**Dedup key**: `(id)` if present, else all non-`timestamp_utc` columns
**Point-in-time field**: `last_update_date_time`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| id | str | int | Yes | id |  |
| data_set | str | int | Yes | dataSet |  |
| data_set_label | str | Yes | dataSetLabel |  |
| indicator | str | Yes | indicator |  |
| period_type | str | Yes | periodType |  |
| period_from | datetime[UTC] | Yes | periodFrom |  |
| period_to | datetime[UTC] | Yes | periodTo |  |
| country_key | str | Yes | countryKey |  |
| country_label | str | Yes | countryLabel |  |
| bz_key | str | Yes | bzKey |  |
| bz_short | str | Yes | bzShort |  |
| bz_long | str | Yes | bzLong |  |
| operator_key | str | Yes | operatorKey |  |
| operator_label | str | Yes | operatorLabel |  |
| tso_eic_code | str | Yes | tsoEicCode |  |
| direction_key | str | Yes | directionKey |  |
| adjacent_systems_key | str | Yes | adjacentSystemsKey |  |
| adjacent_systems_label | str | Yes | adjacentSystemsLabel |  |
| year | str | Yes | year |  |
| month | str | Yes | month |  |
| day | str | Yes | day |  |
| unit | str | Yes | unit |  |
| value | float | Yes | value |  |
| count_point_presents | float | Yes | countPointPresents |  |
| flow_status | str | Yes | flowStatus |  |
| points_names | str | Yes | pointsNames |  |
| last_update_date_time | datetime[UTC] | Yes | lastUpdateDateTime |  |
| data_provider | str | No | derived | Always `entsog` |
| ingested_at | datetime[UTC] | No | derived | Wall-clock at silver write |

### Silver sample

```python
[
    {
        "id": "1AggregatesUKUK---------UK-TSO-0001entryLNG Terminals2026-05-06T00:00:00+00:002026-05-07T00:00:00+00:00Physical Flow",
        "data_set": "1",
        "data_set_label": "Aggregates",
        "indicator": "Physical Flow",
        "period_type": "day",
        "period_from": "2026-05-06T06:00:00+02:00",
        "period_to": "2026-05-07T06:00:00+02:00",
        "country_key": "UK",
        "country_label": "United Kingdom",
        "bz_key": "UK---------",
        "bz_short": "UK",
        "bz_long": "British Balancing Zone",
        "operator_key": "UK-TSO-0001",
        "operator_label": "National Gas Transmission",
        "tso_eic_code": "21X-GB-A-A0A0A-7",
        "direction_key": "entry",
        "adjacent_systems_key": "LNG Terminals",
        "adjacent_systems_label": "LNG Terminals",
        "year": "2026",
        "month": "5",
        "day": "6",
        "unit": "kWh/d",
        "value": 100259283,
        "count_point_presents": "2",
        "flow_status": "Provisionnal",
        "points_names": "Isle of Grain|Milford Haven",
        "last_update_date_time": "2026-05-08T18:33:42+02:00",
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

- **`pointDirection` is the aggregate-zone form**: `bzKey + operatorKey + directionKey + adjacentSystemsKey` (e.g. `UK---------UK-TSO-0001entryLNG Terminals`). NOT the per-point form used in `/operationalData`.
- **`adjacentSystemsKey` enumerates source category**: `LNG Terminals`, `Production`, `Storage`, `Distribution`, plus zone-pair keys for cross-border aggregates.
- **`flowStatus: "Provisionnal"`** (vendor typo): preserve the string as-is in bronze, normalise downstream if needed.
- **HTTP 404 = empty**: as elsewhere.

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
- **Generic transformer**: dynamic schema. Columns are derived from whatever the live response contains.

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
