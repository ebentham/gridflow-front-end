---
source: entsog
dataset_key: physical_flows
vendor: ENTSOG Transparency Platform
last_verified: 2026-05-08
layer_coverage: bronze, silver
---

# ENTSOG — Physical Flows (`indicator=Physical Flow`)

## Overview

Hourly/daily physical gas flows at each operator-point-direction (volumetric throughput delivered).

The dataset is one of 19 indicators served by the same `/operationalData`
endpoint. The (operator, point, direction) tuple selects which physical
location to read; the `indicator` query parameter selects which series
(physical flow, nomination, allocation, etc.) is returned. Records carry
the daily `periodFrom` / `periodTo` window and a `value` in `kWh/d` (or
indicator-specific units for content/quality series).

→ Related concepts:
  [Gas day](../../../20-domain/concepts/gas-day.md)
  [Nominations vs allocations](../../../20-domain/markets/gas-nominations.md)

---

## API endpoint

| Property         | Value |
|------------------|-------|
| Base URL         | `https://transparency.entsog.eu/api/v1` |
| Path             | `/operationalData` |
| Method           | GET |
| Auth             | None (public) |
| Rate limit       | Not vendor-published; project default 5 req/s, validation throttled to 1 req/s |
| Pagination       | `limit` + `offset`; project sets `limit=-1` (all records) |
| Historical depth | Approx. 2010 onwards (operator-dependent) |
| Publication lag  | Same-day for `Provisional` flow status; revised within ~1 week |
| Response format  | JSON |
| Indicator | `Physical Flow` (exact-case — vendor rejects lowercase or hyphen variants) |
| Time zone | `timeZone=UCT` (ENTSOG's spelling — note the typo; not `UTC`) |
| `pointDirection` filter | `operatorKey + pointKey + directionKey` concatenated, no separator (e.g. `UK-TSO-0001ITP-00005exit`) — omitted by connector for `physical_flows` |

### Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `indicator` | str | Yes | Exact-case indicator name | `Physical Flow` |
| `from` | date (YYYY-MM-DD) | Yes | Window start (gas day) | `2026-05-06` |
| `to` | date (YYYY-MM-DD) | Yes | Window end (inclusive) | `2026-05-06` |
| `timeZone` | str | Yes | `UCT` (vendor typo for UTC) | `UCT` |
| `periodType` | str | No | `day` (default) or `hour` | `day` |
| `pointDirection` | str / list[str] | No | Connector deliberately omits this for `physical_flows` — full-system query | (none in default) |
| `forceDownload` | bool | No | Bypass server-side cache | `true` |
| `limit` | int | No | `-1` returns all records | `-1` |

### Working curl example

```bash
# physical_flows: connector deliberately omits the pointDirection filter — full-system fetch
curl --ssl-no-revoke -fsS \
  -H "Accept: application/json" \
  "https://transparency.entsog.eu/api/v1/operationalData?from=2026-05-06&to=2026-05-06&timeZone=UCT&indicator=Physical%20Flow&periodType=day&forceDownload=true&limit=1000"
```

---

## Bronze layer

**Path pattern**: `data/bronze/entsog/physical_flows/<year>/<month>/<day>/raw_<uuid>.json`
**Format**: Raw JSON, as-received. Immutable — never modified after write.
**Granularity**: One file per `fetch()` call (one calendar day per file by convention)

### Bronze sample

```json
{
  "meta": {
    "limit": 1000,
    "offset": 0,
    "count": 1,
    "total": 2,
    "query": {
      "indicator": [
        "Physical Flow"
      ],
      "periodType": "day",
      "pointDirection": "UK-TSO-0001ITP-00005exit",
      "from": "2026-05-06",
      "to": "2026-05-06",
      "timeZone": "UCT"
    },
    "timezone": "CET"
  },
  "operationalData": [
    {
      "id": "1Physical Flowday2026-05-062026-05-07UK-TSO-0001ITP-00005exitkWh/d",
      "dataSet": 1,
      "indicator": "Physical Flow",
      "periodType": "day",
      "periodFrom": "2026-05-06T06:00:00+02:00",
      "periodTo": "2026-05-07T06:00:00+02:00",
      "operatorKey": "UK-TSO-0001",
      "tsoEicCode": "21X-GB-A-A0A0A-7",
      "operatorLabel": "National Gas TSO",
      "pointKey": "ITP-00005",
      "pointLabel": "Bacton (IUK)",
      "tsoItemIdentifier": "21Z000000000083P",
      "directionKey": "exit",
      "unit": "kWh/d",
      "itemRemarks": null,
      "generalRemarks": null,
      "value": 203102928,
      "lastUpdateDateTime": "2026-05-08T19:57:09+02:00",
      "isUnlimited": null,
      "flowStatus": "Provisional",
      "interruptionType": null,
      "restorationInformation": null,
      "capacityType": null,
      "capacityBookingStatus": null,
      "isCamRelevant": false,
      "isNA": null,
      "originalPeriodFrom": null,
      "isCmpRelevant": false,
      "bookingPlatformKey": "PRISMA",
      "bookingPlatformLabel": null,
      "bookingPlatformURL": "https://platform.prisma-capacity.eu/",
      "interruptionCalculationRemark": null,
      "pointType": "Cross-Border Transmission IP between EU and ExtEU",
      "idPointType": 23,
      "isArchived": false
    }
  ]
}
```

---

## Silver layer

**Path pattern**: `data/silver/entsog/physical_flows/year=YYYY/month=MM/physical_flows_YYYYMMDD.parquet`
**Transformer class**: `gridflow.silver.entsog.PhysicalFlowsTransformer`
**Pydantic schema**: `gridflow.schemas.entsog.EntsogPhysicalFlow`
**Dedup key**: `(timestamp_utc, point_key, operator_key, direction_key)` — fields uniquely identifying one daily record per series
**Point-in-time field**: `last_update_date_time`

### Silver schema

| Field | Python type | Nullable | Source field | Notes |
|-------|-------------|----------|--------------|-------|
| `timestamp_utc` | `datetime` | No | `periodFrom` | UTC-aware, derived in silver. |
| `point_key` | `str` | No | `pointKey` | Identifies the gas transmission point. Required. |
| `point_label` | `str` | No | `pointLabel` | Default "" in canonical (EntsogPhysicalFlow.point_label: str = ""). |
| `operator_key` | `str` | No | `operatorKey` | Default "" in canonical. |
| `operator_label` | `str` | No | `operatorLabel` | Default "" in canonical. |
| `direction_key` | `str` | No | `directionKey` | Default "" in canonical. "entry" or "exit". |
| `flow_gwh_per_day` | `float` | No | derived from `value` x unit-conversion | Daily physical flow in GWh. Default 0.0 in canonical. |
| `unit` | `str` | No | `unit` | Default "" in canonical. Raw unit from API (e.g. "kWh/d"). |
| `data_provider` | `str` | No | derived | Always `"entsog"` (canonical default). |

### Silver sample

```python
[
    {
        "timestamp_utc": "2026-05-06T04:00:00+00:00",
        "point_key": "ITP-00005",
        "point_label": "Bacton (IUK)",
        "operator_key": "UK-TSO-0001",
        "operator_label": "National Gas TSO",
        "direction_key": "exit",
        "flow_gwh_per_day": 203.102928,
        "unit": "kWh/d",
        "data_provider": "entsog"
    }
]
```

---

## Bronze response keys

The ENTSO-G physical-flows endpoint returns these raw keys in each bronze record. The silver layer consolidates them into the schema table above; raw keys are preserved here for reference only.

Raw bronze fields (not in silver): `id`, `dataSet`, `indicator`, `periodType`, `periodFrom`, `periodTo`, `tsoEicCode`, `tsoItemIdentifier`, `itemRemarks`, `generalRemarks`, `value`, `lastUpdateDateTime`, `isUnlimited`, `flowStatus`, `interruptionType`, `restorationInformation`, `capacityType`, `capacityBookingStatus`, `isCamRelevant`, `isNA`, `originalPeriodFrom`, `isCmpRelevant`, `bookingPlatformKey`, `bookingPlatformLabel`, `bookingPlatformURL`, `interruptionCalculationRemark`, `pointType`, `idPointType`, `isArchived`.

These keys are available in the bronze layer at `data/bronze/entsog/physical_flows/`. The silver transformer selects and normalises only the fields listed in the schema table above.

---

## Gold layer

None implemented.

---

## Known issues and gotchas

- **Indicator string is exact-case**: the connector sends the exact human-readable form (`Physical Flow`, `Nomination`, `Available through UIOLI long-term`). Sending lowercase or hyphen variants returns 404.
- **`timeZone=UCT` (note typo)**: ENTSOG documents the parameter as `timeZone=UCT` rather than `UTC`. The connector spells it the vendor's way. The response `meta.timezone` echoes back `CET` regardless of the request value.
- **`pointDirection` filter**: built as `operatorKey + pointKey + directionKey` concatenated with no separator (e.g. `UK-TSO-0001ITP-00005exit`). Multi-value lists are comma-joined.
- **Missing data returns HTTP 404**: ENTSOG returns `HTTP 404` with body `{"message":"No result found"}` when an indicator/window/point combination has no rows. This is the vendor's empty convention, not a true failure. The connector's retry policy must let 404 surface.
- **Field-case duplicates**: live records may carry both `isCamRelevant` and `isCAMRelevant` shape (or `isCmpRelevant`/`isCMPRelevant`) depending on indicator. The generic silver transformer `_normalise_column_names` collapses these via `pl.coalesce` into one snake_case column.
- **Datetime placeholders**: `lastUpdateDateTime` and `originalPeriodFrom` may be empty strings, `"-"`, `"N/A"`, or human-formatted strings (`"Jan 15 2024 06:00AM"`). `parse_entsog_datetime` returns `None` for unparseable values rather than raising.
- **`directionKey` casing varies**: lowercase (`entry`/`exit`) in `/operationalData`; capitalised (`Exit`) in `/cmpUnsuccessfulRequests`. Don't compare with `==` across families.
- **Period offset is +02:00 (CET)**: even with `timeZone=UCT`, `periodFrom` carries `+02:00` (CEST in summer / `+01:00` in winter). The silver transformer's `parse_entsog_datetime` converts to UTC.

- **`physical_flows` deliberately drops the `pointDirection` filter** in the connector to fetch a full-system snapshot in one call. All other operationalData datasets attach `DEFAULT_POINT_DIRECTIONS` from `endpoints.py`.

---

## Implementation delta

- **No documented discrepancies** for this indicator. Live API returns the indicator name in `meta.fields` matching the code's exact-case constant in `OPERATIONAL_INDICATORS`.
- **Synthetic fixture**: `tests/fixtures/entsog/physical_flows_response.json` carries placeholder `pointKey: "IUK"` and `operatorKey: "OP-IUK"`. Live data uses real keys (`ITP-00005`, `UK-TSO-0001`). Fixture regeneration is deferred (silver tests depend on the placeholder shape).

---

## Modelling notes

- Used as raw input to gas balance / interconnector flow features in `gridflow_models/`.
- Target candidates: directional flow magnitude (entry vs exit per point).
- Filter on `flowStatus == 'Confirmed'` for backtesting; `Provisional` for live model serving.
- Join with `operator_point_directions` to attach country, balancing zone, and CAM-relevant flags.

---

## Links

- [Official API docs (PDF)](https://transparency.entsog.eu/api/archiveDirectories/8/api-manual/TP_REG715_Documentation_TP_API%20-%20v2.1.pdf)
- [Connector source](../../../../src/gridflow/connectors/entsog/endpoints.py)
- [Silver transformer](../../../../src/gridflow/silver/entsog/physical_flows.py)
- [Pydantic schema](../../../../src/gridflow/schemas/entsog.py)
- [Gold view/builder](none)
- [Domain: gas day](../../../20-domain/concepts/gas-day.md)
